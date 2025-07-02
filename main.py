import sys
from cell import *
import pygame, numpy as np
from pygame.locals import *


CELL_SIZE = 10
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
grid = np.zeros(shape=(SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE))


clock = pygame.time.Clock()
timer = pygame.time.get_ticks()
CellFramePerUpdate = 30  # Number of frames per second for the cell update
GhostCellFix = 0

cell_type = "solid"  # Default cell type
cells = {
    "fire": [],
    "smoke": [],
    "acid": [],
    "water": [],
    "sand": [],
    "wood": [],
    "solid": [],
    "destroy": [],
    "examine": [],
    "time slow": [],
}  # Dictionary to hold cell types and their instances
valid_substance = list(cells.keys()) + ["empty"]  # valid substances each cell can be


def update(dt):
    """
    Update game. Called once per frame.
    dt is the amount of time passed since last frame.
    If you want to have constant apparent movement no matter your framerate,
    what you can do is something like
    x += v * dt
    and this will scale your velocity based on time. Extend as necessary."""

    global cell_type, timer, CellFramePerUpdate, GhostCellFix

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Change selected type
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[2]:
                cell_type = valid_substance[valid_substance.index(cell_type) - 1]

        if pygame.mouse.get_pressed()[0]:
            # Snap to grid
            x = int(pygame.mouse.get_pos()[0] // CELL_SIZE)
            y = int(pygame.mouse.get_pos()[1] // CELL_SIZE)
            if cell_type == "empty":
                # Remove the cell from the list
                for celltype in cells:  # for each cell type
                    for cell in cells[celltype]:  # for each cell in the list
                        if cell.position == (x, y):
                            cell.remove(grid, cells)
            elif cell_type == "examine":
                print(grid[x, y])
            elif grid[x, y] == 0:
                # Set the cell to a color
                # grid[x, y] = 2 if cell_type in ["water", "fire"] else 1
                # cells[f"{cell_type}"].append(Cell(cell_type, (x, y)))
                if cell_type == "wood":
                    cells["wood"].append(BurnSolid((x, y)))
                    grid[x, y] = SOLID_LAYER
                elif cell_type == "solid":
                    cells["solid"].append(Solid((x, y)))
                    grid[x, y] = SOLID_LAYER
                elif cell_type == "water":
                    cells["water"].append(Water((x, y)))
                    grid[x, y] = WATER_LAYER
                elif cell_type == "sand":
                    cells["sand"].append(Sand((x, y)))
                    grid[x, y] = SAND_LAYER
                elif cell_type == "fire":
                    cells["fire"].append(Fire((x, y)))
                    grid[x, y] = FIRE_LAYER
                elif cell_type == "destroy":
                    cells["destroy"].append(Destroy((x, y)))
                    grid[x, y] = EMPTY_LAYER
                elif cell_type == "acid":
                    cells["acid"].append(Acid((x, y)))
                    grid[x, y] = WATER_LAYER
                elif cell_type == "time slow":
                    cell_ = Solid((x, y))
                    cell_.color = (255, 0, 255)
                    cell_.cell_type = "time slow"
                    cells["time slow"].append(cell_)
                    grid[x, y] = SOLID_LAYER

    if pygame.time.get_ticks() - timer > CellFramePerUpdate:
        if len(cells["time slow"]) > 0:
            CellFramePerUpdate = 300
        else:
            CellFramePerUpdate = 30

        for cell in (
            cells["sand"]
            + cells["water"]
            + cells["acid"]
            + cells["fire"]
            + cells["smoke"]
            + cells["destroy"]
        ):
            cell.update(grid, cells)
        timer = pygame.time.get_ticks()

        GhostCellFix += 1
        if GhostCellFix >= 20:
            for celltype in cells.keys():
                for cell in cells[celltype]:
                    cell.fix(grid)


def draw(screen, text_font, text_rect):
    """
    Draw things to the window. Called once per frame.
    """
    screen.fill((0, 0, 0))

    for celltype in cells:
        for cell in cells[celltype]:
            cell.draw(pygame.display.get_surface(), CELL_SIZE)

    text = text_font.render(cell_type.upper(), True, (0, 255, 0))
    screen.blit(text, text_rect)

    # Flip the display so that the things we drew actually show up.
    pygame.display.flip()


def runPyGame():
    # Initialise PyGame.
    pygame.init()

    # Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
    fps = 60.0
    fpsClock = pygame.time.Clock()

    text_font = pygame.font.Font("freesansbold.ttf", 32)
    text = text_font.render("SAND", True, (0, 255, 0))
    text_rect = text.get_rect()

    # Set up the window.
    # width, height = 640, 640
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Main game loop.
    dt = 1 / fps
    while True:
        update(dt)
        draw(screen, text_font, text_rect)
        clock.tick()
        # print(clock.get_fps())
        dt = fpsClock.tick(fps)


if __name__ == "__main__":
    runPyGame()


# TO ADD (According to Pizza and Rick):
# Mud -- Like clay but really soft
# Muddy Mud Mud -- Well, it's like... s-sand but hard?
# Clay -- Like mud but really hard
# Limestone -- Stone that is lime
# Wood -- For making houses
# Bricks -- Hard course material?
# High quality wood -- Fresh off the tree that you chop from trees. Perfect.
# Temperature(?)
# Glass -- looks cool according to pizza
