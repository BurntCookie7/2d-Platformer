import pygame as pg

Textures = {}

def Load_Texture(name, path):
    if name not in Textures:
        Textures[name] = pg.image.load(path).convert_alpha()
    return Textures[name]

def Resource_Path(relative_path):
    import sys, os
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

Grass_Tex = Load_Texture("Grass", Resource_Path("textures/grass.png"))
Grass_Side_Tex = Load_Texture("Grass Side", Resource_Path("textures/grass_side.png"))
Checkpoint_Tex = Load_Texture("Checkpoint", Resource_Path("textures/checkpoint.png"))
Dirt_Tex = Load_Texture("Dirt", Resource_Path("textures/dirt.png"))
Spike_Tex = Load_Texture("Spike", Resource_Path("textures/spike.png"))

Tile_Texture = {
    "G": Grass_Tex,
    "P": Grass_Side_Tex,
    "S": Spike_Tex,
    "C": Checkpoint_Tex,
    "D": Dirt_Tex,
}