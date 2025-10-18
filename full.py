import pygame
import random

pygame.init()
pygame.mixer.init()

# 화면 설정
화면_크기 = (800, 600)
화면 = pygame.display.set_mode(화면_크기)
pygame.display.set_caption("비행기 슈팅 게임 🚀")

# 색상 설정
배경_색 = (0, 0, 0)

# 이미지 불러오기
비행기_이미지 = pygame.image.load("airplane.png")
비행기_이미지 = pygame.transform.scale(비행기_이미지, (40, 40))

탄환_이미지 = pygame.image.load("bullet.png")
탄환_이미지 = pygame.transform.scale(탄환_이미지, (10, 20))

적_이미지 = pygame.image.load("enemy.png")
적_이미지 = pygame.transform.scale(적_이미지, (30, 30))

# 사운드 추가
배경음악 = pygame.mixer.Sound("wrong-place.mp3")
탄환_사운드 = pygame.mixer.Sound("pistol-shot.mp3")
적_피격_사운드 = pygame.mixer.Sound("explode.mp3")

배경음악.play(-1)  # 배경음악 반복 재생

# 비행기 클래스
class 비행기:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.속도 = 5

    def 이동(self, 키):
        if 키[pygame.K_LEFT] and self.x > 0:
            self.x -= self.속도
        if 키[pygame.K_RIGHT] and self.x < 760:
            self.x += self.속도
        if 키[pygame.K_UP] and self.y > 0:
            self.y -= self.속도
        if 키[pygame.K_DOWN] and self.y < 560:
            self.y += self.속도

    def 그리기(self, 화면):
        화면.blit(비행기_이미지, (self.x, self.y))

# 탄환 클래스
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
        if self.활성화:
            화면.blit(탄환_이미지, (self.x, self.y))

# 적 클래스
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

    def 충돌(self, 탄환_객체):
        if 탄환_객체.활성화 and self.x < 탄환_객체.x < self.x + self.크기 and self.y < 탄환_객체.y < self.y + self.크기:
            탄환_객체.활성화 = False
            적_피격_사운드.play()  # 적이 맞았을 때 효과음
            return True
        return False

# 객체 생성
플레이어 = 비행기(370, 500)
탄환_목록 = []
적_목록 = [적(random.randint(0, 770), random.randint(0, 200)) for _ in range(5)]

# 게임 설정
fps = pygame.time.Clock()

# 게임 루프
실행중 = True
while 실행중:
    화면.fill(배경_색)

    # 이벤트 처리
    for 이벤트 in pygame.event.get():
        if 이벤트.type == pygame.QUIT:
            실행중 = False
        elif 이벤트.type == pygame.KEYDOWN:
            if 이벤트.key == pygame.K_SPACE:
                탄환_목록.append(탄환(플레이어.x, 플레이어.y))
                탄환_사운드.play()  # 탄환 발사 소리

    # 키 입력 처리
    키 = pygame.key.get_pressed()
    플레이어.이동(키)
    플레이어.그리기(화면)

    # 탄환 이동 및 충돌 확인
    for 탄 in 탄환_목록[:]:
        탄.이동()
        탄.그리기(화면)

    # 적 이동 및 충돌 확인
    for 적_객체 in 적_목록[:]:
        적_객체.이동()
        적_객체.그리기(화면)

        for 탄 in 탄환_목록[:]:
            if 적_객체.충돌(탄):
                적_목록.remove(적_객체)
                적_피격_사운드.play()  # 적이 맞았을 때 효과음
                탄환_목록.remove(탄) 
                break  # 한 번 충돌하면 더 이상 확인하지 않음


    # 화면 업데이트
    pygame.display.update()
    fps.tick(60)

pygame.quit()

