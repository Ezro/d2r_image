from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
import numpy as np


@dataclass
class OcrResult:
    text: str = None
    original_text: str = None
    word_confidences: list = None
    mean_confidence: float = None
    # these are kept to help train OCR
    original_img: np.ndarray = None
    processed_img: np.ndarray = None

    def __getitem__(key):
        return super().__getattribute__(key)


@dataclass
class ItemQuality(Enum):
    Gray = 'gray'
    Normal = 'normal'
    Magic = 'magic'
    Rare = 'rare'
    Set = 'set'
    Unique = 'unique'
    Crafted = 'crafted'
    Rune = 'rune'
    Runeword = 'runeword'
    Orange = 'orange'


@dataclass
class ItemText:
    color: str = None
    quality: ItemQuality = None
    roi: list[int] = None
    data: np.ndarray = None
    ocr_result: OcrResult = None
    clean_img: np.ndarray = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


@dataclass
class ItemQualityKeyword(Enum):
    LowQuality = 'LOW QUALITY'
    Cracked = 'CRACKED'
    Crude = 'CRUDE'
    Damaged = 'DAMAGED'
    Superior = 'SUPERIOR'


@dataclass_json
@dataclass
class D2Item:
    boundingBox: dict
    name: str
    quality: str
    type: str
    identified: bool
    amount: int
    baseItem: dict
    item: dict
    uniqueItems: list[dict]
    setItems: list[dict]
    itemModifiers: dict

    def __eq__(self, other):
        return self.boundingBox == other.boundingBox and\
            self.name == other.name and\
            self.type == other.type and\
            self.identified == other.identified and\
            self.amount == other.amount and\
            self.baseItem == other.baseItem and\
            self.item == other.item and\
            self.uniqueItems == other.uniqueItems and\
            self.setItems == other.setItems and\
            self.itemModifiers == other.itemModifiers


@dataclass_json
@dataclass
class ScreenReport:
    groundLoot: list[D2Item]
    hoveredItem: D2Item
    npcs: dict
    health: float
    mana: float
    stamina: float
    experience: float