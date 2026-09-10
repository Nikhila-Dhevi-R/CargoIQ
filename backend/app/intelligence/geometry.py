import math
from typing import Tuple, List, Optional

def calculate_iou(boxA: List[float], boxB: List[float]) -> float:
    """Calculates Intersection over Union between two bounding boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0.0, xB - xA)
    inter_h = max(0.0, yB - yA)
    inter_area = inter_w * inter_h

    areaA = max(0.0, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    areaB = max(0.0, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    union_area = areaA + areaB - inter_area
    if union_area <= 0.0:
        return 0.0
    return inter_area / union_area

def calculate_support_ratio(carton_box: List[float], pallet_box: List[float]) -> float:
    """
    Calculates horizontal base support ratio:
    intersection horizontal width between carton base and pallet base / carton base width.
    """
    carton_w = max(1.0, carton_box[2] - carton_box[0])
    carton_bottom = carton_box[3]
    pallet_top = pallet_box[1]

    # Check if carton is sitting near pallet top
    # Vertical tolerance
    if abs(carton_bottom - pallet_top) > 40.0 and carton_bottom < pallet_top - 5:
        # Not on top of pallet
        return 0.0

    inter_x1 = max(carton_box[0], pallet_box[0])
    inter_x2 = min(carton_box[2], pallet_box[2])
    inter_w = max(0.0, inter_x2 - inter_x1)

    return min(1.0, inter_w / carton_w)

def centroid(box: List[float]) -> Tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)

def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
    """Ray casting algorithm to determine if a point [x, y] is inside a polygon."""
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside
