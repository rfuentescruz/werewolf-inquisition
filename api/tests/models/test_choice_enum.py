from django.test import TestCase

from ...models.choice_enum import ChoiceEnum


class ChoiceEnumTest(TestCase):
    def test_choice_enum_like_enum(self):
        """
        Test that ChoiceEnum still behaves like an Enum
        """
        class Foo(ChoiceEnum):
            BAR = 'bar'
            BAZ = 'baz'

        self.assertEquals(Foo.BAR.value, 'bar')
        self.assertEquals(Foo.BAR, Foo('bar'))

        self.assertTrue(isinstance(Foo.BAR, Foo))

        self.assertNotEquals(Foo.BAR, Foo.BAZ)

    def test_choice_enum_callable(self):
        """
        Test that ChoiceEnum is also callable like an Enum
        """
        Foo = ChoiceEnum('Foo', 'BAR BAZ')

        self.assertEquals(Foo.BAR.value, 1)
        self.assertTrue(isinstance(Foo.BAR, Foo))
        self.assertNotEquals(Foo.BAR, Foo.BAZ)

    def test_choice_enum_like_choices(self):
        """
        Test that `choices` will generate list of (name, value) tuples
        """

        class Foo(ChoiceEnum):
            BAR = 'bar'
            BAZ = 'baz'

        self.assertEquals(
            Foo.choices(),
            [('bar', 'Bar'), ('baz', 'Baz')]
        )

    def test_choice_enum_choices_custom_names(self):
        """
        Test item names can be overriden when calling `choices`
        """
        class Foo(ChoiceEnum):
            BAR = 'bar'
            BAZ = 'baz'

            @classmethod
            def get_choice_label(cls, name):
                labels = {'BAR': 'QUX'}

                label = labels[name] if name in labels else name
                return label.capitalize()

        self.assertEquals(
            Foo.choices(),
            [('bar', 'Qux'), ('baz', 'Baz')]
        )

    def test_choice_enum_custom_names_only_for_choices(self):
        """
        Test custom labels do not affect the enum members
        """
        class Foo(ChoiceEnum):
            BAR = 'bar'
            BAZ = 'baz'

            @classmethod
            def get_choice_label(cls, name):
                labels = {'BAR': 'QUX'}

                return labels[name] if name in labels else name

        self.assertEquals(Foo.BAR.value, 'bar')

        with self.assertRaises(AttributeError):
            self.assertEquals(Foo.QUX.value, 'bar')

        with self.assertRaises(AttributeError):
            self.assertEquals(Foo.Qux.value, 'bar')
