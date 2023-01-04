from datetime import datetime
def merge(left_items, right_items):
    sorted_items = []

    left_index = 0
    right_index = 0

    while left_index < len(left_items) and right_index < len(right_items):
        if left_items[left_index] <= right_items[right_index]:
            sorted_items.append(left_items[left_index])
            left_index += 1
        else:
            sorted_items.append(right_items[right_index])
            right_index += 1

    sorted_items.extend(left_items[left_index:])
    sorted_items.extend(right_items[right_index:])

    return sorted_items

def merge_sort(items):
    if len(items) <= 1:
        return items

    middle_index = len(items) // 2
    left_items = items[:middle_index]
    right_items = items[middle_index:]

    left_items = merge_sort(left_items)
    right_items = merge_sort(right_items)

    return merge(left_items, right_items)


print(sorted_dates = merge_sort(dates))
datetime.now()
dates = []