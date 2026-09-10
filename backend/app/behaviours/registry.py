from typing import Dict, Any, List, Type
from app.behaviours.drop_throw import DropThrowBehaviour
from app.behaviours.drag import DragBehaviour
from app.behaviours.overhang import PalletOverhangBehaviour
from app.behaviours.staging import ImproperStagingBehaviour
from app.behaviours.stacking import StackingBehaviour
from app.behaviours.unsupported_stack import UnsupportedStackBehaviour
from app.behaviours.rough_handling import RoughHandlingBehaviour
from app.behaviours.orientation import OrientationBehaviour
from app.behaviours.sequence import SequenceBehaviour
from app.behaviours.equipment import EquipmentBehaviour

class BehaviourRegistry:
    MODULES = [
        DropThrowBehaviour,
        DragBehaviour,
        PalletOverhangBehaviour,
        ImproperStagingBehaviour,
        StackingBehaviour,
        UnsupportedStackBehaviour,
        RoughHandlingBehaviour,
        OrientationBehaviour,
        SequenceBehaviour,
        EquipmentBehaviour,
    ]

    @classmethod
    def get_all_codes(cls) -> List[str]:
        return [m.CODE for m in cls.MODULES]

    @classmethod
    def get_module(cls, code: str):
        for m in cls.MODULES:
            if m.CODE == code:
                return m
        return None
