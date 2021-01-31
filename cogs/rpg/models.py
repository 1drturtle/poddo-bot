import discord

__all__ = ('Character', 'Item', 'Armor', 'Weapon')


class Item:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self.name

    def to_dict(self):
        return {'name': self.name}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Armor(Item):
    def __init__(self, name: str, defense: int):
        self._defense = defense
        super(Armor, self).__init__(name=name)

    @property
    def defense(self):
        return self._defense

    def to_dict(self):
        d = super(Armor, self).to_dict()
        d.update({
            'defense': self.defense
        })


class Weapon(Item):
    def __init__(self, name, damage):
        self._damage = damage
        super(Weapon, self).__init__(name=name)

    @property
    def defense(self):
        return self.defense

    def to_dict(self):
        d = super(Weapon, self).to_dict()
        d.update({
            'damage': self.damage
        })


class Character:
    def __init__(self, owner: int, name: str, exp: int,
                 armor: list[Armor] = [], weapons: list[Weapon] = []):
        self._owner_id = owner
        self._name = name
        self._exp = exp
        self._armor = armor
        self._weapons = weapons

    @property
    def owner_id(self):
        """Discord ID of the owner of this Character."""
        return self._owner_id

    @property
    def name(self):
        """Character's name"""
        return self._name

    @property
    def exp(self):
        """
        Amount of experience points this character has
        :return: Amount of EXP
        :rtype: int
        """
        return self._exp

    @property
    def armor(self):
        """
        List of character's armor items.
        :return: list[Armor]
        """
        return self.armor

    @property
    def armor_value(self):
        """
        The sum of the character's defense level from each armor piece
        :return: The Defense level
        :rtype: int
        """
        if not self.armor:
            return 0
        return sum([a.defense for a in self.armor])

    @property
    def weapons(self):
        return self.weapons

    @property
    def damage_value(self):
        """
        Returns the highest damage value from the character's weapons.
        :return: Damage value
        :rype: int
        """
        if not self.weapons:
            return 0
        return max([w.damage for w in self.weapons])

    def to_dict(self):
        return {
            'owner': self.owner_id,
            'name': self.name,
            'exp': self.exp,
            'armor': [a.to_dict() for a in self.armor],
            'weapons': [w.to_dict() for w in self.weapons]
        }

    @classmethod
    def from_dict(cls, data):
        armor = [Armor.from_dict(a) for a in data['armor']]
        weapons = [Weapon.from_dict(w) for w in data['weapons']]
        return cls(
            owner=data['owner'], name=data['name'], exp=data['exp'],
            armor=armor, weapons=weapons
        )

    @classmethod
    def new(cls, who, name: str):
        """
        Creates a new character for who
        :param who: The User to create the Character for
        :param str name: The name of the new Character
        :return: Character
        """
        return cls(owner=who.id, name=name, exp=0, armor=[], weapons=[])

    async def commit(self, db):
        """
        Saves the character's current state to the provided database.
        :param db: The database to save the character to.
        """

        await db.update_one(
            # Find our Character by name and owner id.
            {'owner': self.owner_id,
             'name': self.name},
            {'$set': self.to_dict()},
            upsert=True
        )
