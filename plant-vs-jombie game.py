import pygame
import sys
import math
import random

# =====================================================
# Pygame 아이소메트릭 좀비 vs 식물 — 업그레이드 적용판
# 적용: 4) 식물 업그레이드, 5) 좀비 탄환 패턴, 6) 소비형 아이템,
#      7) 탄환-타일/호두 상호작용, 10) 히트 피드백
# 조작:
#  - 좌측 패널에서 카드 선택 후 보드 클릭으로 배치
#  - 좌측 패널 하단 "삽"으로 제거, "타일 편집"은 테스트용
#  - 식물 업그레이드: 보드의 식물을 '우클릭'하면 좌측 패널에 옵션 두 개가 뜸 → 클릭해 구매(60)
#  - 소비형 아이템: 좌측 패널에서 "모래주머니" 또는 "냉기 폭탄" 선택 후 보드 클릭
#    * 모래주머니: 해당 칸 20초간 원거리 피해 30% 경감(식물에 적용)
#    * 냉기 폭탄: 클릭한 '행' 전체의 좀비를 2.5초 빙결
#  - 승리: 각 스테이지 120초 후 보스 등장, 보스 처치 시 다음 스테이지. Stage 3 보스 처치 시 SUCCESS!
# =====================================================

WIDTH, HEIGHT = 1000, 700
FPS = 60

GRID_COLS, GRID_ROWS = 7, 5
TILE_W, TILE_H = 120, 60
SHOP_W = 380
BOARD_W = WIDTH - SHOP_W
ORIGIN_X = SHOP_W + BOARD_W // 2
ORIGIN_Y = 150

STAGE_MAX = 3
STAGE_TIME_LIMIT = 120.0

# 경제/가격
MONEY_START_BASE = 200
BASE_INCOME_RATE = 2.8
BASE_INCOME_AMOUNT = 30

COST_PEA = 50
COST_SUN = 50
COST_WALL = 70
COST_ICE = 70

# 업그레이드/아이템 비용 & 지속
UPGRADE_COST = 60
ITEM_SANDBAG_COST = 60   # 타일 원거리 피해 30% 경감 (20초)
ITEM_FREEZE_COST = 80    # 선택 행 2.5초 빙결
SANDBAG_TIME = 20.0
FREEZE_TIME = 2.5

# 색상
WHITE=(255,255,255); BLACK=(0,0,0); YELLOW=(241,196,15)
GREEN=(46,204,113); DARK_GREEN=(30,140,80); ICE_BLUE=(150,210,255)
RED=(231,76,60); LIGHT_GRAY=(170,170,170)
GRASS_A=(34,100,46); MUD=(70,55,40); ROAD=(90,90,95)
ICE=(120,170,220); SPIKE=(120,120,150); FERTILE=(60,120,60)
Z_BASIC=(150,110,170); Z_RUNNER=(110,170,210); Z_TANK=(190,120,90); Z_BOSS=(230,60,80)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Isometric - Upgrade Pack")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("malgungothic", 18)
SMALL = pygame.font.SysFont("malgungothic", 14)
XSMALL = pygame.font.SysFont("malgungothic", 12)
BIG = pygame.font.SysFont("malgungothic", 30, bold=True)
HUGE = pygame.font.SysFont("malgungothic", 40, bold=True)

# --------------------- 유틸 ---------------------

def draw_text(surf, text, pos, color=WHITE, center=False, font=FONT):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surf.blit(img, rect)

def draw_wrapped_text(surf, text, pos, max_width, color=WHITE, font=FONT, line_gap=2):
    """한글 잘림 방지: 글자 단위로 줄바꿈"""
    lines=[]; cur=""
    for ch in str(text):
        if ch=='\n':
            lines.append(cur); cur=""; continue
        if font.size(cur+ch)[0] <= max_width:
            cur+=ch
        else:
            lines.append(cur); cur=ch
    if cur: lines.append(cur)
    x,y=pos
    for ln in lines:
        img=font.render(ln, True, color)
        surf.blit(img,(x,y))
        y += img.get_height()+line_gap

def iso_pos(c, r):
    x = ORIGIN_X + (c - r) * (TILE_W//2)
    y = ORIGIN_Y + (c + r) * (TILE_H//2)
    return x, y

def point_in_diamond(px, py, cx, cy):
    dx = abs(px - cx) / (TILE_W/2); dy = abs(py - cy) / (TILE_H/2)
    return (dx + dy) <= 1.0

def mouse_to_grid(mx, my):
    best=None; best_d=1e9
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cx, cy = iso_pos(c, r)
            if point_in_diamond(mx, my, cx, cy):
                d=(mx-cx)**2+(my-cy)**2
                if d<best_d: best=(c,r); best_d=d
    return best

# --------------------- 타일 ---------------------
TILE_TYPES=['grass','road','mud','spike','ice','fertile']

def draw_tile(surf, cx, cy, ttype, sandbag=False):
    hw, hh=TILE_W//2, TILE_H//2
    pts=[(cx,cy-hh),(cx+hw,cy),(cx,cy+hh),(cx-hw,cy)]
    base_color={
        'grass':GRASS_A,'road':ROAD,'mud':MUD,'spike':SPIKE,'ice':ICE,'fertile':FERTILE
    }[ttype]
    pygame.draw.polygon(surf, base_color, pts)
    tex=pygame.Surface((TILE_W,TILE_H), pygame.SRCALPHA)
    if ttype=='grass':
        for i in range(0,TILE_W+TILE_H,10): pygame.draw.line(tex,(255,255,255,22),(i,0),(0,i),1)
    elif ttype=='road':
        bw,bh=18,8
        for y in range(0,TILE_H,bh):
            offset=(y//bh)%2*(bw//2)
            for x in range(-offset,TILE_W,bw): pygame.draw.rect(tex,(220,220,220,35),(x,y,bw-2,bh-2))
    elif ttype=='mud':
        for i in range(0,TILE_W,14): pygame.draw.arc(tex,(255,230,200,30),(i-20,TILE_H//4,40,20),0,math.pi,2)
    elif ttype=='spike':
        for x in range(6,TILE_W,16): pygame.draw.polygon(tex,(240,240,240,40),[(x,TILE_H//2+10),(x+6,TILE_H//2-2),(x+12,TILE_H//2+10)])
    elif ttype=='ice':
        for i in range(0,TILE_W,16):
            pygame.draw.line(tex,(255,255,255,50),(i,0),(i+8,TILE_H),1)
            pygame.draw.line(tex,(255,255,255,50),(i-8,0),(i,TILE_H),1)
    elif ttype=='fertile':
        for y in range(6,TILE_H,12):
            for x in range(6,TILE_W,12): tex.set_at((x,y),(255,255,255,40))
    surf.blit(tex,(cx-hw,cy-hh), special_flags=pygame.BLEND_PREMULTIPLIED)
    pygame.draw.polygon(surf, BLACK, pts, 1)
    if sandbag:
        overlay=pygame.Surface((TILE_W,TILE_H), pygame.SRCALPHA)
        pygame.draw.polygon(overlay,(210,180,80,90),[(TILE_W//2,TILE_H//2+8),(TILE_W//2+20,TILE_H//2+2),(TILE_W//2,TILE_H//2-6),(TILE_W//2-20,TILE_H//2+2)])
        surf.blit(overlay,(cx-hw,cy-hh))

# --------------------- 파티클 ---------------------
class Particle:
    def __init__(self,x,y,color=(255,255,255),life=0.25):
        self.x=x; self.y=y; self.color=color; self.life=life; self.t=0
        self.vx=random.uniform(-60,60); self.vy=random.uniform(-40,20)
    def step(self,dt):
        self.t+=dt; self.x+=self.vx*dt; self.y+=self.vy*dt; self.vy+=120*dt
    def draw(self,surf):
        if self.t>self.life: return
        k=1-(self.t/self.life)
        pygame.draw.circle(surf,self.color,(int(self.x),int(self.y)),max(1,int(3*k)))

# --------------------- 식물 ---------------------
class PlantBase:
    def __init__(self):
        self.flash=0.0
        self.ranged_resist=1.0  # 원거리 피해 계수(호두/모래주머니 영향)
        self.upgraded=False
        self.upg_name=None
    def on_hit(self,amount):
        self.flash=0.12

class Peashooter(PlantBase):
    def __init__(self,c,r,color=GREEN,fire_rate=1.0):
        super().__init__()
        self.c=c; self.r=r; self.color=color
        self.hp=120; self.max_hp=120
        self.fire_rate=fire_rate; self.timer=0
        self.x,self.y=iso_pos(c,r); self.y-=10
        # 업글
        self.rapid=False
        self.pierce_ap=0  # 방어력 무시량
    def step(self,dt):
        self.timer+=dt; self.flash=max(0.0,self.flash-dt)
    def can_fire(self): return self.timer>=self.fire_rate
    def reset(self): self.timer=0
    def draw(self,surf):
        s=pygame.Surface((TILE_W,TILE_H),pygame.SRCALPHA)
        pygame.draw.ellipse(s,(0,0,0,70),(TILE_W//2-18,TILE_H//2-8,36,16))
        surf.blit(s,(self.x-TILE_W//2,self.y-TILE_H//2+18))
        body=pygame.Rect(0,0,28,32); body.center=(self.x,self.y-6)
        pygame.draw.rect(surf,self.color,body,border_radius=6)
        if self.flash>0: pygame.draw.rect(surf,(255,255,255),body,2,border_radius=6)
        k=max(0,self.hp/self.max_hp); bw=40
        pygame.draw.rect(surf,BLACK,(self.x-bw//2,self.y-28,bw,6),border_radius=3)
        pygame.draw.rect(surf,DARK_GREEN,(self.x-bw//2,self.y-28,int(bw*k),6),border_radius=3)

class IcePeashooter(Peashooter):
    def __init__(self,c,r,fertile=False):
        rate=1.2*(0.9 if fertile else 1.0)
        super().__init__(c,r,color=ICE_BLUE,fire_rate=rate)
        self.slow_plus=False   # 슬로우 지속 +1s
        self.row_slow=False    # 같은 행 인접도 슬로우

class Wallnut(PlantBase):
    def __init__(self,c,r,hp_bonus=0):
        super().__init__()
        self.c=c; self.r=r
        self.hp=420+hp_bonus; self.max_hp=420+hp_bonus
        self.x,self.y=iso_pos(c,r); self.y-=8
        self.ranged_resist=0.7   # (요청7) 원거리 피해 30% 경감
    def step(self,dt): self.flash=max(0.0,self.flash-dt)
    def draw(self,surf):
        s=pygame.Surface((TILE_W,TILE_H),pygame.SRCALPHA)
        pygame.draw.ellipse(s,(0,0,0,80),(TILE_W//2-22,TILE_H//2-6,44,14))
        surf.blit(s,(self.x-TILE_W//2,self.y-TILE_H//2+18))
        body=pygame.Rect(0,0,40,46); body.center=(self.x,self.y-2)
        pygame.draw.rect(surf,(181,101,29),body,border_radius=12)
        if self.flash>0: pygame.draw.rect(surf,(255,255,255),body,2,border_radius=12)
        k=max(0,self.hp/self.max_hp); bw=50
        pygame.draw.rect(surf,BLACK,(self.x-bw//2,self.y-34,bw,6),border_radius=3)
        pygame.draw.rect(surf,(120,200,120),(self.x-bw//2,self.y-34,int(bw*k),6),border_radius=3)

class Sunflower(PlantBase):
    def __init__(self,c,r,fertile=False):
        super().__init__()
        self.c=c; self.r=r
        self.hp=100; self.max_hp=100
        self.x,self.y=iso_pos(c,r); self.y-=10
        self.timer=0; self.rate=5.0; self.amount=25+(10 if fertile else 0)
        self.rate_boost=False; self.amount_boost=False
    def step(self,dt): self.timer+=dt; self.flash=max(0.0,self.flash-dt)
    def can_generate(self): return self.timer>=self.rate
    def reset(self): self.timer=0
    def draw(self,surf):
        s=pygame.Surface((TILE_W,TILE_H),pygame.SRCALPHA)
        pygame.draw.ellipse(s,(0,0,0,70),(TILE_W//2-18,TILE_H//2-8,36,16))
        surf.blit(s,(self.x-TILE_W//2,self.y-TILE_H//2+18))
        pygame.draw.circle(surf,(240,180,30),(int(self.x),int(self.y-6)),16)
        for i in range(8):
            ang=i*math.pi/4; px=int(self.x+22*math.cos(ang)); py=int(self.y-6+22*math.sin(ang))
            pygame.draw.circle(surf,(216,140,20),(px,py),6)
        pygame.draw.rect(surf,(80,160,80),(self.x-6,self.y+2,12,18),border_radius=4)
        if self.flash>0: pygame.draw.circle(surf,(255,255,255),(int(self.x),int(self.y-6)),18,2)
        k=max(0,self.hp/self.max_hp); bw=40
        pygame.draw.rect(surf,BLACK,(self.x-bw//2,self.y-28,bw,6),border_radius=3)
        pygame.draw.rect(surf,(120,200,120),(self.x-bw//2,self.y-28,int(bw*k),6),border_radius=3)

# --------------------- 발사체 ---------------------
class Pea:
    def __init__(self,c,r,dmg=30,color=GREEN,slow=False,ap=0,pierce_count=0):
        self.c=c; self.r=r
        self.speed=3.1
        self.x,self.y=iso_pos(c,r); self.y-=8
        self.radius=6; self.alive=True
        self.dmg=dmg; self.color=color; self.slow=slow
        self.ap=ap                  # 방어력 무시
        self.pierce_count=pierce_count  # 관통 가능 횟수(좀비 기준)
    def step(self,dt):
        self.c+=self.speed*dt
        self.x,self.y=iso_pos(self.c,self.r); self.y-=8
        if self.c>GRID_COLS+1: self.alive=False
    def draw(self,surf):
        pygame.draw.ellipse(surf,(0,0,0,80),(self.x-8,self.y+10,16,6))
        pygame.draw.circle(surf,self.color,(int(self.x),int(self.y)),self.radius)

class ZBullet:
    def __init__(self,c,r,dmg=8,speed=3.4,pierce=False):
        self.c=c; self.r=r
        self.dmg=dmg; self.speed=speed; self.pierce=pierce
        self.x,self.y=iso_pos(c,r); self.y-=6
        self.alive=True
    def step(self,dt):
        self.c-=self.speed*dt
        self.x,self.y=iso_pos(self.c,self.r); self.y-=6
        if self.c<-1.2: self.alive=False
    def draw(self,surf):
        pygame.draw.ellipse(surf,(0,0,0,70),(self.x-6,self.y+8,12,6))
        pygame.draw.circle(surf,(255,200,80),(int(self.x),int(self.y)),5)

# --------------------- 좀비 ---------------------
class Zombie:
    def __init__(self,r,base_speed,hp,dps,color,scale=1.0,armor=0,is_boss=False):
        self.r=r; self.c=GRID_COLS+0.8
        self.base_speed_init=base_speed; self.base_speed=base_speed; self.speed=base_speed
        self.x,self.y=iso_pos(self.c,r); self.y-=6
        self.hp=hp; self.max_hp=hp; self.dps=dps
        self.color=color; self.scale=scale; self.armor=armor
        self.is_boss=is_boss
        self.atk_cd=0; self.alive=True; self.escaped=False
        self.slow_timer=0; self.slow_factor=0.5; self.frozen_timer=0
        # 사격
        self.fire_cd=random.uniform(0.6,1.2)
        self.fire_rate=2.8 if not is_boss else 1.6
        self.bullet_dmg=7 if not is_boss else 12
        self.double_shot=False
        self.spread_shot=is_boss   # 보스 확산탄
        # 보스 패턴
        self.boss_shield=False; self._shield_cd=0.0; self._shield_time=0.0
        self._summon_cd=0.0; self._enraged=False
        self.flash=0.0
    def take_damage(self,raw):
        # AP 적용은 투사체 쪽에서 처리(plant pea)
        dmg=max(1,int(raw - self.armor))
        if self.is_boss and self.boss_shield: dmg=max(1,dmg//2)
        self.hp-=dmg; self.flash=0.12
        return dmg
    def boss_patterns(self,dt,game):
        if not self.is_boss: return
        self._shield_cd-=dt
        if self._shield_cd<=0:
            self.boss_shield=True; self._shield_time=2.0; self._shield_cd=6.0
        if self.boss_shield:
            self._shield_time-=dt
            if self._shield_time<=0: self.boss_shield=False
        self._summon_cd-=dt
        if self._summon_cd<=0:
            self._summon_cd=8.0
            lane=random.randrange(GRID_ROWS)
            bs,hp,dps,col,sc,armor=stage_params(game.stage)['runner']
            game.zombies.append(Zombie(lane,bs,hp,dps,col,sc,armor))
        if not self._enraged and self.hp<=self.max_hp*0.5:
            self._enraged=True; self.base_speed_init*=1.2; self.base_speed=self.base_speed_init; self.dps+=2
    def step(self,dt,game=None):
        if game is not None: self.boss_patterns(dt,game)
        self.flash=max(0.0,self.flash-dt)
        if self.frozen_timer>0:
            self.frozen_timer-=dt; self.speed=0
        elif self.slow_timer>0:
            self.slow_timer-=dt; self.speed=self.base_speed*self.slow_factor
        else:
            self.speed=self.base_speed
        self.atk_cd=max(0,self.atk_cd-dt)
        self.fire_cd=max(0,self.fire_cd-dt)
        self.c-=self.speed*dt
        self.x,self.y=iso_pos(self.c,self.r); self.y-=6
        if self.c<-0.5: self.escaped=True; self.alive=False
    def draw(self,surf):
        pygame.draw.ellipse(surf,(0,0,0,90),(self.x-22*self.scale,self.y+12,44*self.scale,10))
        body=pygame.Rect(0,0,int(34*self.scale),int(42*self.scale)); body.center=(self.x,self.y-4)
        col=(min(255,int(self.color[0]+90*self.flash)),min(255,int(self.color[1]+90*self.flash)),min(255,int(self.color[2]+90*self.flash)))
        pygame.draw.rect(surf,col,body,border_radius=8)
        if self.is_boss and self.boss_shield: pygame.draw.rect(surf,(255,255,255),body,3,border_radius=8)
        k=max(0,self.hp/self.max_hp); bw=int(50*self.scale)
        pygame.draw.rect(surf,BLACK,(self.x-bw//2,self.y-34*self.scale,bw,6),border_radius=3)
        pygame.draw.rect(surf,RED,(self.x-bw//2,self.y-34*self.scale,int(bw*k),6),border_radius=3)

# --------------------- 파라미터 ---------------------

def stage_params(stage):
    if stage == 1:
        return {
            'basic': (0.5, 80, 7,  Z_BASIC, 1.0, 0),
            'runner':(0.9, 65, 7,  Z_RUNNER,0.95,0),
            'tank':  (0.38,150, 9, Z_TANK, 1.2, 2),
            'boss':  (0.5, 380,11, Z_BOSS, 1.6, 3)
        }
    if stage == 2:
        return {
            'basic': (0.55,95, 8,  Z_BASIC, 1.0, 0),
            'runner':(1.0, 75, 8,  Z_RUNNER,1.0, 0),
            'tank':  (0.42,180,10, Z_TANK, 1.25,3),
            'boss':  (0.55,480,12, Z_BOSS, 1.65,4)
        }
    return {
        'basic': (0.6, 110,9,  Z_BASIC, 1.05,0),
        'runner':(1.1, 85, 9,  Z_RUNNER,1.05,0),
        'tank':  (0.46,210,11, Z_TANK, 1.3, 4),
        'boss':  (0.58,560,13, Z_BOSS, 1.7, 5)
    }

STAGE_BG={1:(25,80,25),2:(15,40,80),3:(60,35,20)}

def make_stage_tiles(stage):
    return [[('grass') for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

# --------------------- 게임 ---------------------
class Game:
    def __init__(self):
        self.stage=1; self.success_all=False
        self.reset(full_reset=True)
    def reset(self,full_reset=False):
        self.board=[[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
        self.tiles=[[('grass') for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
        self.tile_buffs={}  # {(c,r): {'sand':time}}
        self.plants=[]; self.projectiles=[]; self.zombies=[]; self.z_bullets=[]; self.particles=[]
        self.money=MONEY_START_BASE+(self.stage-1)*25
        self.income_timer=0; self.elapsed=0; self.spawn_timer=2.0
        self.spawn_rate=6.0-(self.stage-1)*0.5; self.min_spawn=4.0-(self.stage-1)*0.3
        self.game_over=False; self.victory=False
        self.selected=None; self.shovel_mode=False; self.tile_edit=False
        self.item_mode=None  # 'sand' or 'freeze'
        self.upgrade_target=None
        self.boss_spawned=False; self.stop_regular_spawn=False
        if full_reset: self.success_all=False
    # --- 배치/제거/업그레이드 ---
    def place(self,c,r,plant):
        if 0<=c<GRID_COLS and 0<=r<GRID_ROWS and self.board[c][r] is None:
            self.board[c][r]=plant; self.plants.append(plant); return True
        return False
    def remove(self,c,r):
        p=self.board[c][r]
        if p:
            self.board[c][r]=None
            if p in self.plants: self.plants.remove(p)
    def try_upgrade(self,p,opt):
        if getattr(p,'upgraded',False): return False
        if self.money < UPGRADE_COST: return False
        # 각 식물별 두 가지 옵션
        if isinstance(p,Peashooter):
            if opt==1:
                p.rapid=True; p.fire_rate*=0.9; p.upg_name='연사+'
            else:
                p.pierce_ap=2; p.upg_name='관통(AP2)'
        elif isinstance(p,IcePeashooter):
            if opt==1:
                p.slow_plus=True; p.upg_name='슬로우+1s'
            else:
                p.row_slow=True; p.upg_name='행 광역 둔화'
        elif isinstance(p,Sunflower):
            if opt==1:
                p.amount+=10; p.amount_boost=True; p.upg_name='수확+10'
            else:
                p.rate=max(1.5,p.rate-1.0); p.rate_boost=True; p.upg_name='주기-1s'
        elif isinstance(p,Wallnut):
            if opt==1:
                p.ranged_resist=0.6; p.upg_name='철갑(원거리-40%)'
            else:
                p.hp+=120; p.max_hp+=120; p.upg_name='체력+120'
        else:
            return False
        p.upgraded=True
        self.money-=UPGRADE_COST
        return True
    # --- 타일 효과 ---
    def tile_effect_on_zombie(self,z,dt):
        c_idx=max(0,min(GRID_COLS-1,int(round(z.c))))
        ttype=self.tiles[c_idx][z.r]
        base=z.base_speed_init
        if ttype=='road': z.base_speed=base*1.25
        elif ttype=='mud': z.base_speed=base*0.65
        elif ttype=='spike': z.take_damage(8*dt); z.base_speed=base
        elif ttype=='ice': z.slow_timer=max(z.slow_timer,1.5); z.base_speed=base
        else: z.base_speed=base
    # --- 스폰 ---
    def spawn_regular_zombie(self):
        lane=random.randrange(GRID_ROWS)
        p=stage_params(self.stage)
        kind=random.choices(['basic','runner','tank'],weights=[6,3,2])[0]
        bs,hp,dps,col,sc,armor=p[kind]
        z=Zombie(lane,bs,hp,dps,col,sc,armor)
        # 패턴(요청5)
        if kind=='runner':
            z.fire_rate, z.bullet_dmg = 3.2, 6
        elif kind=='tank':
            z.fire_rate, z.bullet_dmg = 3.0, 9
        else:
            z.fire_rate, z.bullet_dmg = 2.8, 7
        self.zombies.append(z)
    def spawn_boss(self):
        if self.boss_spawned: return
        lane=random.randrange(GRID_ROWS)
        bs,hp,dps,col,sc,armor=stage_params(self.stage)['boss']
        z=Zombie(lane,bs,hp,dps,col,sc,armor,is_boss=True)
        z.fire_rate, z.bullet_dmg = 1.5, 12
        self.zombies.append(z)
        self.boss_spawned=True; self.stop_regular_spawn=True
    # --- 좀비 사격 ---
    def zombie_try_shoot(self,z):
        if z.fire_cd>0: return
        row_plants=[p for p in self.plants if p.r==z.r and hasattr(p,'hp')]
        if not row_plants: return
        left_plants=[p for p in row_plants if p.c <= z.c - 0.2]
        if not left_plants: return
        # 패턴: 보스 확산탄, 러너 3연발, 탱커 관통탄
        if z.spread_shot:
            self.z_bullets.append(ZBullet(z.c-0.35, z.r, dmg=z.bullet_dmg))
            if z.r-1>=0: self.z_bullets.append(ZBullet(z.c-0.35, z.r-1, dmg=z.bullet_dmg))
            if z.r+1<GRID_ROWS: self.z_bullets.append(ZBullet(z.c-0.35, z.r+1, dmg=z.bullet_dmg))
            z.fire_cd=z.fire_rate; return
        # 러너: 3연발(동일 프레임 3발)
        if z.fire_rate>=3.1:  # 러너 구분용(위에서 설정됨)
            for _ in range(3): self.z_bullets.append(ZBullet(z.c-0.35, z.r, dmg=z.bullet_dmg))
            z.fire_cd=z.fire_rate; return
        # 탱커: 관통탄
        pierce=False
        if z.bullet_dmg>=9: pierce=True
        self.z_bullets.append(ZBullet(z.c-0.35, z.r, dmg=z.bullet_dmg, pierce=pierce))
        z.fire_cd=z.fire_rate
    # --- 아이템 사용 ---
    def use_sandbag(self,c,r):
        self.tile_buffs[(c,r)]={'sand':SANDBAG_TIME}
    def use_freeze(self,row):
        for z in self.zombies:
            if z.r==row: z.frozen_timer=max(z.frozen_timer, FREEZE_TIME)
    # --- 업데이트 ---
    def update(self,dt):
        if self.game_over or self.victory or self.success_all: return
        self.elapsed+=dt
        # 전역 수입
        self.income_timer+=dt
        if self.income_timer>=BASE_INCOME_RATE:
            self.money+=BASE_INCOME_AMOUNT; self.income_timer=0
        # 타일 버프 시간 경과
        for k in list(self.tile_buffs.keys()):
            if 'sand' in self.tile_buffs[k]:
                self.tile_buffs[k]['sand']-=dt
                if self.tile_buffs[k]['sand']<=0: del self.tile_buffs[k]
        # 120초 → 보스
        if self.elapsed>=STAGE_TIME_LIMIT and not self.boss_spawned:
            self.spawn_boss()
        # 식물 로직
        for p in list(self.plants):
            if isinstance(p,Sunflower):
                p.step(dt)
                if p.can_generate(): self.money+=p.amount; p.reset()
            else:
                p.step(dt)
                if isinstance(p,(Peashooter,IcePeashooter)) and p.can_fire():
                    row_has_z=any(z.r==p.r and z.c>p.c for z in self.zombies)
                    if row_has_z:
                        ap=p.pierce_ap if isinstance(p,Peashooter) else 0
                        if isinstance(p,IcePeashooter):
                            pea=Pea(p.c+0.4,p.r,dmg=28,color=ICE_BLUE,slow=True,ap=ap)
                        else:
                            pea=Pea(p.c+0.4,p.r,ap=ap)
                        self.projectiles.append(pea); p.reset()
        # 플레이어 탄환
        for pea in list(self.projectiles):
            pea.step(dt)
            if not pea.alive: self.projectiles.remove(pea)
        # 스폰
        if not self.stop_regular_spawn:
            self.spawn_timer+=dt
            if self.spawn_timer>=self.spawn_rate:
                self.spawn_regular_zombie(); self.spawn_timer=0
                self.spawn_rate=max(self.min_spawn, self.spawn_rate-0.10)
        # 좀비 이동/공격/사격 + 타일 효과
        escaped=False
        for z in list(self.zombies):
            self.tile_effect_on_zombie(z,dt)
            c_idx=round(z.c); target=None
            if 0<=c_idx<GRID_COLS: target=self.board[c_idx][z.r]
            if target and abs(z.c-c_idx)<0.25:
                if z.atk_cd<=0:
                    if hasattr(target,'hp'): target.hp-=z.dps; target.on_hit(z.dps)
                    z.atk_cd=0.5
                if not isinstance(target,Wallnut): z.base_speed=z.base_speed_init*0
                if hasattr(target,'hp') and target.hp<=0:
                    self.remove(c_idx,z.r); z.base_speed=z.base_speed_init
            self.zombie_try_shoot(z)
            z.step(dt,game=self)
            if z.escaped: escaped=True
            if not z.alive or z.hp<=0:
                if z in self.zombies: self.zombies.remove(z)
        # 완두 ↔ 좀비 충돌 (관통/AP/슬로우)
        for pea in list(self.projectiles):
            for z in list(self.zombies):
                if z.r==pea.r and abs(z.c-pea.c)<0.25:
                    # AP 적용
                    dmg=max(1,int(pea.dmg - max(0,z.armor - pea.ap)))
                    if z.is_boss and z.boss_shield: dmg=max(1,dmg//2)
                    z.hp-=dmg; z.flash=0.12
                    if pea.slow:
                        # 슬로우 효과 적용 (IcePeashooter의 slow_plus 업그레이드 고려)
                        c_idx = max(0, min(GRID_COLS-1, int(pea.c)))
                        shooter = self.board[c_idx][z.r]
                        base_slow = 2.5
                        if isinstance(shooter, IcePeashooter) and shooter.slow_plus:
                            base_slow += 1.0
                        z.slow_timer = max(z.slow_timer, base_slow)
                        # row_slow 업그레이드: 같은 행의 인접 좀비도 둔화
                        if isinstance(shooter, IcePeashooter) and shooter.row_slow:
                            for zz in self.zombies:
                                if zz.r == z.r and zz != z and abs(zz.c - z.c) <= 1.5:
                                    zz.slow_timer = max(zz.slow_timer, base_slow * 0.7)
                    pea.pierce_count-=1
                    if pea.pierce_count<0 and pea in self.projectiles:
                        self.projectiles.remove(pea)
                    break
        # 좀비 탄환 ↔ 식물 충돌 (모래주머니/호두/타일 보정)
        for b in list(self.z_bullets):
            b.step(dt)
            hit=False
            # 충돌 체크
            for p in list(self.plants):
                if p.r==b.r and abs(p.c-b.c)<0.25:
                    # 해당 칸 버프/타일 적용
                    c_idx=max(0,min(GRID_COLS-1,int(round(p.c))))
                    ttype=self.tiles[c_idx][p.r]
                    # 기본 피해
                    eff=b.dmg
                    # 타일 상호작용(요청7)
                    if ttype=='spike': eff=max(1, eff-2)
                    elif ttype=='ice': eff=max(1, eff-1)
                    # 모래주머니 버프
                    if (c_idx,p.r) in self.tile_buffs and 'sand' in self.tile_buffs[(c_idx,p.r)]:
                        eff=int(eff*0.7)
                    # 호두/식물의 원거리 저항
                    eff=int(eff * getattr(p,'ranged_resist',1.0))
                    # 피해 적용
                    if hasattr(p,'hp'):
                        p.hp-=eff; p.on_hit(eff)
                        # 파티클(요청10)
                        for _ in range(3): self.particles.append(Particle(p.x,p.y-8,(255,255,255),0.2))
                    hit=True
                    # 관통탄(탱커)
                    if not b.pierce: break
            if hit and not b.pierce:
                if b in self.z_bullets: self.z_bullets.remove(b)
            if not hit and not b.alive:
                if b in self.z_bullets: self.z_bullets.remove(b)
        # 파티클 업데이트
        for pr in list(self.particles):
            pr.step(dt)
            if pr.t>pr.life and pr in self.particles: self.particles.remove(pr)
        # 패배/클리어
        if escaped: self.game_over=True
        if self.boss_spawned and len(self.zombies)==0:
            if self.stage<STAGE_MAX: self.stage+=1; self.victory=True
            else: self.success_all=True
    # --- 그리기 ---
    def draw(self,surf):
        surf.fill(STAGE_BG.get(self.stage,(20,90,20)))
        # 좌패널
        pygame.draw.rect(surf,(25,25,25),(0,0,SHOP_W,HEIGHT))
        draw_wrapped_text(surf,f"Stage {self.stage}/{STAGE_MAX}",(12,10),SHOP_W-24,WHITE,SMALL)
        draw_wrapped_text(surf,f"Time: {int(self.elapsed)}/{int(STAGE_TIME_LIMIT)}s",(12,32),SHOP_W-24,YELLOW,SMALL)
        draw_wrapped_text(surf,f"돈: {self.money}",(12,54),SHOP_W-24,YELLOW,SMALL)
        draw_wrapped_text(surf,"우클릭으로 업그레이드 대상 선택",(12,78),SHOP_W-24,LIGHT_GRAY,SMALL)
        # 카드 버튼
        y=100; h=56; pad=8
        self.btns={}
        def btn(key,label,y):
            rect=pygame.Rect(12,y,SHOP_W-24,h)
            pygame.draw.rect(surf,(70,70,90),rect,border_radius=10)
            pygame.draw.rect(surf,WHITE,rect,2,border_radius=10)
            draw_wrapped_text(surf,label,(rect.x+12,rect.y+8),rect.width-24,WHITE,SMALL)
            self.btns[key]=rect
        btn('pea', f"완두사수 ({COST_PEA})", y); y+=h+pad
        btn('ice', f"냉동완두 ({COST_ICE})", y); y+=h+pad
        btn('sun', f"해바라기 ({COST_SUN})", y); y+=h+pad
        btn('wall',f"호두 ({COST_WALL})", y); y+=h+pad
        # 아이템
        y+=4
        draw_wrapped_text(surf,"아이템",(12,y),SHOP_W-24,WHITE,SMALL); y+=22
        btn('item_sand', f"모래주머니 ({ITEM_SANDBAG_COST})", y); y+=h+pad
        btn('item_freeze', f"냉기 폭탄 ({ITEM_FREEZE_COST})", y); y+=h+pad
        # 업그레이드 패널
        y+=4
        draw_wrapped_text(surf,"업그레이드(우클릭으로 대상 선택)",(12,y),SHOP_W-24,WHITE,SMALL); y+=22
        # 대상 표시
        if self.upgrade_target is not None:
            nm = type(self.upgrade_target).__name__
            draw_wrapped_text(surf,f"대상: {nm}",(16,y),SHOP_W-32,WHITE,SMALL); y+=22
            # 두 가지 옵션 버튼
            self.btn_upg1=pygame.Rect(12,y,SHOP_W-24,40); y+=40+6
            self.btn_upg2=pygame.Rect(12,y,SHOP_W-24,40); y+=40
            pygame.draw.rect(surf,(90,100,120),self.btn_upg1,border_radius=8); pygame.draw.rect(surf,WHITE,self.btn_upg1,2,border_radius=8)
            pygame.draw.rect(surf,(90,100,120),self.btn_upg2,border_radius=8); pygame.draw.rect(surf,WHITE,self.btn_upg2,2,border_radius=8)
            if isinstance(self.upgrade_target,Peashooter) and not isinstance(self.upgrade_target,IcePeashooter):
                draw_wrapped_text(surf,f"연사 +10%  ({UPGRADE_COST})",(self.btn_upg1.x+10,self.btn_upg1.y+10),self.btn_upg1.width-20,WHITE,SMALL)
                draw_wrapped_text(surf,f"관통(AP2)  ({UPGRADE_COST})",(self.btn_upg2.x+10,self.btn_upg2.y+10),self.btn_upg2.width-20,WHITE,SMALL)
            elif isinstance(self.upgrade_target,IcePeashooter):
                draw_wrapped_text(surf,f"슬로우 +1s ({UPGRADE_COST})",(self.btn_upg1.x+10,self.btn_upg1.y+10),self.btn_upg1.width-20,WHITE,SMALL)
                draw_wrapped_text(surf,f"행 광역 둔화 ({UPGRADE_COST})",(self.btn_upg2.x+10,self.btn_upg2.y+10),self.btn_upg2.width-20,WHITE,SMALL)
            elif isinstance(self.upgrade_target,Sunflower):
                draw_wrapped_text(surf,f"수확 +10  ({UPGRADE_COST})",(self.btn_upg1.x+10,self.btn_upg1.y+10),self.btn_upg1.width-20,WHITE,SMALL)
                draw_wrapped_text(surf,f"주기 -1s  ({UPGRADE_COST})",(self.btn_upg2.x+10,self.btn_upg2.y+10),self.btn_upg2.width-20,WHITE,SMALL)
            elif isinstance(self.upgrade_target,Wallnut):
                draw_wrapped_text(surf,f"철갑(원거리 -40%) ({UPGRADE_COST})",(self.btn_upg1.x+10,self.btn_upg1.y+10),self.btn_upg1.width-20,WHITE,SMALL)
                draw_wrapped_text(surf,f"체력 +120 ({UPGRADE_COST})",(self.btn_upg2.x+10,self.btn_upg2.y+10),self.btn_upg2.width-20,WHITE,SMALL)
        else:
            self.btn_upg1=self.btn_upg2=None
        # 삽/타일 편집
        self.btn_shv=pygame.Rect(12,HEIGHT-150,SHOP_W-24,48)
        pygame.draw.rect(surf,(90,90,90) if not self.shovel_mode else (130,130,130),self.btn_shv,border_radius=10)
        pygame.draw.rect(surf,WHITE,self.btn_shv,2,border_radius=10)
        draw_wrapped_text(surf,"삽 (제거)",(self.btn_shv.x+12,self.btn_shv.y+10),self.btn_shv.width-24,WHITE,SMALL)
        self.btn_edit=pygame.Rect(12,HEIGHT-92,SHOP_W-24,48)
        pygame.draw.rect(surf,(90,70,90) if not self.tile_edit else (140,110,160),self.btn_edit,border_radius=10)
        pygame.draw.rect(surf,WHITE,self.btn_edit,2,border_radius=10)
        draw_wrapped_text(surf,"타일 편집 (클릭시 순환)",(self.btn_edit.x+12,self.btn_edit.y+10),self.btn_edit.width-24,WHITE,SMALL)
        # 보드(타일)
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                cx,cy=iso_pos(c,r)
                sand=((c,r) in self.tile_buffs and 'sand' in self.tile_buffs[(c,r)])
                draw_tile(surf,cx,cy,self.tiles[c][r],sandbag=sand)
        # 집 벽
        for r in range(GRID_ROWS):
            cx,cy=iso_pos(-1,r); pygame.draw.rect(surf,(150,120,80),(cx-6,cy-40,12,80))
        # 깊이 정렬
        depth=[]
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                p=self.board[c][r]
                if p: depth.append((c+r+0.1,('p',p)))
        for pea in self.projectiles: depth.append((pea.c+pea.r+0.2,('pea',pea)))
        for zb in self.z_bullets: depth.append((zb.c+zb.r+0.21,('zb',zb)))
        for z in self.zombies: depth.append((z.c+z.r+0.3,('z',z)))
        depth.sort(key=lambda x:x[0])
        for _,(typ,obj) in depth: obj.draw(surf)
        # 파티클
        for pr in self.particles: pr.draw(surf)
        # 메시지
        if self.game_over:
            draw_text(surf,"패배! 좀비가 집에 도달",(WIDTH//2,HEIGHT//2-30),RED,center=True,font=HUGE)
            draw_text(surf,"R 키로 재시작",(WIDTH//2,HEIGHT//2+10),WHITE,center=True)
        elif self.victory:
            draw_text(surf,f"Stage {self.stage-1} Clear!",(WIDTH//2,HEIGHT//2-40),YELLOW,center=True,font=HUGE)
            draw_text(surf,"아무 키나 눌러 다음 스테이지",(WIDTH//2,HEIGHT//2+4),WHITE,center=True)
        elif self.success_all:
            draw_text(surf,"SUCCESS! 모든 스테이지 클리어!",(WIDTH//2,HEIGHT//2-40),YELLOW,center=True,font=HUGE)
            draw_text(surf,"축하 팡파르!!!",(WIDTH//2,HEIGHT//2+10),WHITE,center=True,font=BIG)
        elif self.boss_spawned and not self.success_all and not self.victory:
            draw_text(surf,"보스 등장! 처치하면 클리어",(WIDTH//2,32),YELLOW,center=True,font=BIG)
        # 마우스 하이라이트
        mx,my=pygame.mouse.get_pos(); g=mouse_to_grid(mx,my)
        if g and not (self.game_over or self.victory or self.success_all):
            cx,cy=iso_pos(*g)
            s=pygame.Surface((TILE_W,TILE_H),pygame.SRCALPHA)
            pygame.draw.polygon(s,(255,255,255,40),[(TILE_W//2,0),(TILE_W,TILE_H//2),(TILE_W//2,TILE_H),(0,TILE_H//2)])
            surf.blit(s,(cx-TILE_W//2,cy-TILE_H//2))
            draw_text(surf,self.tiles[g[0]][g[1]],(cx,cy-40),color=WHITE,center=True,font=SMALL)
    # --- 입력 ---
    def handle_mouse(self,pos,button=1):
        if self.game_over or self.victory or self.success_all: return
        # 좌패널 버튼
        for k,r in getattr(self,'btns',{}).items():
            if r.collidepoint(pos):
                # 아이템 선택
                if k=='item_sand': self.item_mode='sand'; self.selected=None; self.shovel_mode=False; self.tile_edit=False; return
                if k=='item_freeze': self.item_mode='freeze'; self.selected=None; self.shovel_mode=False; self.tile_edit=False; return
                # 업그레이드 버튼(대상 선택돼 있을 때만)
                if k=='upg1' and self.upgrade_target:
                    self.try_upgrade(self.upgrade_target,1); return
                if k=='upg2' and self.upgrade_target:
                    self.try_upgrade(self.upgrade_target,2); return
                # 카드 선택
                self.selected=k; self.shovel_mode=False; self.tile_edit=False; self.item_mode=None
                return
        # 업그레이드 구체 버튼 처리
        if getattr(self,'btn_upg1',None) and self.btn_upg1.collidepoint(pos) and self.upgrade_target:
            self.try_upgrade(self.upgrade_target,1); return
        if getattr(self,'btn_upg2',None) and self.btn_upg2.collidepoint(pos) and self.upgrade_target:
            self.try_upgrade(self.upgrade_target,2); return
        # 삽/편집
        if self.btn_shv.collidepoint(pos): self.shovel_mode=True; self.selected=None; self.tile_edit=False; self.item_mode=None; return
        if self.btn_edit.collidepoint(pos): self.tile_edit=not self.tile_edit; self.selected=None; self.shovel_mode=False; self.item_mode=None; return
        # 보드 클릭
        g=mouse_to_grid(*pos)
        if not g: return
        c,r=g
        # 우클릭: 업그레이드 대상 선택
        if button==3:
            self.upgrade_target=self.board[c][r]
            return
        # 아이템 처리
        if self.item_mode=='sand':
            if self.money>=ITEM_SANDBAG_COST:
                self.use_sandbag(c,r); self.money-=ITEM_SANDBAG_COST
            self.item_mode=None; return
        if self.item_mode=='freeze':
            if self.money>=ITEM_FREEZE_COST:
                self.use_freeze(r); self.money-=ITEM_FREEZE_COST
            self.item_mode=None; return
        # 타일 편집
        if self.tile_edit:
            now=self.tiles[c][r]; idx=TILE_TYPES.index(now)
            self.tiles[c][r]=TILE_TYPES[(idx+1)%len(TILE_TYPES)]; return
        # 삽 모드
        if self.shovel_mode:
            self.remove(c,r); self.shovel_mode=False; return
        if not self.selected: return
        # 배치
        ttype=self.tiles[c][r]; fertile=(ttype=='fertile')
        cost_map={'pea':COST_PEA,'ice':COST_ICE,'sun':COST_SUN,'wall':COST_WALL}
        if self.selected not in cost_map: return
        if self.money < cost_map[self.selected] or self.board[c][r] is not None: return
        if self.selected=='pea':
            rate=1.0*(0.9 if fertile else 1.0); p=Peashooter(c,r,fire_rate=rate)
        elif self.selected=='ice':
            p=IcePeashooter(c,r,fertile=fertile)
        elif self.selected=='sun':
            p=Sunflower(c,r,fertile=fertile)
        else:
            p=Wallnut(c,r,hp_bonus=(60 if fertile else 0))
        if self.place(c,r,p): self.money-=cost_map[self.selected]
        self.selected=None
    def handle_key(self,key):
        if key==pygame.K_r:
            self.stage=1; self.reset(full_reset=True)
        elif self.victory:
            self.victory=False; self.reset()

# --------------------- 메인 ---------------------

def main():
    game=Game(); running=True
    while running:
        dt=clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.MOUSEBUTTONDOWN:
                game.handle_mouse(event.pos, button=event.button)
            elif event.type==pygame.KEYDOWN:
                game.handle_key(event.key)
        game.update(dt); game.draw(screen); pygame.display.flip()
    pygame.quit(); sys.exit()

if __name__=='__main__':
    main()


   # git add .
   # git commit -m "hello"
   # git push
   #seoyuni