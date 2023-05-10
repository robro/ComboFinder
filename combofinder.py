#!/usr/bin/env python
import csv
import operator
import argparse
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
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
    combos: list[Combo] = []
    combo_props = ('Character', 'Notation', 'Startup', 'Drive', 'Super', 'Carry', 'Damage', 'Advantage')

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        padx = 5
        pady = 5
        button_width = 20
        title_font = ('Calibri', 12)
        row_count = 10

        self.title('Combo Finder')
        self.resizable(False, False)

        self.btns = tk.Frame(self, padx=padx, pady=pady)
        self.btns.grid(row=0, sticky='nesw')

        self.import_btn = ttk.Button(self.btns, text='Import combos', width=button_width, command=self.import_combos)
        self.import_btn.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')
        self.filter_btn = ttk.Button(self.btns, text='Filter', width=button_width)
        self.filter_btn.grid(row=0, column=1, padx=15, pady=pady, sticky='w')

        self.main = tk.Frame(self, padx=10, pady=10)
        column_sizes = (100, 200, 100, 100, 100, 100, 100, 100)
        for i, size in enumerate(column_sizes):
            self.main.grid_columnconfigure(i, minsize=size)
        self.main.grid(row=1)
        self.labels = [ttk.Label(self.main, text=column_title, background='gray', anchor='center', padding=padx, font=title_font) for column_title in self.combo_props]
        for i, label in enumerate(self.labels):
            label.grid(row=0, column=i, sticky='nsew')

        self.text_rows = [[tk.Text(self.main, width=1, height=1, border=0, cursor='arrow', padx=padx, pady=pady) for _ in range(len(self.combo_props))] for _ in range(row_count)]
        for i, text_row in enumerate(self.text_rows, 1):
            bg_color = 'white' if i % 2 else 'lightgray'
            for j, text_box in enumerate(text_row):
                # text_box.insert('end', f'{i}{j}')
                text_box.config(bg=bg_color)
                text_box.grid(row=i, column=j, sticky='nsew')
                text_box.config(state='disabled')

        self.message_frame = tk.Frame(self)
        self.message_frame.grid(row=2, sticky='nsew')
        self.message_var = tk.StringVar()
        self.message = tk.Message(self.message_frame, textvariable=self.message_var, width=300)
        self.message.grid()

    def import_combos(self):
        filename = filedialog.askopenfilename(initialdir=os.path.abspath('.'), filetypes=[('Comma separated', '.csv')])
        if not filename:
            return
        
        with open(filename, 'r') as combos_file:
            combos_list = list(csv.reader(combos_file, skipinitialspace=True))[1:]

        self.combos = list(set(Combo(*combo) for combo in combos_list))
        self.update_display()
        self.message_var.set('Combos successfully imported')

    def update_display(self):
        for i, row in enumerate(self.text_rows):
            for j, text in enumerate(row):
                text.config(state='normal')
                text.delete(1.0, 'end')
                if i < len(self.combos):
                    text.insert('end', self.combos[i].get(self.combo_props[j].lower()))
                text.config(state='disabled')


def get_truth(inp, relate, cut):
    ops = {'gt': operator.gt,
           'lt': operator.lt,
           'ge': operator.ge,
           'le': operator.le,
           'eq': operator.eq,
           'ne': operator.ne}
    return ops[relate](inp, cut)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--chr', metavar='CHARACTER')
    parser.add_argument('--nta', metavar='NOTATION')
    parser.add_argument('--stp', nargs=2, metavar=('OP', 'STARTUP'))
    parser.add_argument('--drv', nargs=2, metavar=('OP', 'DRIVE'))
    parser.add_argument('--sup', nargs=2, metavar=('OP', 'SUPER'))
    parser.add_argument('--car', nargs=2, metavar=('OP', 'CARRY'))
    parser.add_argument('--dmg', nargs=2, metavar=('OP', 'DAMAGE'))
    parser.add_argument('--adv', nargs=2, metavar=('OP', 'ADVANTAGE'))
    args = parser.parse_args()

    with open('combos.csv', 'r') as combos_file:
        combos_list = list(csv.reader(combos_file, skipinitialspace=True))[1:]

    combos = set(Combo(*combo) for combo in combos_list)

    filters = {}
    if args.chr:
        filters['character'] = ('eq', args.chr)
    if args.nta:
        filters['notation'] = ('eq', args.nta)
    if args.stp:
        filters['startup'] = (args.stp[0], int(args.stp[1]))
    if args.drv:
        filters['drive'] = (args.drv[0], float(args.drv[1]))
    if args.sup:
        filters['super'] = (args.sup[0], int(args.sup[1]))
    if args.car:
        filters['carry'] = (args.car[0], float(args.car[1]))
    if args.dmg:
        filters['damage'] = (args.dmg[0], int(args.dmg[1]))
    if args.adv:
        filters['advantage'] = (args.adv[0], int(args.adv[1]))

    if filters:
        combos = set(combo for combo in combos if all(get_truth(combo.get(prop), filters.get(prop)[0], filters.get(prop)[1]) for prop in filters))

    combo_count = len(combos)
    print(f'{combo_count} combo{"" if combo_count == 1 else "s"} found', end='\n\n')
    [print(combo) for combo in combos]

if __name__ == "__main__":
    combo_finder = ComboFinder()
    combo_finder.mainloop()
