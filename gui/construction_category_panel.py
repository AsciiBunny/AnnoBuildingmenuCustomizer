from tkinter import HORIZONTAL, Widget

import ttkbootstrap as ttk

from data.construction_menu import ConstructionCategory
from gui.construction_item import ConstructionItem

ROW_WIDTH = 12


class ConstructionCategoryPanel(ttk.Frame):
    current_held: "ConstructionItem" = None

    def __init__(self, master, construction_category: ConstructionCategory, hide_buttons=False):
        super().__init__(master)
        self.construction_category = construction_category
        self["padding"] = 2

        self.items = []
        self.separators = []

        self.buttons = CategoryButtonsPanel(self, self.duplicate_item,
                                            self.hide_item) if not hide_buttons else ttk.Frame(self)

        self.bind_all(f"<<{self.construction_category.guid}-updated>>", self.on_category_change, "+")

        self.build()

    def build(self):
        for item in self.items:
            item.destroy()
        self.items.clear()
        for i, building in enumerate(self.construction_category.contents):
            label = ConstructionItem(self, building)
            label.grid(column=i % ROW_WIDTH, row=i // ROW_WIDTH * 2, sticky="nesw")
            self.items.append(label)

        self.check_empty()
        self.update_separators()
        self.update_buttons()

    def on_category_change(self, event):
        if event.widget != self and self.winfo_exists():
            self.build()

    @classmethod
    def set_current(cls, item: "ConstructionItem"):
        if cls.current_held and cls.current_held.winfo_exists():
            cls.current_held.deselect()

        cls.current_held = item
        cls.current_held.select()

    def shift_selection(self, item: "ConstructionItem"):
        widget = ConstructionCategoryPanel.current_held

        if not widget or widget.is_empty_marker:
            return

        x, y = widget.winfo_pointerxy()
        target = widget.winfo_containing(x, y)

        if not target:
            return

        target_item: ConstructionItem = find_containing_parent_type(target, ConstructionItem)
        if not target_item:
            return

        if widget not in self.items and target_item in self.items:
            target_panel = find_containing_parent_type(widget, ConstructionCategoryPanel)
            target_panel.shift_selection(widget)
            return

        widget_index = self.items.index(widget)

        if target_item not in self.items:
            target_panel = find_containing_parent_type(target, ConstructionCategoryPanel)
            if type(widget.item) == ConstructionCategory and not target_panel.construction_category.parentNode:
                return
            building = self.construction_category.contents[widget_index]
            self.remove_item(widget)
            ConstructionCategoryPanel.current_held = None
            target_panel.insert_item(building)
            return

        target_index = self.items.index(target_item)
        if target_index == widget_index:
            return

        self.items.remove(widget)
        self.items.insert(target_index, widget)
        widget_building = self.construction_category.contents.pop(widget_index)
        self.construction_category.contents.insert(target_index, widget_building)

        assert all(self.construction_category.contents[i] == item.item for i, item in enumerate(self.items))

        self.rebuild_grid()
        self.event_generate(f"<<{self.construction_category.guid}-updated>>")

    def remove_item(self, item: "ConstructionItem"):
        item_index = self.items.index(item)
        self.items.pop(item_index)
        self.construction_category.contents.pop(item_index)
        item.destroy()
        self.rebuild_grid()
        self.event_generate(f"<<{self.construction_category.guid}-updated>>")

    def insert_item(self, building):
        self.items.append(ConstructionItem(self, building))
        self.construction_category.contents.append(building)

        ConstructionCategoryPanel.current_held = self.items[-1]
        ConstructionCategoryPanel.current_held.select()

        self.rebuild_grid()
        self.event_generate(f"<<{self.construction_category.guid}-updated>>")

    def hide_item(self):
        if ConstructionCategoryPanel.current_held not in self.items \
                or ConstructionCategoryPanel.current_held and ConstructionCategoryPanel.current_held.is_empty_marker:
            return
        self.remove_item(ConstructionCategoryPanel.current_held)
        self.event_generate(f"<<{self.construction_category.guid}-updated>>")
        self.winfo_toplevel().event_generate("<<ItemHidden>>", x=ConstructionCategoryPanel.current_held.item.guid)

    def duplicate_item(self):
        if ConstructionCategoryPanel.current_held not in self.items \
                or ConstructionCategoryPanel.current_held and ConstructionCategoryPanel.current_held.is_empty_marker:
            return

        item_index = self.items.index(ConstructionCategoryPanel.current_held)
        building = ConstructionCategoryPanel.current_held.item
        self.items.insert(item_index + 1, ConstructionItem(self, building))
        self.construction_category.contents.insert(item_index + 1, building)
        self.rebuild_grid()
        self.event_generate(f"<<{self.construction_category.guid}-updated>>")

    def rebuild_grid(self):
        for i, label in enumerate(self.items):
            label.grid(column=i % ROW_WIDTH, row=i // ROW_WIDTH * 2, sticky="nesw")
        self.check_empty()

        self.update_separators()
        self.update_buttons()

    def update_separators(self):
        for s in self.separators:
            s.destroy()
        for i in range(((len(self.items) - 1) // ROW_WIDTH) + 1):
            s = ttk.Separator(self, orient=HORIZONTAL)
            s.grid(column=0, row=i * 2 + 1, columnspan=ROW_WIDTH, sticky="ew", pady=5)
            self.separators.append(s)

    def update_buttons(self):
        last_row = ((len(self.items) - 1) // ROW_WIDTH + 1) * 2
        self.buttons.grid(column=0, row=last_row, columnspan=ROW_WIDTH)

    def check_empty(self):
        if len(self.construction_category.contents) == 0:
            self.items.append(ConstructionItem(self))
            self.items[0].grid(column=0, row=0)
        elif len(self.construction_category.contents) >= 1 and any(item.is_empty_marker for item in self.items):
            empty = [item for item in self.items if item.is_empty_marker]
            self.items = [item for item in self.items if not item.is_empty_marker]
            for item in empty:
                item.destroy()
            self.rebuild_grid()


class CategoryButtonsPanel(ttk.Frame):
    def __init__(self, master, on_duplicate_item, on_hide_item):
        super().__init__(master)
        self["padding"] = 2

        self.duplicate_button = ttk.Button(self, text="Duplicate", command=on_duplicate_item)
        self.duplicate_button.grid(column=0, row=0, padx=4)
        self.hide_button = ttk.Button(self, text="Hide", command=on_hide_item)
        self.hide_button.grid(column=1, row=0, padx=4)
        self.new_button = ttk.Button(self, text="New Item", state="disabled")
        self.new_button.grid(column=2, row=0, padx=4)


def find_containing_parent_type(widget: Widget, containing_type):
    if type(widget) == containing_type:
        return widget
    if widget == widget.winfo_toplevel():
        return False
    else:
        return find_containing_parent_type(widget.nametowidget(widget.winfo_parent()), containing_type)
