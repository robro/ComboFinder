#!/usr/bin/env python
import csv
import operator
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from functools import partial
from dataclasses import dataclass


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
    def carry(self) -> float:
        return float(self._carry)

    @property
    def damage(self) -> int:
        return int(self._damage)

    @property
    def advantage(self) -> int:
        return int(self._advantage)

    def get(self, prop: str) -> str:
        return getattr(self, prop)


class ComboFinder(tk.Tk):
    pad = 5
    current_sort = 'character'
    is_reversed = False
    combos: list[Combo] = []
    display_combos: list[Combo] = []
    props = (
        'Character',
        'Notation',
        'Startup',
        'Drive',
        'Super',
        'Carry',
        'Damage',
        'Advantage'
    )
    compares = (
        'Equals',
        'Not Equals',
        'Greater Than',
        'Less Than'
    )
    types = {
        'str': str,
        'int': int,
        'float': float
    }

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        button_width = 15
        row_count = 15

        self.filters = {
            'Character': [tk.StringVar(value='Contains'), tk.StringVar(), 'str'],
            'Notation': [tk.StringVar(value='Contains'), tk.StringVar(), 'str'],
            'Startup': [tk.StringVar(value='Equals'), tk.StringVar(), 'int'],
            'Drive': [tk.StringVar(value='Equals'), tk.StringVar(), 'float'],
            'Super': [tk.StringVar(value='Equals'), tk.StringVar(), 'int'],
            'Carry': [tk.StringVar(value='Equals'), tk.StringVar(), 'float'],
            'Damage': [tk.StringVar(value='Equals'), tk.StringVar(), 'int'],
            'Advantage': [tk.StringVar(value='Equals'), tk.StringVar(), 'int']
        }

        self.title('SF6 Combo Finder')
        self.resizable(False, False)

        # Button frame

        self.button_frame = tk.Frame(self, padx=self.pad, pady=self.pad)
        self.button_frame.grid(row=0, sticky='nesw')

        ttk.Button(self.button_frame, text='Import combos', width=button_width, command=self.import_combos)\
            .grid(row=0, column=0, padx=self.pad, pady=self.pad)
        ttk.Button(self.button_frame, text='Filters', width=button_width, command=self.open_filters)\
            .grid(row=0, column=1, padx=self.pad, pady=self.pad)

        # Info frame

        self.info_frame = tk.Frame(self, padx=10, pady=self.pad)
        column_sizes = (100, 200, 100, 100, 100, 100, 100, 100)
        for column, size in enumerate(column_sizes):
            self.info_frame.grid_columnconfigure(column, minsize=size)
        self.info_frame.grid(row=1, sticky='nsew')

        self.headers = [ttk.Button(self.info_frame, text=prop, name=prop.lower(),
                        command=partial(self.sort_by, prop.lower()))
                        for prop in self.props]
        for column, header in enumerate(self.headers):
            header.grid(row=0, column=column, sticky='nsew')
            header.config(state='disabled')

        self.text_rows = [[
            ttk.Label(self.info_frame, padding=self.pad) for _ in range(len(self.props))]
            for _ in range(row_count)]
        current_row = 1
        for i, row in enumerate(self.text_rows):
            for column, label in enumerate(row):
                label.grid(row=current_row, column=column, sticky='nsew')
                label.config(text=f'{i}{column}')
            if i == len(self.text_rows)-1:
                break
            ttk.Separator(self.info_frame, orient='horizontal')\
                .grid(row=current_row+1, columnspan=8, sticky='nsew')
            current_row += 2

        self.sort_by(self.current_sort)

        # Message frame

        self.message_frame = tk.Frame(self, padx=self.pad, pady=self.pad)
        self.message_frame.grid(row=3, sticky='nsew')

        self.message_var = tk.StringVar()
        tk.Message(self.message_frame, textvariable=self.message_var, width=300)\
            .grid(row=0, column=0, sticky='nsew')

    def open_filters(self):
        try:
            self.filter_window.focus()
            return
        except:
            pass

        self.filter_window = tk.Toplevel(self)
        self.filter_window.title('Filters')
        self.filter_window.resizable(False, False)

        # Filters frame

        self.filters_frame = tk.Frame(self.filter_window, padx=self.pad, pady=self.pad)
        self.filters_frame.grid(row=0)

        for i, prop in enumerate(self.props):
            entry_width = 30
            columnspan = 2
            column = 1
            padx = self.pad
            ttk.Label(self.filters_frame, text=prop, anchor='center', padding=5)\
                .grid(row=i, column=0, sticky='w')
            if i > 1:
                entry_width -= 16
                columnspan = 1
                column = 2
                padx = 0
                ttk.Combobox(self.filters_frame, width=11, textvariable=self.filters[prop][0], values=self.compares)\
                    .grid(row=i, column=1, sticky='w', padx=self.pad, pady=self.pad)
            ttk.Entry(self.filters_frame, width=entry_width, textvariable=self.filters[prop][1])\
                .grid(row=i, column=column, sticky='w', padx=padx, pady=self.pad, columnspan=columnspan)

        # Buttons frame

        self.submit_frame = tk.Frame(self.filter_window, padx=self.pad, pady=self.pad)
        self.submit_frame.grid(row=1)

        ttk.Button(self.submit_frame, text='Submit', command=self.update_combos)\
            .grid(row=0, column=0, padx=self.pad, pady=self.pad, sticky='w')
        ttk.Button(self.submit_frame, text='Reset', command=self.reset_filters)\
            .grid(row=0, column=1, padx=self.pad, pady=self.pad, sticky='w')

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
            for prop in self.filters:
                if not self.filters[prop][1].get():
                    continue
                if not get_truth(combo.get(prop.lower()), self.filters[prop][0].get(),
                        self.types[self.filters[prop][2]](self.filters[prop][1].get())):
                    break
            else:
                matches.append(combo)

        self.display_combos = matches
        self.update_display()
        self.message_var.set(f'Found {len(self.display_combos)} out of {len(self.combos)} total combos')

    def update_display(self):
        self.display_combos.sort(key=lambda x: x.get(self.current_sort), reverse=self.is_reversed)
        state = 'normal' if self.display_combos else 'disabled'
        for header in self.headers:
            header.config(state=state)

        for i, row in enumerate(self.text_rows):
            for j, label in enumerate(row):
                text = self.display_combos[i].get(self.props[j].lower()) if i < len(self.display_combos) else ''
                label.config(text=text)
                
    def sort_by(self, prop: str):
        for header in self.headers:
            default = 'active' if header.winfo_name() == prop else 'normal'
            header.config(default=default)

        self.is_reversed = not self.is_reversed if prop == self.current_sort else False
        self.current_sort = prop
        self.update_display()

    def reset_filters(self):
        for filter in self.filters:
            if filter not in ('Character', 'Notation'):
                self.filters[filter][0].set('Equals')
            self.filters[filter][1].set('')
        
        self.display_combos = self.combos
        self.update_display()
        self.message_var.set('Filters reset')


def get_truth(inp, relate, cut):
    ops = {'Equals': operator.eq,
           'Not Equals': operator.ne,
           'Greater Than': operator.gt,
           'Less Than': operator.lt,
           'Contains': operator.contains}
    return ops[relate](inp, cut)

if __name__ == "__main__":
    combo_finder = ComboFinder()
    combo_finder.mainloop()
