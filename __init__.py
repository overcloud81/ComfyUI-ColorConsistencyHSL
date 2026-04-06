# __init__.py
import importlib.util
import os

module_path = os.path.join(os.path.dirname(__file__), 'ComfyUI-ColorConsistencyHSL.py')
spec = importlib.util.spec_from_file_location("ComfyUI_ColorConsistencyHSL", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ColorConsistencyHSLAdvanced = module.ColorConsistencyHSLAdvanced

NODE_CLASS_MAPPINGS = {
    "Color Consistency HSL Advanced": ColorConsistencyHSLAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Color Consistency HSL Advanced": "HSL Color Consistency Advanced",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
