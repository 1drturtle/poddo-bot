import math
from . import items as Items
import typing

LEVEL_CONSTANT = 2


def calculate_level(xp: int):
    # The current level is calculated using a square-root equation I found on stack overflow
    level = (xp / 200) ** (1 / LEVEL_CONSTANT)
    return level


def xp_for_level(level: int):
    return (level ** LEVEL_CONSTANT) * 200


class Character:
    def __init__(self, name: str, owner_id: int,
                 level: int = 1, xp: int = 0, gold: int = 0,
                 inventory: Items.Inventory = None):
        self.name = name
        self.owner_id = owner_id
        self._level = level
        self._xp = xp
        self.gold = gold

        if inventory is None:
            inventory = Items.Inventory(items=[])
        self.inventory = inventory

    @classmethod
    def new(cls, name, owner_id):
        rod = Items.Item(name='Old Fishing Rod', type_='fishing_rod', stats={
            'fishing': 1
        })
        pick = Items.Item(name='Rusty Pickaxe', type_='Pickaxe', stats={
            'mining': 1
        })
        inv = Items.Inventory(items=[rod, pick])
        return cls(name, owner_id, inventory=inv)

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name', 'N/A'),
            owner_id=data.get('owner_id', None),
            level=data.get('level', 1),
            xp=data.get('xp', 0),
            gold=data.get('gold', 0),
            inventory=Items.Inventory.from_dict(data.get('inventory', {'items': []}))
        )

    def to_dict(self):
        return {
            'name': self.name,
            'owner_id': self.owner_id,
            'level': self.level,
            'xp': self.xp,
            'gold': self.gold,
            'inventory': self.inventory.to_dict()
        }

    async def commit(self, db):
        """
        Commits the character to a database
        :param db: MotorIO async Mongo DB collection
        :return: Update result
        """
        return await db.update_one(
            {'owner_id': self.owner_id, 'name': self.name},
            {'$set': self.to_dict()},
            upsert=True
        )

    def get_stat(self, stat: str) -> int:
        """
        Gets the sum of a stat.
        :param str stat:
        :return: The total
        :rtype: int
        """
        total = 0
        for item in self.inventory.items:
            if value := item.stats.get(stat):
                total += value
        return total

    @property
    def level(self):
        return self._level

    @property
    def xp(self):
        return self._xp

    def level_str(self):
        percent = (self.xp / xp_for_level(self.level + 1)) * 100
        return f'Level {self.level} | `{self.xp}` / `{xp_for_level(self.level + 1)}` ({percent:0.1f}%)'

    def mod_xp(self, amount: int) -> bool:
        """
        Modifies the character's XP and returns a boolean depending if the character leveled.
        :param int amount: The amount of XP to add/subtract to the character.
        :return: True for level up, None for no change, False for level down.
        :rtype: bool or None
        """

        self._xp = self._xp + amount
        self._xp = round(self._xp, 3)
        out = None
        # level up every time our current XP is greater than the next amount.
        while self._xp > (next_xp := xp_for_level(self._level + 1)):
            self._xp -= next_xp
            self._level += 1
            out = True
        # level down while we are below 0 xp, and add the XP from that previous level to our current XP
        while self._xp < 0:
            self._xp += xp_for_level(self._level - 1)
            self._level -= 1
            out = False
        return out
