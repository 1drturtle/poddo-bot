import typing


class Item:
    def __init__(self, name: str, type_: str, stats: dict):
        """
        Class that holds the stats for an Item.

        :param str name: The User-friendly name of the item.
        :param str type_: The type of the item. (`fishing_rod`, `pickaxe`)
        :param dict stats: The stats of the item, in a dictionary.
        """
        self.name = name
        self.stats = stats
        self.type = type_

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name', 'Error'),
            type_=data.get('type', 'Error'),
            stats=data.get('stats', {})
        )

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'stats': self.stats
        }


class Inventory:
    def __init__(self, items: typing.List[Item]):
        """
        Holds a bunch of items.

        :param list[Item] items:
        """
        self.items = items

    @classmethod
    def from_dict(cls, data):
        return cls(
            items=[Item.from_dict(x) for x in data.get('items', [])]
        )

    def to_dict(self):
        return {
            'items': [item.to_dict() for item in self.items]
        }
