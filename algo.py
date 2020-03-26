""" Algorithms implementation in Python"""


def get_start_element(array, start, _end):
    """ Select start element of array"""
    return array[start]


def get_last_element(array, _start, end):
    """ Select last element of array"""
    return array[end - 1]


def get_middle_element(array, start, end):
    """ Select middle element of array"""
    return array[(start + end)//2]


def quick_sort(array, compare=lambda x, y: x < y, pivot_fn=get_start_element,
               start=0, end=None):
    """ Quick Sort algorithm implementation """
    if end is None:
        end = len(array)
    assert start <= end
    if end - start > 1:
        def equal(lhs, rhs):
            return not (compare(lhs, rhs) or compare(lhs, rhs))
        pivot = pivot_fn(array, start, end)
#        trichotomy
        left = start
        right = end - 1
        while True:
            while compare(array[left], pivot):
                left += 1
            while compare(pivot, array[right]):
                right -= 1
            assert not compare(array[left], pivot)
            assert not compare(pivot, array[right])
            if compare(array[right], array[left]):
                array[left], array[right] = array[right], array[left]
            else:
                break
        assert equal(array[left], pivot)
        assert equal(array[right], pivot)
        i = left + 1
        while i <= right:
            assert equal(array[left], pivot)
            assert not compare(pivot, array[right])
            if compare(array[i], pivot):
                array[left], array[i] = array[i], array[left]
                left += 1
            elif compare(pivot, array[i]):
                array[right], array[i] = array[i], array[right]
                right -= 1
                while compare(pivot, array[right]):
                    right -= 1
            else:
                i += 1
        assert equal(array[left], pivot)
        assert equal(array[right], pivot)
        assert left < right + 1
        quick_sort(array, compare, pivot_fn, start, left)
        quick_sort(array, compare, pivot_fn, right + 1, end)


def test_sort():
    """Test sort algorithms"""
    unsorted_arrays = [
        [4, 3, 6, 5, 2, 8, 9, 5, 3, 7, 6, 3, 5, 8, 1, 7, 5, 9, 4, 5, 8, 9, 3,
         4, 7, 8, 8, 3, 5, 6, 8, 9, 7],
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [8, 7, 6, 5, 4, 3, 2, 1],
        [],
        [5, 5, 5, 5],
        ["one", "two", "three", "four", "five", "six", "seven"]
    ]

    sort_algorithms = [
        quick_sort,
        lambda A, compare=lambda x, y: x < y:
        quick_sort(A, compare, get_last_element),
        lambda A, compare=lambda x, y: x < y:
        quick_sort(A, compare, get_middle_element),
    ]

    for unsorted_array in unsorted_arrays:
        sorted_array = unsorted_array.copy()
        print(sorted_array)
        sort_algorithms[0](sorted_array)
        print(sorted_array)
        reverse_sorted_array = unsorted_array.copy()
        sort_algorithms[0](reverse_sorted_array, lambda x, y: x > y)
        print(reverse_sorted_array)
        print()
        assert reverse_sorted_array == sorted_array[::-1]
        for sort_algorithm in sort_algorithms[1:]:
            sorted_array_alt = unsorted_array.copy()
            sort_algorithm(sorted_array_alt)
            assert sorted_array == sorted_array_alt
            reverse_sorted_array = unsorted_array.copy()
            sort_algorithm(reverse_sorted_array, lambda x, y: x > y)
            assert reverse_sorted_array == sorted_array_alt[::-1]


test_sort()
