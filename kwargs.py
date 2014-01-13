def f(**args):
    print args

d = {'a':1, 'b':2, 'c':3}
f(**d)
f(a=1,b=2,c=3)
