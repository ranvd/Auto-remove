import os
UPLOAD_FOLDER = '/home/minired/GraduationProject/Auto-remove/server/uploads'
os.remove(os.path.join(UPLOAD_FOLDER, "root", "video.mp4"))
