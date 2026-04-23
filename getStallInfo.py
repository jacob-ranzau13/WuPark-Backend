from typing import Dict, Tuple

BBoxTuple = Tuple[int, int, int, int]

LOT_1_STALLS: Dict[str, BBoxTuple] = {
    "A1": (0, 0, 0, 0),
    "A2": (0, 0, 0, 0),
    "A3": (0, 0, 0, 0),
    "A4": (0, 0, 0, 0),
    "A5": (0, 0, 0, 0),
    "A6": (0, 0, 0, 0),
    "A7": (0, 0, 0, 0),
    "A8": (0, 0, 0, 0),

    "B2": (0, 0, 0, 0),
    "B3": (0, 0, 0, 0),
    "B4": (0, 0, 0, 0),
    "B5": (0, 0, 0, 0),
    "B6": (0, 0, 0, 0),
    "B7": (0, 0, 0, 0),

    "C2": (0, 0, 0, 0),
    "C3": (0, 0, 0, 0),
    "C4": (0, 0, 0, 0),
    "C5": (0, 0, 0, 0),
    "C6": (0, 0, 0, 0),
    "C7": (0, 0, 0, 0),

    "D1": (0, 0, 0, 0),
    "D2": (0, 0, 0, 0),
    "D3": (0, 0, 0, 0),
    "D4": (0, 0, 0, 0),
    "D5": (0, 0, 0, 0),
    "D6": (0, 0, 0, 0),
    "D7": (0, 0, 0, 0),
    "D8": (0, 0, 0, 0),
}

LOT_2_STALLS: Dict[str, BBoxTuple] = {
    "A1": (92, 339, 118, 455),
    "A2": (154, 341, 190, 457),
    "A3": (212, 343, 264, 457),
    "A4": (274, 344, 335, 457),
    "A5": (335, 343, 407, 459),
    "A6": (396, 348, 480, 461),
    "A7": (458, 350, 553, 461),
    "A8": (520, 349, 629, 465),

    "B2": (194, 196, 228, 265),
    "B3": (241, 199, 282, 265),
    "B4": (288, 201, 336, 266),
    "B5": (336, 198, 390, 268),
    "B6": (384, 201, 443, 267),
    "B7": (432, 202, 496, 268),

    "C2": (216, 126, 247, 174),
    "C3": (256, 129, 292, 173),
    "C4": (296, 129, 336, 174),
    "C5": (336, 129, 382, 175),
    "C6": (376, 127, 427, 175),
    "C7": (420, 127, 473, 177),

    "D1": (203, 53, 227, 89),
    "D2": (236, 55, 262, 88),
    "D3": (269, 57, 300, 89),
    "D4": (304, 57, 337, 87),
    "D5": (336, 58, 375, 88),
    "D6": (371, 57, 412, 88),
    "D7": (405, 57, 447, 89),
    "D8": (438, 57, 487, 90)
}


def make_box(x1: int, y1: int, x2: int, y2: int) -> Dict[str, int]:
    return {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
    }


def shrink_box(box: Dict[str, int], shrink_x: int = 4, shrink_y: int = 4) -> Dict[str, int]:
    new_x1 = box["x1"] + shrink_x
    new_y1 = box["y1"] + shrink_y
    new_x2 = box["x2"] - shrink_x
    new_y2 = box["y2"] - shrink_y

    if new_x1 >= new_x2 or new_y1 >= new_y2:
        return box

    return {
        "x1": new_x1,
        "y1": new_y1,
        "x2": new_x2,
        "y2": new_y2,
    }


def get_row_shrink(stall_id: str) -> Tuple[int, int]:
    row = stall_id[0]

    if row == "A":
        return (4, 4)
    if row == "B":
        return (3, 3)
    if row == "C":
        return (3, 3)
    if row == "D":
        return (4, 4)

    return (4, 4)

def build_stall_config(raw_stalls: Dict[str, BBoxTuple]) -> Dict[str, Dict[str, int]]:
    stalls: Dict[str, Dict[str, int]] = {}

    for stall_id, (x1, y1, x2, y2) in raw_stalls.items():
        box = make_box(x1, y1, x2, y2)
        shrink_x, shrink_y = get_row_shrink(stall_id)
        stalls[stall_id] = shrink_box(box, shrink_x=shrink_x, shrink_y=shrink_y)

    return stalls

def get_stall_config(lot_num: int = 1) -> Dict[str, Dict[str, int]]:
    if lot_num == 1:
        return build_stall_config(LOT_1_STALLS)
    elif lot_num == 2:
        return build_stall_config(LOT_2_STALLS)
    else:
        raise ValueError(f"Invalid lot_num: {lot_num}. Must be 1 or 2.")