import pygame



pygame.init()



# 화면 설정

화면_크기 = (800, 600)

화면 = pygame.display.set_mode(화면_크기)

pygame.display.set_caption("튕기는 원")



# 배경 색

배경_색 = (240, 248, 255)



# 원 초기 위치 및 속도

x, y = 화면_크기[0] // 2, 화면_크기[1] // 2

반지름 = 50

속도 = 1



# 게임 루프

실행중 = True

while 실행중:

    for 이벤트 in pygame.event.get():

        if 이벤트.type == pygame.QUIT:  # X 버튼으로 창 닫기

            실행중 = False



    # 배경 초기화

    화면.fill(배경_색)



    # 원 이동

    y += 속도



    if y < 0 or y > 600:  # 위/아래 벽에 닿으면 방향 변경

        속도 *= -1



    # 원 그리기

    pygame.draw.circle(화면, (255, 0, 0), (x, y), 반지름)

    pygame.display.update()



pygame.quit()
