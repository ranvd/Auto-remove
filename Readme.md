# Announce
There are three ML model in this project.
* BGMv2 (matting model)
* Few-Shot-Patch-Based-Training (style transfer)
* Mask RCNN (segmentation model)

### matting model
Our matting model is modified from https://github.com/PeterL1n/BackgroundMattingV2.git
### style Transfer model
Our Style Transfer model is from https://github.com/OndrejTexler/Few-Shot-Patch-Based-Training 
### Mask RCNN
We use detectron2, from Facebook, as our Mask RCNN model.
https://detectron2.readthedocs.io/en/latest/tutorials/install.html

# Description
This project is NDHU undergraduate project. Our project name is **Robust automatic video matting model on website service**. In the Project we modified the BGMv2 model into specific purpose and provide as a matting service on website.

The back-end of this server is done by `Flask`, and ML model is implemented with `Pytorch`.

# Requirement

* GPU 4G(minimum, fit in some of the FHD resolution video)
* GPU 8G(recommand)

```
torch 1.10.1
detectron2
Flask
```

# Run
step 1.
* move to `server` folder.

step 2.
* type `flask init-db`
* type `flask run`

step 3.
* run ML model by runing `matting_model.py`.

## Caution
* If you are in Linux, and runing `activate.sh`. This script will build the service on your real IP which I highly don't recommand.

# Model weight
* style transfer: https://drive.google.com/file/d/1JXPm0qKmOh6rV8HcvLEN5PZv7BmW_Zw0/view?usp=sharing
  * put this weight under `/server/StyleTransfer/checkpoint`
* matting: https://drive.google.com/file/d/1E1OQU20Z_yPMv5rtgSQrLhyDFTtvSWkm/view?usp=sharing
  * put this weight under `/server/BGMv2/checkpoint`
