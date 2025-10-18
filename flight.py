import pygame

pygame.init()

# 화면 설정
화면 = pygame.display.set_mode((800, 600))
pygame.display.set_caption("이미지 불러오기")

# 이미지 불러오기
비행기_이미지 = pygame.image.load("flight.png")

# 게임 루프
실행중 = True
while 실행중:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            실행중 = False

    # 화면을 하얀색으로 채우기
    화면.fill((255, 255, 255))

    # 이미지 크기 조정 (150 x 100)
    비행기_이미지_조정 = pygame.transform.scale(비행기_이미지, (300, 300))

# 화면에 크기 변경된 이미지 그리기
   

    # 이미지 화면에 그리기
    화면.blit(비행기_이미지_조정, (270, 150))

    pygame.display.update()

pygame.quit()