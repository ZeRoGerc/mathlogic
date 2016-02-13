def outer():
    def inner():
        print(outer.x)
    return inner


outer.x = 0
f = outer()
print(f)

# print(f)
# print(f)
#
# outer()
# print(f)
#
# outer()
# print(f)
