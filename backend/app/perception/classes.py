from typing import Dict, List

WAREHOUSE_CLASSES = {
    0: "person",
    39: "bottle",
    24: "backpack",
    26: "handbag",
    28: "suitcase",
    # COCO maps
}

# Configurable semantic label mappings
CLASS_MAPPING = {
    "person": "person",
    "suitcase": "carton",
    "backpack": "package",
    "box": "carton",
    "carton": "carton",
    "package": "carton",
    "pallet": "pallet",
    "forklift": "forklift",
    "trolley": "trolley",
    "truck": "truck",
    "bed": "mattress"
}

TARGET_CLASSES = ["person", "carton", "package", "pallet", "trolley", "forklift"]
