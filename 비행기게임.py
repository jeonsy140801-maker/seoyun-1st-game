import pygame

import random



pygame.init()



화면_크기 = (800, 600)

화면 = pygame.display.set_mode(화면_크기)

pygame.display.set_caption("슈팅 게임")

폰트 = pygame.font.Font(None, 100)

배경_색 = (0, 0, 0)

전투기 = pygame.image.load("전투기.png")

전투기 = pygame.transform.scale(전투기, (110, 110))

미사일 = pygame.image.load("미사일.png")

미사일 = pygame.transform.scale(미사일, (40, 80))

적_이미지 = pygame.image.load("적.png")

적_이미지 = pygame.transform.scale(적_이미지, (80, 80))

적_이미지 = pygame.transform.flip(적_이미지, False, True)

탄환_사운드 = pygame.mixer.Sound("발사음.mp3")

pygame.mixer.music.load("bgm.mp3")  

pygame.mixer.music.play(-1) 

class 비행기:

    def __init__(self, x, y, hp=3):

        self.x = x

        self.y = y

        self.속도 = 5

        self.최대 = 10

        self.최소 = 1

        self.hp = hp

        self.게임오버 = False

        self.점수 = 0 



    def hp_감소(self):

        if self.hp > 0:

            self.hp -= 1

        if self.hp <= 0:

            self.게임오버 = True



    def 이동(self, 키):

        if 키[pygame.K_LEFT] and self.x > 0:

            self.x -= self.속도

        if 키[pygame.K_RIGHT] and self.x < 760:

            self.x += self.속도

        if 키[pygame.K_UP] and self.y > 0:

            self.y -= self.속도

        if 키[pygame.K_DOWN] and self.y < 560:

            self.y += self.속도



    def 속도조절(self, 키):

        if 키[pygame.K_w] and self.속도 < self.최대:

            self.속도 += 1

        if 키[pygame.K_s] and self.속도 > self.최소:

            self.속도 -= 1



    def 그리기(self, 화면):

         화면.blit(전투기, (self.x, self.y))

        





class 탄환:

    def __init__(self, x, y):

        self.x = x + 15

        self.y = y

        self.속도 = 7

        self.활성화 = True



    def 이동(self):

        if self.활성화:

            self.y -= self.속도

            if self.y < 0:

                self.활성화 = False



    def 그리기(self, 화면):

        화면.blit(미사일, (self.x, self.y))

class 적:

    def __init__(self, x, y):

        self.x = x

        self.y = y

        self.속도 = 2

        self.크기 = 30



    def 이동(self):

        self.y += self.속도

        if self.y > 600:

            self.y = 0

            self.x = random.randint(0, 770)



    def 그리기(self, 화면):

          화면.blit(적_이미지, (self.x, self.y))

    def 충돌(self, 탄환_객체, 플레이어):

        if (탄환_객체.활성화

                and self.x < 탄환_객체.x < self.x + self.크기

                and self.y < 탄환_객체.y < self.y + self.크기):

            탄환_객체.활성화 = False

            플레이어.점수 += 10  

            return True

        return False





플레이어 = 비행기(370, 500)

탄환_목록 = []

적_목록 = [적(random.randint(0, 770), random.randint(0, 200)) for _ in range(5)]



fps = pygame.time.Clock()

실행중 = True



while 실행중:

    화면.fill(배경_색)



    for 이벤트 in pygame.event.get():

        if 이벤트.type == pygame.QUIT:

            실행중 = False

        elif 이벤트.type == pygame.KEYDOWN:

            if 이벤트.key == pygame.K_SPACE:

                탄환_목록.append(탄환(플레이어.x, 플레이어.y))

                탄환_사운드.play()

    키 = pygame.key.get_pressed()

    플레이어.이동(키)

    플레이어.그리기(화면)



    for 탄 in 탄환_목록[:]:

        탄.이동()

        if not 탄.활성화:

            탄환_목록.remove(탄)

        else:

            탄.그리기(화면)



    for 적_객체 in 적_목록[:]:

        적_객체.이동()

        적_객체.그리기(화면)



        for 탄 in 탄환_목록[:]:

            if 적_객체.충돌(탄, 플레이어):

                적_목록.remove(적_객체)

                탄환_목록.remove(탄)

                break

        if(플레이어.x < 적_객체.x <플레이어.x + 40 and 플레이어.y - 30 < 적_객체.y <플레이어.y +30):

            플레이어.hp_감소()

            적_목록.remove(적_객체)

        if 플레이어.게임오버:

            화면.fill((0,0,0))

            텍스트 = 폰트.render("game_over!", True, (250, 0, 0))  

            화면.blit(텍스트, (100, 100)) 

    if len(적_목록) == 0:

        for _ in range(5):

            적_목록.append(적(random.randint(0, 770), random.randint(0, 200)))



  

    텍스트 = 폰트.render(str(플레이어.점수), True, (250, 0, 0))  

    화면.blit(텍스트, (100, 100))

    pygame.display.update()

    fps.tick(60)



pygame.quit()