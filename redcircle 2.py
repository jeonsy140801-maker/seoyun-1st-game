import pygame
import random as r

pygame.init()

pygame.init()
background = pygame.display.set_mode((600, 500))
pygame.display.set_caption("First Pygame!")

player_x = 240
player_y = 180
to_x = 0
to_y = 0

arrows = [
    {"x": r.randint(0, 600), "y": 0, "dir_x": 0, "dir_y": 1},  # 위쪽에서 아래로
    {"x": r.randint(0, 600), "y": 500, "dir_x": 0, "dir_y": -1},  # 아래에서 위로
    {"x": 0, "y": r.randint(0, 500), "dir_x": 1, "dir_y": 0},  # 왼쪽에서 오른쪽으로
    {"x": 600, "y": r.randint(0, 500), "dir_x": -1, "dir_y": 0},  # 오른쪽에서 왼쪽으로
    {"x": r. randint(0,600), "y": 500, "dir_x": 1,"dir_y":-1},
    {"x": r. randint(0,600), "y": 0, "dir_x": 1,"dir_y":1},
    {"x": 600, "y": r.randint(0, 500), "dir_x": -1, "dir_y": -1},
    {"x": 600, "y": r.randint(0, 500), "dir_x": -1, "dir_y": 1},
]
폰트 = pygame.font.Font(None, 24)  # 기본 폰트, 크기 36

play = True
fps = pygame.time.Clock()
score = 0
while play:
    score += 0.1

    for event in pygame.event.get():
        if event.type ==pygame.QUIT:
            play=False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                to_y = -0.5
            elif event.key == pygame.K_DOWN:
                to_y = 0.5
            elif event.key == pygame.K_LEFT:
                to_x = -0.5
            elif event.key == pygame.K_RIGHT:
                to_x = 0.5
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                to_y = 0
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                to_x = 0

    player_x += to_x
    player_y += to_y

    background.fill((0, 0, 0))

    pygame.draw.circle(background, (255,255,255), (player_x, player_y), 10)
    색들 = [(255,0,0), (0,255,0), (0,0,255), (255,255,0)]
    색=0
    for arrow in arrows:
        색+=1
        arrow["x"]+=arrow["dir_x"] *0.5
        arrow["y"]+=arrow["dir_y"] *0.5

        if arrow["x"]<0 or arrow["x"]>600 or arrow["y"]<0 or arrow["y"]>500: 
            if arrow["dir_x"] !=0:
                if arrow ["dir_x"] >0:
                    arrow["x"]=0
                else:
                    arrow["x"] =600

                arrow["y"] = r.randint(0, 500)
            if arrow["dir_y"] !=0:
                if arrow ["dir_y"] >0:
                    arrow["y"]=0
 
                else:
                    arrow["y"] = 500
                arrow["x"]=r.randint(0, 600)

        pygame.draw.circle(background, 색들[색 % 4], (arrow["x"], arrow["y"]), 10)

        distance = ((player_x - arrow["x"]) ** 2 + (player_y - arrow["y"]) ** 2) ** 0.5
        if distance < 20:
            play = False
    점수 = 폰트.render(f"score:{score:.2f}", True, (255, 255, 255))  # 검정색 텍스트
    background.blit(점수, (30, 30))  # (50, 50) 위치에 텍스트 표시

    pygame.display.update()
    fps.tick(100)

pygame.quit()  


