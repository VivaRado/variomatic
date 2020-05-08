import unittest
import collections


class TestGroups(unittest.TestCase):

    def getGroups_generic(self):
        groups, _ = self.objectGenerator("groups")
        groups.update({
            "group 1": ["A", "B", "C"],
            "group 2": ["x", "y", "z"],
            "group 3": [],
            "group 4": ["A"]
        })
        return groups

    # ---
    # len
    # ---

    def test_len_initial(self):
        groups = self.getGroups_generic()
        self.assertEqual(
            len(groups),
            4
        )

    def test_len_clear(self):
        groups = self.getGroups_generic()
        groups.clear()
        self.assertEqual(
            len(groups),
            0
        )

    # -------
    # Queries
    # -------

    def test_find_found(self):
        groups = self.getGroups_generic()
        found = groups.findGlyph("A")
        found.sort()
        self.assertEqual(
            found,
            [u"group 1", u"group 4"]
        )

    def test_find_not_found(self):
        groups = self.getGroups_generic()
        self.assertEqual(
            groups.findGlyph("five"),
            []
        )

    def test_find_invalid_key(self):
        groups = self.getGroups_generic()
        with self.assertRaises(TypeError):
            groups.findGlyph(5)

    def test_contains_found(self):
        groups = self.getGroups_generic()
        self.assertTrue("group 4" in groups)

    def test_contains_not_found(self):
        groups = self.getGroups_generic()
        self.assertFalse("group five" in groups)

    def test_get_found(self):
        groups = self.getGroups_generic()
        self.assertEqual(
            groups["group 1"],
            ("A", "B", "C")
        )

    def test_get_not_found(self):
        groups = self.getGroups_generic()
        with self.assertRaises(KeyError):
            groups["group two"]

    # --------------
    # Kerning Groups
    # --------------

    def getGroups_kerning(self):
        groups = self.getGroups_generic()
        kerningGroups = {
            "public.kern1.A": ["A", "Aacute"],
            "public.kern1.O": ["O", "D"],
            "public.kern2.A": ["A", "Aacute"],
            "public.kern2.O": ["O", "C"]
        }
        groups.update(kerningGroups)
        return groups

    def test_side1KerningGroups(self):
        groups = self.getGroups_kerning()
        expected = {
            "public.kern1.A": ("A", "Aacute"),
            "public.kern1.O": ("O", "D")
        }
        self.assertEqual(groups.side1KerningGroups, expected)

    def test_side2KerningGroups(self):
        groups = self.getGroups_kerning()
        expected = {
            "public.kern2.A": ("A", "Aacute"),
            "public.kern2.O": ("O", "C")
        }
        self.assertEqual(groups.side2KerningGroups, expected)

    # ----
    # Hash
    # ----

    def test_hash(self):
        groups = self.getGroups_generic()
        self.assertEqual(
            isinstance(groups, collections.Hashable),
            True
        )

    # --------
    # Equality
    # --------

    def test_object_equal_self(self):
        groups_one = self.getGroups_generic()
        self.assertEqual(
            groups_one,
            groups_one
        )

    def test_object_not_equal_other(self):
        groups_one = self.getGroups_generic()
        groups_two = self.getGroups_generic()
        self.assertNotEqual(
            groups_one,
            groups_two
        )

    def test_object_equal_self_variable_assignment(self):
        groups_one = self.getGroups_generic()
        a = groups_one
        self.assertEqual(
            groups_one,
            a
        )

    def test_object_not_equal_other_variable_assignment(self):
        groups_one = self.getGroups_generic()
        groups_two = self.getGroups_generic()
        a = groups_one
        self.assertNotEqual(
            groups_two,
            a
        )
