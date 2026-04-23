from typing import Dict, Tuple

BBoxTuple = Tuple[int, int, int, int]

LOT_1_STALLS: Dict[str, BBoxTuple] = {
    "A1": (827, 119, 891, 162),
    "A2": (776, 116, 839, 162),
    "A3": (729, 116, 784, 163),
    "A4": (679, 115, 731, 164),
    "A5": (630, 119, 676, 164),
    "A6": (581, 119, 624, 161),
    "A7": (536, 120, 573, 162),
    "A8": (486, 122, 517, 167),

    "B2": (795, 214, 874, 282),
    "B3": (737, 214, 807, 283),
    "B4": (679, 217, 743, 281),
    "B5": (619, 216, 677, 282),
    "B6": (560, 217, 611, 281),
    "B7": (503, 215, 546, 282),

    "C2": (815, 317, 910, 413),
    "C3": (745, 320, 833, 413),
    "C4": (676, 319, 754, 413),
    "C5": (609, 319, 675, 414),
    "C6": (541, 320, 594, 415),
    "C7": (472, 320, 517, 419),

    "D1": (942, 522, 1095, 693),
    "D2": (851, 522, 986, 694),
    "D3": (764, 524, 880, 696),
    "D4": (674, 526, 774, 691),
    "D5": (587, 527, 671, 689),
    "D6": (496, 524, 564, 692),
    "D7": (407, 524, 457, 690),
    "D8": (324, 524, 348, 692),
}

LOT_2_STALLS: Dict[str, BBoxTuple] = {
    "A1": (276, 521, 312, 684),
    "A2": (363, 519, 416, 683),
    "A3": (452, 519, 521, 677),
    "A4": (540, 518, 627, 677),
    "A5": (631, 519, 731, 677),
    "A6": (720, 517, 837, 673),
    "A7": (808, 513, 945, 673),
    "A8": (898, 511, 1051, 672),

    "B2": (425, 314, 476, 411),
    "B3": (492, 314, 553, 407),
    "B4": (561, 313, 630, 405),
    "B5": (632, 311, 710, 405),
    "B6": (702, 310, 788, 404),
    "B7": (772, 309, 867, 401),

    "C2": (456, 212, 500, 278),
    "C3": (516, 209, 566, 277),
    "C4": (575, 209, 633, 275),
    "C5": (633, 205, 700, 273),
    "C6": (692, 205, 763, 273),
    "C7": (753, 205, 829, 273),
    
    "D1": (438, 110, 472, 156),
    "D2": (488, 109, 528, 155),
    "D3": (536, 109, 581, 153),
    "D4": (586, 108, 633, 153),
    "D5": (635, 107, 688, 150),
    "D6": (684, 106, 742, 152),
    "D7": (733, 106, 796, 149),
    "D8": (782, 101, 850, 149),
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