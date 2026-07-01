import pygame as pg


SCREEN_width = 800
SCREEN_height = 600

screen = pg.display.set_mode((SCREEN_width, SCREEN_height))

clock = pg.time.Clock()

# Sprites
Player = pg.Rect((100, 450, 25, 50))
ground = pg.Rect((0, 500, SCREEN_width, 100))
platform = pg.Rect((300, 430, 100, 70))

# Functions

#Variables
Player_Speed = 3
Player_Xvel = 0
Player_Jump_Height = 6
Player_Yvel = 0
Gravity_Force = 0.2
On_Ground = True
Platforms = [platform]
Push_Direction = -Player_Speed
Movement_Direction = Player_Speed
Player_Bottom = Player.bottom
Collide_Tolerance = 15


run = True
while run:
    screen.fill((0, 0, 0))

    Player_Bottom = Player.bottom

    Player_Xvel = Movement_Direction    
    Player_Yvel += Gravity_Force
    
    Player.y += Player_Yvel
    Player.x += Player_Xvel
    
    #Ground collision
    if Player.colliderect(ground):
        On_Ground = True
        Player_Speed = 3
        Player.bottom = ground.top
        Player_Yvel = 0
    else:
        On_Ground = False
        
    #Platform collision
    
    #Vertical collision
    for objects in Platforms:
        if Player.colliderect(objects) and Player_Yvel > 0 and Player_Bottom <= objects.top + Collide_Tolerance and On_Ground == False:
            On_Ground = True
            Player_Speed = 3
            Player.bottom = objects.top
            Player_Yvel = 0
        
        
    pg.draw.rect(screen, (0, 255, 0), ground)
    pg.draw.rect(screen, (0, 0, 255), platform)
    pg.draw.rect(screen, (255, 0, 0), Player)
    
    # Player Movement
    key = pg.key.get_pressed()
    
    for objects in Platforms:
        if Player.colliderect(objects) and Player_Xvel <= 0:
            Player.left = objects.right
        if Player.colliderect(objects) and Player_Xvel >= 0:
            Player.right = objects.left
    
    Movement_Direction = 0
    if key[pg.K_a] == True:
        Movement_Direction = -Player_Speed
    if key[pg.K_d] == True:
        Movement_Direction = Player_Speed
    if key[pg.K_SPACE] and On_Ground == True:
        Player_Yvel += -Player_Jump_Height
        On_Ground = False
    if key[pg.K_LSHIFT] == True or key[pg.K_RSHIFT] == True:
        Player_Speed = 5
    else:
        Player_Speed = 3
    
    
    Player.clamp_ip(screen.get_rect())
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
    pg.display.update()
    clock.tick(60)
pg.quit()
