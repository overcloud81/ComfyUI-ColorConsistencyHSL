# __init__.py
from .color_consistency_hsl_advanced import ColorConsistencyHSLAdvanced

NODE_CLASS_MAPPINGS = {
    "Color Consistency HSL Advanced": ColorConsistencyHSLAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Color Consistency HSL Advanced": "HSL Color Consistency Advanced",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']