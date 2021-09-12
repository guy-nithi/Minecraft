class Caves:
    def __init__(self):
        self.caveDic = {}
        self.buildCaves()

    def buildCaves(self):
        self.caveDic = { 'x9z9': -9, 'x10z9': -9, 'x11z9': -9, 'x9z10': -9, 'x9z11': -9}

    def checkCave(self, _x, _z):
        tempStr = self.caveDic.get('x'+str(int(_x)) +'z'+str(int(_z)))
        return tempStr

    def makeCave(self,_x,_z,_height):
        tempStr = ('x'+str(int(_x)) +'z'+str(int(_z)))
        self.caveDic[tempStr] = _height