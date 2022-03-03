import cv2
import os
import pytest
from d2r_image import processing
from d2r_image.screen_objects import TownNpcScreenObjects, ScreenObject

@pytest.mark.parametrize("filename, screen_object, valid", [
    ('malah1.png', TownNpcScreenObjects.Malah, True),
    ('malah2.png', TownNpcScreenObjects.Malah, True),
    ('malah3.png', TownNpcScreenObjects.Malah, True),
    ('malah4.png', TownNpcScreenObjects.Malah, True),
    ('malah5.png', TownNpcScreenObjects.Malah, True),
])
def test_get_npc_coords(filename: str, screen_object: ScreenObject, valid: bool):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_npc_coords',
        f'{filename}')
    image = cv2.imread(image_path)
    match = processing.get_npc_coords(image, screen_object)
    assert match.valid == valid

