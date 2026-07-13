import pygame as pg
import sys, os, subprocess


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

from tile_data import Tile_Texture, Player_Tex, Resource_Path, Player_Image
from tile_data import Rainbow_Tex, PWalk1, PWalk2, PDash, PFall, Heart_Empty_Tex, Heart_Full_Tex

#Functions
def World_To_Screen(rect, camera_x, camera_y):
    return pg.Rect(rect.x - camera_x, rect.y - camera_y, rect.width, rect.height)

def Set_Checkpoint(checkpoint):
    global Checkpoint_X, Checkpoint_Y
    Checkpoint_X = checkpoint.rect.x
    Checkpoint_Y = checkpoint.rect.y
    
def Spawn_At_Checkpoint():
    global Checkpoint_X, Checkpoint_Y, Player_Xvel, Player_Yvel, Dashing, Dash_Delay, Walljump_Push, Player_Health
    Player.x = Checkpoint_X
    Player.y = Checkpoint_Y
    Player_Xvel = 0
    Player_Yvel = 0
    Dashing = False
    Dash_Delay = 0
    Walljump_Push = 0
    Player_Health = Player_Hearts

def Toggle_Fullscreen():
    global Fullscreen, screen
    Fullscreen = not Fullscreen
    if Fullscreen:
        screen = pg.display.set_mode((SCREEN_width, SCREEN_height), pg.FULLSCREEN | pg.SCALED)
    else:
        screen = pg.display.set_mode((SCREEN_width, SCREEN_height), pg.SCALED)
        
def Set_Level(path):
    with open(path, "r") as file:
        lines = file.readlines()
    return [line.rstrip("\n") for line in lines]

def Grid_To_Pixels(col, row):
    return col * Tile_Size, row * Tile_Size

def Point_In_Triangle(px, py, triangle):
    (x1, y1), (x2, y2), (x3, y3) = triangle
    d1 = (px - x2) * (y1 - y2) - (x1 - x2) * (py - y2)
    d2 = (px - x3) * (y2 - y3) - (x2 - x3) * (py - y3)
    d3 = (px - x1) * (y3 - y1) - (x3 - x1) * (py - y1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)

def Rect_Triangle_Collision(rect, triangle):
    corners = [
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.left, rect.bottom),
        (rect.right, rect.bottom),
    ]
    for corner in corners:
        if Point_In_Triangle(corner[0], corner[1], triangle):
            return True
    return False

def Trin_Transparent(surface):
    rect = surface.get_bounding_rect()
    return surface.subsurface(rect).copy()

def Load_Level(level):
    global Level_Layout, ground, Solids, Hazards, Landable, Checkpoints, Current_Map, Checkpoint_Y, Checkpoint_X
    
    Level_Layout = Set_Level(Resource_Path(f"levels/{Current_Map}.txt"))
    
            
    All_Platforms.empty()
    Solids.empty()
    Landable.empty()
    Hazards.empty()
    Checkpoints.empty()
    Level_End_Triggers.empty()
    Spawn_X = 100
    Spawn_Y = 450
    ground = None
            
    
    Level_Layout = Set_Level(Resource_Path(f"levels/{level}.txt"))
    
    for row_index, row in enumerate(Level_Layout):
        for col_index, symbol in enumerate(row):
            if symbol == ".":
                continue
            
            x, y = Grid_To_Pixels(col_index, row_index)
            
            if symbol == "X":
                Spawn_X, Spawn_Y = x, y
            
            obj_class = Tile_Class[symbol]
            texture = Tile_Texture[symbol]
            obj = obj_class(x, y, Tile_Size, Tile_Size, texture)
            
            if symbol in Tile_Rotaion:
                obj = obj_class(x, y, Tile_Size, Tile_Size, texture, rotation=Tile_Rotaion[symbol])
            else:
                obj = obj_class(x,y, Tile_Size, Tile_Size, texture)
            
            All_Platforms.add(obj)
            if symbol == "P":
                Solids.add(obj)
                Landable.add(obj)
            elif symbol in ("^", "v", "<", ">"):
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
            elif symbol == "E":
                Level_End_Triggers.add(obj)
                
    Current_Map = f"{level}"
                
    
    Player.topleft = (Spawn_X, Spawn_Y)
    Checkpoint_X, Checkpoint_Y = Spawn_X, Spawn_Y      


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

class Spike(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture, rotation=0):
        super().__init__()
        spike_width = width // 2
        spike_height = height // 2
        base_image = pg.transform.scale(texture, (spike_width, spike_height))
        self.image = pg.transform.rotate(base_image, rotation)
        self.rotation = rotation
        
        # Anchor the spike flush against whichever surface it's pointing away from
        if rotation == 0:      # pointing up, sits on floor
            self.rect = self.image.get_rect(midbottom=(x + width // 2, y + height))
        elif rotation == 180:  # pointing down, hangs from ceiling
            self.rect = self.image.get_rect(midtop=(x + width // 2, y))
        elif rotation == 90:   # pointing left, sits on right wall
            self.rect = self.image.get_rect(midright=(x + width, y + height // 2))
        elif rotation == 270:  # pointing right, sits on left wall
            self.rect = self.image.get_rect(midleft=(x, y + height // 2))
        
        self.triangle = self._build_triangle(rotation)
    
    def _build_triangle(self, rotation):
        if rotation == 0:
            return [
                (self.rect.left, self.rect.bottom),
                (self.rect.right, self.rect.bottom),
                (self.rect.centerx, self.rect.top),
            ]
        elif rotation == 180:
            return [
                (self.rect.left, self.rect.top),
                (self.rect.right, self.rect.top),
                (self.rect.centerx, self.rect.bottom),
            ]
        elif rotation == 90:
            return [
                (self.rect.right, self.rect.top),
                (self.rect.right, self.rect.bottom),
                (self.rect.left, self.rect.centery),
            ]
        elif rotation == 270:
            return [
                (self.rect.left, self.rect.top),
                (self.rect.left, self.rect.bottom),
                (self.rect.right, self.rect.centery),
            ]
    
    def check_collision(self, player_rect):
        if not player_rect.colliderect(self.rect):
            return False
        return Rect_Triangle_Collision(player_rect, self.triangle)
    
class Checkpoint(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture):
        super().__init__()
        self.image = pg.transform.scale(texture, (width // 2 , height // 2))
        self.rect = self.image.get_rect(center=(x + width // 2, y + height // 2))

class Menu_Button(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((0, 255, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        
class Level_End(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture):
        super().__init__()
        self.image = pg.transform.scale(texture, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        
class Player_Spawn(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture):
        super().__init__()
        self.image = pg.transform.scale(texture, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        
class Trail(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, texture):
        super().__init__()
        self.image = pg.transform.scale(texture, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.lifetime = 15
        self.max_lifetime = 15
        
    def update(self):
        self.lifetime -= 1
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        alpha = max(0, alpha)
        self.image.set_alpha(alpha)
        if self.lifetime <= 0:
            self.kill()


Tile_Size = 50
Level_Layout = Set_Level(Resource_Path("levels/level1.txt"))

Tile_Legend = {
    "G": "Ground",
    "P": "Platform",
    "^": "Spike",
    "C": "Checkpoint",
    "D": "Platform",
    "E": "Level_End",
    "X": "Player_Spawn"
    
}

Tile_Class = {
    "G": Ground,
    "P": Platform,
    "^": Spike,
    "<": Spike,
    ">": Spike,
    "v": Spike,
    "C": Checkpoint,
    "D": Platform,
    "E": Level_End,
    "X": Player_Spawn,
}

Tile_Rotaion = {
    "^": 0,
    "v": 180,
    "<": 90,
    ">": 270,
}

#Sprites
Player = pg.Rect((100, 450, 25, 50))
Player_Image = pg.transform.scale(Player_Tex, (Player.width, Player.height))
#Menu Buttons
New_Game = Menu_Button(300, 300, 190, 50)
Editor = Menu_Button(300, 370, 190, 50)
New_Game_Text = Button_Font.render("New Game", True, (255, 255, 255))
Editor_Text = Button_Font.render("Editor", True, (255, 255, 255))
Title_Text = Title_Font.render("2d Platformer", True, (255, 255, 255))
#UI
Heart_Tex = pg.transform.scale(Heart_Full_Tex, (25, 25))

#Groups
All_Platforms = pg.sprite.Group()
Solids = pg.sprite.Group()
Landable = pg.sprite.Group()
Hazards = pg.sprite.Group()
Checkpoints = pg.sprite.Group()
Menu_Buttons = pg.sprite.Group(New_Game, Editor)
Level_End_Triggers = pg.sprite.Group()
Trails = pg.sprite.Group()

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
        elif symbol in ("^", "v", "<", ">"):
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
        elif symbol == "E":
            Level_End_Triggers.add(obj)
        

#Variables
Player_Speed = 3
Player_Xvel = 0
Player_Jump_Height = 8
Player_Hearts = 3
Player_Health = Player_Hearts
Player_Yvel = 0
Sprinting = False
Movement_Direction = Player_Speed
Gravity_Force = 0.4
On_Ground = True
Player_Bottom = Player.bottom
Player_Top = Player.top
Collide_Tolerance = 5
Coyote_Timer_Max = 10
Coyote_Timer = 0
Camera_X = 0
Camera_Y = 0
Deadzone_Height = 80
Deadzone_Width = 100
Screen_Player_X = Player.centerx - Camera_X
Screen_Player_Y = Player.centery - Camera_Y
Checkpoint_X = 100
Checkpoint_Y = 600
Checkpoint_Location = (Checkpoint_X, Checkpoint_Y)
Touching_Wall = False
Can_Walljump = False
Touching_Wall_Left = False
Touching_Wall_Right = False
Walljump_Push = 0
Walljump_Decay = 0.85
Max_Down_Speed = 5
Max_Up_Speed = 7
Fullscreen = False
run = False
menu = False
Dash_Delay = 0
Dash_Speed = 25
Can_Dash = True
Level_Number = 1
Current_Map = f"level{Level_Number}"
Going_Left = False
Going_Right = False
Dash_Key_Held = False
Dashing = False
Trail_Spawn_Timer = 0
Train_Spawn_Interval = 2
Walk_Frames = [PWalk1, PWalk2]
Walk_Frame_Index = 0
Walk_Anim_Timer = 0
Walk_Anim_Speed = 8
Was_On_Ground_This_Frame = False
Falling = False
Invincibility_Timer = 0
Invincibility_Duration = 45


menu = True
while menu:
    screen.fill((0, 200, 255))
    
    
    for buttons in Menu_Buttons:
        screen.blit(buttons.image, World_To_Screen(buttons.rect, Camera_X, Camera_Y))
    screen.blit(New_Game_Text, (310, 310))
    screen.blit(Title_Text, (185, 100))
    screen.blit(Editor_Text, (345, 380))
        
    
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            if New_Game.rect.collidepoint(event.pos):
                menu = False
                run = True
            elif Editor.rect.collidepoint(event.pos):
                menu = False
                run = False
                subprocess.Popen(["python", "level_editor.py"])
        if event.type == pg.QUIT:
            menu = False
            run = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_F11:
                Toggle_Fullscreen()
    pg.display.update()
    clock.tick(60)

Load_Level("level1")
while run:
    screen.fill((0, 200, 255))

    if Touching_Wall == True:
        Gravity_Force = 0.05
    elif Touching_Wall == False:
        Gravity_Force = 0.4
    elif Dash_Delay >0:
        Gravity_Force = 0
        
    
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
        if hazards.check_collision(Player) and Invincibility_Timer <= 0:
            Player_Health -= 1
            Invincibility_Timer = Invincibility_Duration

            Player_Yvel = -6
            if Player_Health <= 0:
                Spawn_At_Checkpoint()
            
    #Checkpoint collision
    for checkpoints in Checkpoints:
        if Player.colliderect(checkpoints):
            Set_Checkpoint(checkpoints)
    
    #Level end collision
    for triggers in Level_End_Triggers:
        if Player.colliderect(triggers.rect):
            Level_Number += 1
            Current_Map = f"level{Level_Number}"
            Load_Level(f"level{Level_Number}")
    
    #Vertical collision
    Was_On_Ground_This_Frame = False
    
    for objects in Landable:
        horizontally_overlapping = Player.right > objects.rect.left and Player.left < objects.rect.right
        vertically_close = (
            Player_Yvel >= 0
            and Player_Bottom <= objects.rect.top + Collide_Tolerance
            and Player.bottom >= objects.rect.top - Collide_Tolerance
        )
        if horizontally_overlapping and vertically_close:
            On_Ground = True
            Can_Dash = True
            Player.bottom = objects.rect.top
            Player_Yvel = 0
            Was_On_Ground_This_Frame = True
    if not Was_On_Ground_This_Frame:
        On_Ground = False
    for objects in Solids:
        if Player.colliderect(objects.rect) and Player_Yvel < 0 and Player_Top >= objects.rect.bottom:
            Player.top = objects.rect.bottom
            Player_Yvel = 0
    
    Player_Bottom = Player.bottom
    Player_Top = Player.top
    
    if Dash_Delay > 0:
        Player_Yvel -= Player_Yvel
        Player_Speed *= 2
    else:
        Dashing = False
    
    Is_Walking = Movement_Direction != 0 and On_Ground
    
    if Is_Walking:
        Walk_Anim_Timer += 1
        if Walk_Anim_Timer >= Walk_Anim_Speed:
            Walk_Anim_Timer = 0
            Walk_Frame_Index = (Walk_Frame_Index + 1) % len(Walk_Frames)
    else:
        Walk_Frame_Index = 0
        Walk_Anim_Timer = 0
    
    #Player Movement
    key = pg.key.get_pressed()
    
    #Horizontal collision
    Touching_Wall = False
    Can_Walljump = False
    for objects in Solids:
        if Player.colliderect(objects.rect):
            had_vertical_overlap = Player_Bottom > objects.rect.top and Player_Top < objects.rect.bottom
            if had_vertical_overlap:
                if Player_Xvel < 0:
                    Player.left = objects.rect.right
                    Touching_Wall = True
                    if Going_Right == True:
                        Can_Dash = False
                    else:
                        Can_Dash = True
                    Dash_Delay = 0
                    Touching_Wall_Right = True
                    Touching_Wall_Left = False
                    if On_Ground == False:
                        Can_Walljump = True
                elif Player_Xvel > 0:
                    Player.right = objects.rect.left
                    Touching_Wall = True
                    Dash_Delay = 0
                    if Going_Left == True:
                        Can_Dash = False
                    else:
                        Can_Dash = True
                    Touching_Wall_Right = False
                    Touching_Wall_Left = True
                    if On_Ground == False:
                        Can_Walljump = True
    if Touching_Wall == True:
        Max_Down_Speed = 2
    else:
        Max_Down_Speed = 5
    
    if Dash_Delay > 0:
        Dash_Delay -= 1
    
    Movement_Direction = 0
    if key[pg.K_a] == True:
        Movement_Direction = -Player_Speed
        Going_Left = True
        Going_Right = False
    if key[pg.K_d] == True:
        Movement_Direction = Player_Speed
        Going_Right = True
        Going_Left = False
        
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
        
    if On_Ground == True:
        if key[pg.K_LSHIFT] == True or key[pg.K_RSHIFT] == True:
            Player_Speed = 5
            Player_Jump_Height = 8
        else:
            Player_Speed = 3
            Player_Jump_Height = 8
    else:
        Player_Speed = 3
        Player_Jump_Height = 8
                
    Ctrl_Pressed = key[pg.K_LCTRL] == True or key[pg.K_RCTRL] == True
    
    if Ctrl_Pressed and not Dash_Key_Held:
        if Dash_Delay <= 0:
            if Can_Dash == True:
                if On_Ground == False:
                    Sprinting = False
                    Can_Dash = False
                    Dashing = True
                    Dash_Delay = 20
                    Gravity_Force = 0
                    Player_Yvel -= Player_Yvel
                    if Going_Left:
                        Player_Xvel = -Dash_Speed
                    elif Going_Right:
                        Player_Xvel = Dash_Speed
                    
    
    Dash_Key_Held = Ctrl_Pressed
            
    
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

    if Dashing == True:
        Trail_Spawn_Timer -= 1
        if Trail_Spawn_Timer <= 0:
            new_trail = Trail(Player.x - 10, Player.y, Player.width, Player.height, Rainbow_Tex)
            Trails.add(new_trail)
            Trail_Spawn_Timer = Train_Spawn_Interval
            
    if Invincibility_Timer > 0:
        Invincibility_Timer -= 1
            
    if On_Ground == False and Touching_Wall == False and Player_Yvel >= 0:
        Falling = True
    else:
        Falling = False

    Trails.update()

    for objects in All_Platforms:
        screen.blit(objects.image, World_To_Screen(objects.rect, Camera_X, Camera_Y))
        
    for trail in Trails:
        screen.blit(trail.image, World_To_Screen(trail.rect, Camera_X, Camera_Y))
    
    if Is_Walking:
        current_walk_tex = Walk_Frames[Walk_Frame_Index]
        Player_Image = pg.transform.scale(current_walk_tex, (30, 50))
    elif Dashing:
        Player_Image = pg.transform.scale(PDash, (30, 50))
    elif Falling:
        Player_Image = pg.transform.scale(PFall, (30, 50))
    else:
        Player_Image = pg.transform.scale(Player_Tex, (25, 50))
        
    if Going_Left == True:
        Player_Image = pg.transform.flip(Player_Image, True, False)
    
    heart_loc = 25
    for i in range(Player_Hearts):
        if i < Player_Health:
            Heart_Tex = pg.transform.scale(Heart_Full_Tex, (32, 32))
            screen.blit(Heart_Tex, (heart_loc, 25))
        else:
            Heart_Tex = pg.transform.scale(Heart_Empty_Tex, (32, 32))
            screen.blit(Heart_Tex, (heart_loc, 25))
        heart_loc += 32
            
    Player_Sprite_Rect = Player_Image.get_rect(center=Player.center)
    if Invincibility_Timer > 0 and Invincibility_Timer % 6 < 3:
        pass  # skip drawing this frame to create a blink effect
    else:
        screen.blit(Player_Image, World_To_Screen(Player_Sprite_Rect, Camera_X, Camera_Y))
    print(Falling)
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            print(event.pos)
        if event.type == pg.QUIT:
            run = False
            menu = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_F11:
                Toggle_Fullscreen()
    pg.display.update()
    clock.tick(60)
pg.quit()