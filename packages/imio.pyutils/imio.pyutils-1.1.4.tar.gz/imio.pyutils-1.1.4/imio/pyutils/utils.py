# -*- coding: utf-8 -*-
#
# python utils methods
# IMIO <support@imio.be>
#
from __future__ import print_function

from collections import defaultdict
from collections import OrderedDict
from itertools import chain
from operator import methodcaller
from six import ensure_str
from six import string_types
from six.moves import map
from six.moves import range
from six.moves import zip

import copy
import itertools
import logging
import time
import timeit


def add_key_if_value(dic, key, value, strict=False):
    """Add a key to a dict only if a value or is not None.

    :param dic: input dictionary
    :param key: key to add
    :param value: value to add
    :param strict: if True, add only if value is considered boolean True
    """
    if strict:
        if value:
            dic[key] = value
    elif value is not None:
        dic[key] = value


def all_of_dict_values(dic, keys, labels=[], sep=u"="):
    """Returns a not empty values list from a dict following given keys.

    :param dic: input dictionary
    :param keys: searched keys
    :param labels: corresponding labels
    :param sep: separator between label and value
    :return: list with corresponding values.
    """
    if labels and len(labels) != len(keys):
        raise ValueError(u"labels length must be the same as keys length")
    ret = []
    for i, key in enumerate(keys):
        if dic.get(key):
            ret.append(labels and u"{}{}{}".format(labels[i], labels[i] and sep or u"", dic[key]) or dic[key])
    return ret


def append(lst, value):
    lst.append(value)
    return value


def ftimed(f, nb=100, fmt="{:.7f}"):
    duration, ret = timed(f, nb=nb)
    return fmt.format(duration), ret


def get_clusters(numbers=[], separator=", "):
    """Return given p_numbers by clusters.
    When p_numbers=[1,2,3,5,6,8,9,10,15,17,20],
    the result is '1-3, 5-6, 8-10, 15, 17, 20'."""
    clusters = itertools.groupby(numbers, lambda n, c=itertools.count(): n - next(c))
    res = []
    for group, cluster in clusters:
        clust = list(cluster)
        if len(clust) > 1:
            res.append("{0}-{1}".format(clust[0], clust[-1]))
        else:
            res.append("{0}".format(clust[0]))
    return separator.join(res)


def display_offset_number(number, offset):
    """Display a number with an offset. For example when p_number=123 and offset=100, it returns '1.23'"""
    if number % offset == 0:
        return str(int(number / offset))
    return "{}.{}".format(number // offset, number % offset)


def get_ordinal_clusters(
    numbers=[], cluster_format="{0}-{1}", single_cluster_format="{0}", separator=", ", offset=100, as_str=True
):
    """Return given p_numbers by clusters while taking care of the offset (used for sub numering).
    p_offset should be a power of 10, it doesn't make any sense otherwise.
    When p_numbers=[100,200,300,400,500,501,502,521,522,540,550,700,1200,1300] and p_offset=100,
    the result is '1-5.2, 5.21-5.22, 5.40, 5.50, 7, 12-13'."""

    def _is_in_cluster(number, cluster, offset):
        """Check if a number is in a cluster.
        A number is in a cluster if it follows directly the last number according to the offset"""
        if len(cluster) > 0:
            if number % offset == 0:
                return number - cluster[-1] == offset
            return number - cluster[-1] == 1
        return True

    # Initialize the first group
    clusters = []
    if numbers:
        current_cluster = [numbers[0]]
        for num in numbers[1:]:
            if _is_in_cluster(num, current_cluster, offset):
                current_cluster.append(num)
            else:  # we'll start a new cluster
                clusters.append(current_cluster)
                current_cluster = [num]
        clusters.append(current_cluster)  # Add the last one

    if not as_str:
        return clusters

    res = []
    for cluster in clusters:
        if len(cluster) > 1:
            res.append(
                cluster_format.format(
                    display_offset_number(cluster[0], offset), display_offset_number(cluster[-1], offset)
                )
            )
        else:
            res.append(single_cluster_format.format(display_offset_number(cluster[0], offset)))
    return separator.join(res)


def insert_in_ordereddict(dic, value, after_key="", at_position=None):
    """Insert a tuple in an new Ordereddict.

    :param dic: the original OrderedDict
    :param value: a tuple (key, value) that will be added at correct position
    :param after_key: key name after which the tup is added
    :param at_position: position at which the tup is added. Is also a default if after_key is not found
    :return: a new OrderedDict or None if insertion position is undefined
    """
    position = None
    if after_key:
        position = odict_index(dic, after_key, delta=1)
    if position is None and at_position is not None:
        position = at_position
    if position is None:
        return None
    if position >= len(list(dic.keys())):
        return OrderedDict(list(dic.items()) + [value])
    tuples = []
    for i, tup in enumerate(dic.items()):
        if i == position:
            tuples.append(value)
        tuples.append(tup)
    if not tuples:  # dic was empty
        tuples.append(value)
    return OrderedDict(tuples)


def iterable_as_list_of_list(lst, cols=1):
    """Transform an iterable as list of list.

    :param lst: input iterable
    :param cols: number of columns in the sublists
    :return: list of lists
    """
    res = []
    sublist = []
    for i, item in enumerate(lst, start=1):
        sublist.append(item)
        if not i % cols:
            if sublist:
                res.append(sublist)
            sublist = []
    # put the last sublist in res
    if sublist:
        res.append(sublist)
    return res


def letters_sequence(nth, letters="abcdefghijklmnopqrstuvwxyz"):
    """Return a letters sequence corresponding to the nth number. Useful to generate a lettered suffix.

    :param nth: nth sequence (0 giving nothing and 1 the first letter)
    :param letters: letters to consider
    :return: a sequenced string
    """
    res = ""
    for pos in radix_like_starting_1(nth, len(letters)):
        res += letters[pos - 1]
    return res


def merge_dicts(dicts, as_dict=True):
    """Merge dicts, extending values of each dicts,
       useful for example when the value is a list.

    :param dicts: the list of dicts to mergeinput iterable
    :param as_dict: return a dict instead the defaultdict instance
    :return: a single dict (or defaultdict)
    """
    dd = defaultdict(list)

    # iterate dictionary items
    dict_items = list(map(methodcaller("items"), dicts))
    for k, v in chain.from_iterable(dict_items):
        dd[k].extend(v)
    return as_dict and dict(dd) or dd


def odict_index(odic, key, delta=0):
    """Get key position in an ordereddict"""
    for i, k in enumerate(odic):
        if k == key:
            return i + delta
    return None


def odict_pos_key(odic, pos):
    """Get key corresponding at position"""
    keys = [k for k in odic]
    if pos < 0 or pos >= len(keys):
        return None
    else:
        return keys[pos]


def one_of_dict_values(dic, keys):
    """Take the first value not empty in a dict following given keys"""
    for key in keys:
        if dic.get(key):
            return dic[key]
    return None


def radix_like_starting_1(n, base, L=[]):  # noqa
    """Returns a list of positional numbers following a given base but starting with 1 and not 0.
    It's like normal base positions but ignoring 0. Useful for non mathematical sequence (a b aa ab ba bb ...)

    :param n: the number to analyze
    :param base: the base to use
    :param L: the working list (mist not be originally filled)
    :return: a list of positional numbers
    """
    if n <= 0:
        L.reverse()
        return L
    else:
        return radix_like_starting_1((n % base) and (n // base) or (n // base) - 1, base, L + [(n % base) or base])


def replace_in_list(lst, value, replacement, generator=False):
    """Replace a value in a list of values.

    :param lst: the list containing value to replace
    :param value: the value to be replaced
    :param replacement: the new value to replace with
    :param generator: will return a generator instead a list when set to True
    :return: a new list/generator with replaced values
    """

    def _replacer(lst, value, replacement):
        new_lst = list(lst)
        for item in new_lst:
            if item == value:
                yield replacement
            else:
                yield item

    res = _replacer(lst, value, replacement)
    if not generator:
        res = list(res)
    return res


def safe_encode(value, encoding="utf-8"):
    """Converts a value to encoding, only when it is not already encoded."""
    try:
        return ensure_str(value, encoding=encoding)
    except TypeError:
        return value


def setup_logger(logger, replace=logging.StreamHandler, level=20):
    """Modify logger handler level

    :param logger: logger to modify
    :param replace: handler type to replace
    :param level: level to set
    """
    for i_c, container in enumerate((logger, logger.parent)):
        found = [i for i, hdl in enumerate(container.handlers) if isinstance(hdl, logging.StreamHandler)]
        if found:
            if i_c:
                logger.parent = container = copy.copy(logger.parent)
            break
    else:
        return
    idx = found[0]
    osh = copy.copy(container.handlers[idx])
    osh.setLevel(level)
    # remove handler from original container handlers (often parent)
    container.handlers = [hdl for i, hdl in enumerate(container.handlers) if i != idx]
    # put handler in logger handlers
    logger.handlers.append(osh)
    logger.setLevel(level)


def sort_by_indexes(lst, indexes, reverse=False):
    """Sort a list following a second list containing the order"""
    return [val for (_, val) in sorted(zip(indexes, lst), key=lambda x: x[0], reverse=reverse)]


def timed(f, nb=100):  # TODO must be removed and replaced by timeit
    start = time.time()
    for i in range(nb):
        ret = f()
    return (time.time() - start) / nb, ret  # difference of time is float


def time_elapsed(start, cond=True, msg=u"", dec=3, min=0.0):
    """Print elapsed time from start.

    :param start: start time gotten from time_start function
    :param cond: print condition
    :param msg: message to include in print
    :param dec: decimal precision (default to 3)
    :param min: minimal elapsed value print

    Usage:
    from imio.pyutils.utils import time_elapsed, time_start
    start = time_start()
    ...
    time_elapsed(start, cond=obj.id=='myid', msg=u'myfunc')
    """
    if not cond:
        return
    elapsed = timeit.default_timer() - start
    if elapsed < min:
        return
    print((u"* {{}}: {{:.{}f}} seconds".format(dec).format(msg, elapsed)))


def time_start():
    """To be used with time_elapsed."""
    return timeit.default_timer()


def listify(value, force=False):
    """Ensure given value is a list-like iterable.

    :param value: the value to turn into a list if not already the case
    :param force: if value is a tuple, returned as a list
    """
    if isinstance(value, string_types):
        value = [value]
    if force and not isinstance(value, list):
        value = list(value)
    return value
