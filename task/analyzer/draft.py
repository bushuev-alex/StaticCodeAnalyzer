import re
import os
line = "test"
res = re.match("^[a-z0-9_]*_?[a-z0-9]*$", line)
res2 = re.match("", line)
res3 = re.match("", line)
print(res)
print(res2)
print(res3[0])

"""
a = [1, 2, 3]
b = a.copy()
a.append(4)
print(b)

empty_l = []
empty_l.append(empty_l)

print(empty_l)    # [[...]]
print(empty_l.copy())

print(2 % 4)
"""

a = "class UserAgent"
print(a.find('class',))
print(True and False)


print(os.path.abspath(os.curdir))
