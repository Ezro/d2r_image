import cv2
import os
import pytest
from d2r_image.screen_object_helpers import detect_screen_object
from d2r_image.screen_objects import MainMenuScreenObjects, ScreenObject


@pytest.mark.parametrize("filename, screen_object, rect_count", [
    ('main_menu1.png', MainMenuScreenObjects.PlayBtn, 1),
    ('main_menu_difficulties.png', MainMenuScreenObjects.Normal, 1),
    ('main_menu_difficulties.png', MainMenuScreenObjects.Nightmare, 1),
    ('main_menu_difficulties.png', MainMenuScreenObjects.Hell, 1),
    ('main_menu1.png', MainMenuScreenObjects.Online, 1),
    ('main_menu1.png', MainMenuScreenObjects.Offline, 0),
    ('main_menu_offline.png', MainMenuScreenObjects.Offline, 1),
])
def test_main_menu_screen_objects(filename: str, screen_object: ScreenObject, rect_count: int):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'screen_objects',
        'main_menu',
        f'{filename}')
    image = cv2.imread(image_path)
    rects = detect_screen_object(screen_object, image)
    assert len(rects) == rect_count
