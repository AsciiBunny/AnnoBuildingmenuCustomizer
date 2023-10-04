from tkinter import filedialog, messagebox

import ttkbootstrap as ttk

from data import config
from data.construction_menu import MenuState
from data.saved_state import save_state, load_state
from generate_mod import generate_mod


class FileButtonsPanel(ttk.Frame):
    def __init__(self, master, menu_state: MenuState, on_load_state):
        super().__init__(master)
        self.menu_state = menu_state
        self.on_load_state = on_load_state

        self["padding"] = 2

        self.load_button = ttk.Button(self, text="Load State", default="active",
                                      command=self.on_load_button)
        self.load_button.grid(row=0, column=1, sticky="ew", padx=4)

        self.save_button = ttk.Button(self, text="Save State", default="active",
                                      command=self.on_save_button)
        self.save_button.grid(row=0, column=0, sticky="ew", padx=4)

        self.generate_button = ttk.Button(self, text="Generate Mod", default="active",
                                          command=self.on_generate_button)
        self.generate_button.grid(row=0, column=2, sticky="ew", padx=4)

    def on_load_button(self):
        filename = filedialog.askopenfilename(parent=self, filetypes=[["JSON", "json"]])
        if not filename:
            return
        print("Loading:", filename)
        success, hidden_items = load_state(filename, self.menu_state)
        if success:
            self.on_load_state(hidden_items)

    def on_save_button(self):
        filename = filedialog.asksaveasfilename(parent=self, initialfile="Building-menu state.json",
                                                filetypes=[["JSON", "json"]])
        if not filename:
            return
        print("Saving:", filename)
        save_state(filename, self.menu_state)

    def on_generate_button(self):
        if len(config.MOD_FOLDERS) > 0:
            should_update = messagebox.askyesnocancel("ABC: Generating Mod",
                                                      "Do you want to automatically install in your (first) mod "
                                                      "folder?")
            if should_update:
                out_dir_path = config.MOD_FOLDERS[0]
            elif should_update is None:
                return
            else:
                out_dir_path = filedialog.askdirectory()

        generate_mod(self.menu_state.menu, out_dir_path)

        save_path = "./last_generated_state.json"
        print("Saving:", save_path)
        save_state(save_path, self.menu_state)

        messagebox.showinfo("ABC: Generating Mod",
                            "Your custom building-menu mod was generated successfully!\n\nThe current state was also saved to last_generated_state.json in the same folder as the exe so you can later continue customizing from this point.")
