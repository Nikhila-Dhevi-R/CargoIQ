from typing import List, Dict, Any, Optional, Tuple
from app.intelligence.geometry import point_in_polygon, centroid

DEFAULT_ZONES: List[Dict[str, Any]] = [
    {
        "name": "Loading Bay 1",
        "color": "#ef4444",
        "description": "Inbound primary truck unloading bay",
        "polygon": [[0.02, 0.15], [0.35, 0.15], [0.35, 0.85], [0.02, 0.85]]
    },
    {
        "name": "Loading Bay 2",
        "color": "#f97316",
        "description": "Inbound secondary unloading bay",
        "polygon": [[0.36, 0.15], [0.65, 0.15], [0.65, 0.50], [0.36, 0.50]]
    },
    {
        "name": "Staging Zone A",
        "color": "#3b82f6",
        "description": "Primary sorting and palletizing pad",
        "polygon": [[0.36, 0.52], [0.65, 0.52], [0.65, 0.88], [0.36, 0.88]]
    },
    {
        "name": "Staging Zone B",
        "color": "#8b5cf6",
        "description": "Buffer and inspection staging area",
        "polygon": [[0.68, 0.15], [0.98, 0.15], [0.98, 0.55], [0.68, 0.55]]
    },
    {
        "name": "Dispatch Area",
        "color": "#10b981",
        "description": "Outbound order staging and packing lane",
        "polygon": [[0.68, 0.58], [0.98, 0.58], [0.98, 0.90], [0.68, 0.90]]
    }
]

class ZoneManager:
    def __init__(self, zones: Optional[List[Dict[str, Any]]] = None):
        self.zones = zones or DEFAULT_ZONES

    def get_zone_for_point(self, norm_x: float, norm_y: float) -> str:
        for z in self.zones:
            poly = z.get("polygon", [])
            if poly and point_in_polygon((norm_x, norm_y), poly):
                return z.get("name", "General Area")
        return "General Walkway"

    def get_zone_for_box(self, box: List[float], img_w: int, img_h: int) -> str:
        cx, cy = centroid(box)
        norm_x = cx / max(1.0, float(img_w))
        norm_y = cy / max(1.0, float(img_h))
        return self.get_zone_for_point(norm_x, norm_y)
