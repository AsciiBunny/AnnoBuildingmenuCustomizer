import tkinter as tk

import ttkbootstrap as ttk

from data import values
from data.construction_menu import ConstructionCategory, MenuState
from gui.construction_category_panel import ConstructionCategoryPanel


class WorkspaceWindow(tk.Toplevel):
    def __init__(self, root, menu_state: MenuState):
        super().__init__(root, height=200, width=354, name="!workspace_window")
        self.menu_state = menu_state

        self.minsize(width=354, height=0)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: root.on_close(self))
        self.title(values.SUB_WINDOW_NAME + "Workspace")
        self.attributes('-topmost', 'true')

        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.grid(sticky="nesw")

        self.workspace_category = ConstructionCategory(-1, "workspace", "Workspace", "no_img")
        self.workspace_category.parentNode = True
        self.workspace_panel = ConstructionCategoryPanel(self.notebook, self.workspace_category)
        self.notebook.add(self.workspace_panel, text="Workspace", sticky="ns")

        self.hidden_category = ConstructionCategory(-1, "hidden_items", "Hidden Items", "no_img")
        self.hidden_panel = ConstructionCategoryPanel(self.notebook, self.hidden_category, True)
        self.notebook.add(self.hidden_panel, text="Hidden Items", sticky="ns")

        self.bind_all("<<ItemHidden>>", self.on_item_hidden, "+")

    def on_item_hidden(self, event):
        item = self.menu_state.get(event.x)
        if item not in self.hidden_category.contents:
            self.hidden_panel.insert_item(item)

    def reset(self, hidden_items: list[int]):
        self.workspace_category.contents.clear()
        self.workspace_panel.build()
        self.hidden_category.set_contents(hidden_items, self.menu_state)
        self.hidden_panel.build()
