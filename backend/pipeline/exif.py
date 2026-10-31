"""Decode upright photos and optional GPS coordinates."""
from typing import BinaryIO
import cv2
import numpy as np
from PIL import Image, ImageOps
from .config import MAX_SIDE
from .types import LatLon


def read_gps(image_path: str) -> LatLon | None:
    """Decode EXIF DMS coordinates; invalid metadata is absent GPS."""
    try:
        with Image.open(image_path) as image:
            gps = image.getexif().get_ifd(34853)
        def decimal(values, ref):
            degrees, minutes, seconds = map(float, values)
            value = degrees + minutes/60 + seconds/3600
            if isinstance(ref, bytes):
                ref = ref.decode()
            if ref not in ('N', 'S', 'E', 'W'):
                raise ValueError('Invalid hemisphere')
            return -value if ref in ('S', 'W') else value
        lat, lon = decimal(gps[2], gps[1]), decimal(gps[4], gps[3])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        return LatLon(lat, lon)
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, ZeroDivisionError):
        return None


class UnreadableImage(ValueError):
    """The supplied file cannot be decoded as an image."""


def read_bgr(source: str | BinaryIO) -> np.ndarray:
    """Decode upright image pixels and shrink phone photos before allocating BGR."""
    try:
        with Image.open(source) as image:
            upright = ImageOps.exif_transpose(image)
            upright.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
            rgb = np.asarray(upright.convert('RGB'))
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as error:
        raise UnreadableImage('Unreadable image. Upload a valid JPEG or PNG photo.') from error
