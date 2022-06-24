# List comprehension
num_list = [num for num in range(3)]
# [0, 1, 2]

# Dict comprehension
num_dict = {num: str(num) for num in range(3)}
# {0: '0', 1: '1', 2: '2'}

# Set comprehension
num_set = {num for num in range(3)}
# {0, 1, 2}

# Generator comprehension
num_gen = (num for num in range(3))
# <generator object <genexpr> at 0x7f53a372dcf0>
