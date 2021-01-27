
int_var = 10


class Conteiner:
    x: int


print("id={0}, int_var={1}".format(id(int_var), int_var))

cnt = Conteiner
cnt.x = 50
print("id={0}, int_var={1}".format(id(cnt), cnt.x))
print("")

for i in range(5):
    int_var = int_var + 1
    cnt.x = cnt.x + 1
    print("id={0}, int_var={1}".format(id(int_var), int_var))

print("")
print("id={0}, int_var={1}".format(id(int_var), int_var))
print("id={0}, int_var={1}".format(id(cnt), cnt.x))
