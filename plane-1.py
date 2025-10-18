import pygame
import random

pygame.init()

# 화면 설정
화면_크기 = (800, 600)
화면 = pygame.display.set_mode(화면_크기)
pygame.display.set_caption("비행기 슈팅 게임 🚀")

# 색상 설정
배경_색 = (0, 0, 0)

폰트 = pygame.font.Font(None, 24)  # 기본 폰트, 크기 36

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
        pygame.draw.polygon(화면, (0, 255, 0), [(self.x, self.y), (self.x + 20, self.y - 30), (self.x + 40, self.y)])
        


# 탄환 클래스
class 탄환:
    def __init__(self, x, y): # 플레이어의 x,y 좌표를 받음음
        self.x = x + 15  # 비행기 중앙에서 발사
        self.y = y
        self.속도 = 7
        self.활성화 = True  # 바로 활성화된 상태로 생성

    def 이동(self):
        if self.활성화:
            self.y -= self.속도
            if self.y < 0:
                self.활성화 = False

    def 그리기(self, 화면):
        if self.활성화:
            pygame.draw.rect(화면, (255, 0, 0), (self.x, self.y, 5, 10))

# 적 클래스
class 적:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.속도 = 2
        self.크기 = 30

    def 이동(self):
        self.y += self.속도
        if self.y > 600:  # 화면을 벗어나면 다시 위에서 생성
            self.y = 0
            self.x = random.randint(0, 770)

    def 그리기(self, 화면):
        pygame.draw.rect(화면, (255, 255, 0), (self.x, self.y, self.크기, self.크기))

    def 충돌(self, 탄환_객체):
        if 탄환_객체.활성화 and self.x < 탄환_객체.x < self.x + self.크기 and self.y < 탄환_객체.y < self.y + self.크기:
            탄환_객체.활성화 = False  # 탄환도 제거
            return True
        return False




# 객체 생성
플레이어 = 비행기(370, 500)
탄환_목록 = []
적_목록 = []
for i in range(5):
    적_목록.append(적(random.randint(0, 770), random.randint(0, 200)))


# 게임 설정
fps = pygame.time.Clock()
score=0

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
                # 스페이스바를 누를 때마다 새로운 탄환 생성
                탄환_목록.append(탄환(플레이어.x, 플레이어.y))

    # 키 입력 처리
    키 = pygame.key.get_pressed()
    플레이어.이동(키)
    플레이어.그리기(화면)

    # 탄환 이동 및 그리기
    for 탄 in 탄환_목록[:]:  # 리스트 복사본으로 순회
        탄.이동()
        if not 탄.활성화:  # 화면을 벗어나면 삭제, 적을 맞춤춤
            탄환_목록.remove(탄)
        else:
            탄.그리기(화면)

    # 적 이동 및 충돌 확인
    for 적_객체 in 적_목록[:]:
        적_객체.이동()
        적_객체.그리기(화면)

        # 충돌 확인
        for 탄 in 탄환_목록[:]:
            if 적_객체.충돌(탄):
                적_목록.remove(적_객체)
                탄환_목록.remove(탄) 
                score+=10 # 충돌 시 탄환도 삭제
                break  # 한 번 충돌하면 더 이상 확인하지 않음

    if len(적_목록) == 0:
        for i in range(5):
            적_목록.append(적(random.randint(0, 770), random.randint(0, 200)))

       
    점수_텍스트 = 폰트.render(f"score:{score}", True, (255, 255, 255))  # 휜색 텍스트
    화면.blit(점수_텍스트, (30, 30))  # (30, 30) 위치에 텍스트 표시
        


    # 화면 업데이트
    pygame.display.update()
    fps.tick(60)

pygame.quit()
