import pygame

pygame.init()

# 화면 설정
화면_크기 = (800, 600)
화면 = pygame.display.set_mode(화면_크기)
pygame.display.set_caption("매끄럽게 움직이기")

# 색상 설정
배경_색 = (240, 248, 255)
도형_색 = (255, 0, 0)

# 도형 초기 위치
x, y = 400, 300

# 키 상태 변수
움직이는_상태 = {"UP": False, "DOWN": False, "LEFT": False, "RIGHT": False}
도형_크기=50
# 게임 루프
실행중 = True
while 실행중:
    for 이벤트 in pygame.event.get():
        if 이벤트.type == pygame.QUIT:
            실행중 = False
        elif 이벤트.type == pygame.KEYDOWN:
            if 이벤트.key == pygame.K_a:
                도형_크기-=5
            if 이벤트.key == pygame.K_s:
                도형_크기+=5
            if 이벤트.key == pygame.K_UP:
                움직이는_상태["UP"] = True
            elif 이벤트.key == pygame.K_DOWN:
                움직이는_상태["DOWN"] = True
            elif 이벤트.key == pygame.K_LEFT:
                움직이는_상태["LEFT"] = True
            elif 이벤트.key == pygame.K_RIGHT:
                움직이는_상태["RIGHT"] = True
        elif 이벤트.type == pygame.KEYUP:
            if 이벤트.key == pygame.K_UP:
                움직이는_상태["UP"] = False
            elif 이벤트.key == pygame.K_DOWN:
                움직이는_상태["DOWN"] = False
            elif 이벤트.key == pygame.K_LEFT:
                움직이는_상태["LEFT"] = False
            elif 이벤트.key == pygame.K_RIGHT:
                움직이는_상태["RIGHT"] = False
           


    # 도형 움직임
    if 움직이는_상태["UP"]:
        y -= 0.5
    if 움직이는_상태["DOWN"]:
        y += 0.5
    if 움직이는_상태["LEFT"]:
        x -= 0.5
    if 움직이는_상태["RIGHT"]:
        x += 0.5
    if y < 0:
        y=600
    if y>600:
        y=0
    if x<0:
        x=800
    if x>800:
        x=0        
        
    # 화면 업데이트
    화면.fill(배경_색)
    pygame.draw.rect(화면, 도형_색, (x, y, 도형_크기, 도형_크기))
    pygame.display.update()

pygame.quit()