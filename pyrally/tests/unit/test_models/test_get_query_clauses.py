from nose.tools import assert_equal
from pyrally.models import get_query_clauses


def test_generates_query_strings_correctly():

    query_1 = get_query_clauses(['a = 1', 'b = 2', 'c = 3'], ' or ')
    result = get_query_clauses([query_1, 'd = 4'])

    assert_equal(result, '(((a = 1) or (b = 2)) or (c = 3)) and (d = 4)')


def test_full_example():
    clauses = []
    clauses.append(get_query_clauses(
                                        ['Owner.name = alex.couper@test.com',
                                         'Owner.name = bill@twe.com'], ' or '))

    assert_equal(clauses[0],
                '(Owner.name = alex.couper@test.com) or '
                '(Owner.name = bill@twe.com)')

    clauses.append(get_query_clauses(['State = "Defined"',
                                           'State = "In Progress"',
                                           'State = "Completed"',
                                           'State = "Accepted"'], ' or '))

    assert_equal(clauses[1],
                 '(((State = "Defined") or (State = "In Progress")) '
                 'or (State = "Completed")) or (State = "Accepted")')

    clauses.append(get_query_clauses(
                                        ['WorkProduct.FormattedId = "US524"']))
    result = get_query_clauses(clauses)
    assert_equal(result,
                '(((Owner.name = alex.couper@test.com) or '
                '(Owner.name = bill@twe.com)) and ((((State = "Defined") '
                'or (State = "In Progress")) or (State = "Completed")) '
                'or (State = "Accepted"))) and '
                '(WorkProduct.FormattedId = "US524")')


def test_handles_single_clauses():
    result = get_query_clauses(['a = 1'])

    assert_equal(result, 'a = 1')


def test_with_or_simple():
    result = get_query_clauses(['a = 1', 'b = 2'], ' or ')
    assert_equal(result, '(a = 1) or (b = 2)')


def test_with_or_more_complex():
    result = get_query_clauses(['a = 1', 'b = 2', 'c = 3'], ' or ')
    assert_equal(result, '((a = 1) or (b = 2)) or (c = 3)')


def test_with_or_more_complex_2():
    result = get_query_clauses(['a = 1', 'b = 2', 'c = 3'], ' or ')
    result = get_query_clauses([result, 'd = 4'])
    assert_equal(result, '(((a = 1) or (b = 2)) or (c = 3)) and (d = 4)')


def test_long_or_set():
    result = get_query_clauses(['A = "1"',
                              'B = "2"',
                              'C = "3"',
                              'D = "4"'], ' or ')

    assert_equal(result,
                 '(((A = "1") or (B = "2")) or (C = "3")) or (D = "4")')
