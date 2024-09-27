# -*- coding: utf-8 -*-
"""Final_Yolo_7

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ReeB2sJw-2G8BiYOsXXkaJfLaff_qg2p

# Initiate YOLOv7
"""

# Commented out IPython magic to ensure Python compatibility.
!git clone https://github.com/WongKinYiu/yolov7.git       # clone
# %cd yolov7
!pip install -r requirements.txt      # install modules
# !wget https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt # download pretrained weight

"""# Insert the dataset from Google Drive"""

from google.colab import drive
drive.mount('/content/drive')

!unzip "/content/drive/MyDrive/final_dataset.zip" -d /content/yolov7
#!unzip "/content/drive/MyDrive/Geology/test.zip" -d /content/yolov7
#!unzip "/content/drive/MyDrive/Geology/valid.zip" -d /content/yolov7

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/yolov7

"""# Initiate Training"""

!python /content/yolov7/train.py --weights yolov7.pt --data /content/yolov7/data.yaml --workers 4 --batch-size 32 --img 416  --cfg cfg/training/yolov7.yaml --name yolov7 --epoch 200

!python test.py --data /content/yolov7/data.yaml --img 416 --batch 32 --conf 0.5 --iou 0.50 --weights /content/yolov7/runs/train/yolov72/weights/best.pt --name yolov7

"""#Detect images"""

!python detect.py --weights /content/yolov7/runs/train/yolov72/weights/best.pt --conf 0.50 --img-size 640 --source "/content/Test_109/yolov7_test/*.jpg" --project /content/drive/MyDrive/Colab_Notebooks --name "output_109" --save-txt

"""# Quantifying detected objects"""

import os
import json

# Path to the output directory containing the results from YOLOv7
output_dir = '/content/drive/MyDrive/Colab_Notebooks/output_1092/labels' #Change the path based on the path you want to save it

# Initialize a counter
total_objects = 0

# Loop through the output files and count the number of objects
for output_file in os.listdir(output_dir):
    if output_file.endswith('.txt'):  # Assuming the output is in .txt files
        with open(os.path.join(output_dir, output_file), 'r') as f:
            detections = f.readlines()
            total_objects += len(detections)  # Each line corresponds to one object

print(f"Total number of objects detected: {total_objects}")

!unzip "/content/drive/MyDrive/Colab_Notebooks/yolov7_test_109.zip" -d /content/Test_109

#display inference on ALL test images

import glob
from IPython.display import Image, display

i = 0
limit = 10000 # max images to print
for imageName in glob.glob('/content/yolov7/yolov7_test/*.jpg'): #assuming JPG
    if i < limit:
      display(Image(filename=imageName))
      print("\n")
    i = i + 1

"""#Detect video"""

!python detect.py --weights /content/yolov7/runs/train/yolov73/weights/best.pt --conf 0.5 --img-size 640 --source /content/drive/MyDrive/MOVA0598.avi

"""# Video from local machine"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/gdrive/MyDrive/yolov7
from google.colab import files
uploaded = files.upload()

"""#Video from Google Drive link"""

# Commented out IPython magic to ensure Python compatibility.
#change URL
# %cd /content/gdrive/MyDrive/yolov7
!gdown https://drive.google.com/uc?id=1csuLHWkDf6yPm-q3z2K3ZAd6WOfKc0vy

"""# Yolov7 Inference Video"""

#give the full path to video, your video will be in the Yolov7 folder
video_path = r'C:\Users\admin\Desktop\Stamatia'

import cv2
import torch

# Initializing video object
video = cv2.VideoCapture(video_path)


#Video information
fps = video.get(cv2.CAP_PROP_FPS)
w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
nframes = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

# Initialzing object for writing video output
output = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'DIVX'),fps , (w,h))
torch.cuda.empty_cache()
# Initializing model and setting it for inference
with torch.no_grad():
  weights, imgsz = opt['weights'], opt['img-size']
  set_logging()
  device = select_device(opt['device'])
  half = device.type != 'cpu'
  model = attempt_load(weights, map_location=device)  # load FP32 model
  stride = int(model.stride.max())  # model stride
  imgsz = check_img_size(imgsz, s=stride)  # check img_size
  if half:
    model.half()

  names = model.module.names if hasattr(model, 'module') else model.names
  colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
  if device.type != 'cpu':
    model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))

  classes = None
  if opt['classes']:
    classes = []
    for class_name in opt['classes']:
      classes.append(opt['classes'].index(class_name))

  for j in range(nframes):

      ret, img0 = video.read()
      if ret:
        img = letterbox(img0, imgsz, stride=stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
          img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment= False)[0]


        pred = non_max_suppression(pred, opt['conf-thres'], opt['iou-thres'], classes= classes, agnostic= False)
        t2 = time_synchronized()
        for i, det in enumerate(pred):
          s = ''
          s += '%gx%g ' % img.shape[2:]  # print string
          gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]
          if len(det):
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()

            for c in det[:, -1].unique():
              n = (det[:, -1] == c).sum()  # detections per class
              s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

            for *xyxy, conf, cls in reversed(det):

              label = f'{names[int(cls)]} {conf:.2f}'
              plot_one_box(xyxy, img0, label=label, color=colors[int(cls)], line_thickness=3)

        print(f"{j+1}/{nframes} frames processed")
        output.write(img0)
      else:
        break


output.release()
video.release()

from IPython.display import HTML
from base64 import b64encode
import os

# Input video path
save_path = '/content/drive/MyDrive/Sæter_deponi_T1_Zoom.mpg'

# Compressed video path
compressed_path = "/content/yolov7/runs/detect/exp4/Sæter_deponi_T1_Zoom.mpg"

os.system(f"ffmpeg -i {save_path} -vcodec libx264 {compressed_path}")

# Show video
mp4 = open(compressed_path,'rb').read()
data_url = "data:video/mpg;base64," + b64encode(mp4).decode()
HTML("""
<video width=400 controls>
      <source src="%s" type="video/mpg">
</video>
""" % data_url)

"""#Evaluation"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir runs/train

from IPython.display import Image
display(Image("/content/gdrive/MyDrive/yolov7/runs/train/exp/F1_curve.png", width=400, height=400))
display(Image("/content/gdrive/MyDrive/yolov7/runs/train/exp/PR_curve.png", width=400, height=400))
display(Image("/content/gdrive/MyDrive/yolov7/runs/train/exp/confusion_matrix.png", width=500, height=500))

"""#Download files"""

from google.colab import files
import os

dir_to_zip = '/content/yolov7/runs/detect/exp11' #@param {type: "string"}
output_filename = 'results_4.zip' #@param {type: "string"}
delete_dir_after_download = "No"  #@param ['Yes', 'No']

os.system( "zip -r {} {}".format( output_filename , dir_to_zip ) )

if delete_dir_after_download == "Yes":
    os.system( "rm -r {}".format( dir_to_zip ) )

files.download( output_filename )

!unzip "/content/yolov7/yolov7_molluscs.zip" -d /content/drive/MyDrive/Geology #Change based on your files

! ffmpeg -i "/content/yolov7/runs/detect/exp4/Zoom.mpg" -codec copy "/content/drive/MyDrive/Geology/molluscs.mp4" #Change based on your files