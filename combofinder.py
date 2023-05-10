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

    def __str__(self) -> str:
        return f'CHR: {self.character}\n\
NTA: {self.notation}\n\
STP: {self.startup} frames\n\
DRV: {self.drive} bars\n\
SUP: {self.super} bars\n\
CAR: {self.carry:.0%}\n\
DMG: {self.damage}\n\
ADV: {"+" if int(self.advantage) >= 0 else ""}{self.advantage}\n'


class ComboFinder(tk.Tk):
    combos: set = None

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title('Combo Finder')
        self.resizable(False, False)

        self.frame = tk.Frame(self, padx=10, pady=10)
        self.frame.pack()

        self.combo_import_btn = ttk.Button(self.frame, text='Import combos', width=40, command=self.import_combos)
        self.combo_import_btn.grid(row=0, column=0, padx=5, pady=5)

        self.text = tk.Text(self.frame, relief='flat', cursor='arrow', width=40, state='disabled')
        self.text.grid(row=1, column=0, padx=5, pady=5)

        self.msg_var = tk.StringVar()
        self.message = tk.Message(self.frame, textvariable=self.msg_var, width='300p')
        self.message.grid(row=2, column=0, padx=5, pady=5, sticky='w')

    def import_combos(self):
        filename = filedialog.askopenfilename(initialdir=os.path.abspath('.'), filetypes=[('CSV', '.csv')])

        with open(filename, 'r') as combos_file:
            combos_list = list(csv.reader(combos_file, skipinitialspace=True))[1:]

        self.combos = set(Combo(*combo) for combo in combos_list)
        self.update_combos()
        self.msg_var.set('Combos successfully imported')

    def update_combos(self):
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        self.text.insert('end', '\n'.join(combo.__str__() for combo in self.combos))
        self.text['state'] = 'disabled'


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
