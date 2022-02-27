import numpy as np
from d2r_image.data_models import ItemQuality

GAUS_FILTER = (19, 1)
EXPECTED_HEIGHT_RANGE = [round(num) for num in [x / 1.5 for x in [14, 40]]]
EXPECTED_WIDTH_RANGE = [round(num) for num in [x / 1.5 for x in [60, 1280]]]
BOX_EXPECTED_WIDTH_RANGE = [200, 900]
BOX_EXPECTED_HEIGHT_RANGE = [24, 710]

ITEM_COLORS = ['white', 'gray', 'blue', 'green', 'yellow', 'gold', 'orange']

COLORS = {
    "black": "0, 0, 0, 180, 255, 15",
    "black_descr": "0, 0, 0, 180, 255, 25",
    "item_highlight": "90, 235, 130, 115, 255, 160",
    "white": "0, 0, 150, 180, 20, 255",
    "gray": "0, 0, 90, 180, 20, 130",
    "blue": "114, 100, 190, 125, 132, 255",
    "green": "56, 190, 190, 63, 255, 255",
    "yellow": "27, 110, 190, 33, 145, 255",
    "gold": "20, 75, 140, 26, 95, 230",
    "orange": "20, 190, 190, 23, 255, 255",
    "red": "3, 160, 160, 9, 255, 220",
    "health_potion": "170, 100, 76, 190, 255, 255",
    "mana_potion": "105, 20, 76, 135, 255, 255",
    "rejuv_potion": "140, 50, 40, 160, 255, 255",
    "skill_charges": "70, 30, 25, 150, 163, 255",
    "health_globe_red": "178, 110, 20, 183, 255, 255",
    "health_globe_green": "47, 90, 20, 54, 255, 255",
    "mana_globe": "117, 120, 20, 121, 255, 255",
}

# min and max hsv range (opencv format: h: [0-180], s: [0-255], v: [0, 255])
# h_min, s_min, v_min, h_max, s_max, v_max
for key in COLORS:
    COLORS[key] = np.split(np.array([int(x)
                           for x in COLORS[key].split(",")]), 2)

# all rois are in  [left, top, width, height] format
UI_ROI = {
    "chat_line_1": (12, 537, 391, 25),
    "save_and_exit": (500, 233, 273, 173),
    "play_btn": (426, 616, 320, 71),
    "difficulty_select": (536, 236, 210, 320),
    "gold_btn": (927, 491, 267, 100),
    "inventory_gold": (980, 510, 150, 40),
    "gold_btn_stash": (150, 480, 40, 65),
    "health_globe": (160, 580, 240, 140),
    "mana_globe": (887, 580, 240, 140),
    "health_slice": (309, 610, 7, 101),
    "mana_slice": (961, 610, 7, 101),
    "cut_skill_bar": (0, 0, 1280, 653),
    "reduce_to_center": (120, 60, 1040, 540),
    "search_npcs": (120, 0, 1040, 620),
    "merc_icon": (0, 0, 100, 100),
    "loading_left_black": (0, 0, 350, 720),
    "death": (513, 193, 253, 50),
    "tp_search": (353, 120, 547, 400),
    "repair_btn": (318, 473, 90, 80),
    "left_inventory": (35, 92, 378, 378),
    "right_inventory": (866, 348, 379, 152),
    "skill_right": (664, 673, 41, 41),
    "skill_right_expanded": (655, 375, 385, 255),
    "skill_left": (574, 673, 41, 41),
    "main_menu_top_left": (0, 0, 100, 100),
    "gamebar_anchor": (600, 650, 90, 90),
    "gamebar_belt_expandable": (792, 659, 28, 28),
    "repair_needed": (1000, 0, 280, 280),
    "wp_act_roi": (42, 66, 365, 53),
    "stash_btn_roi": (20, 52, 412, 53),
    "enemy_info": (440, 15, 405, 150),
    "shrine_check": (500, 50, 350, 100),
    "character_select": (1033, 44, 226, 554),
    "character_online_status": (1033, 19, 226, 25),
    # character_sub_roi is with respect to matched active character template),
    "character_name_sub_roi": (8, 22, 192, 32),
    "cube_area_roi": (167, 209, 113, 152),
    "cube_btn_roi": (160, 368, 125, 57),
    "xp_bar_text": (369, 630, 554, 34),
    "corpse": (459, 195, 414, 213),
    "chat_icon": (7, 555, 43, 41),
    "left_panel_header": (0, 0, 450, 54),
    "right_panel_header": (830, 0, 450, 54),
    "npc_dialogue": (458, 4, 21, 140),
    "bind_skill": (516, 619, 251, 29),
}


QUALITY_COLOR_MAP = {
    'white': ItemQuality.Normal,
    'gray': ItemQuality.Gray,
    'blue': ItemQuality.Magic,
    'green': ItemQuality.Set,
    'yellow': ItemQuality.Rare,
    'gold': ItemQuality.Unique,
    'orange': ItemQuality.Orange
}
