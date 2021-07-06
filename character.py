from typing import Union
from dataclasses import dataclass

NAME = 'name'
HP = 'hp'
XP = 'xp'
MAX_HP = 'max_hp'
MAX_XP = 'max_xp'

AC = 'ac'
INIT = 'ini'
SPD = 'spd'
PWR = 'pwr'

CHR = 'chr'
INT = 'int'
WIS = 'wis'
STR = 'str'
DEX = 'dex'
CON = 'con'


class Stat:
    def __init__(self, base) -> None:
        self.base = base
        self.modifiers = 0

    def __str__(self) -> str:
        if self.modifiers == 0:
            return str(self.base)

        sign = '+' if self.modifiers > 0 else '-'
        return f'{self.base + self.modifiers} ({sign}{self.modifiers})'


DEFAULT_BATTLE_STATS = {
    AC: 4,
    INIT: 4,
    SPD: 4,
    PWR: 3
}

DEFAULT_PERSON_STATS = {
    CHR: 4,
    INT: 4,
    WIS: 4,
    STR: 4,
    DEX: 4,
    CON: 4,
}

DEFAULT_CHARACTER_TRAITS = {
    HP: 0,
    MAX_HP: 10,
    XP: 0,
    MAX_XP: 10,
    NAME: 'NoName',
}


@dataclass
class EffectStats:
    hp: int = 0
    ac: int = 0
    init: int = 0
    spd: int = 0
    chr: int = 0
    intel: int = 0
    wis: int = 0
    str: int = 0
    dex: int = 0
    con: int = 0


@dataclass
class Effect:
    name: str
    desc: str
    stats: EffectStats


class Item(Effect):
    pass


class Ability(Effect):
    pass


class Character:
    def __init__(self) -> None:
        self.battle_stats = dict(DEFAULT_BATTLE_STATS)
        self.person_stats = dict(DEFAULT_PERSON_STATS)
        self.other_traits = dict(DEFAULT_CHARACTER_TRAITS)

        self.items = []
        self.abilities = []
        self.effects = []

    def get_stat(self, name) -> Union[int, str]:
        if name in self.battle_stats:
            return self.battle_stats[name]
        elif name in self.person_stats:
            return self.person_stats[name]
        else:
            return self.other_traits[name]

    def set_stat(self, name, value):
        value = int(value) if name != NAME else value
        if name in self.battle_stats:
            self.battle_stats[name] = value
        elif name in self.person_stats:
            self.person_stats[name] = value
        else:
            self.other_traits[name] = value
