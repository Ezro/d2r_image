import cv2
import os
import pytest
from d2r_image import processing
from d2r_image.data_models import D2ItemList


@pytest.mark.parametrize("filename, expected_file", [
    ('2_slot_mixed_potions.png', '2_slot_mixed_potions.json'),
    ('4_slot_mixed_potions.png', '4_slot_mixed_potions.json'),
    ('4_slot_mixed_consumables.png', '4_slot_mixed_consumables.json'),
])
def test_belt(filename: str, expected_file: str):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'screen_objects',
        'belt',
        f'{filename}')
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    expected_items_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'screen_objects',
        'belt',
        expected_file)
    belt = processing.get_belt(image)
    belt_expected = D2ItemList.from_json(open(expected_items_path).read())
    assert len(belt.items) == len(belt_expected.items)
    for item in belt_expected.items:
        if item is None:
            break
        assert item in belt.items
