def quick_sort(A, start=0, end=None):
    if end == None:
        end = len(A)
    assert(start <= end)
    if end - start <= 1:
        return
    pivot = A[start]
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
    quick_sort(A, start, left)
    quick_sort(A, right + 1, end)

A = [4,3,6,5,2,8,9,5,3,7,6,3,5,8,1,7,5,9,4,5,8,9,3,4,7,8,8,3,5,6,8,9,7]
print(A)
quick_sort(A)
print(A)
A = [1,2,3,4,5,6,7,8,9]
print(A)
quick_sort(A)
print(A)
A = [8,7,6,5,4,3,2,1]
print(A)
quick_sort(A)
print(A)
A = [25]
print(A)
quick_sort(A)
print(A)
A = []
print(A)
quick_sort(A)
print(A)
A = [5,5,5,5]
print(A)
quick_sort(A)
print(A)
