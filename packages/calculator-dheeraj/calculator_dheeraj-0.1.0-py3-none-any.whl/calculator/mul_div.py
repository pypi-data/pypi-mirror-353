def mul(a,b):
    return a*b
def div(a,b):
    try:
        return a/b
    except Exception as e:
        return e
    

# from .add_sub import add,sub
from . import add_sub

print(add_sub.add(2, 3))
print(add_sub.sub(5, 1))