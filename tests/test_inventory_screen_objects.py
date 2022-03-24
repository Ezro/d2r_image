# import cv2
# import os
# import pytest
# from d2r_image import processing
# from d2r_image.data_models import D2ItemList


# @pytest.mark.parametrize("filename, expected_file", [
#     ('all_gems_runes_consumables.png', 'all_gems_runes_consumables.json'),
# ])
# def test_inventory(filename: str, expected_file: str):
#     image_path = os.path.join(
#         os.path.dirname(__file__),
#         'resources',
#         'screen_objects',
#         'inventory',
#         f'{filename}')
#     image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
#     expected_items_path = os.path.join(
#         os.path.dirname(__file__),
#         'resources',
#         'screen_objects',
#         'inventory',
#         expected_file)
#     inventory = processing.get_inventory(image)
#     inventory_expected = D2ItemList.from_json(open(expected_items_path).read())
#     assert len(inventory.items) == len(inventory_expected.items)
#     for item in inventory_expected.items:
#         if item is None:
#             break
#         assert item in inventory.items
