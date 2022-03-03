import cv2
import os
import pytest
from d2r_image.screen_object_helpers import detect_screen_object
from d2r_image.screen_objects import LoadingScreenObjects, ScreenObject


@pytest.mark.parametrize("filename, screen_object, valid", [
    ('loading.png', LoadingScreenObjects.Loading, True),
    ('exiting_game.png', LoadingScreenObjects.ExitingGame, True),
])
def test_main_menu_screen_objects(filename: str, screen_object: ScreenObject, valid: bool):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'screen_objects',
        'loading',
        f'{filename}')
    image = cv2.imread(image_path)
    match = detect_screen_object(screen_object, image)
    assert match.valid == valid
