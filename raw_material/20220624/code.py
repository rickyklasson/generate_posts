items = ['fox', 'racoon', 'hedgehog']

# Each item in an 'enumerate' object is a tuple
for enumerated_item in enumerate(items):
    print(enumerated_item)
# (0, 'fox')
# (1, 'racoon')
# (2, 'hedgehog')

# Unpacking the 'enumerate' object
for idx, item in enumerate(items):
    print(f'Idx: {idx} -> {item}')
# Idx: 0 -> fox
# Idx: 1 -> racoon
# Idx: 2 -> hedgehog
