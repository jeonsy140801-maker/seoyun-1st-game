class 비행기:
    def __init__(self, high):
        self.high = high
    def 이륙(self):
        self.high += 10
    def 착륙(self):
        self.high -= 10

대한항공=비행기(0)
대한항공.이륙()
대한항공.이륙()
대한항공.착륙()

print(대한항공.high)
