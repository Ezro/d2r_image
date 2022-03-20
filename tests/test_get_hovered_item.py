import os
import cv2
import pytest
from d2r_image import processing
from d2r_image.data_models import HoveredItem


@pytest.mark.parametrize("filename, expected_file", [
    ('war_travs.png', 'war_travs.json'),
    ('unid_hsarus_iron_heel.png', 'unid_hsarus_iron_heel.json'),
    ('unid_rare_dagger.png', 'unid_rare_dagger.json'),
    ('cold_skiller.png', 'cold_skiller.json'),
    ('torch.png', 'torch.json'),
    ('spirit.png', 'spirit.json'),
])
def test_hovered_item(filename: str, expected_file: str):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_hovered_item',
        f'{filename}')
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    expected_items_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_hovered_item',
        expected_file)
    result = processing.get_hovered_item(image)
    expected = HoveredItem.from_json(open(expected_items_path).read())
    assert result == expected


# test_hovered_item('cold_skiller.png', 'cold_skiller.json'),
# test_hovered_item('spirit.png', 'spirit.json'),
# test_hovered_item('torch.png', 'torch.json'),
# test_hovered_item('war_travs.png', 'cold_skiller.json'),
# test_hovered_item('unid_hsarus_iron_heel.png', 'cold_skiller.json'),
# test_hovered_item('unid_rare_dagger.png', 'cold_skiller.json'),