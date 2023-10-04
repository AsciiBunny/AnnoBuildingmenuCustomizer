from tkinter import Widget

import ttkbootstrap as ttk
import ttkbootstrap.constants as styles
from PIL import ImageTk

from data.construction_menu import ConstructionCategory, Building
from data.images import ImageCache
from gui.category_window import CategoryWindow

ROW_WIDTH = 12


class ConstructionItem(ttk.LabelFrame):
    def __init__(self, parent, item: ConstructionCategory | Building = None):
        self.parent = parent
        self.item = item
        if item:
            self.name = item.text if item.text else item.name
            self.is_empty_marker = False
        else:
            self.name = "Empty Category"
            self.is_empty_marker = True
        super().__init__(parent, text=item.guid if item else "")

        self["padding"] = 2
        self["width"] = 15 * 6

        self.binds(self)

        img = ImageCache.get(item.icon_path if item else "no_img", type(item) == ConstructionCategory)

        icon_img = ImageTk.PhotoImage(img)
        self.icon = ttk.Label(self, image=icon_img)
        self.icon.image = icon_img
        self.icon["padding"] = 5
        self.icon["width"] = 96
        self.icon.grid(row=0)
        self.binds(self.icon)

        # text below image
        self.name_label = ttk.Label(self, text=self.name)
        self.name_label["wraplength"] = 15 * 6
        self.name_label.grid(row=1)
        self.binds(self.name_label)

    def binds(self, widget: Widget):
        widget.bind('<ButtonPress-1>', self.on_click)
        widget.bind('<B1-Motion>', self.on_move)
        widget.bind('<Double-Button-1>', self.on_double_click)

    def on_click(self, event):
        self.parent.set_current(self)

    def on_move(self, event):
        self.parent.shift_selection(self)

    def on_double_click(self, event):
        if type(self.item) == ConstructionCategory:
            CategoryWindow(self, self.item)

    def select(self):
        self.configure(bootstyle=styles.DARK)

    def deselect(self):
        self.configure(bootstyle=styles.DEFAULT)
