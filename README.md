# ComfyUI-ColorConsistencyHSL

A ComfyUI custom node for color/luminance consistency correction.  
Supports independent matching of **Luminance (L)**, **Hue (H)**, and **Saturation (S)** with multiple anchor modes and mask protection.

**Bilingual UI** (Chinese/English) – adapts automatically to your ComfyUI language setting.

## Features
- Independent control of L, H, S
- Four anchor modes:
  - Statistical match
  - Pixel-perfect
  - Luminance statistical + color exact
  - Color exact (hue/saturation pixel-perfect, luminance unchanged)
- Luminance matching in **LAB L channel** (perceptual) or **linear RGB luminance** (physical)
- Auto mask / external mask with feathering
- Protect edited regions with adjustable strength
- Automatic size alignment with interpolation options
- Fully documented (bilingual comments in code)

## Installation

### Option 1: ComfyUI Manager (Recommended)
Search for "Color Consistency HSL" in ComfyUI Manager and install directly.

### Option 2: Git Clone
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/yourusername/ComfyUI-ColorConsistencyHSL.git