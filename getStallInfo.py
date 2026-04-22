from typing import Dict


LOT_1_STALLS: Dict[str, Dict[str, int]] = {
    "A1": {"x1": 403,  "y1": 81,  "x2": 597,  "y2": 197},
    "A2": {"x1": 405,  "y1": 218, "x2": 598,  "y2": 330},
    "A3": {"x1": 402,  "y1": 356, "x2": 601,  "y2": 482},
    "A4": {"x1": 402,  "y1": 500, "x2": 602,  "y2": 631},
    "A5": {"x1": 890,  "y1": 55,  "x2": 1115, "y2": 174},
    "A6": {"x1": 897,  "y1": 200, "x2": 1124, "y2": 320},
    "A7": {"x1": 902,  "y1": 356, "x2": 1132, "y2": 471},
    "A8": {"x1": 912,  "y1": 497, "x2": 1151, "y2": 634},
}

LOT_2_STALLS: Dict[str, Dict[str, int]] = {
    "B1": {"x1": 0, "y1": 0, "x2": 0, "y2": 0},
    "B2": {"x1": 0, "y1": 0, "x2": 0, "y2": 0},
    "B3": {"x1": 0, "y1": 0, "x2": 0, "y2": 0},
    "B4": {"x1": 0, "y1": 0, "x2": 0, "y2": 0},
    "B5": {"x1": 0, "y1": 0, "x2": 0, "y2": 0},
    "B6": {"x1": 0, "y1": 0, "x2": 0, "y2": 0},
    "B7": {"x1": 0, "y1": 0, "x2": 0, "y2": 0},
    "B8": {"x1": 0, "y1": 0, "x2": 0, "y2": 0},
}


def get_stall_config(lot_num: int = 1) -> Dict[str, Dict[str, int]]:
    if lot_num == 1:
        return LOT_1_STALLS
    elif lot_num == 2:
        return LOT_2_STALLS
    else:
        raise ValueError(f"Invalid lot_num: {lot_num}. Must be 1 or 2.")