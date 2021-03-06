import cv2
import os
import pytest
from d2r_image import processing


@pytest.mark.parametrize("filename, expected_health, expected_mana", [
    ('25.82_79.08.png', 25.82, 79.08),
    ('67.59_0.65.png', 67.59, 0.65),
    ('80_32.66.png', 80, 32.66),
    ('46.69_65.png', 46.69, 65),
])
def test_get_health_mana(filename, expected_health, expected_mana):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_health_mana',
        f'{filename}')
    image = cv2.imread(image_path)
    actual_health = processing.get_health(image)
    actual_mana = processing.get_mana(image)
    assert abs(actual_health - expected_health) < 5
    assert abs(actual_mana - expected_mana) < 5


@pytest.mark.parametrize("filename, expected_health", [
    ('100.png', 100),
    ('90.png', 90),
    ('80.png', 80),
    ('62.5.png', 62.5),
    ('50.png', 50),
    ('40.png', 40),
    ('30.png', 30),
    ('17.5.png', 17.5),
])
def test_get_merc_health(filename, expected_health):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_merc_health',
        f'{filename}')
    image = cv2.imread(image_path)
    actual_health = processing.get_merc_health(image)
    assert actual_health == expected_health
