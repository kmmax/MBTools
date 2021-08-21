hash_table = {}
keywords = ["NAME{}".format(i) for i in range(1000)]
for key in keywords:
    hash_table[hash(key)] = key

for key, name in hash_table.items():
    print("{0}: {1}".format(key, name))

d = {"one": 1, "two": 2}
var1 = d.get("one")
var2 = d.get("tree")
print(var1)
print(var2)
