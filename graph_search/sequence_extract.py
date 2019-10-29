my_sorted_list = [0,2,5,7,8,9]
my_sequences = []
for idx,item in enumerate(my_sorted_list):
    if not idx or item-1 != my_sequences[-1][-1]:
        my_sequences.append([item])
    else:
        my_sequences[-1].append(item)

print(my_sequences)