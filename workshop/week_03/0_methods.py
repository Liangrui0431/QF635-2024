def method_A():
    print('this is method A')
    method_B()

def method_B():
    print('this is method B')
    method_C()

def method_C():
    print('this is method C')

method_A()