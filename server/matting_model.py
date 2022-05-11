import sqlite3

from time import sleep, time
import sys
import torch
import shutil
import json

from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torchvision import transforms as T
from torchvision.transforms.functional import to_pil_image
from threading import Thread
from tqdm import tqdm
from PIL import Image
from threading import Thread


''' include model dependency '''
# model
from BGMv2.dataset import VideoDataset, ZipDataset, ImagesDataset
from BGMv2.dataset import augmentation as A
from BGMv2.model import MattingBase, MattingRefine
from BGMv2.inference_utils import HomographicAlignment

# mask r-cnn
from mask_rcnn import *

def model_main_function():
    with open('appconfig.json', 'r') as jsonfile:
        app_info = json.load(jsonfile)
    # database connection
    # print(app_info)
    # model
    model_setting = {
        "backbone" :'resnet50',
        "backbone_scale" :0.25,
        "refine_mode" : 'sampling',
        "refine_sample_pixels" : 80_000,
        "refine_threshold" : 0.7,
        "refine_kernel_size" : 3,
        "checkpoint_dir" : os.path.join("BGMv2", "checkpoint", "epoch-9.pth")
    }
    model = get_model(model_setting)
    #model = "none"
    while(True):
        # dataset 連線
        queue = sqlite3.connect(
            app_info['QUEUE'],
            detect_types=sqlite3.PARSE_COLNAMES
        )
        queue.row_factory = sqlite3.Row

        # dataset request: get current waiting queue
        waiting_queue = queue.execute(
            "SELECT * FROM Queue ORDER BY created"
        ).fetchall()
        waiting_queue = [ dict(result) for result in waiting_queue]

        for data in waiting_queue:
            print("Processing data: ", data)
            video_name = model_infer(model, app_info, data)
            #video_name = data['v_path'].split(os.sep)[-1] # 暫時
            db = sqlite3.connect(
                app_info['DATABASE'],
                detect_types=sqlite3.PARSE_COLNAMES
            )
            db.row_factory = sqlite3.Row

            nb_name = data['nb_path'].split(os.sep)[-1] # 這個其實是 sa_name。
            db.execute(
                """INSERT INTO video (v_name, vsa_name, b_name, bsa_name, author_id, nb_name) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (data['v_name'], video_name, 'none', 'none', data['author_id'], nb_name)
            )
            db.commit()
            db.close()

        waiting_queue = [(c['created'],) for c in waiting_queue]
        queue.executemany(
            """DELETE FROM Queue
            WHERE created = (?)
            """,
            waiting_queue
        )
        queue.commit()
        queue.close()

        sleep(10)
    return

# ---------------- Model infer utils ------------------------
cuda = "cuda"
device = torch.device(cuda)

class VideoWriter:
    def __init__(self, path, frame_rate, width, height):
        self.out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, (width, height))
        
    def add_batch(self, frames):
        frames = frames.mul(255).byte()
        frames = frames.cpu().permute(0, 2, 3, 1).numpy()
        for i in range(frames.shape[0]):
            frame = frames[i]
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.out.write(frame)
            

class ImageSequenceWriter:
    def __init__(self, path, extension):
        self.path = path
        self.extension = extension
        self.index = 0
        os.makedirs(path)
        
    def add_batch(self, frames):
        Thread(target=self._add_batch, args=(frames, self.index)).start()
        self.index += frames.shape[0]
            
    def _add_batch(self, frames, index):
        frames = frames.cpu()
        for i in range(frames.shape[0]):
            frame = frames[i]
            frame = to_pil_image(frame)
            frame.save(os.path.join(self.path, str(index + i).zfill(5) + '.' + self.extension))


def writer(img, path):
    img = to_pil_image(img[0].cpu())
    img.save(path)


# Mask-RCNN 取得 mask
def get_mask(src):
    img = src.cpu().permute(0,2,3,1).numpy().astype(np.float32)
    batch, h, w, c= img.shape
    mask = np.zeros((batch,1,h,w), np.float32)
    for i in range(len(img)):
        outputs = predictor(cv2.cvtColor(img[i]*255, cv2.COLOR_RGB2BGR))
        pred_class = outputs["instances"].get('pred_classes').to('cpu').numpy()

        if(0 in pred_class):
            #print("find people!!")
            pred_mask = outputs["instances"].get('pred_masks').to('cpu').numpy()
            index = np.where(pred_class == 0)
            for dex in index[0]:
                #print("mask: ", mask[i][0].shape)
                #print("pred: ", pred_mask[dex].shape)
                mask[i][0] += pred_mask[dex]
    
    return torch.from_numpy(mask).type(torch.float32).cuda(non_blocking=True)


# 以下先不要用
'''
獲得 model，所有 model 需要的設應都放在 setting 裡面
'''
def get_model(setting):
    model = MattingRefine(
        setting['backbone'],
        setting['backbone_scale'],
        setting['refine_mode'],
        setting['refine_sample_pixels'],
        setting['refine_threshold'],
        setting['refine_kernel_size']
    )
    
    model = model.to(device).eval()
    model.load_state_dict(torch.load(setting['checkpoint_dir'], map_location=device), strict=False)
    return model


'''

'''
def isVideo(type: str):
    return (type[-3:].lower() == 'mp4' or type[-3:].lower() == 'avi')

def isImage(type: str):
    return (type[-3:].lower() == 'jpg' or type[-3:].lower() == 'png')

def model_infer(model, app_info, data):
    if(isVideo(data['v_path'])):
        return model_infer_video(model, app_info, data)
    elif(isImage(data['v_path'])):
        return model_infer_image(model, app_info, data)
    else:
        return False

'''
回傳 vsa_name。
'''
def model_infer_video(model, app_info, data):
    v_name = data['v_name']
    vsa_name = v_name[:-4] + str(time()) + v_name[-4:]
    v_path  = data['v_path']
    b_path = data['b_path']
    nb_path = data['nb_path']
    opt = data['opt']

    vid = VideoDataset(v_path)
    bgr = [Image.open(b_path).convert('RGB')]
    if(isVideo(nb_path)):
        new_bgr = VideoDataset(nb_path)
    elif(isImage(nb_path)):
        new_bgr = [Image.open(nb_path).convert('RGB')]

    shape = (vid.width, vid.height)

    dataset = ZipDataset([vid, bgr, new_bgr], transforms=A.PairCompose([
        A.PairApply(nn.Identity()),
        A.PairApply(nn.Identity()),
        A.PairApply(T.ToTensor())
    ]))

    path = (app_info['UPLOAD_FOLDER'], data['author'], 'videos')
    output_dir = os.path.join(*path)
    writer = VideoWriter(os.path.join(output_dir, vsa_name), vid.frame_rate, *shape)
    
    # 決定要不要載入風格轉換模型
    opt = int(opt)
    if(opt % 2 == 1):
        STF_checkpoint = os.path.join("StyleTransfer","checkpoint","model_00001.pth")
        STF_model = (torch.load(STF_checkpoint, map_location=lambda storage, loc: storage))
        STF_model = STF_model.to(device).eval().type(torch.half)

    with torch.no_grad():
        for input_batch in tqdm(DataLoader(dataset, batch_size=1, pin_memory=True)):
            src, bgr, tgt_bgr = input_batch
            src = src.to(device, non_blocking=True)
            bgr = bgr.to(device, non_blocking=True)
            tgt_bgr = tgt_bgr.to(device, non_blocking=True)

            reshape = T.Resize(src.shape[2:])
            tgt_bgr = reshape(tgt_bgr)
            bgr = reshape(bgr)

            mask = get_mask(src)

            pha, fgr, _, _, err, ref = model(src, bgr, mask)
            com = fgr * pha + tgt_bgr * (1-pha)
            
            if (opt % 2 == 1):
                com = STF_model(com.to(torch.float16))
                com =  (com.clamp(-1,1) + 1) * 0.5
            

            writer.add_batch(com)

    return vsa_name

def model_infer_image(model, app_info, data):
    v_name = data['v_name']
    vsa_name = v_name[:-4] + str(time()) + v_name[-4:]
    v_path  = data['v_path']
    b_path = data['b_path']
    nb_path = data['nb_path']
    opt = data['opt']

    vid = [Image.open(v_path).convert('RGB')]
    bgr = [Image.open(b_path).convert('RGB')]
    new_bgr = [Image.open(nb_path).convert('RGB')]

    dataset = ZipDataset([
        vid, bgr, new_bgr
    ], transforms=A.PairCompose([
        A.PairApply(nn.Identity()),
        A.PairApply(T.ToTensor())
    ]))

    path = (app_info['UPLOAD_FOLDER'], data['author'], 'videos')
    output_dir = os.path.join(*path)

    # 決定要不要載入風格轉換模型
    opt = int(opt)
    if(opt % 2 == 1):
        STF_checkpoint = os.path.join("StyleTransfer","checkpoint","model_00001.pth")
        STF_model = (torch.load(STF_checkpoint, map_location=lambda storage, loc: storage))
        STF_model = STF_model.to(device).eval().type(torch.half)

    with torch.no_grad():
        for (src, bgr, tgt_bgr) in tqdm(DataLoader(dataset, batch_size=1, pin_memory=True)):
            src = src.to(device, non_blocking=True)
            bgr = bgr.to(device, non_blocking=True)
            tgt_bgr = tgt_bgr.to(device, non_blocking=True)

            reshape = T.Resize(src.shape[2:])
            tgt_bgr = reshape(tgt_bgr)
            bgr = reshape(bgr)

            mask = get_mask(src)

            pha, fgr, _, _, err, ref = model(src, bgr, mask)

            com = fgr * pha + tgt_bgr * (1-pha)
            if (opt % 2 == 1):
                com = STF_model(com.to(torch.float16))
                com =  (com.clamp(-1,1) + 1) * 0.5
            
            Thread(target=writer, args=(com, os.path.join(output_dir, vsa_name))).start()
            

    return vsa_name



if __name__ == "__main__":
    model_main_function()