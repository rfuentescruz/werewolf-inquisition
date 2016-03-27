from enum import Enum


class ChoiceEnum(object):
    CUSTOM_NAMES = {}

    @classmethod
    def choices(cls):
        choices = []
        for name, item in cls.__members__.items():
            if name in cls.CUSTOM_NAMES:
                name = cls.CUSTOM_NAMES[name]

            choices.append((name, item.value))
