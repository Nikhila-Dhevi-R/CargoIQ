from typing import List, Dict, Any, Optional
from app.intelligence.geometry import calculate_iou, calculate_support_ratio, centroid, euclidean_distance

class SceneGraph:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def build_frame_graph(self, detections: List[Dict[str, Any]], zone_manager, img_w: int, img_h: int):
        """
        detections: list of dicts with keys:
            track_id, class_name, bbox [x1, y1, x2, y2], confidence
        """
        self.nodes.clear()
        self.edges.clear()

        # Add nodes
        for d in detections:
            tid = d["track_id"]
            cname = d["class_name"]
            box = d["bbox"]
            node_id = f"{cname.upper()}_{tid}"
            zone = zone_manager.get_zone_for_box(box, img_w, img_h)
            self.nodes[node_id] = {
                "id": node_id,
                "track_id": tid,
                "class_name": cname,
                "bbox": box,
                "centroid": centroid(box),
                "zone": zone
            }

        node_list = list(self.nodes.values())
        n = len(node_list)

        for i in range(n):
            n1 = node_list[i]
            # Relation: inside_zone
            self.edges.append({
                "source": n1["id"],
                "target": n1["zone"],
                "relation": "inside_zone"
            })

            for j in range(i + 1, n):
                n2 = node_list[j]
                dist = euclidean_distance(n1["centroid"], n2["centroid"])
                iou = calculate_iou(n1["bbox"], n2["bbox"])

                # Spatial proximity
                if dist < 160.0:
                    self.edges.append({
                        "source": n1["id"],
                        "target": n2["id"],
                        "relation": "near",
                        "distance": round(dist, 1)
                    })

                # Person interacting with product/carton
                if (n1["class_name"] == "person" and n2["class_name"] in ["carton", "package", "box"]) or \
                   (n2["class_name"] == "person" and n1["class_name"] in ["carton", "package", "box"]):
                    p_node = n1 if n1["class_name"] == "person" else n2
                    c_node = n2 if n1["class_name"] == "person" else n1
                    if dist < 120.0 or iou > 0.05:
                        self.edges.append({
                            "source": p_node["id"],
                            "target": c_node["id"],
                            "relation": "interacting_with"
                        })

                # Carton supported by pallet
                if (n1["class_name"] in ["carton", "package", "box"] and n2["class_name"] == "pallet"):
                    sup = calculate_support_ratio(n1["bbox"], n2["bbox"])
                    if sup > 0.1:
                        self.edges.append({
                            "source": n1["id"],
                            "target": n2["id"],
                            "relation": "supported_by",
                            "support_ratio": round(sup, 2)
                        })
                elif (n2["class_name"] in ["carton", "package", "box"] and n1["class_name"] == "pallet"):
                    sup = calculate_support_ratio(n2["bbox"], n1["bbox"])
                    if sup > 0.1:
                        self.edges.append({
                            "source": n2["id"],
                            "target": n1["id"],
                            "relation": "supported_by",
                            "support_ratio": round(sup, 2)
                        })

    def get_relations_for_object(self, object_label: str) -> List[Dict[str, Any]]:
        return [e for e in self.edges if e.get("source") == object_label or e.get("target") == object_label]
