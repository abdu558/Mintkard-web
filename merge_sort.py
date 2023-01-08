from datetime import datetime,timedelta
# def merge(left_items, right_items):
#     sorted_items = []

#     left_index = 0
#     right_index = 0

#     while left_index < len(left_items) and right_index < len(right_items):
#         if left_items[left_index] <= right_items[right_index]:
#             sorted_items.append(left_items[left_index])
#             left_index += 1
#         else:
#             sorted_items.append(right_items[right_index])
#             right_index += 1

#     sorted_items.extend(left_items[left_index:])
#     sorted_items.extend(right_items[right_index:])

#     return sorted_items

# def merge_sort(items):
#     if len(items) <= 1:
#         return items

#     middle_index = len(items) // 2
#     left_items = items[:middle_index]
#     right_items = items[middle_index:]

#     left_items = merge_sort(left_items)
#     right_items = merge_sort(right_items)

#     return merge(left_items, right_items)




# datetime.now()
# dates = [datetime.now(),datetime.now(),datetime.now()]
# print(sorted_dates = merge_sort(dates))




# def merge_sort(list: [int]):
#     list_length = len(list)
    
#     if list_length == 1:
#         return list
    
#     mid_point = list_length // 2
    
#     left_half = merge_sort(list[:mid_point])
#     right_half = merge_sort(list[mid_point:])
#     print(left_half,right_half)
#     return merge(left_half, right_half)

# def merge(left, right):
#     output = []
#     i = j = 0
    
#     while (i < len(left) and j < len(right)):
#         if left[i] < right[j]:
#             output.append(left[i])
#             i +=1
#         else:
#             output.append(right[j])
#             j +=1
#     output.extend(left[i:])
#     output.extend(right[j:])
    
#     return output

# one = datetime.now()
# two = datetime.now() - timedelta(1)
# three =  datetime.now() - timedelta(2)
# four = datetime.now() - timedelta(3)
# unsorted_list = [one,three,two,four]
# sorted_list = merge_sort(unsorted_list)
# print(unsorted_list)
# print(sorted_list)

# def merge_sort(list):
#     mid = len(list) //2

#     left = list[:mid]
#     right = list[mid:]
#     if left>1:
#         left = merge_sort(left)
#     if right > 1:
#         right = merge_sort(right)
def merge_sort(dates):
    if len(dates)<=1:
        return dates
    mid = len(dates) //2
    left = dates[:mid]
    right = dates[mid:]
    left = merge_sort(left)
    right = merge_sort(right)
    return merge(left,right,dates)

def merge(left,right,dates):
    i=j=k=0
    while i <len(left) and j < len(right):
        if left[i] < right[j]:
            dates[k] = left[i]
            i+=1
        else:
            dates[k]=right[j]
            j+=1

        k+=1

    while i<len(left):
        dates[k]=left[i]
        i+=1
        k+=1

    while j<len(right):
        dates[k] = right[j]
        j+=1
        k+=1

one = datetime.now()
two = datetime.now() - timedelta(1)
three =  datetime.now() - timedelta(2)
four = datetime.now() - timedelta(3)
unsorted_list = [one,three,two,four]
sorted_list = merge_sort(unsorted_list)
print(unsorted_list)
print(sorted_list)

def merge_sort(dates):
    dates_len = len(dates)
    if dates_len <=1:
        return dates
        
    #divide and conquer
    middle = dates_len //2
    right = merge_sort(dates[middle:])
    left = merge_sort(dates[:middle])
    
    return merge_list(left,right)
    
def merge_list(left,right):
    dates_list = []
    l=r=0#left and right
    while (r <len(right) and l<len(left)):
        if left[l] < right[r]:
            dates_list.append(left[l])
            l = l+1
        else:
            dates_list.append(right[r])
            r = r+1
    dates_list.extend(left[l:])
    dates_list.extend(right[r:])
    return dates_list
