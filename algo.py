def get_start_element(A, start, end):
    return A[start]

def get_last_element(A, start, end):
    return A[end - 1]

def get_middle_element(A, start, end):
    return A[(start + end)//2]

def quick_sort(A, pivot_fn=get_start_element, start=0, end=None):
    if end == None:
        end = len(A)
    assert(start <= end)
    if end - start > 1:
        pivot = pivot_fn(A, start, end)
        left = start
        right = end - 1
        while True:
            while A[left] < pivot:
                left += 1
            while A[right] > pivot:
                right -= 1
            assert(A[left] >= pivot >= A[right])
            if A[left] > A[right]:
                A[left], A[right] = A[right], A[left]
            else:
                break
        assert(A[left] == pivot)
        assert(A[right] == pivot)
        i = left + 1
        while i <= right:
            assert(A[left] == pivot)
            assert(A[right] <= pivot)
            if A[i] < pivot:
                A[left], A[i] = A[i], A[left]
                left += 1
            elif A[i] > pivot:
                A[right], A[i] = A[i], A[right]
                right -= 1
                while A[right] > pivot:
                    right -= 1
            else:
                i += 1
        assert(A[left] == pivot)
        assert(A[right] == pivot)
        assert(left < right + 1)
        quick_sort(A, pivot_fn, start, left)
        quick_sort(A, pivot_fn, right + 1, end)

def test_sort():
    
    unsorted_arrays = [
        [4,3,6,5,2,8,9,5,3,7,6,3,5,8,1,7,5,9,4,5,8,9,3,4,7,8,8,3,5,6,8,9,7],
        [1,2,3,4,5,6,7,8,9],
        [8,7,6,5,4,3,2,1],
        [],
        [5,5,5,5],
        ["one", "two", "three", "four", "five", "six", "seven"]
    ]
    
    sort_algorithms = [
        quick_sort,
        lambda A: quick_sort(A, get_last_element),
        lambda A: quick_sort(A, get_middle_element),
    ]
    
    for A in unsorted_arrays:
        B = A.copy()
        print(B)
        sort_algorithms[0](B)
        print(B)
        for sort_algorithm in sort_algorithms[1:]:
            C = A.copy()
            sort_algorithm(C)
            assert(B == C)

test_sort()
