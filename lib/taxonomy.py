#taxonomy.py

class Game():
    def __init__(self, game) -> None:
        self.game = game
        
class Dimension(Game):
    def __init__(self, game, dimension) -> None:
        super().__init__(game)
        self.dimension = dimension

class Plane(Dimension):
    def __init__(self, game, dimension, plane) -> None:
        super().__init__(game, dimension)
        self.plane = plane

class World(Plane):
    def __init__(self, game, dimension, plane, world) -> None:
        super().__init__(game, dimension, plane)
        self.world = world

class Land(World):
    def __init__(self, game, dimension, plane, world, land) -> None:
        super().__init__(game, dimension, plane, world)
        self.land = land

class Region(Land):
    def __init__(self, game, dimension, plane, world, land, region) -> None:
        super().__init__(game, dimension, plane, world, land)
        self.region = region

class Area(Region):
    def __init__(self, game, dimension, plane, world, land, region, area) -> None:
        super().__init__(game, dimension, plane, world, region)
        self.area = area

class Section(Area):
    def __init__(self, game, dimension, plane, world, land, region, area, section) -> None:
        super().__init__(game, dimension, plane, world, land, region, area)
        self.section = section

class Location(Section):
    def __init__(self, game, dimension, plane, world, land, region, area, section, location) -> None:
        super().__init__(game, dimension, plane, world, land, region, area, section)
        self.location = location

class Level(Location):
    def __init__(self, game, dimension, plane, world, land, region, area, section, location, level) -> None:
        super().__init__(game, dimension, plane, world, land, region, area, section, location)
        self.level = level

class Position(Level):
    def __init__(self, game, dimension, plane, world, land, region, area, section, location, level, position) -> None:
        super().__init__(game, dimension, plane, world, land, region, area, section, location, level)
        self.position = position

class Encounter(Level):
    def __init__(self, game, dimension, plane, world, land, region, area, section, location, level, position, encounter) -> None:
        super().__init__(game, dimension, plane, world, land, region, area, section, location, level, position)
        self.encounter = encounter
    