hash_table = {}
keywords = ["NAME{}".format(i) for i in range(1000)]
for key in keywords:
    hash_table[hash(key)] = key

for key, name in hash_table.items():
    print("{0}: {1}".format(key, name))