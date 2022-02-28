D2R Image is a package aimed to help in parsing text clusters representing items on the ground or text in hovered tooltips

### Install
```
pip install -i https://test.pypi.org/simple/ d2r-image
```
### Usage
```py
import cv2
from PIL import Image
from d2r_image import processing

image = Image.open('test_image.png')
image_data = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
text_clusters = processing.crop_text_clusters(image_data)
# Draw the clusters
for text_cluster in text_clusters:
    cv2.rectangle(
        image_data,
        (x, y),
        (x+w, y+h),
        debug_line_map[text_cluster.quality.value],
        1)
cv2.imshow('test_image', image)
cv2.waitKey()
```
### Demo
d2r-image comes with a demo.py file for previewing the output of different use cases within the game. These can be ran as follows:
```py
from d2r_image import demo

demo.demo_all_images()
```