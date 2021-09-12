from perlin_noise import PerlinNoise
from ursina import Entity, color, Vec3

class Trees:
    def __init__(self):
        self.noise = PerlinNoise(seed=4)

    def checkTree(self, _x, _y, _z):
        freq = 5
        amp = 100
        TreeChance = ((self.noise([_x/freq,_z/freq]))*amp)
        print(str(TreeChance))
        if TreeChance > 30:
            self.plantTree(_x, _y, _z)

    def plantTree(self, _x, _y, _z):
        from random import randint
        tree = Entity(model = None, position=Vec3(_x,_y,_z))
        crown = Entity(model='cube',scale=6,y=7,color=color.green)
        trunk = Entity(model='cube',scale_y=9,scale_x = 0.6,scale_z = 0.6,color=color.brown, collider='box')
        crown.parent = tree
        trunk.parent = tree
        tree.y += 4
        tree.rotation_y = randint(0,360)