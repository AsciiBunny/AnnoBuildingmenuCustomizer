from pathlib import Path

from PIL import Image

from data.util import resource_path


class ImageCache:
    _images = {}

    @classmethod
    def get(cls, path: Path | str, is_category=False):
        if path not in cls._images:
            if not cls.load(path):
                path = "no_img"
        img = cls._images[path]

        if is_category:
            img = img.copy()
            img_overlay = cls.get("category_overlay")
            img.paste(img_overlay, (0, 0), img_overlay)

        return img

    @classmethod
    def load(cls, path: Path):
        if path in cls._images:
            return True
        if not path.is_file():
            return False
        try:
            img = Image.open(path)
            img.thumbnail((96, 96))
            cls._images[path] = img
            return True
        except Exception:
            return False


ImageCache.load(resource_path("category.dds"))
ImageCache._images["category_overlay"] = ImageCache.get(resource_path("category.dds"))
ImageCache.load(resource_path("no_img.dds"))
ImageCache._images["no_img"] = ImageCache.get(resource_path("no_img.dds"))
