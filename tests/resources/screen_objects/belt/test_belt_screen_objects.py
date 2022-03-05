import cv2
import os
import pytest
from d2r_image import processing
from d2r_image.data_models import ScreenObject


BELT_EXPECTED_MAP = {
    '2_slot_mixed_potions.png': ['health', 'health', 'empty', 'empty', 'health', 'health', 'empty', 'empty', None, None, None, None, None, None, None, None],
    '4_slot_mixed_potions.png': ['health', 'health', 'mana', 'mana', 'health', 'health', 'mana', 'mana', 'health', 'health', 'empty', 'mana', 'health', 'health', 'empty', 'mana']
}


@pytest.mark.parametrize("filename", [
    ('4_slot_mixed_potions.png'),
])
def test_belt(filename: str):
    image_path = os.path.join(
        os.path.dirname(__file__),
        f'{filename}')
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    belt = processing.get_belt(image)
    assert belt == BELT_EXPECTED_MAP[filename]


test_belt('4_slot_mixed_potions.png')