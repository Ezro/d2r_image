from dataclasses import dataclass
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
