# D2R Image
D2R Image is a package aimed to help in providing an API for answering common questions when looking at a Dablo II: Resurrected image:

- get_ground_loot(image: np.ndarray) -> D2ItemList
- get_health(image: np.ndarray) -> float
- get_mana(image: np.ndarray) -> float
- get_stamina(image: np.ndarray) -> float (TODO)
- get_stamina(image: np.ndarray) -> float (TODO)
- get_merc_health(image: np.ndarray) -> float
<!-- - get_belt(image: np.ndarray) -> D2ItemList
- get_inventory(image: np.ndarray) -> D2ItemList (WIP) -->
- get_hovered_item(image: np.ndarray) -> tuple[HoveredItem, ItemText]
<!-- - get_hovered_item(image: np.ndarray) -> D2Item | None
- get_npc_coords(npc: NPC) -> (x, y) | None
- find_items_by_name(name: str) -> list[(x, y)] | None
- whats_in_image(image: np.ndarray) -> TODO: SreenReport
- get_health(image: np.ndarray) -> float | None
- get_mana(image: np.ndarray) -> float | None
- get_stamina(image: np.ndarray) -> float | None
- get_experience(image: np.ndarray) -> float | None  -->
## GroundItem (List)
---
D2Item is one of the core data models returned by the d2r-image library. It aims to represent a Diablo II item that's on the ground, being hovered, or detected by an image reference (e.g., equipped green Shako)
```py
class GroundItem:
    BoundingBox: dict # x, y, w, h
    Name: str # e.g., Hand Axe, 1015 GOLD, Ormus' Robes
    Quality: str # e.g., gray, normal, magic, rare, set, unique, runeword, rune
    Text: str # raw OCR text e.g., HAND AXE
    BaseItem: dict
    Item: Union[dict, None]
    NTIPAliasType: int
    NTIPAliasClassID: int
    NTIPAliasClass: Union[int, None]
    NTIPAliasQuality: int
    NTIPAliasFlag: dict
```
```py
class GroundItemList:
    items: list[Union[GroundItem, None]]
```
## HoveredItem
```py
class HoveredItem:
    Name: str # e.g., DAGGER, SPIRIT, CHILLING GRAND CHARM OF VITA
    Quality: str # e.g., gray, normal, magic, rare, set, unique, runeword, rune
    Text: str
    BaseItem: dict
    Item: Union[dict, None]
    NTIPAliasType: int
    NTIPAliasClassID: int
    NTIPAliasClass: Union[int, None]
    NTIPAliasQuality: int
    NTIPAliasStat: Union[dict, None]
    NTIPAliasFlag: dict
```
## Install
---
**IMPORTANT**

Pre-requisite: Prior to pip installing be sure to install tesserocr from conda-forge:
```
conda install -c conda-forge tesserocr
```
---
then run
```
pip install d2r-image
```

_Microsoft Visual Studio C++ Build Tools may be required for tesserocr install_
## Usage
---
**IMPORTANT**

It's very important that when using this library your Diablo II: Resurrected screenshots adhere to the following settings, otherwise results may vary:
```json
{
    "Gamma": 155,
    "GammaHD": 3024,
    "PaperWhiteNits": 200,
    "MaxLuminance": 600,
    "HDRContrast": 200,
    "Contrast": 100,
    "Screen Resolution (Windowed)": "1280x720",
    "Resolution Scale": 100,
    "Sharpening": 6,
    "Game Resolution": 1,
    "Light Quality": 2,
    "Blended Shadows": 0,
    "Perspective": 0,
    "VSync": 1,
    "Framerate Cap": 60,
    "Framerate Target": 0,
    "Window Mode": 0,
    "Graphic Presets": 4,
    "Texture Quality": 4,
    "Texture Anisotropy": 0,
    "Ambient Occlusion Quality": 0,
    "Character Detail": 2,
    "Environment Detail": 2,
    "Atmospherics Quality": 2,
    "Transparency Quality": 3,
    "Shadow Quality": 1,
    "Anti Aliasing": 0,
    "Dynamic Resolution Scaling": 0,
    "Vfx Lighting Quality": 0,
    "Safe Screen Percent": 100,
    "Graphics Mode": 0,
    "NVIDIA DLSS": 0,
    "Chat Font Size": 0,
    "Combat Feedback": 0,
    "Camera Shake": 0,
    "Low Vision Mode": 1,
    "Color Blind Mode": 0,
    "Color Blind Strength": 100,
    "Show Clock": 1,
    "Auto Gold Enabled": 0,
    "Chat Gem Mode": 1,
    "Item Name Display": 1,
    "Chat Background": 0,
    "Always Run": 1,
    "Quick Cast Enabled": 0,
    "Display Active Skill Bindings": 0,
    "Lobby Wide Item Drop Enabled": 1,
    "Item Tooltip Hotkey Appender": 1
}
```
---
Python Example:
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
## Demo
---
d2r-image comes with a demo.py file for previewing the output of different use cases within the game. These can be ran as follows:
```py
from d2r_image import demo

demo.get_ground_loot()
demo.get_health_mana()
```
## Screenshots
---
![random_items](screenshots/random_items.png)
![sets_and_uniques](screenshots/sets_and_uniques.png)
![consumables](screenshots/all_consumables.png)
![get_belt](screenshots/get_belt.png)
![baal](screenshots/baal.png)
![trav](screenshots/trav.png)