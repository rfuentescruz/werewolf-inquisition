from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        choices = []
        for item in list(cls):
            choices.append((cls.get_choice_label(item.name), item.value))

        return choices

    @classmethod
    def get_choice_label(cls, name):
        """
        Override this method to provide a different label to an Enum vale
        """
        return name
