# -*- coding: utf-8 -*-
#
# tests utis methods
# IMIO <support@imio.be>
#
from collections import OrderedDict
from imio.pyutils.system import hashed_filename
from imio.pyutils.system import read_dir_filter
from imio.pyutils.system import read_recursive_dir
from imio.pyutils.utils import add_key_if_value
from imio.pyutils.utils import all_of_dict_values
from imio.pyutils.utils import append
from imio.pyutils.utils import get_clusters
from imio.pyutils.utils import get_ordinal_clusters
from imio.pyutils.utils import insert_in_ordereddict
from imio.pyutils.utils import iterable_as_list_of_list
from imio.pyutils.utils import letters_sequence
from imio.pyutils.utils import listify
from imio.pyutils.utils import merge_dicts
from imio.pyutils.utils import odict_pos_key
from imio.pyutils.utils import one_of_dict_values
from imio.pyutils.utils import radix_like_starting_1
from imio.pyutils.utils import replace_in_list
from imio.pyutils.utils import safe_encode
from imio.pyutils.utils import sort_by_indexes

import os
import types
import unittest


class TestUtils(unittest.TestCase):
    """ """

    def test_add_key_if_value(self):
        dic = {}
        add_key_if_value(dic, "a", None)
        self.assertDictEqual(dic, {})
        add_key_if_value(dic, "a", "", strict=True)
        self.assertDictEqual(dic, {})
        add_key_if_value(dic, "a", "")
        self.assertDictEqual(dic, {"a": ""})
        add_key_if_value(dic, "b", "b")
        self.assertDictEqual(dic, {"a": "", "b": "b"})
        add_key_if_value(dic, "c", "c", strict=True)
        self.assertDictEqual(dic, {"a": "", "b": "b", "c": "c"})

    def test_all_of_dict_values(self):
        self.assertListEqual(all_of_dict_values({1: None, 2: "Good", 3: "", 4: "job"}, [1, 2, 3, 4]), ["Good", "job"])
        self.assertListEqual(
            all_of_dict_values({1: None, 2: "Good", 3: "", 4: "job"}, [2, 4], labels=[u"Two", u"Four"]),
            ["Two=Good", "Four=job"],
        )
        self.assertListEqual(
            all_of_dict_values({1: None, 2: "Good", 3: "", 4: "job"}, [2, 4], labels=[u"Two", u""]), ["Two=Good", "job"]
        )
        self.assertRaises(ValueError, all_of_dict_values, {}, [1], labels=[1, 2])
        self.assertListEqual(all_of_dict_values({}, [1, 2]), [])

    def test_append(self):
        lst = [1]
        self.assertEqual(append(lst, 2), 2)
        self.assertListEqual(lst, [1, 2])

    def test_get_clusters(self):
        self.assertEqual(get_clusters([1, 2, 3, 5, 6, 8, 10, 15]), "1-3, 5-6, 8, 10, 15")
        self.assertEqual(get_clusters([1, 2, 3, 5, 5.1, 5.3, 6, 8, 10, 15]), "1-3, 5, 5.1, 5.3, 6, 8, 10, 15")
        self.assertEqual(get_clusters([1, 2, 4, 5, 15], separator="|"), "1-2|4-5|15")

    def test_get_ordinal_clusters(self):
        self.assertEqual(get_ordinal_clusters([100, 200, 300, 500, 600, 800, 1000, 1500]), "1-3, 5-6, 8, 10, 15")
        self.assertEqual(
            get_ordinal_clusters([100, 200, 300, 500, 501, 503, 600, 700, 1000, 1500]), "1-3, 5-5.1, 5.3, 6-7, 10, 15"
        )
        self.assertEqual(
            get_ordinal_clusters([100, 200, 300, 400, 500, 501, 502, 521, 522, 540, 550, 1200, 1300], separator="|"),
            "1-5.2|5.21-5.22|5.40|5.50|12-13",
        )
        self.assertEqual(
            get_ordinal_clusters(
                [100, 200, 300, 301, 302, 321, 322, 340, 1199, 1200, 1300], cluster_format="from {} to {}"
            ),
            "from 1 to 3.2, from 3.21 to 3.22, 3.40, 11.99, from 12 to 13",
        )
        self.assertEqual(
            get_ordinal_clusters([100, 200, 250, 400, 700], single_cluster_format="({})"), "1-2, (2.50), (4), (7)"
        )
        self.assertEqual(get_ordinal_clusters([10, 20, 30, 31, 32, 110, 112, 130], offset=10), "1-3.2, 11, 11.2, 13")
        self.assertListEqual(
            get_ordinal_clusters([100, 200, 250, 400, 700], as_str=False), [[100, 200], [250], [400], [700]]
        )
        self.assertEqual(get_ordinal_clusters([]), '')
        self.assertEqual(get_ordinal_clusters([], as_str=False), [])
        self.assertEqual(get_ordinal_clusters(), '')
        self.assertEqual(get_ordinal_clusters(as_str=False), [])

    def test_insert_in_ordered_dict(self):
        dic = OrderedDict([("a", 1), ("b", 2)])
        self.assertEqual(insert_in_ordereddict(dic, ("bad", 3)), None)
        self.assertEqual(
            list(insert_in_ordereddict(dic, ("c", 3), after_key="a").items()), [("a", 1), ("c", 3), ("b", 2)]
        )
        self.assertEqual(
            list(insert_in_ordereddict(dic, ("c", 3), after_key="b").items()), [("a", 1), ("b", 2), ("c", 3)]
        )
        self.assertEqual(insert_in_ordereddict(dic, ("bad", 3), after_key="unk"), None)
        self.assertEqual(
            list(insert_in_ordereddict(dic, ("c", 3), after_key="unk", at_position=1).items()),
            [("a", 1), ("c", 3), ("b", 2)],
        )
        self.assertEqual(
            list(insert_in_ordereddict(dic, ("c", 3), at_position=0).items()), [("c", 3), ("a", 1), ("b", 2)]
        )
        self.assertEqual(
            list(insert_in_ordereddict(dic, ("c", 3), at_position=1).items()), [("a", 1), ("c", 3), ("b", 2)]
        )
        self.assertEqual(
            list(insert_in_ordereddict(dic, ("c", 3), at_position=10).items()), [("a", 1), ("b", 2), ("c", 3)]
        )
        self.assertEqual(list(insert_in_ordereddict(OrderedDict([]), ("c", 3), at_position=1).items()), [("c", 3)])
        self.assertEqual(list(insert_in_ordereddict(dic, ("c", 3), at_position=-1).items()), [("a", 1), ("b", 2)])

    def test_iterable_as_list_of_list(self):
        lst = [1, 2, 3, 4]
        self.assertListEqual(iterable_as_list_of_list(lst, 4), [lst])
        self.assertListEqual(iterable_as_list_of_list(lst, 6), [lst])
        self.assertListEqual(iterable_as_list_of_list(lst, 2), [[1, 2], [3, 4]])
        self.assertListEqual(iterable_as_list_of_list(lst, 1), [[1], [2], [3], [4]])
        self.assertListEqual(iterable_as_list_of_list(lst, 3), [[1, 2, 3], [4]])
        self.assertRaises(ZeroDivisionError, iterable_as_list_of_list, lst, 0)

    def test_letters_sequence(self):
        tests = [
            {"lt": "ab", "nths": [(0, ""), (1, "a"), (2, "b"), (3, "aa"), (6, "bb"), (9, "aba")]},
            {
                "lt": "abcdefghijklmnopqrstuvwxyz",
                "nths": [(15, "o"), (26, "z"), (27, "aa"), (100, "cv"), (702, "zz"), (703, "aaa")],
            },
        ]
        for dic in tests:
            lt = dic["lt"]
            for n, res in dic["nths"]:
                self.assertEqual(
                    letters_sequence(n, lt), res, "n:{},res:{} <=> {}".format(n, res, letters_sequence(n, lt))
                )

    def test_merge_dicts(self):
        self.assertEqual(merge_dicts([{"a": [1]}, {"a": [2]}]), {"a": [1, 2]})
        self.assertEqual(merge_dicts([{"a": [1], "b": [0]}, {"a": [2]}]), {"a": [1, 2], "b": [0]})
        self.assertEqual(
            merge_dicts([{"a": [1], "b": [0]}, {"a": [2]}, {"a": [2], "b": [1], "c": [4]}]),
            {"a": [1, 2, 2], "b": [0, 1], "c": [4]},
        )

    def test_odict_pos_key(self):
        dic = OrderedDict([("a", 1), ("b", 2)])
        self.assertIsNone(odict_pos_key(dic, -1))
        self.assertIsNone(odict_pos_key(dic, 3))
        self.assertEqual(odict_pos_key(dic, 0), "a")
        self.assertEqual(odict_pos_key(dic, 1), "b")

    def test_one_of_dict_values(self):
        self.assertEqual(one_of_dict_values({1: None, 3: "", 4: "job"}, [1, 2, 3, 4]), "job")

    def test_radix_like_starting_1(self):
        # Considering a sequence of 2 letters a, b => base 2 (similar to bit values 0, 1 base 2)
        self.assertListEqual(radix_like_starting_1(0, 2), [])  # corresponding to nothing (bit would be 0)
        self.assertListEqual(radix_like_starting_1(1, 2), [1])  # corresponding to a (bit would be 1)
        self.assertListEqual(radix_like_starting_1(2, 2), [2])  # corresponding to b (bit would be 10)
        self.assertListEqual(radix_like_starting_1(3, 2), [1, 1])  # corresponding to aa (bit would be 11)
        self.assertListEqual(radix_like_starting_1(4, 2), [1, 2])  # corresponding to ab (bit would be 100)
        self.assertListEqual(radix_like_starting_1(5, 2), [2, 1])  # corresponding to ba
        self.assertListEqual(radix_like_starting_1(6, 2), [2, 2])  # corresponding to bb
        self.assertListEqual(radix_like_starting_1(7, 2), [1, 1, 1])  # corresponding to aaa

    def test_replace_in_list(self):
        self.assertEqual(replace_in_list([1, 2, 3], 1, 4), [4, 2, 3])
        self.assertEqual(replace_in_list([1, 2, 3], 4, 5), [1, 2, 3])
        self.assertEqual(replace_in_list([1, 2, 3, 1], 1, 5), [5, 2, 3, 5])
        # generator
        res = replace_in_list([1, 2, 3], 1, 4, generator=True)
        self.assertTrue(isinstance(res, types.GeneratorType))
        self.assertEqual(list(res), [4, 2, 3])

    def test_safe_encode(self):
        self.assertEqual(safe_encode(u"xx"), "xx")
        self.assertEqual(safe_encode(b"xx"), "xx")
        self.assertEqual(safe_encode(5), 5)

    def test_sort_by_indexes(self):
        lst = ["a", "b", "c", "d", "e", "f", "g"]
        indexes = [1, 3, 5, 2, 4, 6, 6]
        self.assertEqual(sort_by_indexes(lst, indexes), ["a", "d", "b", "e", "c", "f", "g"])
        lst = ["a", "b", "c", "d", "e"]
        indexes = [1, 3, 2, 9, 9]
        self.assertEqual(sort_by_indexes(lst, indexes), ["a", "c", "b", "d", "e"])

    def test_listify(self):
        self.assertEqual(listify("value"), ["value"])
        self.assertEqual(listify(["value"]), ["value"])
        self.assertEqual(listify(("value")), ["value"])
        self.assertEqual(listify(("value",)), ("value",))
        self.assertEqual(listify(("value",), force=True), ["value"])


class TestSystem(unittest.TestCase):
    """ """

    def setUp(self):
        file_dir = os.path.dirname(__file__)
        self.dir = file_dir.replace("/pyutils", "")

    def test_read_recursive_dir(self):
        res = read_recursive_dir(self.dir, "")
        self.assertEqual(len([path for path in res if path.endswith(".py")]), 8)
        self.assertIn("__init__.py", res)
        self.assertIn("pyutils/__init__.py", res)
        # include folder
        self.assertNotIn("pyutils", res)
        res = read_recursive_dir(self.dir, "", with_folder=True)
        self.assertIn("pyutils", res)
        # include full path
        self.assertEqual(len([path for path in res if path.endswith("/pyutils")]), 0)
        res = read_recursive_dir(self.dir, "", with_folder=True, with_full_path=True)
        self.assertEqual(len([path for path in res if path.endswith("/pyutils")]), 1)
        # exclude patterns
        self.assertTrue([path for path in res if path.endswith(".pyc")])
        res = read_recursive_dir(self.dir, "", exclude_patterns=[r"\.pyc$"])
        self.assertFalse([path for path in res if path.endswith(".pyc")])
        res = read_recursive_dir(self.dir, "", exclude_patterns=[r"^pyutils/", r"\.pyc$"])
        self.assertEqual(len(res), 1)

    def test_read_dir_filter(self):
        res = read_dir_filter(self.dir)
        self.assertIn("__init__.py", res)
        self.assertIn("pyutils", res)
        res = read_dir_filter(self.dir, with_path=True)
        self.assertNotIn("__init__.py", res)
        self.assertIn(os.path.join(self.dir, "__init__.py"), res)
        self.assertIn(os.path.join(self.dir, "pyutils"), res)
        res = read_dir_filter(self.dir, extensions=["py"])
        self.assertIn("__init__.py", res)
        self.assertNotIn("pyutils", res)
        res = read_dir_filter(self.dir, only_folders=True)
        self.assertNotIn("__init__.py", res)
        self.assertIn("pyutils", res)
        res = read_dir_filter(self.dir, patterns=[r".*\.py$"])
        self.assertIn("__init__.py", res)
        self.assertNotIn("pyutils", res)

    def test_hashed_filename(self):
        self.assertEqual(hashed_filename("", ""), "")
        self.assertEqual(hashed_filename("test.txt", ""), "test.txt")
        self.assertEqual(hashed_filename("test.txt", "", 20), "test.txt")
        self.assertEqual(
            hashed_filename("test.txt", "the string value to differentiate some files"),
            "test_f9fde993c5b66b18fce3a03bf2bd1e11e05c598b.txt",
        )
        self.assertEqual(
            hashed_filename("test.txt", "the string value to differentiate some file"),
            "test_b99fae91a375c3b6fa36fa23a34c666f79375ffe.txt",
        )
