""" Algorithms implementation in Python"""


import graphics


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
    """Quick Sort algorithm implementation"""
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


def insertion_sort(array, compare=lambda x, y: x < y):
    """Insertion sort"""
    for top in range(1, len(array)):
        k = top
        while k > 0 and compare(array[k], array[k - 1]):
            array[k], array[k - 1] = array[k - 1], array[k]
            k -= 1


def choice_sort(array, compare=lambda x, y: x < y):
    """Choice sort"""
    for pos in range(0, len(array) - 1):
        for k in range(pos + 1, len(array)):
            if compare(array[k], array[pos]):
                array[k], array[pos] = array[pos], array[k]


def bubble_sort(array, compare=lambda x, y: x < y):
    """Bubble sort"""
    for bypass in range(1, len(array)):
        for k in range(0, len(array) - bypass):
            if compare(array[k + 1], array[k]):
                array[k + 1], array[k] = array[k], array[k + 1]


def counting_sort(array, order=0):
    """Counting sort"""
    frequencies = []
    for k in array:
        if k >= len(frequencies):
            frequencies.extend([0]*(k + 1 - len(frequencies)))
        frequencies[k] += 1
    if order == 0:
        for k, frequency in enumerate(frequencies):
            array[order:order + frequency] = [k]*frequency
            order += frequency
    else:
        for k, frequency in enumerate(frequencies):
            array[order:order - frequency:-1] = [k]*frequency
            order -= frequency


def check_sorted(array, compare=lambda x, y: x < y):
    """Check if array is sorted"""
    for i in range(len(array) - 1):
        if compare(array[i + 1], array[i]):
            return False
    return True


def test_check_sorted():
    """ Test check_sorted() function """
    unsorted_arrays = [
        [1, 2, 3, 4, 3],
        [1, 0, 2],
        [10, 9],
        [10, 10, 9],
        [10, 9, 9],
        ["one", "two", "three", "four", "five", "six", "seven"]
    ]
    sorted_arrays = [
        [1, 2, 3, 4, 5],
        [1, 1, 2],
        [1, 2, 2],
        [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        [1, 2, 3, 10, 10, 10, 10, 10, 20, 30, 30],
        [1000],
        [],
        ["five", "four", "one", "seven", "six", "three", "two"],
        ["a", "aa", "aa", "ab", "b"]
    ]
    for unsorted_array in unsorted_arrays:
        print(unsorted_array, "is", "sorted" if check_sorted(unsorted_array)
              else "unsorted")
        assert not check_sorted(unsorted_array)
    for sorted_array in sorted_arrays:
        print(sorted_array, "is", "sorted" if check_sorted(sorted_array)
              else "unsorted")
        assert check_sorted(sorted_array)


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
        insertion_sort,
        choice_sort,
        bubble_sort,
    ]

    int_sort_algorithms = [
        counting_sort
    ]

    for unsorted_array in unsorted_arrays:
        sorted_array = unsorted_array.copy()
        print("Unsorted:         ", unsorted_array)
        sort_algorithms[0](sorted_array)
        print("Sorted ascending: ", sorted_array)
        reverse_sorted_array = unsorted_array.copy()
        sort_algorithms[0](reverse_sorted_array, lambda x, y: x > y)
        print("Sorted descending:", reverse_sorted_array)
        print(sort_algorithms[0].__doc__, ":",
              "passed" if check_sorted(sorted_array) else "failed")
        print(sort_algorithms[0].__doc__, "reverse :",
              "passed" if reverse_sorted_array == sorted_array[::-1]
              else "failed")
        assert check_sorted(sorted_array)
        assert reverse_sorted_array == sorted_array[::-1]
        for sort_algorithm in sort_algorithms[1:]:
            sorted_array_alt = unsorted_array.copy()
            sort_algorithm(sorted_array_alt)
            reverse_sorted_array = unsorted_array.copy()
            sort_algorithm(reverse_sorted_array, lambda x, y: x > y)
            label = sort_algorithm.__doc__
            if label is None:
                label = sort_algorithm
            print(label, ":", "passed" if sorted_array == sorted_array_alt
                  else "failed")
            print(label, "reverse :",
                  "passed" if reverse_sorted_array == sorted_array_alt[::-1]
                  else "failed")
            assert sorted_array == sorted_array_alt
            assert reverse_sorted_array == sorted_array_alt[::-1]
        if len(unsorted_array) == 0 or isinstance(unsorted_array[0], int):
            for sort_algorithm in int_sort_algorithms:
                sorted_array_alt = unsorted_array.copy()
                sort_algorithm(sorted_array_alt)
                reverse_sorted_array = unsorted_array.copy()
                sort_algorithm(reverse_sorted_array, -1)
                label = sort_algorithm.__doc__
                if label is None:
                    label = sort_algorithm
                print(label, ":", "passed" if sorted_array == sorted_array_alt
                      else "failed")
                print(label, "reverse :", "passed"
                      if reverse_sorted_array == sorted_array_alt[::-1]
                      else "failed")
                assert sorted_array == sorted_array_alt
                assert reverse_sorted_array == sorted_array_alt[::-1]
        print()


def is_prime_number_brute_force(number):
    """check whether n is prime"""
    for divisor in range(2, number):
        if number % divisor == 0:
            return False
    return number > 1


def eratosthenes_sieve(up_to):
    """ Calculates Eratosthenes sieve"""
    sieve = [True]*(up_to + 1)
    sieve[0] = sieve[1] = False
    for k in range(2, len(sieve)):
        if sieve[k]:
            for i in range(2*k, len(sieve), k):
                sieve[i] = False
    while not sieve[-1]:
        sieve.pop()
    return sieve


def print_eratosthenes_sieve(up_to, width):
    """ Prints prime numbers table using Eratosthenes sieve"""
    sieve = eratosthenes_sieve(up_to)
    column = 0
    field_width = len(str(len(sieve))) + 1
    for k in range(2, len(sieve)):
        if sieve[k]:
            column += 1
            print(k, end=' '*(field_width - len(str(k))) if column % width
                  else '\n')
    if column % width:
        print()


def test_primes():
    """Test prime numbers algorithms"""
    assert eratosthenes_sieve(97) == eratosthenes_sieve(100)
    assert eratosthenes_sieve(100) != eratosthenes_sieve(101)
    print_eratosthenes_sieve(6000, 20)
    sieve = eratosthenes_sieve(1000)
    for number, is_prime in enumerate(sieve):
        assert is_prime_number_brute_force(number) == is_prime


window = graphics.GraphWin("Test", 300, 300)

test_primes()
print()
test_check_sorted()
print()
test_sort()
