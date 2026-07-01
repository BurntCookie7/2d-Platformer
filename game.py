import pygame as pg


SCREEN_width = 800
SCREEN_height = 600

Level_Width = 1600
Level_Height = 1200

screen = pg.display.set_mode((SCREEN_width, SCREEN_height))

clock = pg.time.Clock()

#Classes
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        

class Ground(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((0, 250, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        
class Hazard(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        
class Checkpoint(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((0, 255, 50))
        self.rect = self.image.get_rect(topleft=(x, y))



#Sprites
Player = pg.Rect((100, 450, 25, 50))
ground = Ground(-1000, 500, Level_Width * 4, Level_Height * 4)
platform1 = Platform(300, 430, 100, 70)
platform2 = Platform(500, 350, 100, 70)
death_plane1 = Hazard(700, 490, 75, 10)
checkpoint1 = Checkpoint(525, 275, 50, 75)

#Groups
All_Platforms = pg.sprite.Group(ground, platform1, platform2, death_plane1, checkpoint1) #Every platform the Player collides with
Solids = pg.sprite.Group(platform1, platform2) #Only the platform that act with walls or side collisions
Hazards = pg.sprite.Group(death_plane1) #Anything that kills the player
Checkpoints = pg.sprite.Group(checkpoint1) #Checkpoints for the player to spawn after death

#Variables
Player_Speed = 3
Player_Xvel = 0
Player_Jump_Height = 6
Player_Yvel = 0
Sprinting = False
Movement_Direction = Player_Speed
Gravity_Force = 0.2
On_Ground = True
Platforms = [platform1, platform2]
Player_Bottom = Player.bottom
Player_Top = Player.top
Collide_Tolerance = 15
Coyote_Timer_Max = 10
Coyote_Timer = 0
Prev_Rect = Player.copy()
Camera_X = 0
Camera_Y = 0
Deadzone_Height = 80
Deadzone_Width = 100
Screen_Player_X = Player.centerx - Camera_X
Screen_Player_Y = Player.centery - Camera_Y
Checkpoint_X = 100
Checkpoint_Y = 450

#Functions
def World_To_Screen(rect, camera_x, camera_y):
    return pg.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)

def Set_Checkpoint(checkpoint):
    global Checkpoint_X, Checkpoint_Y
    Checkpoint_X = checkpoint.rect.x
    Checkpoint_Y = checkpoint.rect.y
    

def Spawn_At_Checkpoint():
    global Checkpoint_X, Checkpoint_Y
    Player.x = Checkpoint_X
    Player.y = Checkpoint_Y
    

run = True
while run:
    screen.fill((0, 200, 255))

    Player_Bottom = Player.bottom
    Player_Top = Player.top
    
    Player_Xvel = Movement_Direction    
    Player_Yvel += Gravity_Force
    
    Player.y += Player_Yvel
    Player.x += Player_Xvel
    
    #Ground collision
    if Player.colliderect(ground):
        On_Ground = True
        Player_Speed = 3
        Player.bottom = ground.rect.top
        Player_Yvel = 0
        
    #Hazard collision
    for hazards in Hazards:
        if Player.colliderect(hazards):
            Spawn_At_Checkpoint()
            
    #Checkpoint collision
    for checkpoints in Checkpoints:
        if Player.colliderect(checkpoints):
            Set_Checkpoint(checkpoints)
            print("checkpoint set")
    
    #Vertical collision
    for objects in Solids:
        if Player.colliderect(objects.rect) and Player_Yvel > 0 and Player_Bottom <= objects.rect.top + Collide_Tolerance:
            On_Ground = True
            Player_Speed = 3
            Player.bottom = objects.rect.top
            Player_Yvel = 0
        if Player.colliderect(objects.rect) and Player_Top > objects.rect.bottom:
            Player.top = objects.rect.bottom
            Player_Yvel = 0
    
    #Player Movement
    key = pg.key.get_pressed()
    
    for objects in Solids:
        if Player.colliderect(objects.rect) and Player_Xvel <= 0 and Player_Bottom >= objects.rect.top:
            Player.left = objects.rect.right
        if Player.colliderect(objects.rect) and Player_Xvel >= 0 and Player_Bottom >= objects.rect.top:
            Player.right = objects.rect.left
    
    Movement_Direction = 0
    if key[pg.K_a] == True:
        Movement_Direction = -Player_Speed
    if key[pg.K_d] == True:
        Movement_Direction = Player_Speed
        
    if On_Ground:
        Coyote_Timer = Coyote_Timer_Max
    else:
        Coyote_Timer -= 1    
    
    if key[pg.K_SPACE] and Coyote_Timer > 0:
        Player_Yvel += -Player_Jump_Height
        On_Ground = False
        Coyote_Timer = 0
        
    if key[pg.K_LSHIFT] == True or key[pg.K_RSHIFT] == True and On_Ground:
        Player_Speed = 5
        Player_Jump_Height = 8
    else:
        if On_Ground:
            Player_Speed = 3
            Player_Jump_Height = 6
            
    if key[pg.K_LCTRL] == True or key[pg.K_RCTRL] and On_Ground == False:
        print(On_Ground)
        Player.x += 2
        
    
    Screen_Player_X = Player.centerx - Camera_X
    Screen_Player_Y = Player.centery - Camera_Y
    
    Left_Bound = SCREEN_width // 2 - Deadzone_Width
    Right_Bound = SCREEN_width // 2 + Deadzone_Width
    Top_Bound = SCREEN_height // 2 - Deadzone_Height
    Bottom_Bound = SCREEN_height // 2 + Deadzone_Height
    
    if Screen_Player_X < Left_Bound:
        Camera_X -= (Left_Bound - Screen_Player_X)
    elif Screen_Player_X > Right_Bound:
        Camera_X += (Screen_Player_X - Right_Bound)
    if Screen_Player_Y < Top_Bound:
        Camera_Y -= (Top_Bound - Screen_Player_Y)
    elif Screen_Player_Y > Bottom_Bound:
        Camera_Y += (Screen_Player_Y - Bottom_Bound)

    
    for objects in All_Platforms:
        screen.blit(objects.image, World_To_Screen(objects.rect, Camera_X, Camera_Y))
    pg.draw.rect(screen, (255, 0, 0), World_To_Screen(Player, Camera_X, Camera_Y))
    
    Player.clamp_ip(pg.Rect(0, 0, Level_Width, Level_Height))
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
    pg.display.update()
    clock.tick(60)
pg.quit()
