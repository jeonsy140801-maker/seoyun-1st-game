class 비행기:
    def __init__(self, speed):
        self.speed = speed
    def 가속(self):
        self.speed += 10   

대한항공=비행기(0)
대한항공.가속()
대한항공.가속()
대한항공.가속()

print(대한항공.speed)

   