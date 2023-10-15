import tkinter as tk
from time import sleep
from tkinter import messagebox

import ttkbootstrap as ttk

from data import values
from data.construction_menu import MenuState, Session, TabType
from gui.construction_category_panel import ConstructionCategoryPanel
from gui.file_buttons_panel import FileButtonsPanel


class MainWindow(tk.Tk):
    def __init__(self, menu_state: MenuState):
        super().__init__()
        self.menu_state = menu_state

        self.title(values.MAIN_WINDOW_NAME)
        self.resizable(False, False)

        self.bind("<Configure>", self.on_configure)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.notebooks: dict[str, ttk.Notebook] = {}
        self.current_notebook: ttk.Notebook = None
        self.session_selection = tk.StringVar(value=Session.OLD_WORLD.value + ":" + TabType.FUNCTIONAL_BY_TIER.value)

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.grid(sticky="ns", column=0, row=0, rowspan=10, padx=(0, 4))

        for session in menu_state.menu:
            self.tree.insert("", tk.END, session.value, text=session.get_name())

            self.notebooks[session.value] = {}

            for type in TabType:
                self.tree.insert(session.value, tk.END, session.value + ":" + type.value, text=type.get_name())

                n = ttk.Notebook(self, bootstyle="primary")
                self.notebooks[session.value][type.value] = n
                for menu in menu_state.menu[session].get_list(type):
                    frame = ConstructionCategoryPanel(n, menu)
                    assert menu == menu_state.construction_categories[menu.guid]
                    n.add(frame, text=menu.text, sticky="ns")

        self.tree.selection_set(self.session_selection.get())
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)

        self.buttons = FileButtonsPanel(self, menu_state, self.on_load_state)
        self.buttons.grid(row=0, column=1, sticky="ew")

    def select_session(self):
        selected = self.session_selection.get()
        if ":" not in selected:
            return

        if self.current_notebook:
            self.current_notebook.grid_forget()

        self.current_notebook = self.notebooks[selected.split(":")[0]][selected.split(":")[1]]
        self.current_notebook.grid(row=1, column=1)

    def item_selected(self, event: tk.Event):
        self.session_selection.set(self.tree.selection()[0])
        self.select_session()

    def on_close(self, parent=None):
        self.tk.eval('wm stackorder ' + str(self))
        if messagebox.askyesno(
                message='Are you sure you want to close the program?',
                icon='question',
                title='Close',
                parent=self if not parent else parent):
            self.destroy()

    def on_configure(self, e):
        if e.widget == self:
            sleep(0.005)

    def on_load_state(self, hidden_items: list[int]):
        for session in self.menu_state.menu:
            for tab_type in TabType:
                notebook = self.notebooks[session.value][tab_type.value]
                for index, menu in enumerate(self.menu_state.menu[session].get_list(tab_type)):
                    tab = notebook.nametowidget(notebook.tabs()[index])
                    if type(tab) == ConstructionCategoryPanel:
                        tab.build()

        self.nametowidget("!workspace_window").reset(hidden_items)
