# ComfyUI-ColorConsistencyHSL

**HSL Color Consistency Advanced**  
A ComfyUI custom node for color/luminance consistency correction. Works with any image editing, enhancement, or upscaling workflow – especially optimized to address color shift issues caused by models like Flux.2-Klein.  
**Bilingual UI** – menu options automatically display in Chinese or English based on your ComfyUI language setting.

**HSL色彩一致性高级节点**  
适用于任何图像编辑、增强或放大工作流的色彩/亮度一致性校正节点。特别针对 Flux.2-Klein 等模型导致的色彩偏移问题进行了优化。  
**双语界面** – 根据 ComfyUI 语言设置，菜单选项自动显示中文或英文。

This node is designed for image editing model workflows, ideal for scenarios where images undergo high-definition upscaling or local content editing while preserving original colors. It enables color matching for heavily stylized images, effectively correcting unintended color shifts inevitably introduced by image editing models—a capability nearly impossible to achieve through other means.

本节点专为图像编辑模型工作流设计，适用于高清重绘放大或局部内容编辑后需保留原始色彩的图像。它能够对强烈风格化的图像进行色彩匹配，有效纠正图像编辑模型在生成过程中不可避免的意外色彩偏移——这是其他方法几乎无法实现的。

---

## Features / 功能亮点

- Universal applicability: works with any image editing/enhancement workflow / 通用性强：适用于任何图像编辑/增强工作流
- Independent control of L, H, S / 亮度、色相、饱和度独立控制
- Four anchor modes / 四种锚定模式：
  - Statistical match / 统计匹配
  - Pixel-perfect / 像素级精确
  - Luminance statistical + color exact / 亮度统计 + 色彩精确
  - Color exact (hue/saturation pixel-perfect, luminance unchanged) / 色彩精确（色相/饱和度像素级精确，亮度不变）
- Luminance matching in **LAB L channel** (perceptual) or **linear RGB luminance** (physical) / 亮度匹配可选 **LAB L 通道**（感知均匀）或 **线性RGB亮度**（物理准确）
- Auto mask / external mask with feathering / 自动蒙版 / 外部蒙版，支持羽化
- Protect edited regions with adjustable strength / 编辑区域保护强度可调
- Automatic size alignment with interpolation options / 自动尺寸对齐，可选插值方式
- Bilingual comments in code / 代码内含中英文注释

---

## Installation / 安装

### Option 1: ComfyUI Manager (recommended)
Search for **"Color Consistency HSL"** in ComfyUI Manager and install directly.

### Option 2: Git Clone
cd ComfyUI/custom_nodes/
git clone https://github.com/yourusername/ComfyUI-ColorConsistencyHSL.git

### Option 3: Manual Download
Download the ZIP and extract into `ComfyUI/custom_nodes/` folder.

Restart ComfyUI. The node will appear in the `image/postprocessing` category as **“HSL Color Consistency Advanced”** (English) or **“色彩亮度一致性混合 (HSL高级版)”** (Chinese).

---

## Dependencies / 依赖

- `scipy` (optional, only for feathering; if missing, feathering will be disabled but node still works)  
  `scipy`（可选，仅用于羽化；如未安装，羽化功能禁用但节点仍可运行）

Install with:
pip install scipy

---

## Parameters / 参数说明

| Parameter | Description |
|-----------|-------------|
| `reference` | Reference image (original) / 参考图像（原图） |
| `target` | Target image (edited) / 目标图像（编辑后） |
| `mode` | Channels to match: luminance, hue, saturation, any combination / 要匹配的通道：亮度、色相、饱和度，任意组合 |
| `anchor_mode` | Matching mode: statistical, pixel-perfect, luminance stat+color exact, color exact / 匹配模式：统计匹配、像素级精确、亮度统计+色彩精确、色彩精确 |
| `luma_space` | Space for luminance matching: LAB L channel or linear RGB luminance / 亮度匹配空间：LAB L通道 或 线性RGB亮度 |
| `align_corners` | Align corners when scaling (reduces pixel shift) / 缩放时对齐四角（减少像素偏移） |
| `interpolation` | Interpolation method for scaling: bilinear / nearest / 缩放插值方式：双线性 / 最近邻 |
| `force_match_size` | Auto-scale reference to match target size if different / 若尺寸不同，自动缩放参考图以匹配目标 |
| `luma_strength` | Strength of luminance statistical matching (0=original, 1=full match) / 亮度统计匹配强度（0=保留原图，1=完全匹配） |
| `strength` | Global blend strength / 整图混合强度 |
| `protect_strength` | Proportion of original image retained in edit area (0=full match, 1=full original) / 编辑区域保留原图的比例（0=完全匹配，1=完全原图） |
| `feather_radius` | Feather radius for mask (pixels) / 蒙版羽化半径（像素） |
| `auto_mask` | Enable auto mask generation based on image difference / 启用基于图像差异的自动蒙版 |
| `mask_threshold` | Threshold for auto mask (0-1) / 自动蒙版阈值 |
| `external_mask` | Optional external mask (white=edit area, black=stable) / 可选外部蒙版（白色=编辑区域，黑色=稳定区域） |

---

## Usage Example / 使用示例

This node can be used in any image editing/upscaling workflow. Below is a typical example:  
该节点可用于任何图像编辑/放大工作流。以下是一个典型示例：

[Load Image] (original) → [Edit Model] → [Load Image] (edited)
                                   ↓
[original] → [Color Consistency HSL] (reference)
[edited]   → [Color Consistency HSL] (target)
[optional mask] → [Color Consistency HSL] (external_mask)
                                   ↓
[Color Consistency HSL] → [Save Image]

While the node is universally applicable, it is particularly effective for addressing color shift issues caused by models like Flux.2-Klein.  
虽然该节点通用性强，但它在解决 Flux.2-Klein 等模型引起的色彩偏移问题上尤为出色。

Recommended settings for Flux.2-Klein edits with luminance preservation:  
针对 Flux.2-Klein 增强且需保留亮度的推荐设置：
- `mode`: `luminance+hue+saturation`
- `anchor_mode`: `luminance stat + color exact`
- `luma_strength`: 0.5
- `protect_strength`: 0.3 (adjust based on edit area)
- `feather_radius`: 15

---

## License / 许可证

MIT License. See [LICENSE](LICENSE) for details.

## Author / 作者

**overcloud81** (@github @modelscope) with deepseek  
Copyright © 2026 overcloud81. All rights reserved.
