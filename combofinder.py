#!/usr/bin/env python
import csv
import operator
import argparse
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
    def super(self) -> float:
        return float(self._super)
    
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
DRV: {"+" if self.drive >= 0.0 else ""}{self.drive} bars\n\
SUP: {"+" if self.super >= 0.0 else ""}{self.super} bars\n\
CAR: {self.carry:.0%}\n\
DMG: {self.damage}\n\
ADV: {"+" if int(self.advantage) >= 0 else ""}{self.advantage}\n'
    
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

    combos = set([Combo(*combo) for combo in combos_list])
    
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
        filters['super'] = (args.sup[0], float(args.sup[1]))
    if args.car:
        filters['carry'] = (args.car[0], float(args.car[1]))
    if args.dmg:
        filters['damage'] = (args.dmg[0], int(args.dmg[1]))
    if args.adv:
        filters['advantage'] = (args.adv[0], int(args.adv[1]))

    if filters:
        filtered_combos = [combo for combo in combos if all(get_truth(combo.get(prop), filters.get(prop)[0], filters.get(prop)[1]) for prop in filters)]
        combo_count = len(filtered_combos)
        print(f'{combo_count} combo{"s" if combo_count > 1 else ""} found', end='\n\n')
        [print(combo) for combo in filtered_combos]
    else:
        print(f'{len(combos)} combos found', end='\n\n')
        [print(combo) for combo in combos]
        

if __name__ == "__main__":
    main()
