
# Yolo Dataset Redactor
<img src="https://raw.githubusercontent.com/lexter0705/yolo_dataset_redactor/refs/heads/master/Logo.svg"/>

- Small library for yolo datasets

# Examples:
## yolo_dataset_redactor.video
Video:
```python
from yolo_dataset_redactor.video import Video

video_path = "./videos/some.mp4"

images_path = "./images" # path for save images
period = 100 # every {period} frames save image
prefix = "png" # image suffixes

video = Video(video_path)

video.split(images_path, period, prefix)
```
Videos:
```python
from yolo_dataset_redactor.video import Videos

videos_path = "./videos"

images_path = "./images" # path for save images
period = 100 # every {period} frames save image
video_suffixes = ["mp4"] # videos suffixes
image_suffix = "png" # image suffixes

videos = Videos(videos_path, video_suffixes)

videos.split(images_path, period, image_suffix)
```

## yolo_dataset_redactor.image
Image:
```python
from yolo_dataset_redactor.image import Image

image_path = "./images/some.png" # image path

new_size = (640, 640) # image resized to {new_size}

image = Image(image_path)

image.resize(new_size)
```
Images:
```python
from yolo_dataset_redactor.image import Images

image_path = "./images" # images path
suffixes = ["png"] # images suffixes

new_size = (640, 640) # images resized to {new_size}

images = Images(image_path, suffixes)

images.resize(new_size)
```