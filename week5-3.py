class 비행기:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def 위치변경(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

대한항공=비행기(0,0)
대한항공.위치변경(100,200)
print(대한항공.x, 대한항공.y)