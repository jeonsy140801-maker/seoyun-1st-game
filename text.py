import pygame

pygame.init()

# 화면 설정
화면_크기 = (500, 500)
화면 = pygame.display.set_mode(화면_크기)
pygame.display.set_caption("mouse event")

# 색상 설정
배경_색 = (0,0,0)
x = 250
y = 250

반지름 = 30

pen_down = False

# 게임 루프
실행중 = True
while 실행중:
    for event in pygame.event.get(): # []
        if event.type == pygame.QUIT:
            실행중 = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f"마우스 버튼 눌림: {event.button}, 위치: {event.pos}")  
            if event.button==1:
                pen_down =True
            if event.button == 3:
                화면.fill(배경_색)
        elif event.type == pygame.MOUSEBUTTONUP:
            print(f"마우스 버튼 뗌: {event.button}, 위치: {event.pos}")
            pen_down =False
        elif event.type == pygame.MOUSEMOTION:
            print(f"마우스 이동: {event.pos}")
            if pen_down:
                x = event.pos[0]
                y = event.pos[1]
                pygame.draw.circle(화면,(255,255,255),(x,y),반지름)
                
        elif event.type == pygame.MOUSEWHEEL:
            print(f"마우스 휠: {event.y}")
            if event.y == 1 and 반지름 <=100:
                반지름 +=1 
            if event.y == -1 and 반지름 >=5:
                반지름 -=1    
    

    
    pygame.display.update()

pygame.quit()