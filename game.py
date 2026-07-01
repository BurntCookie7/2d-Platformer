import pygame as pg
import sys

pg.init()
pg.font.init()

SCREEN_width = 800
SCREEN_height = 600

Level_Width = 1600
Level_Height = 1200

screen = pg.display.set_mode((SCREEN_width, SCREEN_height), pg.SCALED)
pg.display.set_caption("2d Platformer")
clock = pg.time.Clock()

Button_Font = pg.font.SysFont(None, 48)
Title_Font = pg.font.SysFont(None, 100)


Textures = {}


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

def Load_Texture(name, path):
    if name not in Textures:
        Textures[name] = pg.image.load(path).convert_alpha()
    return Textures[name]

def Toggle_Fullscreen():
    global Fullscreen, screen
    Fullscreen = not Fullscreen
    if Fullscreen:
        screen = pg.display.set_mode((SCREEN_width, SCREEN_height), pg.FULLSCREEN | pg.SCALED)
    else:
        screen = pg.display.set_mode((SCREEN_width, SCREEN_height), pg.SCALED)

#Classes
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture):
        super().__init__()
        self.image = pg.transform.scale(texture, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

class Ground(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture):
        super().__init__()
        self.image = pg.transform.scale(texture, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

class Hazard(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture):
        super().__init__()
        self.image = pg.transform.scale(texture, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

class Checkpoint(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture):
        super().__init__()
        self.image = pg.transform.scale(texture, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

class Menu_Button(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((0, 255, 50))
        self.rect = self.image.get_rect(topleft=(x, y))

#Textures
Grass_Tex = Load_Texture("Grass", "textures/grass.png")
Grass_Side_Tex = Load_Texture("Grass Side", "textures/grass_side.png")
Checkpoint_Tex = Load_Texture("Checkpoint", "textures/checkpoint.png")

#Sprites
Player = pg.Rect((100, 450, 25, 50))
ground = Ground(-1000, 500, Level_Width * 4, Level_Height * 4, Grass_Tex)
platform1 = Platform(300, 430, 100, 70, Grass_Side_Tex)
platform2 = Platform(500, 350, 100, 70, Grass_Side_Tex)
platform3 = Platform(700, 250, 20, 150, Grass_Side_Tex)
platform4 = Platform(430, 135, 100, 70, Grass_Side_Tex)
death_plane1 = Hazard(700, 490, 75, 10, Grass_Tex)
checkpoint1 = Checkpoint(525, 275, 50, 50, Checkpoint_Tex)
Start_Button = Menu_Button(250, 300, 300, 50)
Start_Text = Button_Font.render("Start", True, (255, 255, 255))
Title_Text = Title_Font.render("2d Platformer", True, (255, 255, 255))

#Groups
All_Platforms = pg.sprite.Group(ground, platform1, platform2, platform3, platform4, death_plane1, checkpoint1) #Every platform the Player collides with
Solids = pg.sprite.Group(platform1, platform2, platform3, platform4) #Only the platform that act with walls or side collisions
Hazards = pg.sprite.Group(death_plane1) #Anything that kills the player
Checkpoints = pg.sprite.Group(checkpoint1) #Checkpoints for the player to spawn after death
Menu_Buttons = pg.sprite.Group(Start_Button)

#Variables
Player_Speed = 3
Player_Xvel = 0
Player_Jump_Height = 8
Player_Yvel = 0
Sprinting = False
Movement_Direction = Player_Speed
Gravity_Force = 0.4
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
Touching_Wall = False
Can_Walljump = False
Touching_Wall_Left = False
Touching_Wall_Right = False
Walljump_Push = 0
Walljump_Decay = 0.85
Max_Down_Speed = 5
Max_Up_Speed = 7
Fullscreen = False

menu = True
while menu:
    screen.fill((0, 200, 255))
    
    for buttons in Menu_Buttons:
        screen.blit(buttons.image, World_To_Screen(buttons.rect, Camera_X, Camera_Y))
    screen.blit(Start_Text, (360,310))
    screen.blit(Title_Text, (200, 100))
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if Start_Button.rect.collidepoint(event.pos):
                    menu = False
        if event.type == pg.QUIT:
            menu = False
    pg.display.update()
    clock.tick(60)


run = True
while run:
    screen.fill((0, 200, 255))

    if Touching_Wall == True:
        Gravity_Force = 0.05
    else:
        Gravity_Force = 0.4
    
    Player_Xvel = Movement_Direction + Walljump_Push  
    Walljump_Push *= Walljump_Decay
    if abs(Walljump_Push) < 0.1:
        Walljump_Push = 0
        
    Player_Yvel += Gravity_Force
    if Player_Yvel > Max_Down_Speed:
        Player_Yvel = Max_Down_Speed
    elif Player_Yvel < -Max_Up_Speed:
        Player_Yvel = -Max_Up_Speed
    
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
    
    Player_Bottom = Player.bottom
    Player_Top = Player.top
    
    #Player Movement
    key = pg.key.get_pressed()
    
    Touching_Wall = False
    Can_Walljump = False
    for objects in Solids:
        if Player.colliderect(objects.rect):
            had_vertical_overlap = Player_Bottom > objects.rect.top and Player_Top < objects.rect.bottom
            if had_vertical_overlap:
                if Player_Xvel < 0:
                    Player.left = objects.rect.right
                    Touching_Wall = True
                    Touching_Wall_Right = True
                    Touching_Wall_Left = False
                    if On_Ground == False:
                        Can_Walljump = True
                elif Player_Xvel > 0:
                    Player.right = objects.rect.left
                    Touching_Wall = True
                    Touching_Wall_Right = False
                    Touching_Wall_Left = True
                    if On_Ground == False:
                        Can_Walljump = True
    if Touching_Wall == True:
        Max_Down_Speed = 2
    else:
        Max_Down_Speed = 5
        
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
    elif key[pg.K_SPACE] and Touching_Wall == True:
        if On_Ground == False and Can_Walljump == True:
            if Touching_Wall_Left == True and Touching_Wall_Right == False:
                Player_Yvel += -Player_Jump_Height - 20
                Walljump_Push = -Player_Speed * 2
            if Touching_Wall_Left == False and Touching_Wall_Right == True:
                Player_Yvel += -Player_Jump_Height - 20
                Walljump_Push = Player_Speed * 2
        
        
    if key[pg.K_LSHIFT] == True or key[pg.K_RSHIFT] == True and On_Ground == True:
        Player_Speed = 5
        Player_Jump_Height = 8
    else:
        if On_Ground:
            Player_Speed = 3
            Player_Jump_Height = 8
            
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
    pg.draw.rect(screen, (250, 0, 250), World_To_Screen(Player, Camera_X, Camera_Y))
    
    Player.clamp_ip(pg.Rect(0, 0, Level_Width, Level_Height))
    print(On_Ground)
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            print(event.pos)
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_F11:
                Toggle_Fullscreen()
    pg.display.update()
    clock.tick(60)
pg.quit()
