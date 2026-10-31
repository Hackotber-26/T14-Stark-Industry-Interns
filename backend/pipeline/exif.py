"""Read optional GPS coordinates from image metadata."""
from PIL import Image
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
