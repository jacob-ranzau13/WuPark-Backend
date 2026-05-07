from typing import Dict, Tuple

BBoxTuple = Tuple[int, int, int, int]

LOT_1_STALLS: Dict[str, BBoxTuple] = {
    "A1": (264, 523, 287, 673),
    "A2": (349, 525, 395, 675),
    "A3": (441, 528, 487, 683),
    "A4": (528, 529, 585, 682),
    "A5": (613, 534, 688, 684),
    "A6": (697, 536, 781, 689),
    "A7": (798, 541, 870, 680),
    "A8": (887, 539, 971, 682),

    "B2": (425, 332, 459, 424),
    "B3": (493, 337, 533, 422),
    "B4": (559, 340, 608, 423),
    "B5": (628, 339, 684, 428),
    "B6": (694, 343, 761, 431),
    "B7": (760, 345, 837, 431),

    "C2": (462, 241, 493, 300),
    "C3": (521, 243, 555, 303),
    "C4": (578, 245, 620, 304),
    "C5": (634, 247, 683, 305),
    "C6": (690, 249, 747, 306),
    "C7": (749, 250, 807, 309),

    "D1": (451, 149, 476, 190),
    "D2": (499, 151, 528, 189),
    "D3": (547, 152, 577, 193),
    "D4": (594, 157, 630, 197),
    "D5": (642, 157, 682, 196),
    "D6": (688, 160, 730, 198),
    "D7": (734, 161, 782, 202),
    "D8": (783, 162, 828, 203),
}

LOT_2_STALLS: Dict[str, BBoxTuple] = {
    "A1": (857, 127, 885, 170),
    "A2": (805, 128, 835, 172),
    "A3": (753, 133, 788, 176),
    "A4": (702, 137, 740, 178),
    "A5": (647, 139, 693, 181),
    "A6": (600, 142, 644, 185),
    "A7": (548, 143, 596, 186),
    "A8": (504, 149, 545, 189),

    "B2": (832, 223, 868, 281),
    "B3": (768, 224, 811, 286),
    "B4": (706, 228, 750, 287),
    "B5": (644, 231, 691, 290),
    "B6": (583, 230, 634, 296),
    "B7": (520, 235, 576, 297),

    "C2": (861, 320, 902, 406),
    "C3": (785, 324, 830, 404),
    "C4": (709, 326, 763, 410),
    "C5": (632, 326, 694, 411),
    "C6": (558, 331, 623, 415),
    "C7": (491, 336, 553, 420),

    "D1": (1030, 510, 1055, 665),
    "D2": (922, 509, 967, 670),
    "D3": (818, 512, 873, 666),
    "D4": (711, 516, 787, 670),
    "D5": (613, 515, 700, 670),
    "D6": (516, 521, 613, 670),
    "D7": (432, 523, 520, 673),
    "D8": (342, 529, 426, 669),
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