import logging
import sys
from pathlib import Path

from data import config
from data.construction_menu import read_extracted_assets, store_base_state, read_mod_assets, mark_parent_categories
from data.mod import load_mods
from data.util import timer
from gui.main_window import MainWindow
from gui.workspace_window import WorkspaceWindow

if __name__ == "__main__":

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    printHandler = logging.StreamHandler(sys.stdout)
    printHandler.setFormatter(logFormatter)
    rootLogger.addHandler(printHandler)

    fileHandler = logging.FileHandler(Path("abc.log"), 'w+')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    if config.exists():
        config.read()
    else:
        config.create_new()

    with timer() as t:
        logging.info("Loading base-game...")
        menu_state = read_extracted_assets()
        if "no_mods" not in sys.argv:
            logging.info("Loading mods...")
            mods, load_order = load_mods()
            read_mod_assets(menu_state, mods, load_order)
        mark_parent_categories(menu_state)
        store_base_state(menu_state)

    logging.info("Loaded assets in: {:.2f}s".format(t()))

    logging.info("Loading a lot of icons...")

    with timer() as t:
        window = MainWindow(menu_state)
        window.after(100, lambda: WorkspaceWindow(window, menu_state))

    logging.info("Constructed GUI in: {:.2f}s".format(t()))

    window.mainloop()
