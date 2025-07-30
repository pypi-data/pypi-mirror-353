def add(a,b):
    return a+b
def sub(a,b):
    return a-b


# if we run this file only then below code will run , if we import this file in other file then this will not run
#run as a script not as a module 
if __name__=="main":
    print(add(100,200))
    print(sub(200-100))

# print(add(100,200))
# print(sub(200,100))