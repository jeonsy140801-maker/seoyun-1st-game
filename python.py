import pygame

pygame.init()

# 화면 설정
화면_크기 = (800, 600)
화면 = pygame.display.set_mode(화면_크기)
pygame.display.set_caption("원 안과 원 밖 판별")

# 색상 설정
배경_색 = (255, 255, 255)
원_색 = (0, 0, 255)

# 원 설정
원_반지름 = 30
원_위치 = [400, 300]  # 원의 중심 좌표
원_잡힘=False
# 게임 루프
실행중 = True
while 실행중:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            실행중 = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 마우스와 원 중심 간 거리 계산
            x1,y1 = event.pos
            x2,y2 = 원_위치   
            거리 = ( ((x2 - x1) ** 2) + ((y2 - y1) ** 2) ) ** 0.5
            if 거리<= 원_반지름:
               원_잡힘=True
        elif event.type ==pygame.MOUSEBUTTONUP:
            원_잡힘 =False     
        elif event.type == pygame.MOUSEMOTION and 원_잡힘:
             원_위치[0], 원_위치[1]=event.pos

    # 화면 초기화
    화면.fill(배경_색)
    pygame.draw.circle(화면, 원_색, 원_위치, 원_반지름)
    pygame.display.update()

pygame.quit()