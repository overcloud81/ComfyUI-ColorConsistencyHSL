# Version: 5.2 (Final) - Bilingual UI & Comments
# Author: overcloud81(@github @modelscope) with deepseek
# Copyright (c) 2025 overcloud81. All rights reserved.
# 功能：支持亮度(L)、色相(H)、饱和度(S)独立匹配，新增“色彩精确”模式（色相/饱和度像素级精确，亮度不变）
#       所有参数已设为合理默认值，开箱即用
# Features: Independent matching of Luminance (L), Hue (H), Saturation (S). New "Color Exact" mode (pixel-perfect hue/saturation, luminance unchanged).
#           All parameters have sensible defaults for out-of-the-box use.

import torch
import numpy as np
from scipy.ndimage import gaussian_filter
import folder_paths
import os

class ColorConsistencyHSLAdvanced:
    """
    HSL-based color consistency node.
    Supports independent matching of Luminance, Hue, Saturation.
    Four anchor modes: statistical match, pixel-perfect, luminance stat + color exact, color exact.
    Bilingual UI (Chinese/English) with automatic adaptation based on ComfyUI language setting.
    """
    @classmethod
    def INPUT_TYPES(cls):
        # 检测 ComfyUI 语言设置 / Detect ComfyUI language setting
        is_chinese = cls._is_chinese_locale()
        
        # 根据语言设置选择菜单文字 / Select menu text based on language
        if is_chinese:
            mode_list = ["亮度", "色相", "饱和度", "亮度+色相", "亮度+饱和度", "色相+饱和度", "亮度+色相+饱和度"]
            anchor_mode_list = ["统计匹配", "像素级精确", "亮度统计+色彩精确", "色彩精确"]
            luma_space_list = ["LAB L通道", "线性RGB亮度"]
            interpolation_list = ["bilinear", "nearest"]
            mode_default = "亮度+色相+饱和度"
            anchor_default = "统计匹配"
            luma_default = "LAB L通道"
        else:
            mode_list = ["luminance", "hue", "saturation", "luminance+hue", "luminance+saturation", "hue+saturation", "luminance+hue+saturation"]
            anchor_mode_list = ["statistical match", "pixel-perfect", "luminance stat + color exact", "color exact"]
            luma_space_list = ["LAB L channel", "linear RGB luminance"]
            interpolation_list = ["bilinear", "nearest"]
            mode_default = "luminance+hue+saturation"
            anchor_default = "statistical match"
            luma_default = "LAB L channel"
        
        return {
            "required": {
                "reference": ("IMAGE",),
                "target": ("IMAGE",),
                "mode": (mode_list, {"default": mode_default}),
                "anchor_mode": (anchor_mode_list, {
                    "default": anchor_default,
                    "tooltip": "色彩精确：色相和饱和度像素级精确，亮度不变 / Color exact: pixel-perfect hue/saturation, luminance unchanged"
                }),
                "luma_space": (luma_space_list, {
                    "default": luma_default,
                    "tooltip": "亮度统计匹配的空间（仅当亮度参与匹配时有效） / Space for luminance statistical matching (only when luminance is matched)"
                }),
                "align_corners": ("BOOLEAN", {"default": True, "tooltip": "对齐四角，True可减少像素偏移 / Align corners, True reduces pixel shift"}),
                "interpolation": (interpolation_list, {"default": "bilinear", "tooltip": "缩放插值方式 / Interpolation method for scaling"}),
                "force_match_size": ("BOOLEAN", {"default": False, "tooltip": "强制尺寸一致（不一致时自动缩放） / Force size match (auto-scale if different)"}),
                "luma_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "亮度统计匹配强度（仅亮度参与统计匹配时有效） / Strength of luminance statistical matching (only when luminance is matched statistically)"
                }),
                "strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "整图混合强度 / Global blend strength"
                }),
                "protect_strength": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "编辑区域保留原图的比例 / Proportion of original image retained in edit area"
                }),
                "feather_radius": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "slider",
                    "tooltip": "蒙版羽化半径（像素） / Mask feather radius (pixels)"
                }),
                "auto_mask": ("BOOLEAN", {"default": False, "tooltip": "启用自动蒙版 / Enable auto mask"}),
                "mask_threshold": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "自动蒙版阈值 / Auto mask threshold"
                }),
            },
            "optional": {
                "external_mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "blend"
    CATEGORY = "image/postprocessing"

    @staticmethod
    def _is_chinese_locale():
        """检测是否为中文界面 / Detect if UI is in Chinese"""
        try:
            # 方法1: 检查 ComfyUI 配置文件 / Check ComfyUI config file
            config_path = os.path.join(folder_paths.base_path, "comfy.settings.json")
            if os.path.exists(config_path):
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    lang = config.get("Comfy.Locale", {}).get("value", "en")
                    if isinstance(lang, str):
                        return lang.startswith('zh') or lang == 'zh-CN' or lang == 'zh-TW'
            
            # 方法2: 检查环境变量 / Check environment variable
            lang_env = os.environ.get('COMFYUI_LANG', '')
            if lang_env.startswith('zh'):
                return True
                
            # 默认英文 / Default to English
            return False
        except:
            return False

    def blend(self, reference, target, mode, anchor_mode, luma_space, align_corners, interpolation, force_match_size,
              luma_strength, strength, protect_strength, feather_radius, auto_mask, mask_threshold, external_mask=None):
        # 参数有效性验证 / Parameter validation
        valid_interpolations = ["bilinear", "nearest"]
        if interpolation not in valid_interpolations:
            print(f"警告: interpolation '{interpolation}' 无效，使用默认 'bilinear' / Warning: interpolation '{interpolation}' invalid, using default 'bilinear'")
            interpolation = "bilinear"

        # 安全裁剪数值参数 / Safely clip numeric parameters
        luma_strength = np.clip(luma_strength, 0.0, 1.0)
        protect_strength = np.clip(protect_strength, 0.0, 1.0)
        strength = np.clip(strength, 0.0, 1.0)
        feather_radius = max(0, int(feather_radius))
        mask_threshold = np.clip(mask_threshold, 0.0, 1.0)

        # 将中英文模式映射到通道索引列表 / Map Chinese/English mode to channel indices
        mode_map = {
            "亮度": [0], "luminance": [0],
            "色相": [1], "hue": [1],
            "饱和度": [2], "saturation": [2],
            "亮度+色相": [0, 1], "luminance+hue": [0, 1],
            "亮度+饱和度": [0, 2], "luminance+saturation": [0, 2],
            "色相+饱和度": [1, 2], "hue+saturation": [1, 2],
            "亮度+色相+饱和度": [0, 1, 2], "luminance+hue+saturation": [0, 1, 2],
        }
        channels_to_match = mode_map.get(mode, [0, 1, 2])  # 默认全通道 / default all channels

        # 转换为 (B,H,W,C) float32 0-1 / Convert to (B,H,W,C) float32 0-1
        ref_np = self._prepare_image(reference)
        tgt_np = self._prepare_image(target)

        # 批次兼容 / Batch compatibility
        if ref_np.shape[0] == 1 and tgt_np.shape[0] > 1:
            ref_np = np.repeat(ref_np, tgt_np.shape[0], axis=0)
        elif tgt_np.shape[0] == 1 and ref_np.shape[0] > 1:
            tgt_np = np.repeat(tgt_np, ref_np.shape[0], axis=0)
        elif ref_np.shape[0] != tgt_np.shape[0]:
            raise ValueError(f"批次不匹配: ref {ref_np.shape[0]}, tgt {tgt_np.shape[0]} / Batch mismatch: ref {ref_np.shape[0]}, tgt {tgt_np.shape[0]}")

        # 尺寸检查与处理 / Size check and handling
        if ref_np.shape[1:3] != tgt_np.shape[1:3]:
            if force_match_size:
                print(f"警告: force_match_size=True 但尺寸不一致，将自动缩放参考图以匹配目标图。 / Warning: force_match_size=True but sizes differ, auto-scaling reference to match target.")
            ref_tensor = torch.from_numpy(ref_np).permute(0, 3, 1, 2)
            mode_map_interp = {"bilinear": "bilinear", "nearest": "nearest"}
            ref_tensor = torch.nn.functional.interpolate(ref_tensor, size=tgt_np.shape[1:3], mode=mode_map_interp[interpolation], align_corners=align_corners if interpolation == "bilinear" else None)
            ref_np = ref_tensor.permute(0, 2, 3, 1).numpy()

        # 获取原始蒙版（白色=编辑区域，黑色=稳定区域） / Get raw mask (white=edit area, black=stable area)
        raw_mask = self._get_mask(ref_np, tgt_np, auto_mask, mask_threshold, external_mask)

        # 羽化蒙版 / Feather mask
        mask = self._feather_mask(raw_mask, feather_radius) if raw_mask is not None else None

        # 色相/饱和度处理始终在 LAB 空间进行，亮度处理根据 luma_space 选择
        # Hue/saturation always processed in LAB space, luminance processing depends on luma_space
        ref_lab = self._rgb_to_lab(ref_np)
        tgt_lab = self._rgb_to_lab(tgt_np)

        # 将 a,b 转换为极坐标：色相 H (角度) 和 饱和度 S (模长)
        # Convert a,b to polar: Hue H (angle) and Saturation S (magnitude)
        ref_H, ref_S = self._cartesian_to_polar(ref_lab[..., 1], ref_lab[..., 2])
        tgt_H, tgt_S = self._cartesian_to_polar(tgt_lab[..., 1], tgt_lab[..., 2])

        # 构建 HSL 堆叠：L, H, S（L 可能来自 LAB 或 线性亮度）
        # Build HSL stack: L, H, S (L may come from LAB or linear luminance)
        if luma_space in ["LAB L通道", "LAB L channel"]:
            ref_luma = ref_lab[..., 0]
            tgt_luma = tgt_lab[..., 0]
        else:  # 线性RGB亮度 / linear RGB luminance
            ref_lin = self._srgb_to_linear(ref_np)
            tgt_lin = self._srgb_to_linear(tgt_np)
            ref_luma = 0.2126 * ref_lin[..., 0] + 0.7152 * ref_lin[..., 1] + 0.0722 * ref_lin[..., 2]
            tgt_luma = 0.2126 * tgt_lin[..., 0] + 0.7152 * tgt_lin[..., 1] + 0.0722 * tgt_lin[..., 2]

        ref_hsl = np.stack([ref_luma, ref_H, ref_S], axis=-1)
        tgt_hsl = np.stack([tgt_luma, tgt_H, tgt_S], axis=-1)

        # 根据锚定模式生成匹配结果 / Generate matching result based on anchor mode
        matched_hsl = tgt_hsl.copy()

        if anchor_mode in ["统计匹配", "statistical match"]:
            matched_hsl = self._match_channels_hsl(ref_hsl, tgt_hsl, mask, channels_to_match, luma_strength)
        elif anchor_mode in ["像素级精确", "pixel-perfect"]:
            for ch in channels_to_match:
                matched_hsl[..., ch] = ref_hsl[..., ch]
        elif anchor_mode in ["亮度统计+色彩精确", "luminance stat + color exact"]:
            # 亮度统计匹配，色相/饱和度精确 / luminance statistical match, hue/saturation exact
            for ch in channels_to_match:
                if ch == 0:  # 亮度 / luminance
                    if mask is None:
                        ref_mean = ref_hsl[..., ch].mean(axis=(1,2), keepdims=True)
                        ref_std = ref_hsl[..., ch].std(axis=(1,2), keepdims=True)
                        tgt_mean = tgt_hsl[..., ch].mean(axis=(1,2), keepdims=True)
                        tgt_std = tgt_hsl[..., ch].std(axis=(1,2), keepdims=True)
                        adjusted = (tgt_hsl[..., ch] - tgt_mean.squeeze()) / (tgt_std.squeeze() + 1e-8) * ref_std.squeeze() + ref_mean.squeeze()
                        matched_hsl[..., ch] = luma_strength * adjusted + (1 - luma_strength) * tgt_hsl[..., ch]
                    else:
                        for i in range(ref_hsl.shape[0]):
                            stable = mask[i] < 0.5
                            if np.sum(stable) == 0:
                                stable = np.ones_like(mask[i], dtype=bool)
                            ref_vals = ref_hsl[i, ..., ch][stable]
                            tgt_vals = tgt_hsl[i, ..., ch][stable]
                            ref_mean = ref_vals.mean()
                            ref_std = ref_vals.std()
                            tgt_mean = tgt_vals.mean()
                            tgt_std = tgt_vals.std()
                            adjusted = (tgt_hsl[i, ..., ch] - tgt_mean) / (tgt_std + 1e-8) * ref_std + ref_mean
                            matched_hsl[i, ..., ch] = luma_strength * adjusted + (1 - luma_strength) * tgt_hsl[i, ..., ch]
                else:  # 色相或饱和度 / hue or saturation
                    matched_hsl[..., ch] = ref_hsl[..., ch]
        else:  # "色彩精确" / "color exact"
            # 只对色相(1)和饱和度(2)进行像素级精确替换 / pixel-perfect replacement only for hue(1) and saturation(2)
            for ch in [1, 2]:
                if ch in channels_to_match:
                    matched_hsl[..., ch] = ref_hsl[..., ch]
            # 亮度(0)保持原样 / luminance(0) unchanged

        # 从匹配后的 HSL 分离出 L、H、S / Extract L, H, S from matched HSL
        matched_luma = matched_hsl[..., 0]
        matched_H = matched_hsl[..., 1]
        matched_S = matched_hsl[..., 2]

        # 将极坐标转换回 a,b / Convert polar back to a,b
        matched_a, matched_b = self._polar_to_cartesian(matched_H, matched_S)

        # 根据 luma_space 重建最终图像 / Reconstruct final image based on luma_space
        if luma_space in ["LAB L通道", "LAB L channel"]:
            matched_lab = np.stack([matched_luma, matched_a, matched_b], axis=-1)
            matched_rgb = self._lab_to_rgb(matched_lab)
        else:  # 线性RGB亮度 / linear RGB luminance
            tgt_lin = self._srgb_to_linear(tgt_np)
            eps = 1e-8
            scale = matched_luma / (tgt_luma + eps)
            scale = scale[..., np.newaxis]
            matched_lin = tgt_lin * scale
            matched_rgb = self._linear_to_srgb(matched_lin)

        # 合成最终结果：背景区域完全使用 matched_rgb，编辑区域根据 protect_strength 混合 matched_rgb 和原图
        # Composite final result: background uses matched_rgb fully, edit area blends matched_rgb and original based on protect_strength
        if mask is None:
            final_rgb = matched_rgb
        else:
            mask_exp = mask[..., np.newaxis]
            edit_blend = protect_strength * tgt_np + (1 - protect_strength) * matched_rgb
            final_rgb = (1 - mask_exp) * matched_rgb + mask_exp * edit_blend

        # 强度混合（整图混合） / Strength blend (global)
        blended_rgb = strength * final_rgb + (1 - strength) * tgt_np
        blended_rgb = np.clip(blended_rgb, 0.0, 1.0)

        out_tensor = torch.from_numpy(blended_rgb).to(reference.device)
        return (out_tensor,)

    # ---------- 辅助函数 / Helper functions ----------
    def _prepare_image(self, img):
        """将输入图像统一为 (B,H,W,C) float32 0-1 格式 / Normalize input image to (B,H,W,C) float32 0-1"""
        if isinstance(img, torch.Tensor):
            img = img.cpu().numpy()
        img = img.astype(np.float32)

        if img.ndim == 4 and img.shape[1] in (1, 3, 4) and img.shape[3] not in (1, 3, 4):
            img = np.transpose(img, (0, 2, 3, 1))
        elif img.ndim == 3:
            img = img[np.newaxis, ...]

        if img.max() > 1.0:
            img = img / 255.0
        return img

    def _get_mask(self, ref, tgt, auto_mask, threshold, external_mask):
        """获取蒙版：白色=编辑区域，黑色=稳定区域 / Get mask: white=edit area, black=stable area"""
        if external_mask is not None:
            mask = self._prepare_mask(external_mask, tgt.shape[1:3])
            return mask
        elif auto_mask:
            diff = np.mean(np.abs(ref - tgt), axis=-1)
            mask = (diff > threshold).astype(np.float32)
            return mask
        else:
            return None

    def _prepare_mask(self, mask, target_size):
        """将蒙版转为 (B,H,W) float32 0-1 并调整尺寸 / Convert mask to (B,H,W) float32 0-1 and resize"""
        if isinstance(mask, torch.Tensor):
            mask = mask.cpu().numpy()
        mask = mask.astype(np.float32)

        if mask.ndim == 4:
            if mask.shape[1] == 1:
                mask = mask[:, 0, :, :]
            elif mask.shape[-1] == 1:
                mask = mask[..., 0]
        elif mask.ndim == 2:
            mask = mask[np.newaxis, ...]

        if mask.max() > 1.0:
            mask = mask / 255.0

        if mask.shape[1:3] != target_size:
            mask_tensor = torch.from_numpy(mask).unsqueeze(1)
            mask_tensor = torch.nn.functional.interpolate(mask_tensor, size=target_size, mode='bilinear', align_corners=False)
            mask = mask_tensor.squeeze(1).numpy()
        return mask

    def _feather_mask(self, mask, radius):
        """对蒙版进行高斯模糊羽化 / Gaussian blur feathering on mask"""
        if radius <= 0 or mask is None:
            return mask
        B, H, W = mask.shape
        feathered = np.zeros_like(mask)
        for i in range(B):
            feathered[i] = gaussian_filter(mask[i], sigma=radius, mode='reflect')
        return feathered

    def _cartesian_to_polar(self, a, b):
        """笛卡尔坐标 (a,b) 转极坐标 (角度, 模长) / Cartesian to polar (angle, magnitude)"""
        H = np.arctan2(b, a)
        S = np.sqrt(a**2 + b**2)
        return H, S

    def _polar_to_cartesian(self, H, S):
        """极坐标 (角度, 模长) 转笛卡尔坐标 (a,b) / Polar to Cartesian (a,b)"""
        a = S * np.cos(H)
        b = S * np.sin(H)
        return a, b

    def _match_channels_hsl(self, ref_hsl, tgt_hsl, mask, channels, luma_strength=1.0):
        """
        对指定通道进行统计匹配（带蒙版） / Statistical matching on specified channels (with mask)
        channels: list of channel indices to match (0=L, 1=H, 2=S)
        """
        result = tgt_hsl.copy()
        B, H, W, C = ref_hsl.shape

        if mask is None:
            for ch in channels:
                ref_mean = ref_hsl[..., ch].mean(axis=(1,2), keepdims=True)
                ref_std = ref_hsl[..., ch].std(axis=(1,2), keepdims=True)
                tgt_mean = tgt_hsl[..., ch].mean(axis=(1,2), keepdims=True)
                tgt_std = tgt_hsl[..., ch].std(axis=(1,2), keepdims=True)
                adjusted = (tgt_hsl[..., ch] - tgt_mean.squeeze()) / (tgt_std.squeeze() + 1e-8) * ref_std.squeeze() + ref_mean.squeeze()
                if ch == 0:
                    result[..., ch] = luma_strength * adjusted + (1 - luma_strength) * tgt_hsl[..., ch]
                else:
                    result[..., ch] = adjusted
        else:
            for i in range(B):
                stable = mask[i] < 0.5
                if np.sum(stable) == 0:
                    stable = np.ones_like(mask[i], dtype=bool)
                for ch in channels:
                    ref_vals = ref_hsl[i, ..., ch][stable]
                    tgt_vals = tgt_hsl[i, ..., ch][stable]
                    ref_mean = ref_vals.mean()
                    ref_std = ref_vals.std()
                    tgt_mean = tgt_vals.mean()
                    tgt_std = tgt_vals.std()
                    adjusted = (tgt_hsl[i, ..., ch] - tgt_mean) / (tgt_std + 1e-8) * ref_std + ref_mean
                    if ch == 0:
                        result[i, ..., ch] = luma_strength * adjusted + (1 - luma_strength) * tgt_hsl[i, ..., ch]
                    else:
                        result[i, ..., ch] = adjusted
        return result

    # ---------- sRGB 与线性 RGB 转换 / sRGB to/from linear RGB ----------
    def _srgb_to_linear(self, rgb):
        """sRGB 非线性转线性 RGB (OETF逆变换) / sRGB to linear RGB (inverse OETF)"""
        rgb = np.clip(rgb, 0.0, 1.0)
        linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
        return linear.astype(np.float32)

    def _linear_to_srgb(self, linear):
        """线性 RGB 转 sRGB 非线性 (EOTF变换) / Linear RGB to sRGB (EOTF)"""
        linear = np.clip(linear, 0.0, 1.0)
        srgb = np.where(linear <= 0.0031308, linear * 12.92, 1.055 * (linear ** (1/2.4)) - 0.055)
        return srgb.astype(np.float32)

    # ---------- LAB 转换 / LAB conversion ----------
    def _rgb_to_lab(self, rgb):
        """RGB 转 LAB (近似公式，基于D65) / RGB to LAB (approximate, D65)"""
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        # 转 XYZ / to XYZ
        x = 0.412453 * r + 0.357580 * g + 0.180423 * b
        y = 0.212671 * r + 0.715160 * g + 0.072169 * b
        z = 0.019334 * r + 0.119193 * g + 0.950227 * b
        # 归一化 D65 / normalize D65
        x /= 0.950456
        z /= 1.088754
        # 非线性变换 / nonlinear transform
        eps = 0.008856
        k = 903.3
        def f(t):
            return np.where(t > eps, t ** (1/3), (k * t + 16) / 116)
        fx = f(x)
        fy = f(y)
        fz = f(z)
        L = 116 * fy - 16
        a = 500 * (fx - fy)
        b_lab = 200 * (fy - fz)
        return np.stack([L, a, b_lab], axis=-1)

    def _lab_to_rgb(self, lab):
        """LAB 转 RGB / LAB to RGB"""
        L, a, b_lab = lab[..., 0], lab[..., 1], lab[..., 2]
        fy = (L + 16) / 116
        fx = a / 500 + fy
        fz = fy - b_lab / 200
        eps = 0.008856
        k = 903.3
        def finv(t):
            return np.where(t > eps, t ** 3, (116 * t - 16) / k)
        x = finv(fx) * 0.950456
        y = finv(fy)
        z = finv(fz) * 1.088754
        # XYZ 转 RGB / XYZ to RGB
        r =  3.240479 * x - 1.537150 * y - 0.498535 * z
        g = -0.969256 * x + 1.875992 * y + 0.041556 * z
        b =  0.055648 * x - 0.204043 * y + 1.057311 * z
        return np.stack([r, g, b], axis=-1)


NODE_CLASS_MAPPINGS = {
    "Color Consistency HSL Advanced": ColorConsistencyHSLAdvanced,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Color Consistency HSL Advanced": "色彩亮度一致性混合 (HSL高级版)",
}
