import json
import sys
from pathlib import Path
from tkinter import messagebox, filedialog

MOD_IO_FOLDER = ""
MOD_FOLDERS = []

_config_tried_to_load = False
_config_read_successfully = False


def exists():
    config_file_path = Path("config.json")
    return config_file_path.exists()


def create_new():
    empty_config = {
    }

    _load_config(config=empty_config)

    with open(Path("config.json"), 'w') as file:
        json.dump(empty_config, file, indent=2)


def _load_config(config):
    try:
        if not config["has_no_mod.io"]:
            assert type(config["mod.io_folder"]) == str

            global MOD_IO_FOLDER
            MOD_IO_FOLDER = config["mod.io_folder"]
            MOD_IO_FOLDER = Path(MOD_IO_FOLDER)
            assert MOD_IO_FOLDER.exists() and MOD_IO_FOLDER.is_dir()
    except Exception as e:
        mod_io_path = Path("C:/Users/Public/mod.io/4169/mods")
        if mod_io_path.exists():
            config["has_no_mod.io"] = False
            config["mod.io_folder"] = str(mod_io_path)
            MOD_IO_FOLDER = mod_io_path
        else:
            while messagebox.askyesno("Generating config", "Could not find your mod.io folder, do you have one?"):
                given_folder = filedialog.askdirectory(title="Mod.io folder location", mustexist=True)
                if Path(given_folder).exists() and Path(given_folder).name == "mods":
                    config["has_no_mod.io"] = False
                    config["mod.io_folder"] = given_folder
                    MOD_IO_FOLDER = Path(given_folder)
                    break
            if "mod.io_folder" not in config:
                config["has_no_mod.io"] = True

    try:
        assert type(config["mod_folders"]) == list
        assert all(type(line) == str for line in config["mod_folders"])

        global MOD_FOLDERS
        MOD_FOLDERS = config["mod_folders"]
        MOD_FOLDERS = [Path(folder) for folder in MOD_FOLDERS]
        assert len(MOD_FOLDERS) > 0
        assert all(Path(folder).exists() for folder in MOD_FOLDERS)
    except Exception as e:
        while messagebox.askyesno("Generating config", "Could not find your manual mods folder, do you have one?"):
            given_folder = filedialog.askdirectory(title="Manual mods folder location", mustexist=True)
            if Path(given_folder).exists() and Path(given_folder).name.casefold() == "mods".casefold():
                config["mod_folders"] = [given_folder]
                MOD_FOLDERS = config["mod_folders"]
                MOD_FOLDERS = [Path(folder) for folder in MOD_FOLDERS]
                break
        if "mod_folders" not in config or len(config["mod_folders"]) == 0:
            messagebox.showerror("You need a mod folder",
                                 "You need to have a manual mod folder, please create either [User]\Documents\Anno 1800\mods or or \mods in your Anno 1800 install folder and then restart this tool.")
            sys.exit()

    global _config_read_successfully
    _config_read_successfully = True


def read():
    global _config_read_successfully, _config_tried_to_load
    _config_tried_to_load = True

    config_file_path = Path("config.json")

    if not config_file_path.exists():
        return

    with open(config_file_path, 'rt') as file:
        data = json.load(file)
        _load_config(data)

