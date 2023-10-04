import json
from pathlib import Path

import chardet

from data import config


def open_auto_encoding(path: Path, mode):
    detected = chardet.detect(open(path, "rb").read())
    return open(path, mode, encoding=detected["encoding"])


class Mod:
    is_modio_mod = False

    def __init__(self, path: Path, is_base_game=False):
        assert path.is_dir()
        self.path = path
        self.is_base_game = is_base_game
        if not is_base_game:
            self._read_mod_json()
            self.assets_path = self.path / "data" / "config" / "export" / "main" / "asset" / "assets.xml"
            self.nested = (self.path.parent / "modinfo.json").exists()
        else:
            self._base_game_json_values()

    def _read_mod_json(self):
        json_path = self.path / "modinfo.json"
        if not json_path.exists():
            self._default_json_values()
            return

        with open_auto_encoding(json_path, 'rt') as modinfo_f:
            try:
                self.modinfo = json.load(modinfo_f)
                self.name = self.modinfo["ModID"]
                self.full_name = f'[{self.modinfo["Category"]["English"]}] {self.modinfo["ModName"]["English"]}'
                self.version = self.modinfo["Version"]
                self.load_after = self.modinfo["LoadAfterIds"] if "LoadAfterIds" in self.modinfo else []
            except:
                self._default_json_values()

    def _default_json_values(self):
        self.valid_modinfo = False
        self.name = self.path.parts[-1]
        self.full_name = self.name
        self.version = "unknown"
        self.load_after = []

    def _base_game_json_values(self):
        self.valid_modinfo = False
        self.name = "Anno 1800"
        self.full_name = self.name
        self.version = "unknown"
        self.load_after = []

    def __str__(self):
        return f"<{self.name} : {self.version}>"

    def is_newer_than(self, other: "Mod"):
        assert self.name == other.name
        if self.version == other.version:
            return False
        if self.version == "unknown":
            return False
        if other.version == "unknown":
            return True
        sv = [int(number) for number in self.version.split(".")]
        ov = [int(number) for number in other.version.split(".")]
        return sv >= ov


def load_mods_in_path(path: Path, folder_glob: str, mods: dict[str, Mod]):
    mod_folders = [folder.parent for folder in list(path.glob("**/modinfo.json"))]
    mod_folders = list(set(mod_folders) | set([folder for folder in path.glob(folder_glob) if folder.is_dir()]))
    mod_names = set()
    for folder in mod_folders:
        if folder.name[0] == "-":
            continue
        mod = Mod(folder)
        if mod.name not in mods or mod.name in mods and mod.is_newer_than(mods[mod.name]):
            mods[mod.name] = mod
            mod_names.add(mod.name)
        else:
            print("keeping", mods[mod.name], "over", mod, mod.path)
    return mod_names


def sort_mods(mods: list[Mod]):
    return sorted(mods, key=lambda mod: (mod.full_name, not mod.is_modio_mod))


def sort_load_order(mods: dict[str, Mod]):
    loading_queue = [mod.name for mod in sort_mods(list(mods.values()))]

    priority_mods = []
    delayed_mods = []

    for mod_name in loading_queue.copy():
        mod = mods[mod_name]
        if len(mod.load_after) > 0:
            if mod_name in loading_queue:
                loading_queue.remove(mod_name)
            if "*" in mod.load_after:
                delayed_mods.append(mod_name)
            else:
                priority_mods.append(mod_name)

    loaded = set()
    load_order: list[str] = []
    for mod_name in priority_mods:
        append_mod(mod_name, loaded, load_order, mods)

    for mod_name in loading_queue:
        append_mod(mod_name, loaded, load_order, mods)

    for mod_name in delayed_mods:
        append_mod(mod_name, loaded, load_order, mods)

    return load_order


def append_mod(mod_name: str, loaded: set[str], load_order: list[str], mods: dict[str, Mod]):
    if mod_name in loaded or mod_name not in mods:
        return
    mod = mods[mod_name]
    loaded.add(mod_name)
    for load_after_name in mod.load_after:
        append_mod(load_after_name, loaded, load_order, mods)
    load_order.append(mod.name)


def load_mods():
    mods: dict[str, Mod] = {}

    modio_mods = load_mods_in_path(config.MOD_IO_FOLDER, "*/*/", mods)
    for mod in mods.values():
        mod.is_modio_mod = True
    print(len(modio_mods), "mod.io mods loaded")

    user_mods = []
    for location in config.MOD_FOLDERS:
        user_mods += load_mods_in_path(location, "*/", mods)
    print(len(user_mods), "user mods loaded")

    print(len(user_mods) + len(modio_mods), "total mods loaded")

    load_order = sort_load_order(mods)

    return mods, load_order
