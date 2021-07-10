from typing import Union, List, Dict
from dataclasses import dataclass
import dataclasses
import itertools
import resourceManager

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
class EffectTrait:
    name: str
    amt: int


@dataclass
class Effect:
    name: str
    desc: str
    traits: List[EffectTrait]


@dataclass
class Item:
    name: str
    desc: str
    passives: List[str]
    actives: List[str]
    abilities: List[str]
    hidden_actives: List[str]


RANGE = 'range'
TO_HIT = 'to_hit'
DICE = 'dice'
DAMAGE_TYPE = 'damage_type'
DEFAULT_WEAPON_STATS = {
    RANGE: 0,
    TO_HIT: 0,
    DICE: 0,
    DAMAGE_TYPE: ''
}


hidden_effect_id = '???'
hidden_effect = Effect('???', '???', [EffectTrait('???', 1)])


def active_selector(item):
    def _selector():
        return [a if a not in item.hidden_actives else hidden_effect_id for a in item.actives]
    return _selector


@dataclass
class Ability:
    name: str
    desc: str
    passives: List[str]
    actives: List[str]
    stats: dataclasses.field(default_factory=lambda: dict(DEFAULT_WEAPON_STATS))


class Character:
    def __init__(self) -> None:
        self.battle_stats = dict(DEFAULT_BATTLE_STATS)
        self.person_stats = dict(DEFAULT_PERSON_STATS)
        self.other_traits = dict(DEFAULT_CHARACTER_TRAITS)

        self.items: List[str] = []
        self.item_qtys: Dict[str, int] = {}
        self.active_items: List[str] = []
        self.abilities: List[str] = []
        self.effects: List[str] = []

    def get_effects(self) -> List[str]:
        passive_item_effects = (eff for item in self.items for eff in resourceManager.get_item(item).passives)
        active_item_effects = (eff for item in self.items
                               for eff in resourceManager.get_item(item).actives if item in self.active_items)
        abilities = self.get_abilities()
        ability_effects = (eff for ability in abilities for eff in resourceManager.get_ability(ability).passives)
        effects = iter(self.effects)
        all_effects = itertools.chain(effects, passive_item_effects, active_item_effects, ability_effects)
        return list(all_effects)

    def get_abilities(self) -> List[str]:
        abilities = iter(self.abilities)
        item_abilities = (a for item in self.items
                          for a in resourceManager.get_item(item).abilities if item in self.active_items)
        all_abilities = itertools.chain(abilities, item_abilities)
        return list(all_abilities)

    def get_stat_names(self) -> List[str]:
        names = list(self.battle_stats.keys())
        names.extend(self.person_stats.keys())
        names.extend(self.other_traits.keys())
        return names

    def raw_stat(self, name) -> Union[int, str]:
        if name in self.battle_stats:
            return self.battle_stats[name]
        elif name in self.person_stats:
            return self.person_stats[name]
        else:
            return self.other_traits[name]

    def calc_stat(self, name):
        stat = self.raw_stat(name)
        all_effects = self.get_effects()
        filtered_traits = [t for e in all_effects for t in resourceManager.get_effect(e).traits if t.name == name]

        if len(filtered_traits) > 0:
            base = stat
            modifier = sum(t.amt for t in filtered_traits)
            return base, modifier, True
        else:
            return stat, 0, False

    def get_stat(self, name):
        base, mod, modified = self.calc_stat(name)
        return base + mod if modified else base

    def fmt_stat(self, name):
        base, mod, modified = self.calc_stat(name)
        sign = '+' if mod >= 0 else ''
        return f'{base + mod}\n({base}{sign}{mod})' if modified else str(base)

    def set_stat(self, name, value):
        value = int(value) if name != NAME else value
        if name in self.battle_stats:
            self.battle_stats[name] = value
        elif name in self.person_stats:
            self.person_stats[name] = value
        else:
            self.other_traits[name] = value


DEFAULT_CHARACTER = Character()
