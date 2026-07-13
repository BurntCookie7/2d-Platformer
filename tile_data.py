import pygame as pg
import sys, os

Textures = {}

def Load_Texture(name, path):
    if name not in Textures:
        Textures[name] = pg.image.load(path).convert_alpha()
    return Textures[name]

def Bundled_Resource_Path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

def External_Resource_Path(relative_path):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

Grass_Tex = Load_Texture("Grass", Bundled_Resource_Path("textures/grass.png"))
Grass_Side_Tex = Load_Texture("Grass Side", Bundled_Resource_Path("textures/grass_side.png"))
Checkpoint_Tex = Load_Texture("Checkpoint", Bundled_Resource_Path("textures/checkpoint.png"))
Dirt_Tex = Load_Texture("Dirt", Bundled_Resource_Path("textures/dirt.png"))
Spike_Tex = Load_Texture("Spike", Bundled_Resource_Path("textures/spike.png"))
Level_End_Tex = Load_Texture("Level End", Bundled_Resource_Path("textures/grass.png"))
Player_Tex = Load_Texture("Player", Bundled_Resource_Path("textures/player.png"))
Rainbow_Tex = Load_Texture("Rainbow", Bundled_Resource_Path("textures/rainbow.png"))
PWalk1 = Load_Texture("Walk1", Bundled_Resource_Path("textures/player_walk1.png"))
PWalk2 = Load_Texture("Walk2", Bundled_Resource_Path("textures/player_walk2.png"))
PDash = Load_Texture("Dash", Bundled_Resource_Path("textures/player_dash.png"))
PFall = Load_Texture("Fall", Bundled_Resource_Path("textures/player_fall.png"))
Spawn_Tex = Load_Texture("Spawn", Bundled_Resource_Path("textures/spawn.png"))
Heart_Full_Tex = Load_Texture("Heart Full", Bundled_Resource_Path("textures/heart_full.png"))
Heart_Empty_Tex = Load_Texture("Heart Empty", Bundled_Resource_Path("textures/heart_empty.png"))
Player_Image = pg.transform.scale(Player_Tex, (25, 50))

Tile_Texture = {
    "G": Grass_Tex,
    "P": Grass_Side_Tex,
    "^": Spike_Tex,
    "v": Spike_Tex,
    ">": Spike_Tex,
    "<": Spike_Tex,
    "C": Checkpoint_Tex,
    "D": Dirt_Tex,
    "E": Level_End_Tex,
    "X": Spawn_Tex,
}