text = """<select name="LookingBodyType">
<option value="0" selected="">I prefer not to say</option>
<option value="1">Average</option>
<option value="2">Ample</option>
<option value="3">Athletic</option>
<option value="4">Attractive</option>
<option value="5">Slim</option>
<option value="6">Very Cuddly</option>
</select>"""
"""text = re.findall('>.*<', text)
text = list(map(lambda x: x.replace('<', ''), text))
text = list(map(lambda x: x.replace('>', ''), text))

test = [i for i in range(100000, 0, -1)]

"""


def heaplify(array, n, i):
    largest = i
    left_child = i * 2 + 1
    right_child = i * 2 + 2

    if left_child < n and array[largest] < array[left_child]:
        largest = left_child

    if right_child < n and array[largest] < array[right_child]:
        largest = right_child

    if largest != i:
        array[largest], array[i] = array[i], array[largest]
        heaplify(array, n, largest)


"""

for i in range(len(test) // 2, -1, -1):
    heaplify(test, len(test), i)
for i in range(len(test) - 1, 0, -1):
    test[i], test[0] = test[0], test[i]  # свап
    heaplify(test, i, 0)"""
"""print(test)
"""
"""def heap(array, n, i):
    largest = i
    left_child = i*2 + 1
    right_child = i*2 + 2

    if left_child<n and array[largest] < array[left_child]:
        largest = left_child

    if right_child<n and array[largest] < array[right_child]:
        largest = right_child

    if largest != i:
        array[largest], array[i] = array[i], array[largest]
        array = heap(array, n, largest)
    return array
print(test)
for i in range(len(test)):
    test = test[:i] + heap(test[i:], len(test[i:]), 0)
    print(test)
    print(i)"""
