import cv2
import os
import pytest
from d2r_image import processing

def rgbToHSV(r, g, b):
    """Convert RGB color space to HSV color space
    
    @param r: Red
    @param g: Green
    @param b: Blue
    return (h, s, v)  
    """
    maxc = max(r, g, b)
    minc = min(r, g, b)
    colorMap = {
        id(r): 'r',
        id(g): 'g',
        id(b): 'b'
    }
    if colorMap[id(maxc)] == colorMap[id(minc)]:
        h = 0
    elif colorMap[id(maxc)] == 'r':
        h = 60.0 * ((g - b) / (maxc - minc)) % 360.0
    elif colorMap[id(maxc)] == 'g':
        h = 60.0 * ((b - r) / (maxc - minc)) + 120.0
    elif colorMap[id(maxc)] == 'b':
        h = 60.0 * ((r - g) / (maxc - minc)) + 240.0
    v = maxc
    if maxc == 0.0:
        s = 0.0
    else:
        s = 1.0 - (minc / maxc)
    return (h, s, v)


@pytest.mark.parametrize("filename, expected_experience", [
])
def test_get_experience(filename, expected_experience):
    image_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'get_experience',
        f'{filename}')
    image = cv2.imread(image_path)
    # actual_health = processing.get_health(image)
    actual_experience = processing.get_experience(image)
    # actual_mana = processing.get_mana(image)
    # assert abs(actual_health - expected_health) < 5
    # assert abs(actual_mana - expected_mana) < 5


# test_get_experience('1.png', '')