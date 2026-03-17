# ComfyUI-ColorConsistencyHSL

**HSL Color Consistency Advanced**  
A ComfyUI custom node for color/luminance consistency correction. Works with any image editing, enhancement, or upscaling workflow – especially optimized to address color shift issues caused by models like Flux.2-Klein.  
**Bilingual UI** – menu options automatically display in Chinese or English based on your ComfyUI language setting.

**HSL色彩一致性高级节点**  
适用于任何图像编辑、增强或放大工作流的色彩/亮度一致性校正节点。特别针对 Flux.2-Klein 等模型导致的色彩偏移问题进行了优化。  
**双语界面** – 根据 ComfyUI 语言设置，菜单选项自动显示中文或英文。

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
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/yourusername/ComfyUI-ColorConsistencyHSL.git
