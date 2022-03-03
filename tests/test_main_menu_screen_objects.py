import cv2
import os
import pytest
from d2r_image.screen_object_helpers import detect_screen_object
from d2r_image.screen_objects import MainMenuScreenObjects, ScreenObject


@pytest.mark.parametrize("filename, screen_object, valid", [
    ('main_menu1.png', MainMenuScreenObjects.PlayBtn, True),
    ('main_menu_difficulties.png', MainMenuScreenObjects.Normal, True),
    ('main_menu_difficulties.png', MainMenuScreenObjects.Nightmare, True),
    ('main_menu_difficulties.png', MainMenuScreenObjects.Hell, True),
    ('main_menu1.png', MainMenuScreenObjects.Online, True),
    ('main_menu1.png', MainMenuScreenObjects.Offline, False),
    ('main_menu_offline.png', MainMenuScreenObjects.Offline, True),
])
def test_main_menu_screen_objects(filename: str, screen_object: ScreenObject, valid: bool):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'screen_objects',
        'main_menu',
        f'{filename}')
    image = cv2.imread(image_path)
    match = detect_screen_object(screen_object, image)
    assert match.valid == valid
