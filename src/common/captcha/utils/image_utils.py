"""图片处理工具"""

import base64
import io
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from PIL import Image


def validate_image(image: Union[str, Path, bytes]) -> bytes:
    """
    验证并转换图片为字节数据

    Args:
        image: 图片路径、字节数据或文件对象

    Returns:
        bytes: 图片字节数据

    Raises:
        ValueError: 图片格式不支持或文件不存在
    """
    if isinstance(image, bytes):
        return image
    elif isinstance(image, (str, Path)):
        path = Path(image)
        if not path.exists():
            raise ValueError(f"图片文件不存在: {path}")
        return path.read_bytes()
    else:
        raise ValueError(f"不支持的图片类型: {type(image)}")


def resize_image(
    image_data: bytes, max_width: int = 800, max_height: int = 600, quality: int = 85
) -> bytes:
    """
    调整图片大小

    Args:
        image_data: 图片字节数据
        max_width: 最大宽度
        max_height: 最大高度
        quality: 压缩质量 (1-100)

    Returns:
        bytes: 调整后的图片字节数据
    """
    try:
        # 打开图片
        image = Image.open(io.BytesIO(image_data))

        # 计算新尺寸
        width, height = image.size
        if width <= max_width and height <= max_height:
            return image_data

        # 计算缩放比例
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        # 调整大小
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 保存为字节数据
        output = io.BytesIO()
        resized_image.save(output, format="JPEG", quality=quality, optimize=True)
        return output.getvalue()

    except Exception as e:
        raise ValueError(f"图片调整失败: {e}") from e


def convert_format(
    image_data: bytes, target_format: str = "JPEG", quality: int = 85
) -> bytes:
    """
    转换图片格式

    Args:
        image_data: 图片字节数据
        target_format: 目标格式 (JPEG, PNG, WEBP)
        quality: 压缩质量 (1-100)

    Returns:
        bytes: 转换后的图片字节数据
    """
    try:
        # 打开图片
        image = Image.open(io.BytesIO(image_data))

        # 如果是 RGBA 模式且目标格式是 JPEG, 转换为 RGB
        if image.mode == "RGBA" and target_format.upper() == "JPEG":
            # 创建白色背景
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])  # 使用 alpha 通道作为 mask
            image = background

        # 保存为指定格式
        output = io.BytesIO()
        image.save(output, format=target_format, quality=quality, optimize=True)
        return output.getvalue()

    except Exception as e:
        raise ValueError(f"图片格式转换失败: {e}") from e


def get_image_info(image_data: bytes) -> Dict[str, Union[int, str]]:
    """
    获取图片信息

    Args:
        image_data: 图片字节数据

    Returns:
        Dict[str, Union[int, str]]: 图片信息字典
    """
    try:
        image = Image.open(io.BytesIO(image_data))

        return {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
            "size_bytes": len(image_data),
        }

    except Exception as e:
        raise ValueError(f"获取图片信息失败: {e}") from e


def encode_base64(image_data: bytes) -> str:
    """
    将图片编码为 base64 字符串

    Args:
        image_data: 图片字节数据

    Returns:
        str: base64 编码的字符串
    """
    return base64.b64encode(image_data).decode("utf-8")


def decode_base64(base64_string: str) -> bytes:
    """
    将 base64 字符串解码为图片字节数据

    Args:
        base64_string: base64 编码的字符串

    Returns:
        bytes: 图片字节数据
    """
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ValueError(f"base64 解码失败: {e}") from e


def is_valid_image_format(image_data: bytes) -> bool:
    """
    检查是否为有效的图片格式

    Args:
        image_data: 图片字节数据

    Returns:
        bool: 是否为有效图片格式
    """
    try:
        Image.open(io.BytesIO(image_data))
        return True
    except Exception:
        return False


def get_image_format(image_data: bytes) -> Optional[str]:
    """
    获取图片格式

    Args:
        image_data: 图片字节数据

    Returns:
        Optional[str]: 图片格式, 无法识别返回 None
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        return image.format
    except Exception:
        return None


def optimize_for_captcha(
    image_data: bytes,
    target_size: Tuple[int, int] = (200, 80),
    enhance_contrast: bool = True,
) -> bytes:
    """
    为验证码识别优化图片

    Args:
        image_data: 图片字节数据
        target_size: 目标尺寸 (width, height)
        enhance_contrast: 是否增强对比度

    Returns:
        bytes: 优化后的图片字节数据
    """
    try:
        image = Image.open(io.BytesIO(image_data))

        # 转换为灰度图
        if image.mode != "L":
            image = image.convert("L")

        # 调整大小
        image = image.resize(target_size, Image.Resampling.LANCZOS)

        # 增强对比度
        if enhance_contrast:
            from PIL import ImageEnhance

            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # 增强对比度

        # 保存为字节数据
        output = io.BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()

    except Exception as e:
        raise ValueError(f"图片优化失败: {e}") from e
