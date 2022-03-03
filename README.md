D2R Image is a package aimed to help in providing an API for answering common questions when looking at a D2R image:

- get_ground_loot(image: np.ndarray) -> list[D2Item] | None 
- get_hovered_item(image: np.ndarray) -> D2Item | None 
- get_npc_coords(npc: NPC) -> (x, y) | None 
- find_items_by_name(name: str) -> list[(x, y)] | None 
- whats_in_image(image: np.ndarray) -> TODO: SreenReport 
- get_health(image: np.ndarray) -> float | None 
- get_mana(image: np.ndarray) -> float | None 
- get_stamina(image: np.ndarray) -> float | None 
- get_experience(image: np.ndarray) -> float | None 
### D2Item
D2Item is one of the core data models returned by the d2r-image library. It aims to represent a Diablo II item that's on the ground, being hovered, or detected by an image reference (e.g., equipped green Shako)
```py
class D2Item:
    boundingBox: dict # x, y, w, h
    name: str # e.g., HAND AXE, 1015 GOLD, ORMUS' ROBES
    quality: str # e.g., gray, normal, set, unique, runeword, rune
    type: str # e.g., helm, mace, axe, shield
    identified: bool # whether the item is identified or not
    amount: int # e.g., 1015 (where name is 1015 GOLD)
    baseItem: dict # d2data base item
    item: dict # d2data item
    uniqueItems: list[dict] # list of possible d2data unique items
    setItems: list[dict] # list of possible d2data set items
    itemModifiers: dict # TODO: d2data parsed modifiers for a hovered tooltip
```
### Install
**IMPORTANT**

Pre-requisite: Prior to pip installing be sure to install tesserocr from conda-forge:
```
conda install -c conda-forge tesserocr
```
then run
```
pip install d2r-image
```

_Microsoft Visual Studio C++ Build Tools may be required for tesserocr install_
### Usage
```py
import cv2
from PIL import Image
from d2r_image import processing

# Grab an input image
image = Image.open('test_image.png')
# Convert color to BGR for cv2 (should this be in processing?)
image_data = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
# d2r_image get_ground_loot() API call
items = processing.get_ground_loot(image_data)
# Draw the items
for item in items:
    x, y, w, h = item.boundingBox.values()
    cv2.rectangle(
        image_data,
        (x, y),
        (x+w, y+h),
        debug_line_map[item.quality],
        1)
cv2.imshow('test_image', image)
cv2.waitKey()
# d2r_image get_health() and get_mana() API calls
health = processing.get_health(image_data)
mana = processing.get_mana(image_data)
print(f'HP: {health}    MP: {mana}')
```
### Demo
d2r-image comes with a demo.py file for previewing the output of different use cases within the game. These can be ran as follows:
```py
from d2r_image import demo

demo.get_ground_loot()
demo.get_health_mana()
```