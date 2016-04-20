from .choice_enum import ChoiceEnum


class Phases(ChoiceEnum):
    INITIAL = 0
    DAY = 1
    VOTING = 2
    NIGHT = 3
