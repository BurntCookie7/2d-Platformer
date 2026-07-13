import pygame as pg
import sys, os, subprocess
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.title("Level Editor")
Editor = tk.Frame(root)
Options = tk.Frame(root)
Options.pack()

SCREEN_width, SCREEN_height = 1000, 700

embed = tk.Frame(Editor, width=SCREEN_width, height=SCREEN_height)
embed.pack(side=tk.LEFT)

sidebar = tk.Frame(Editor, width=200, height=SCREEN_height, bg="gray")
sidebar.pack(side=tk.LEFT)

root.update()

os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
if os.name == 'nt':
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    
pg.init()
screen = pg.display.set_mode((SCREEN_width, SCREEN_height))
pg.display.set_caption("Level Editor")
clock = pg.time.Clock()

from tile_data import Tile_Texture, External_Resource_Path

Tile_Size = 25
Grid_Cols = 30
Grid_Rows = 15
Selected_Symbol = "P"
Grid = [["." for _ in range(Grid_Cols)] for _ in range(Grid_Rows)]
Grid_Pixel_Width = Grid_Cols * Tile_Size
Grid_Pixel_Height = Grid_Rows * Tile_Size
Offset_X = (SCREEN_height - Grid_Pixel_Height) // 2
Offset_Y = (SCREEN_width - Grid_Pixel_Width) // 2
Pan_X, Pan_Y = 0, 0
Dragging = False
Last_Mouse_Pos = (0, 0)

def Draw_Grid():
    for row in range(Grid_Rows):
        for col in range(Grid_Cols):
            symbol = Grid[row][col]
            x = col * Tile_Size + Offset_X + Pan_X
            y = row * Tile_Size + Offset_Y + Pan_Y
            if symbol == ".":
                pg.draw.rect(screen, (60, 60 ,60), (x, y, Tile_Size, Tile_Size), 1)
            else:
                texture = Tile_Texture[symbol]
                scaled = pg.transform.scale(texture, (Tile_Size, Tile_Size))
                if symbol in Tile_Rotaion:
                    scaled = pg.transform.rotate(scaled, Tile_Rotaion[symbol])
                screen.blit(scaled, (x, y))

def Screen_To_Grid(pos):
    x, y = pos
    grid_x = x - Offset_X - Pan_X
    grid_y = y - Offset_Y - Pan_Y
    return grid_y // Tile_Size, grid_x // Tile_Size
        
def Draw_Ground_Preview():
    ground_row_y = Grid_Rows * Tile_Size + Offset_Y + Pan_Y
    dirt_start_y = ground_row_y + Tile_Size
    
    ground_texture = pg.transform.scale(Tile_Texture["G"], (Tile_Size, Tile_Size))
    dirt_texture = pg.transform.scale(Tile_Texture["D"], (Tile_Size, Tile_Size))
    
    for col in range(Grid_Cols):
        x = col * Tile_Size + Offset_X + Pan_X
        screen.blit(ground_texture, (x, ground_row_y))
        for i in range(7):
            screen.blit(dirt_texture, (x, dirt_start_y + i * Tile_Size))

def Srtip_Auto_Footer(lines):
    trimmed = lines[:]
    
    while trimmed and len(trimmed[-1]) >0 and all(ch == "D" for ch in trimmed[-1]):
        trimmed.pop()
        
    while trimmed and len(trimmed[-1]) > 0 and all(ch == "G" for ch in trimmed[-1]):
        trimmed.pop()
    
    return trimmed
    
def Load_Level_Editor(path):
    path = filedialog.askopenfilename(
        initialdir=External_Resource_Path("levels"),
        filetypes=[("Text files", "*.txt")],
    )
    if not path:  # cancelled
        return
    
    global Grid, Grid_Rows
    with open(path, "r") as file:
        lines = [line.rstrip("\n") for line in file.readlines()]
        
    trimmed_lines = Srtip_Auto_Footer(lines)
    
    Grid = [list(line.ljust(Grid_Cols, ".")) for line in trimmed_lines]
    Grid_Rows = len(Grid)
    print(f"Loaded {path}")
    

def Game_Loop():
    global Dragging, Last_Mouse_Pos, Pan_X, Pan_Y
    screen.fill((30, 30, 30))
    Draw_Grid()
    Draw_Ground_Preview()
    pg.display.flip()
    
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            row, col = Screen_To_Grid(event.pos)
            if 0 <= row < Grid_Rows and 0 <= col < Grid_Cols:
                if event.button == 1:
                    Grid[row][col] = Selected_Symbol
                elif event.button == 3:
                    Grid[row][col] = "."
                elif event.button == 2:
                    Dragging = True
                    Last_Mouse_Pos = event.pos
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 2:
                Dragging = False
        elif event.type == pg.MOUSEMOTION:
            if Dragging == True:
                dx = event.pos[0] - Last_Mouse_Pos[0]
                dy = event.pos[1] - Last_Mouse_Pos[1]
                Pan_X += dx
                Pan_Y += dy
                Last_Mouse_Pos = event.pos
        elif event.type == pg.MOUSEWHEEL:
            if event.y == 1:
                Zoom_In()
            elif event.y == -1:
                Zoom_Out()
            elif event.x == 1:
                Pan_X -= 5
            elif event.x == -1:
                Pan_X += 5
                
    root.after(16, Game_Loop)

def Recalculate_Offset():
    global Offset_Y, Offset_X
    grid_pixel_width = Grid_Cols * Tile_Size
    grid_pixel_height = Grid_Rows * Tile_Size
    Offset_X = (SCREEN_width - grid_pixel_width) // 2
    Offset_Y = (SCREEN_height - grid_pixel_height) // 2

def Select_Symbol(symbol):
    global Selected_Symbol
    Selected_Symbol = symbol
    
def Save_Level_As():
    path = filedialog.asksaveasfilename(
        initialdir=External_Resource_Path("levels"),
        defaultextension=".txt",
        filetypes=[("text files", "*.txt")],
    )
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ground_row = "G" * Grid_Cols
    dirt_rows = ["D" * Grid_Cols for _ in range(7)]
    
    with open(path, "w") as file:
        for row in Grid:
            file.write("".join(row) + "\n")
        file.write(ground_row + "\n")
        for rows in dirt_rows:
            file.write(rows + "\n")
    print(f"Saved to {path}")
    
def Set_Width_Height(width, height):
    global Grid_Cols, Grid_Rows, Grid, Offset_X, Offset_Y
    Grid_Cols = width
    Grid_Rows = height
    Grid = [["." for _ in range(Grid_Cols)] for _ in range(Grid_Rows)]
    Grid_Pixel_Width = Grid_Cols * Tile_Size
    Grid_Pixel_Height = Grid_Rows * Tile_Size
    Offset_X = (SCREEN_width - Grid_Pixel_Width) // 2
    Offset_Y = (SCREEN_height - Grid_Pixel_Height) // 2
    Options.pack_forget()
    Editor.pack()

def Zoom_In():
    global Tile_Size
    Tile_Size += 10
    Recalculate_Offset()
    Draw_Grid()
    
def Zoom_Out():
    global Tile_Size
    Tile_Size = max(1, Tile_Size - 5)
    Recalculate_Offset()
    Draw_Grid()
    
def Quit_To_Game():
    root.destroy()
    pg.quit()
    
    clean_env = os.environ.copy()
    clean_env.pop('SDL_WINDOWID', None)
    clean_env.pop('SDL_VIDEODRIVER', None)
    
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(os.path.abspath(sys.executable))
        game_path = os.path.join(base_dir, "game.exe")
        subprocess.Popen([game_path], env=clean_env)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        game_path = os.path.join(base_dir, "game.py")
        subprocess.Popen([sys.executable, game_path], env=clean_env)

Tile_Rotaion = {
    "^": 0,
    "v": 180,
    "<": 90,
    ">": 270,
}

Default_Width = tk.StringVar()
Default_Height = tk.StringVar()
Default_Width.set("30")
Default_Height.set("15")
#tk.Button(sidebar, text="Zoom In", command=Zoom_In).pack()
#tk.Button(sidebar, text="Zoom Out", command=Zoom_Out).pack()
tk.Button(sidebar, text="Ground (G)", command=lambda: Select_Symbol("G")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Platform (P)", command=lambda: Select_Symbol("P")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Dirt (D)", command=lambda: Select_Symbol("D")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Spike UP (^)", command=lambda: Select_Symbol("^")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Spike DOWN (v)", command=lambda: Select_Symbol("v")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Spike LEFT (<)", command=lambda: Select_Symbol("<")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Spike RIGHT (>)", command=lambda: Select_Symbol(">")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Checkpoint (C)", command=lambda: Select_Symbol("C")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Level End (E)", command=lambda: Select_Symbol("E")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Player Spawn (X)", command=lambda: Select_Symbol("X")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Save", command=lambda: Save_Level_As()).pack(fill=tk.X, pady=10)
tk.Button(sidebar, text="Load", command=lambda: Load_Level_Editor("levels/level1.txt")).pack(fill=tk.X, pady=2)
tk.Button(sidebar, text="Quit To Game", command=Quit_To_Game).pack(fill=tk.X, pady=2)
Width_Entry_Title = tk.Label(Options, text="Grid Width").pack()
Width_Entry = tk.Entry(Options, textvariable=Default_Width)
Width_Entry.pack()
Height_Entry_Title = tk.Label(Options, text="Grid Height").pack()
Height_Entry = tk.Entry(Options, textvariable=Default_Height)
Height_Entry.pack()
Options_Confirm = tk.Button(Options, text="Confirm", command=lambda: Set_Width_Height(int(Width_Entry.get()), int(Height_Entry.get()))).pack()

Game_Loop()
root.mainloop()