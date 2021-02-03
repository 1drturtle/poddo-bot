import math

LEVEL_CONSTANT = 2


def calculate_level(xp: int):
    # The current level is calculated using a square-root equation I found on stack overflow
    level = (xp/200) ** (1/LEVEL_CONSTANT)
    return level


def xp_for_level(level: int):
    return (level ** LEVEL_CONSTANT) * 200


class Character:
    def __init__(self, name: str, owner_id: int,
                 level: int = 1, xp: int = 0, gold: int = 0):
        self.name = name
        self.owner_id = owner_id
        self._level = level

        self._xp = xp

        self.gold = gold

    @classmethod
    def from_dict(cls, data):
        return cls(
                data['name'], data['owner_id'],
                level=data.get('level', 1), xp=data.get('xp', 0), gold=data.get('gold', 0)
            )

    def to_dict(self):
        return {
            'name': self.name,
            'owner_id': self.owner_id,
            'level': self.level,
            'xp': self.xp,
            'gold': self.gold
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


    @property
    def level(self):
        return self._level

    @property
    def xp(self):
        return self._xp

    def mod_xp(self, value):
        """
        Function for modifying XP. Returns True if the character levels up otherwise returns None.
        Returns False if the character goes down a level
        :param value: XP to add or subtract
        :return:
        """
        self._xp += value
        if self.xp > (next_xp := xp_for_level(self.level + 1)):
            self._xp -= next_xp
            self._level += 1
            # keep calculating until we are in a level range
            while self.xp > xp_for_level(self.level + 1) and self.xp != 0:
                self.mod_xp(0)
            return True
        elif self.xp < 0:
            self._xp -= xp_for_level(self.level - 1)
            # can't go below level 1
            if self.level - 1 <= 1:
                self._xp = 0
                self._level = 1
            else:
                self._level -= 1
            # keep calculating until we are in a level range
            while self.xp < xp_for_level(self.level + 1) and self.xp != 0:
                self.mod_xp(0)
            return False
        return None

    def level_str(self):
        percent = (self.xp / xp_for_level(self.level + 1)) * 100
        return f'Level {self.level} | {self.xp}/{xp_for_level(self.level+1)} ({percent:0.1f}%)'
