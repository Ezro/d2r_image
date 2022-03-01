from dataclasses import dataclass
from enum import Enum
from typing import Tuple
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


@dataclass
class BoundingBox:
    center: Tuple[int, int] = None
    x: int = None
    y: int = None
    w: int = None
    h: int = None


@dataclass
class D2Item:
    boundingBox: BoundingBox = None
    name: str = None
    baseItem: dict = None
    uniqueItems: list[dict] = None
    setItems: list[dict] = None
    item: dict = None


@dataclass
class ScreenReport:
    groundLoot: list[D2Item] = None
    hoveredItem: D2Item = None
    npcs: dict = None
    health: float = None
    mana: float = None
    stamina: float = None
    experience: float = None