from typing import Optional
import pygame, random


EMPTY_LAYER = 0
SOLID_LAYER = 1
SAND_LAYER = 2
WATER_LAYER = 3
FIRE_LAYER = 4


class Cell:
    def __init__(
        self,
        cell_type: str = "solid",
        position: tuple[int, int] = (0, 0),
        layer: int = 1,
    ) -> None:

        self.cell_type = cell_type  # Type of cell (e.g. solid, sand, water)
        self.position = position  # Position of the cell in the grid
        self.cell_layer = layer

    # Move the cell on the grid
    def move(self, grid, dx: int, dy: int, fill_type=0) -> None:
        grid[self.position[0]][self.position[1]] = fill_type
        self.position = (self.position[0] + dx, self.position[1] + dy)
        grid[self.position[0]][self.position[1]] = self.cell_layer

    # Gets the neighbors of the cell
    # 0 1 2
    # 3 8 4
    # 5 6 7
    def neighbors(self, grid) -> list:
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                # Check if the neighbor is within bounds
                if (
                    self.position[0] + j < 0
                    or self.position[0] + j >= len(grid)
                    or self.position[1] + i < 0
                    or self.position[1] + i >= len(grid[0])
                ):
                    neighbors.append(-1)
                    continue

                # Append neighbor cell
                neighbors.append(int(grid[self.position[0] + j][self.position[1] + i]))
        neighbors.append(int(grid[self.position[0]][self.position[1]]))
        return neighbors

    # Draw the cell on the screen
    def draw(self, screen, cell_size) -> None:
        pygame.draw.rect(
            screen,
            self.color,
            (
                self.position[0] * cell_size,
                self.position[1] * cell_size,
                cell_size,
                cell_size,
            ),
        )

    # Makes sure that the grid is synced and that there are no ghost cells
    def fix(self, grid):
        if grid[self.position[0], self.position[1]] != self.cell_layer:
            grid[self.position[0], self.position[1]] = self.cell_layer

    def remove(self, grid, cell_dict):
        grid[self.position[0], self.position[1]] = 0
        cell_dict[self.cell_type].remove(self)


# Burnable Solid Cell
# Layer: 1
class BurnSolid(Cell):
    def __init__(self, position=(0, 0)):
        super().__init__("burn solid", position)

        self.color = (130, 70, 52)
        self.burn_damage = 25


# Standard Solid Cell
# Layer: 1
class Solid(Cell):
    def __init__(self, position=(0, 0)):
        super().__init__("solid", position)

        self.color = (255, 255, 255)


# Sand Cell
# Layer: 2
class Sand(Cell):
    def __init__(self, position=(0, 0)):
        super().__init__("sand", position, SAND_LAYER)

        self.color = (194, 178, 128)
        self.friction = 0.1
        self.chance = 1

    def update(self, grid, cell_dict):
        neighbors = self.neighbors(grid)

        # Reset chance to fall to the side if there is something above
        if neighbors[1] != EMPTY_LAYER:
            self.chance = random.random()

        # Fall if able to (Ignore water)
        if neighbors[6] in (EMPTY_LAYER, WATER_LAYER):
            self.move(grid, 0, 1)

        # Fall to the side
        elif self.chance > self.friction:
            if (
                random.choice([0, 1])
                and neighbors[5] == EMPTY_LAYER
                and neighbors[3] == EMPTY_LAYER
            ):
                self.move(grid, -1, 1)
                self.chance = random.random()
            elif neighbors[7] == EMPTY_LAYER and neighbors[4] == EMPTY_LAYER:
                self.move(grid, 1, 1)
                self.chance = random.random()


# Water Cell
# Layer: 3
class Water(Cell):
    def __init__(self, position=(0, 0)):
        super().__init__("water", position, WATER_LAYER)

        self.color = (0, 100, 255)
        self.direction = random.choice([0, 1])

    # Updates the cell
    def update(self, grid, cell_dict):
        neighbors = self.neighbors(grid)

        # Move up if there is sand where there is water
        if neighbors[8] == SAND_LAYER:
            self.move(grid, 0, -1, SAND_LAYER)
        # Move down if possible, update random moving direction
        elif neighbors[6] in [EMPTY_LAYER, FIRE_LAYER]:
            self.move(grid, 0, 1)
            self.direction = random.choice([0, 1])
        else:
            # Fall to the sides
            if (
                random.choice([0, 1])
                and neighbors[5] in [EMPTY_LAYER, FIRE_LAYER]
                and neighbors[3] in [EMPTY_LAYER, FIRE_LAYER]
            ):
                self.move(grid, -1, 1)
            elif neighbors[7] in [EMPTY_LAYER, FIRE_LAYER] and neighbors[4] in [
                EMPTY_LAYER,
                FIRE_LAYER,
            ]:
                self.move(grid, 1, 1)
            else:
                # If the direction is right and is available to move to, move to the right
                if self.direction and neighbors[3] in [EMPTY_LAYER, FIRE_LAYER]:
                    self.move(grid, -1, 0)
                # Check if you can move to the left and direction is left
                elif neighbors[4] in [EMPTY_LAYER, FIRE_LAYER]:
                    self.move(grid, 1, 0)
                    # self.direction = 0 if self.direction == 1 else 1
                # Recheck right and move
                elif neighbors[3] in [EMPTY_LAYER, FIRE_LAYER]:
                    self.move(grid, -1, 0)
                    self.direction = 0 if self.direction == 1 else 1
                # Flip direction
                else:
                    self.direction = 0 if self.direction == 1 else 1

        self.color = (
            0,
            100 - self.position[1],
            255 - self.position[1],
        )


# Fire Cell
# Layer: 4
class Fire(Cell):
    def __init__(self, position=(0, 0)):
        super().__init__("fire", position, FIRE_LAYER)

        variation = random.randrange(10, 100)
        self.color = (255 - variation, 120 - variation, 0)
        self.direction = random.choice([0, 1])
        self.lifetime = 200

    # Update Cell
    def update(self, grid, cell_dict):
        neighbors = self.neighbors(grid)

        self.lifetime -= 1

        # Move fire upwards and less to the sides
        normal = random.normalvariate(5, 10)
        # if random.random() < 0.2:
        # pass
        if neighbors[8] == WATER_LAYER:
            self.remove(grid, cell_dict)
            return

        if normal < 2 and neighbors[0] == EMPTY_LAYER and neighbors[3] == EMPTY_LAYER:
            self.move(grid, -1, -1)
        elif normal > 8 and neighbors[1] == EMPTY_LAYER and neighbors[4] == EMPTY_LAYER:
            self.move(grid, 1, -1)
        elif neighbors[1] == EMPTY_LAYER:
            self.move(grid, 0, -1)
        elif (
            self.direction
            and neighbors[1] == FIRE_LAYER
            and neighbors[3] == EMPTY_LAYER
        ):
            self.move(grid, -1, 0)
        elif neighbors[1] == FIRE_LAYER and neighbors[4] == EMPTY_LAYER:
            self.move(grid, 1, 0)
        elif (
            neighbors[0] == -1
            or neighbors[1] == -1
            or neighbors[2] == -1
            or self.lifetime <= 0
        ):
            self.remove(grid, cell_dict)
        else:
            self.direction = random.choice([0, 1])

        if SOLID_LAYER in neighbors:
            # print(neighbors)
            # Loop through neighboring
            for y in range(-1, 2):
                for x in range(-1, 2):
                    for cell in cell_dict["burn solid"]:
                        # Get the solid cell
                        if cell.position == (
                            self.position[0] + x,
                            self.position[1] + y,
                        ):
                            if cell.burn_damage < 0:
                                cell.remove(grid, cell_dict)
                                grid[cell.position[0]][cell.position[1]] = 2
                                cell_dict["fire"].append(
                                    Fire((cell.position[0], cell.position[1]))
                                )
                            else:
                                cell.burn_damage -= 1
