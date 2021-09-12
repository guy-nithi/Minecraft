from ursina import Entity, color, Vec3
from numpy import floor

class Mining_system:
    def __init__(self, _subject, _axe, _camera, _subsets):

        # We create a reference to these here,
        # so that we can use them in this buildTool()
        # and elsewhere?
        self.subject = _subject
        self.camera = _camera
        self.axe = _axe

        self.tDic = {}
        self.buildTex = 'build_texture.png'
        self.cubeModel = 'moonCube.obj'
        self.builds = Entity(model=self.cubeModel,texture=self.buildTex)

        self.subsets = _subsets

        self.wireTex = 'wireframe.png'
        self.stoneTex = 'grass_mono.png'
        # Build tool entity -- floating wireframe cube.
        self.bte = Entity(model='cube',texture=self.wireTex,scale=1.01)
        
        self.build_distance = 3

        self.buildMode = -1

        # Our new block type system...
        self.blockTypes = []
        # Stone
        self.blockTypes.append(color.rgb(255, 255, 255))
        # Grass
        self.blockTypes.append(color.rgb(0,255,0))
        # dirt
        self.blockTypes.append(color.rgb(255,0,0))
        # Redstone
        self.blockTypes.append(color.rgb(255,80,100))
        # Netherite
        self.blockTypes.append(color.rgb(0, 0, 0))
        # Our current block type.
        self.blockType = 0 # I.e. stone

    def input(self, key):
        if key == 'scroll up':
            self.build_distance += 1
        if key == 'scroll down':
            self.build_distance -= 1

        if self.buildMode == 1 and key == 'right mouse up':
            # e = mouse.hovered_entity
            # if not e:
            self.build()
            self.axe.shake(duration=0.3, magnitude=7, direction=(-1, 1))
            # self.axe.position = Vec3(0.3, -0.5, 2.8)
        elif self.buildMode == 1 and key == 'left mouse up':
            self.mine()
            self.axe.shake(duration=0.3, magnitude=7, direction=(-1, 1))
            # self.axe.position = Vec3(0.3, -0.5, 2.8)
        # else:
            # self.axe.position = Vec3(2, 0, 2.8)
            # I.e. return axe to defualt position if not in build mode


        if key == 'f': self.buildMode *= -1
        """
        if key == '1': blockType=BTYPE.GRASS
        if key == '2': blockType=BTYPE.STONE
        if key == '3': blockType=BTYPE.DIRT
        if key == '4': blockType=BTYPE.REDSTONE
        """    

    # This is called from the main update loop.
    def buildTool(self):
        if self.buildMode == -1:
            self.bte.visible = False
            return
        else: self.bte.visible = True
        self.bte.position = round(self.subject.position + self.camera.forward * self.build_distance)
        self.bte.y += 2
        self.bte.y = round(self.bte.y)
        self.bte.x = round(self.bte.x)
        self.bte.z = round(self.bte.z)
        self.bte.color = self.blockTypes[self.blockType]

    def mineSpawn(self):
        # Spawn one block below dig position?
        if self.tDic.get('x'+str(self.bte.x)+'y'+str(self.bte.y-1)+'z'+str(self.bte.z)) == None:
            
            # record gap location in dictionary.
            self.tDic['x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z)] = 'gap'

            e = Entity(model=self.cubeModel, texture=self.buildTex)
            # Shrink spawned block block so that it
            # matches the size of ordinary terrain.
            e.scale *= 0.99999
            e.color = self.blockTypes[0]
            e.position = self.bte.position
            e.y -= 1
            # Parent spawned cube into build entity.
            e.parent = self.builds
            # Record newly spawned block on dictionary.
            self.tDic['x'+str(self.bte.x)+'y'+str(e.y)+'z'+str(self.bte.z)] = e.y

        # OK -- now spawn 4 'cave wall' cubes.
        # For each cube, first check whether:
        # 1) No terrain there already
        # 2) No gaps
        # 3) No terrain below this pos
        x = self.bte.x
        y = self.bte.y
        z = self.bte.z
        pos1 = (x+1,y,z)
        pos2 = (x-1,y,z)
        pos3 = (x,y,z+1)
        pos4 = (x,y,z-1)
        spawnPos = []
        spawnPos.append(pos1)
        spawnPos.append(pos2)
        spawnPos.append(pos3)
        spawnPos.append(pos4)
        for i in range(4):
            x = spawnPos[i][0]
            z = spawnPos[i][2]
            y = spawnPos[i][1]

            # We can ask None both times because
            # this covers both gaps and terrain
            # being in these position(i.e
            # potential cave wall and below
            # potential cave wall.
            if self.tDic.get('x'+str(x)+'y'+str(y)+'z'+str(z)) == None and \
                self.tDic.get('x'+str(x)+'y'+str(y-1)+'z'+str(z)) == None:
                    e = Entity(model=self.cubeModel, texture=self.buildTex)
                    # Shrink spawned block block so that it
                    # matches the size of ordinary terrain.
                    e.scale *= 0.99999
                    e.color = self.blockTypes[0]
                    e.position = spawnPos[i]
                    # Parent spawned cube into build entity.
                    e.parent = self.builds
                    # Record newly spawned block on dictionary.
                    self.tDic['x'+str(x)+'y'+str(y)+'z'+str(z)] = e.y

    # Place a block at the bte's position
    def build(self):
        if self.buildMode == -1: return
        e = Entity(model=self.cubeModel, position =self.bte.position)
        # e.collider = 'box'
        # e.texture = self.stoneTex
        e.texture = self.buildTex
        e.scale *= 0.99999
        # Netherite colour for testing :)
        e.color = self.blockTypes[4]
        # e.color = self.blockTypes[self.blockType]
        e.parent = self.builds
        self.tDic['x'+str(e.x)+'y'+str(e.y)+'z'+str(e.z)] = 'b'
        self.builds.combine()
        # Shaking animation won;t work since we're destorying the temp block(.combine()).
        # e.shake(duration=0.5,speed=0.01)

    def mine(self):

        vChange = False

        for v in self.builds.model.vertices:
            if (v[0] >=self.bte.x - 0.5 and
                v[0] <=self.bte.x + 0.5 and
                v[1] >=self.bte.y - 0.5 and
                v[1] <=self.bte.y + 0.5 and
                v[2] >=self.bte.z - 0.5 and
                v[2] <=self.bte.z + 0.5):

                v[1] = 9999
                vChange = True
                self.tDic['x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z)] = 'gap'

        if vChange == True:
            buildBlock = True
            if self.tDic.get('x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z)) \
                != 'b':
                buildBlock = False
                self.mineSpawn()
            self.builds.model.generate()
            if buildBlock == False:
                self.builds.combine()
            # Not done! Also combine newly spawned blocks
            # into builds entity :)
            return
        
        totalV = 0
        for s in range(len(self.subsets)):
            vChange = False
            for v in self.subsets[s].model.vertices:
                if (v[0] >=self.bte.x - 0.5 and
                    v[0] <=self.bte.x + 0.5 and
                    v[1] >=self.bte.y - 0.5 and
                    v[1] <=self.bte.y + 0.5 and
                    v[2] >=self.bte.z - 0.5 and
                    v[2] <=self.bte.z + 0.5):
                    # Yes!
                    # v[1] -= 1
                    # move vertex high into air to
                    # give illusion of being destroyed
                    v[1] = 9999
                    vChange = True
                    self.tDic['x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z)] = 'gap'
                    totalV += 1
                    # The mystery of 36 vertices!! :o
                    # print('TotalV = ' + str(totalV))
                    if totalV==36: break
            if vChange == True:
                self.mineSpawn()
                # Now that we've spawned what (if anything)
                # we need to, update subset model. Done.
                self.subsets[s].model.generate()
                self.builds.combine()
                return