import re
import os
import pkgutil
from enum import Enum

I_1 = re.compile(r"(?<=[%I0-9\-+])I|I(?=[%I0-9\-+])")
II_U = re.compile(r"(?<=[A-Z])II|II(?=[A-Z])|1?=[a-z]")
One_I = re.compile(r"(?<=[A-Z])1|1(?=[A-Z])|1?=[a-z]")
OneOne_U = re.compile(r"(?<=[A-Z])11|11(?=[A-Z])|1?=[a-z]")

class TrainedDataSets(Enum):
    engd2r_inv_th = 'engd2r_inv_th'
    engd2r_inv_th_fast = 'engd2r_inv_th_fast'
    engd2r_ui = "engd2r_ui"

OCR_WORKING_DIR = os.path.join(os.getenv('APPDATA'), 'd2r_image')
ocr_config_data = pkgutil.get_data(
    __name__,
    "resources/tessdata/ocr_config.txt")
OCR_CONFIG = ocr_config_data.decode()

ERROR_RESOLUTION_MAP = {
    'SHIFLD': 'SHIELD',
    'SPFAR': 'SPEAR',
    'GLOVFS': 'GLOVES',
    'GOLP': 'GOLD',
    'TELEFORT': 'TELEPORT',
    'TROPHV': 'TROPHY',
    'CLAVMORE': 'CLAYMORE',
    'MAKIMUM': 'MAXIMUM',
    'DEKTERITY': 'DEXTERITY',
    'DERTERITY': 'DEXTERITY',
    'QUAHTITY': 'QUANTITY',
    'DEFERSE': 'DEFENSE',
    'ARMGR': 'ARMOR',
    'ARMER': 'ARMOR',
    'COMDAT': 'COMBAT',
    'WEAPORS': 'WEAPONS',
    'AXECLASS': 'AXE CLASS',
    'IOX%': '10%',
    'IO%': '10%',
    'TWYO': 'TWO',
    'ATTRIOUTES': 'ATTRIBUTES',
    'MONARCHI': 'MONARCH',
    '10 RUNE': 'IO RUNE',
    '1O RUNE': 'IO RUNE',
    'I0 RUNE': 'IO RUNE'
}