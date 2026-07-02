import pygame as pg
import sys, os


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
        
def Load_Level(path):
    with open(path, "r") as file:
        lines = file.readlines()
    return [line.rstrip("\n") for line in lines]

def Grid_To_Pixels(col, row):
    return col * Tile_Size, row * Tile_Size

def Resource_Path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path
    

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
Grass_Tex = Load_Texture("Grass", Resource_Path("textures/grass.png"))
Grass_Side_Tex = Load_Texture("Grass Side", Resource_Path("textures/grass_side.png"))
Checkpoint_Tex = Load_Texture("Checkpoint", Resource_Path("textures/checkpoint.png"))
Dirt_Tex = Load_Texture("Dirt", Resource_Path("textures/dirt.png"))
Spike_Tex = Load_Texture("Spike", Resource_Path("textures/spike.png"))

Tile_Size = 25
Level_Layout = Load_Level(Resource_Path("levels/level1.txt"))

Tile_Legend = {
    "G": "Ground",
    "P": "Platform",
    "H": "Hazard",
    "C": "Checkpoint",
    
}

#Sprites
Player = pg.Rect((100, 450, 25, 50))

Tile_Class = {
    "G": Ground,
    "P": Platform,
    "H": Hazard,
    "C": Checkpoint,
    "D": Platform,
}

Tile_Texture = {
    "G": Grass_Tex,
    "P": Grass_Side_Tex,
    "H": Spike_Tex,
    "C": Checkpoint_Tex,
    "D": Dirt_Tex,
}

#Groups
All_Platforms = pg.sprite.Group()
Solids = pg.sprite.Group()
Landable = pg.sprite.Group()
Hazards = pg.sprite.Group()
Checkpoints = pg.sprite.Group()
ground = None

for row_index, row in enumerate(Level_Layout):
    for col_index, symbol in enumerate(row):
        if symbol == ".":
            continue
        obj_class = Tile_Class[symbol]
        texture = Tile_Texture[symbol]
        x, y = Grid_To_Pixels(col_index, row_index)
        obj = obj_class(x, y, Tile_Size, Tile_Size, texture)
        
        All_Platforms.add(obj)
        if symbol == "P":
            Solids.add(obj)
            Landable.add(obj)
        elif symbol == "H":
            Hazards.add(obj)
        elif symbol == "C":
            Checkpoints.add(obj)
        elif symbol == "G":
            Solids.add(obj)
            Landable.add(obj)
            if ground is None:
                ground = obj
        elif symbol == "D":
            Solids.add(obj)
        

#Variables
Player_Speed = 3
Player_Xvel = 0
Player_Jump_Height = 8
Player_Yvel = 0
Sprinting = False
Movement_Direction = Player_Speed
Gravity_Force = 0.4
On_Ground = True
Player_Bottom = Player.bottom
Player_Top = Player.top
Collide_Tolerance = 15
Coyote_Timer_Max = 10
Coyote_Timer = 0
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

    #Hazard collision
    for hazards in Hazards:
        if Player.colliderect(hazards):
            Spawn_At_Checkpoint()
            
    #Checkpoint collision
    for checkpoints in Checkpoints:
        if Player.colliderect(checkpoints):
            Set_Checkpoint(checkpoints)
    
    #Vertical collision
    for objects in Landable:
        if Player.colliderect(objects.rect) and Player_Yvel > 0 and Player_Bottom <= objects.rect.top + Collide_Tolerance:
            On_Ground = True
            Player_Speed = 3
            Player.bottom = objects.rect.top
            Player_Yvel = 0
    for objects in Solids:
        if Player.colliderect(objects.rect) and Player_Yvel < 0 and Player_Top >= objects.rect.bottom:
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
    #print(On_Ground)
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