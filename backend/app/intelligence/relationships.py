from typing import Dict, Any, List, Optional
from app.intelligence.geometry import calculate_iou, calculate_support_ratio, centroid, euclidean_distance

class SpatialRelationships:
    @staticmethod
    def is_carrying(person_box: List[float], carton_box: List[float]) -> bool:
        """Determines if a person is likely carrying or holding a carton."""
        p_cx, p_cy = centroid(person_box)
        c_cx, c_cy = centroid(carton_box)
        dist = euclidean_distance((p_cx, p_cy), (c_cx, c_cy))
        # Carton is typically in front of/overlapping chest/hands of person
        return dist < 90.0 and (carton_box[1] > person_box[1] + 10)

    @staticmethod
    def is_on_pallet(carton_box: List[float], pallet_box: List[float]) -> float:
        return calculate_support_ratio(carton_box, pallet_box)

    @staticmethod
    def is_near_floor(carton_box: List[float], frame_height: int) -> bool:
        # Bottom of carton is in bottom 25% of frame
        return carton_box[3] >= frame_height * 0.75
