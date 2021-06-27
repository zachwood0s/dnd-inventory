import utils

HP = 'hp'
XP = 'xp'
MAX_HP = 'max_hp'
MAX_XP = 'max_xp'

AC = 'ac'
INIT = 'init'
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


class Item:
    def __init__(self, name, desc) -> None:
        self.name = name
        self.desc = desc


class Ability:
    def __init__(self, name, desc) -> None:
        self.name = name
        self.desc = desc


class Character:
    def __init__(self) -> None:
        self.name = 'NoName'

        self.health = 0
        self.max_health = 10

        self.xp = 0
        self.max_xp = 100

        self.battle_stats = dict(DEFAULT_BATTLE_STATS)
        self.person_stats = dict(DEFAULT_PERSON_STATS)

        self.items = []

        self.abilities = []

    def get_stat(self, name) -> str:
        if name == HP:
            return self.health

        if name == XP:
            return self.xp

        if name == MAX_HP:
            return self.max_health
        if name == MAX_XP:
            return self.max_xp

        # have this so I can maybe make some calcs using items?
        if name in self.battle_stats:
            return self.battle_stats[name]
        else:
            return self.person_stats[name]

    def set_stat(self, name, value):
        value = int(value)
        if name == HP:
           self.health = value
        elif name == XP:
            value = utils.clamp(value, 0, self.max_xp)
            self.xp = value
        elif name == MAX_HP:
            self.max_health = value
        elif name == MAX_XP:
            self.max_xp = value
        elif name in self.battle_stats:
            self.battle_stats[name] = value
        else:
            self.person_stats[name] = value

        return value
