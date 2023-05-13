#!/usr/bin/env python
import csv
import operator
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from functools import partial
from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class Combo:

    _character: str
    _notation: str
    _startup: str
    _drive: str
    _super: str
    _carry: str
    _damage: str
    _advantage: str
    _position: str

    @property
    def character(self) -> str:
        return str(self._character)

    @property
    def notation(self) -> str:
        return str(self._notation)

    @property
    def startup(self) -> int:
        return int(self._startup)

    @property
    def drive(self) -> float:
        return float(self._drive)

    @property
    def super(self) -> int:
        return int(self._super)

    @property
    def carry(self) -> int:
        return int(self._carry)

    @property
    def damage(self) -> int:
        return int(self._damage)

    @property
    def advantage(self) -> int:
        return int(self._advantage)

    @property
    def position(self) -> str:
        return str(self._position)

    def get(self, prop: str, display=False):
        if prop == 'carry' and display:
            return f'{self.carry}%'
        if prop == 'advantage' and display:
            return f'{"+" if self.advantage >= 0 else ""}{self.advantage}'
        return getattr(self, prop)


@dataclass
class ComboFilter:

    label: str
    compare: tk.StringVar
    value: tk.StringVar
    type: str
    column_size: int
    has_entry: bool = True
    options: tuple[str] = None

    def __post_init__(self):
        self.default_compare = self.compare.get()
        self.default_value = self.value.get()


class ComboFinder(tk.Tk):

    padding = 5
    combos_per_page = 10
    current_sort = ''
    is_reversed = False
    combos: list[Combo] = []
    display_combos: list[Combo] = []

    operators = (
        'Equals',
        'Greater Than',
        'Less Than'
    )
    positions = (
        'Any',
        'Fullscreen',
        'Midscreen',
        'Corner'
    )
    types = {
        'str': str,
        'int': int,
        'float': float
    }

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title('SF6 Combo Finder')
        self.iconbitmap('icon.ico')
        self.resizable(False, False)
        self.current_page = tk.IntVar(value=1)
        self.filters = (
            ComboFilter('Character', tk.StringVar(value='Contains'), tk.StringVar(), 'str', 100),
            ComboFilter('Notation', tk.StringVar(value='Contains'), tk.StringVar(), 'str', 200),
            ComboFilter('Startup', tk.StringVar(value=self.operators[0]), tk.StringVar(), 'int', 100, options=self.operators),
            ComboFilter('Drive', tk.StringVar(value=self.operators[0]), tk.StringVar(), 'float', 100, options=self.operators),
            ComboFilter('Super', tk.StringVar(value=self.operators[0]), tk.StringVar(), 'int', 100, options=self.operators),
            ComboFilter('Carry', tk.StringVar(value=self.operators[0]), tk.StringVar(), 'int', 100, options=self.operators),
            ComboFilter('Damage', tk.StringVar(value=self.operators[0]), tk.StringVar(), 'int', 100, options=self.operators),
            ComboFilter('Advantage', tk.StringVar(value=self.operators[0]), tk.StringVar(), 'int', 100, options=self.operators),
            ComboFilter('Position', tk.StringVar(value=self.operators[0]), tk.StringVar(value=self.positions[0]), 'str', 100,
                        options=self.positions, has_entry=False),
        )
        self.labels = [filter.label for filter in self.filters]

        # Top frame

        self.top_frame = tk.Frame(self, padx=self.padding, pady=self.padding)
        self.top_frame.grid(row=0, sticky='nesw')

        button_width = 15

        ttk.Button(self.top_frame, text='Import combos', width=button_width, command=self.import_combos)\
            .grid(row=0, column=0, padx=self.padding, pady=self.padding)
        ttk.Button(self.top_frame, text='Filters', width=button_width, command=self.open_filters)\
            .grid(row=0, column=1, padx=self.padding, pady=self.padding)

        # Combo frame

        self.create_combo_frame()

        # Bottom frame

        self.bottom_frame = tk.Frame(self, padx=self.padding, pady=self.padding)
        self.bottom_frame.grid(row=3, sticky='nsew')

        self.message_var = tk.StringVar()
        tk.Message(self.bottom_frame, textvariable=self.message_var, width=300)\
            .pack(side='left', pady=self.padding)
        
        self.page_up_btn = ttk.Button(self.bottom_frame, text='>', width=3, command=self.page_up)
        self.page_up_btn.pack(side='right', padx=self.padding)

        self.page_entry = ttk.Entry(self.bottom_frame, width=3, textvariable=self.current_page)
        self.page_entry.pack(side='right')
        self.page_entry.bind('<Return>', self.update_display)
        self.page_entry.config(state='disabled')

        self.page_down_btn = ttk.Button(self.bottom_frame, text='<', width=3, command=self.page_down)
        self.page_down_btn.pack(side='right', padx=self.padding)

        page_sizes = (5, 10, 20)
        page_box_values = [f'{size} per page' for size in page_sizes]

        self.per_page_var = tk.StringVar(value=page_box_values[1])
        self.per_page_box = ttk.Combobox(self.bottom_frame, width=12, textvariable=self.per_page_var, values=page_box_values, state='readonly')
        self.per_page_box.pack(side='right', padx=self.padding)
        self.per_page_box.bind('<<ComboboxSelected>>', self.update_combo_frame)
        ttk.Label(self.bottom_frame, text='Show:').pack(side='right', padx=self.padding)

        self.sort_by('character')

    def create_combo_frame(self):
        try:
            self.combo_frame.destroy()
        except AttributeError:
            pass

        self.combo_frame = tk.Frame(self, padx=10, pady=self.padding)
        for column, size in enumerate([prop.column_size for prop in self.filters]):
            self.combo_frame.grid_columnconfigure(column, minsize=size)
        self.combo_frame.grid(row=1, sticky='nsew')

        self.headers = [ttk.Button(self.combo_frame, text=filter.label, name=filter.label.lower(),
                        command=partial(self.sort_by, filter.label.lower()))
                        for filter in self.filters]
        for column, header in enumerate(self.headers):
            header.grid(row=0, column=column, sticky='nsew')
            header.config(state='disabled')

        self.combo_rows = [[
            ttk.Label(self.combo_frame, padding=self.padding) for _ in range(len(self.filters))]
            for _ in range(self.combos_per_page)]
        current_row = 1
        for row in self.combo_rows:
            for column, label in enumerate(row):
                label.grid(row=current_row, column=column, sticky='nsew')
            ttk.Separator(self.combo_frame, orient='horizontal')\
                .grid(row=current_row+1, columnspan=len(self.filters), sticky='nsew')
            current_row += 2

    def update_combo_frame(self, event: tk.Event):
        new_value = int(event.widget.get().split()[0])
        if self.combos_per_page == new_value:
            return
        self.combos_per_page = new_value
        self.create_combo_frame()
        self.update_display()

    def open_filters(self):
        try:
            self.filter_window.focus()
            return
        except:
            pass

        self.filter_window = tk.Toplevel(self)
        self.filter_window.title('Filters')
        self.filter_window.iconbitmap('icon.ico')
        self.filter_window.resizable(False, False)

        # Filters frame

        self.filters_frame = tk.Frame(self.filter_window, padx=self.padding, pady=self.padding)
        self.filters_frame.grid(row=0)

        full_width = 33
        part_width = 15

        for i, filter in enumerate(self.filters):
            ttk.Label(self.filters_frame, text=filter.label, anchor='center', padding=self.padding)\
                .grid(row=i, column=0, sticky='w')
            if filter.options:
                textvar = filter.compare if filter.has_entry else filter.value
                ttk.Combobox(self.filters_frame, width=part_width-3, textvariable=textvar, values=filter.options, state='readonly')\
                    .grid(row=i, column=1, sticky='w', padx=self.padding, pady=self.padding)
            if filter.has_entry:
                width = part_width if filter.options else full_width
                column = 2 if filter.options else 1
                columnspan = 1 if filter.options else 2
                sticky = 'e' if filter.options else 'w'
                ttk.Entry(self.filters_frame, width=width, textvariable=filter.value)\
                    .grid(row=i, column=column, sticky=sticky, padx=self.padding, pady=self.padding, columnspan=columnspan)

        # Buttons frame

        self.submit_frame = tk.Frame(self.filter_window, padx=self.padding, pady=self.padding)
        self.submit_frame.grid(row=1)

        ttk.Button(self.submit_frame, text='Submit', command=self.update_combos)\
            .grid(row=0, column=0, padx=self.padding, pady=self.padding, sticky='w')
        ttk.Button(self.submit_frame, text='Reset', command=self.reset_filters)\
            .grid(row=0, column=1, padx=self.padding, pady=self.padding, sticky='w')

    def import_combos(self):
        filename = filedialog.askopenfilename(initialdir=os.path.abspath('.'), filetypes=[('Comma separated', '.csv')])
        if not filename:
            return
        with open(filename, 'r') as combos_file:
            combos_list = list(csv.reader(combos_file, skipinitialspace=True))[1:]

        self.combos = list(set(Combo(*combo) for combo in combos_list))
        self.display_combos = self.combos
        self.update_display()
        self.message_var.set(f'Imported {len(self.combos)} total combos')

    def update_combos(self):
        matches = []
        for combo in self.combos:
            for filter in self.filters:
                if not filter.value.get():
                    continue
                if filter.label == 'Position' and filter.value.get() == 'Any':
                    continue
                if not self.get_truth(combo.get(filter.label.lower()), filter.compare.get(),
                        self.types[filter.type](filter.value.get())):
                    break
            else:
                matches.append(combo)

        self.display_combos = matches
        self.update_display()
        self.message_var.set(f'Found {len(self.display_combos)} out of {len(self.combos)} total combos')

    def update_display(self, event=None):
        self.display_combos.sort(key=lambda x: x.get(self.current_sort), reverse=self.is_reversed)
        total_pages = max(1, ceil(len(self.display_combos) / self.combos_per_page))

        self.current_page.set(min(self.current_page.get(), total_pages))
        self.current_page.set(max(self.current_page.get(), 1))

        header_state = 'normal' if self.display_combos else 'disabled'
        page_entry_state = 'normal' if total_pages > 1 else 'disabled'
        down_btn_state = 'normal' if self.current_page.get() > 1 else 'disabled'
        up_btn_state = 'normal' if self.current_page.get() < total_pages else 'disabled'

        for header in self.headers:
            header.config(state=header_state)
            default = 'active' if header.winfo_name() == self.current_sort else 'normal'
            header.config(default=default)
        self.page_entry.config(state=page_entry_state)
        self.page_down_btn.config(state=down_btn_state)
        self.page_up_btn.config(state=up_btn_state)

        start_index = (self.combos_per_page*self.current_page.get())-self.combos_per_page
        for i, row in enumerate(self.combo_rows, start_index):
            for j, label in enumerate(row):
                text = self.display_combos[i].get(self.labels[j].lower(), display=True)\
                       if i < len(self.display_combos) else ''
                label.config(text=text)

    def sort_by(self, prop: str):
        self.is_reversed = not self.is_reversed if prop == self.current_sort else False
        self.current_sort = prop
        self.update_display()

    def reset_filters(self):
        for filter in self.filters:
            filter.compare.set(filter.default_compare)
            filter.value.set(filter.default_value)

        self.display_combos = self.combos
        self.update_display()
        self.message_var.set('Filters reset')

    def page_down(self):
        self.current_page.set(self.current_page.get()-1)
        self.update_display()

    def page_up(self):
        self.current_page.set(self.current_page.get()+1)
        self.update_display()

    def get_truth(self, inp, relate, cut):
        ops = {'Equals': operator.eq,
               'Greater Than': operator.gt,
               'Less Than': operator.lt,
               'Contains': operator.contains}
        return ops[relate](inp, cut)


if __name__ == "__main__":
    combo_finder = ComboFinder()
    combo_finder.mainloop()
