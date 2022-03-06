import cv2
import os
import pytest
from d2r_image.screen_object_helpers import detect_screen_object
from d2r_image.screen_objects import LoadingScreenObjects, ScreenObject


@pytest.mark.parametrize("filename, screen_object, rect_count", [
    ('loading.png', LoadingScreenObjects.Loading, 1),
    ('exiting_game.png', LoadingScreenObjects.ExitingGame, 1),
])
def test_main_menu_screen_objects(filename: str, screen_object: ScreenObject, rect_count: int):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'screen_objects',
        'loading',
        f'{filename}')
    image = cv2.imread(image_path)
    rects = detect_screen_object(screen_object, image)
    assert len(rects) == rect_count
