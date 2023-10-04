import os
from pathlib import Path

from PIL import Image

raw_icons = Path("raw/3dicons")

f = []
for (dirpath, dirnames, filenames) in os.walk(raw_icons):
    for file in filenames:
        f.append(Path(dirpath, file))

for img_path in f:
    assert img_path.parts[-1][-5] in ["0", "1", "2", "3", "4"], img_path.parts[-1] and img_path.parts[-1][-5] == "_"
    if img_path.parts[-1][-5] == "0":
        dst_path = ["resources", "icons"] + list(img_path.parts[2:])
        dst_path[-1] = dst_path[-1][:-6] + ".png"  # dst_path[-1][-4:]
        dst_path = Path(*dst_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        # copy(img_path, dst_path)
        img = Image.open(img_path)
        img.thumbnail((96, 96))
        img.save(dst_path)


dep_icons = [
    "resources/template_mod/[Addon] A_Modified_Ornaments_Tab/data/ui/2kimages/main/3dicons/harbor_menu_tab_0.dds",
    "resources/template_mod/[Addon] A_Modified_Ornaments_Tab/data/ui/2kimages/main/3dicons/modding_menu_tab_0.dds"
]
for img_path in dep_icons:
    img_path = Path(img_path)
    assert img_path.parts[-1][-5] in ["0", "1", "2", "3", "4"], img_path.parts[-1] and img_path.parts[-1][-5] == "_"
    if img_path.parts[-1][-5] == "0":
        dst_path = ["resources", "icons"] + list(img_path.parts[8:])
        dst_path[-1] = dst_path[-1][:-6] + ".png"  # dst_path[-1][-4:]
        dst_path = Path(*dst_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        # copy(img_path, dst_path)
        img = Image.open(img_path)
        img.thumbnail((96, 96))
        img.save(dst_path)
