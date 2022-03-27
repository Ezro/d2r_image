from enum import Enum
import numpy as np
from typing import Union
from dataclasses import dataclass
from dataclasses_json import dataclass_json


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
    quality: Union[str, None]
    type: Union[str, None]
    identified: bool
    amount: Union[int, None]
    baseItem: Union[dict, None]
    item: Union[dict, None]
    uniqueItems: Union[list[dict], None]
    setItems: Union[list[dict], None]
    itemModifiers: Union[dict, None]

    def __eq__(self, other):
        if self and not other:
            return False
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
class D2Data:
    BaseItem: dict
    Item: Union[dict, None]
    ItemModifiers: Union[dict, None]

    def __eq__(self, other):
        if self and not other:
            return False
        return self.to_json() == other.to_json()


@dataclass_json
@dataclass
class GroundItem:
    BoundingBox: dict
    Name: str
    Quality: str
    Text: str
    BaseItem: dict
    Item: Union[dict, None]
    NTIPAliasType: int
    NTIPAliasClassID: int
    NTIPAliasClass: Union[int, None]
    NTIPAliasQuality: int
    NTIPAliasFlag: dict

    def __eq__(self, other):
        if self and not other:
            return False
        return self.to_json() == other.to_json()


@dataclass_json
@dataclass
class GroundItemList:
    items: list[Union[GroundItem, None]]


@dataclass_json
@dataclass
class HoveredItem:
    Name: str
    Quality: str
    Text: str
    BaseItem: dict
    Item: Union[dict, None]
    NTIPAliasType: int
    NTIPAliasClassID: int
    NTIPAliasClass: Union[int, None]
    NTIPAliasQuality: int
    NTIPAliasStat: Union[dict, None]
    NTIPAliasFlag: dict

    def __eq__(self, other):
        if self and not other:
            return False
        return self.to_json() == other.to_json()

    def as_dict(self):
        return {
            'Name': self.Name,
            'Quality': self.Quality,
            'Text': self.Text,
            'BaseItem': self.BaseItem,
            'Item': self.Item,
            'NTIPAliasType': self.NTIPAliasType,
            'NTIPAliasClassID': self.NTIPAliasClassID,
            'NTIPAliasClass': self.NTIPAliasClass,
            'NTIPAliasQuality': self.NTIPAliasQuality,
            'NTIPAliasStat': self.NTIPAliasStat,
            'NTIPAliasFlag': self.NTIPAliasFlag,
        }


@dataclass_json
@dataclass
class InventoryItem:
    boundingBox: dict
    type: Union[str, None]
    item: Union[dict, None]
    baseItems: Union[list[dict], None]
    uniqueItems: Union[list[dict], None]
    setItems: Union[list[dict], None]

    def __eq__(self, other):
        if self and not other:
            return False
        return self.boundingBox == other.boundingBox and\
            self.type == other.type and\
            self.item == other.item and\
            self.baseItems == other.baseItems and\
            self.uniqueItems == other.uniqueItems and\
            self.setItems == other.setItems


@dataclass_json
@dataclass
class D2ItemList:
    items: list[Union[D2Item, None]]


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


@dataclass
class ScreenObject:
    _screen_object = None
    refs: list[str]
    inp_img: np.ndarray = None
    roi: list[float] = None
    time_out: float = 30
    threshold: float = 0.68
    best_match: bool = False
    use_grayscale: bool = False

    def __call__(self, cls):
        cls._screen_object = self
        return cls
