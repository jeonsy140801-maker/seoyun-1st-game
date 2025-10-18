class 자동차:

    def __init__(self,이름,x,y,속력,연료량):

        self.이름 = 이름 

        self.x = x

        self.y = y

        self.방향 = 0 

        self.속력 = 속력 

        self.연료량 = 연료량

        self.주행거리 = 0

    def 가속(self):

        print("가속합니다!")

        self.연료량 -= 1

        if self.속력 >= 300:

            print("최고속도입니다!")

            return

        self.속력 += 10

        print(f"현재속력:{self.속력}")

    def 감속(self):

        print("감속합니다!")

        self.연료량 -= 1

        if self.속력 <= 0:

            print("정지상태입니다!")

            return

        self.속력 -= 10

        print(f"현재속력:{self.속력}")

    def 핸들링(self,방향):

        print(f"{방향}으로 핸들을 돌립니다!")

        if 방향=="오른쪽":
            self.방향+=1
            if self.방향==4:
                self.방향==0
        
        elif 방향=="왼쪽":
            self.방향-=1
            if self.방향==-1:
                self.방향==3
        
    def 엑셀(self):

        if self.연료량 <= 0:

            print("연료가 없습니다!")

            return

        self.가속()
    

        if self.방향 == 0:

            self.y -= self.속력

        elif self.방향 == 1: 

            self.x += self.속력

        elif self.방향 == 2:

            self.y += self.속력

        elif self.방향 == 3:

            self.x -= self.속력

        print(f"현재위치:({self.x},{self.y})")




    def 브레이크(self):

        if self.연료량<=0:

            print("연료가 없습니다!")

            return

        self.감속()

    

    def 주유(self,돈):

        print(f"{돈}원을 주유합니다!")

        self.연료량 += 돈 // 1500

        if self.연료량 > 100:

            self.연료량 = 100

        ### 돈에 따라서 연료량이 올라가고 내려갑니다!

    def 계기판보기(self):

        print(f"이름:{self.이름}")
        print(f"위치:({self.x},{self.y})")
        print(f"방향:{self.방향}")
        print(f"속력:{self.속력}")
        print(f"연료량:{self.연료량}")
        print(f"주행거리:{self.주행거리}")


        ## 모든 정보를 출력합니다. 
        

c=자동차("car", 0, 0, 0, 100)
c. 주유(30000)
c. 엑셀()
c. 계기판보기()