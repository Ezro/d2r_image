import pkgutil
import time
import cv2
import keyboard
import io
from PIL import Image
import os
from d2r_image.processing import crop_text_clusters
from d2r_image.data_models import ItemQuality
from pkg_resources import resource_listdir
import numpy as np


def demo_all_images():
    print('Loading all demo images. This may take a few seconds...\n')
    debug_line_map = {
        ItemQuality.Gray.value: (123, 123, 123),
        ItemQuality.Gray.value: (123, 123, 123),
        ItemQuality.Normal.value: (208, 208, 208),
        ItemQuality.Magic.value: (178, 95, 95),
        ItemQuality.Rare.value: (107, 214, 214),
        ItemQuality.Set.value: (0, 238, 0),
        ItemQuality.Unique.value: (126, 170, 184),
        ItemQuality.Orange.value: (0, 160, 219)
    }
    all_image_data = []
    all_images = []
    total_elapsed_time = 0
    demo_image_count = 0
    resource_paths = ['ground', 'hover']
    for resource_path in resource_paths:
        for image_name in resource_listdir(f'd2r_image.resources.demo_images.{resource_path}', ''):
            if not image_name.lower().endswith('.png'):
                continue
            image_bytes = pkgutil.get_data(
                __name__,
                f'resources/demo_images/{resource_path}/{image_name}')
            image = Image.open(io.BytesIO(image_bytes))
            image_data = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
            start = time.time()
            text_clusters = crop_text_clusters(image_data)
            end = time.time()
            elapsed = round(end-start, 2)
            # print(f'Processed {image} in {elapsed} seconds')
            total_elapsed_time += elapsed
            for text_cluster in text_clusters:
                x, y, w, h = text_cluster.roi
                cv2.rectangle(
                    image_data,
                    (x, y),
                    (x+w, y+h),
                    debug_line_map[text_cluster.quality.value],
                    1)
            all_image_data.append(image_data)
            all_images.append(image)
            demo_image_count += 1
    # print('\n')
    print(f'Processing all {demo_image_count} image(s) took {round(total_elapsed_time, 2)} ({round(total_elapsed_time / demo_image_count, 2)} avg)')
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    print('Press f12 to quit')
    for image in all_image_data:
        cv2.imshow('D2R Image Demo', image)
        cv2.waitKey()
    cv2.destroyAllWindows()