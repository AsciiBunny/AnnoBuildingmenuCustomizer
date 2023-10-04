import tkinter as tk

from data.construction_menu import ConstructionCategory
import gui.construction_category_panel


class CategoryWindow(tk.Toplevel):
    def __init__(self, root, category: ConstructionCategory):
        super().__init__(root, height=200, width=500)
        self.minsize(width=354, height=0)
        self.resizable(False, False)
        self.name = category.text if category.text else category.name
        self.title("ABC - " + self.name)

        self.attributes('-topmost', 'true')
        # self.lift(root)

        self.category = category
        panel = gui.construction_category_panel.ConstructionCategoryPanel(self, self.category)
        panel.grid(sticky="nesw")
