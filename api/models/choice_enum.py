from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        choices = []
        for item in list(cls):
            choices.append((item.value, cls.get_choice_label(item.name)))

        return choices

    @classmethod
    def get_choice_label(cls, name):
        """
        Override this method to provide a different label to an Enum vale
        """
        return name.capitalize()
