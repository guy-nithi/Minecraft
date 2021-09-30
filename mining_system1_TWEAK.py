from random import randrange, randint, random
from ursina import Entity, color, Vec3
from numpy import floor

class Mining_system:
    def __init__(self, _subject, _axe, _camera, _subsets, _megasets):

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
        self.megasets = _megasets

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
        self.blockTypes.append(color.rgba(72,49,33,255))
        # Redstone
        self.blockTypes.append(color.rgb(255,80,100))
        # Netherite
        self.blockTypes.append(color.rgb(0,0,0))
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

        if key == '1': self.blockType=0
        if key == '2': self.blockType=1
        if key == '3': self.blockType=2
        if key == '4': self.blockType=3
        if key == '5': self.blockType=4

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

    def adjustShadeAndRotation(self, _block):
        from copy import copy
        # Change colour to soil
        _block.color = copy(self.blockTypes[2])
        # Adjust the tintt of this block;s colour.
        shade = randrange(-16,64)/256
        _block.color[0] += shade
        _block.color[1] += shade
        _block.color[2] += shade
        # Add random rotation.
        _block.rotation_y = (90 * randint(0,3))
        _block.rotation_z = (90 * randint(0,3))
        _block.rotation_x = (90 * randint(0,3))

    def mineSpawn(self):
        from copy import copy # For copying colours.
        # Spawn one block below dig position?
        if self.tDic.get('x'+str(self.bte.x)+'y'+str(self.bte.y-1)+'z'+str(self.bte.z)) == None:
            
            # record gap location in dictionary.
            self.tDic['x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z)] = 'gap'

            e = Entity(model=self.cubeModel, texture=self.buildTex)
            # Shrink spawned block block so that it
            # matches the size of ordinary terrain.
            e.scale *= 0.99999
            e.position = self.bte.position
            e.y -= 1

            self.adjustShadeAndRotation(e)

            # Parent spawned cube into build entity.
            e.parent = self.builds
            # Record newly spawned block on dictionary.
            self.tDic['x'+str(self.bte.x)+'y'+str(e.y)+'z'+str(self.bte.z)] = e.y
            self.builds.combine()

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
                        e.position = spawnPos[i]
                        self.adjustShadeAndRotation(e)
                        # Parent spawned cube into build entity.
                        e.parent = self.builds
                        # Record newly spawned block on dictionary.
                        self.tDic['x'+str(x)+'y'+str(y)+'z'+str(z)] = e.y

    # Place a block at the bte's position
    def build(self):
        if self.buildMode == -1: return

        # Is there already a block here?
        whatsHere = self.tDic.get('x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z))
        # Is so, return. No buildy
        if whatsHere != 'gap' and whatsHere != None:
            return


        e = Entity(model=self.cubeModel, position =self.bte.position)
        # e.collider = 'box'
        # e.texture = self.stoneTex
        e.texture = self.buildTex
        e.scale *= 0.99999
        # Netherite colour for testing :)
        e.color = self.blockTypes[4]
        e.color = self.blockTypes[self.blockType]
        e.parent = self.builds
        self.tDic['x'+str(e.x)+'y'+str(e.y)+'z'+str(e.z)] = 'b'
        self.builds.combine()
        # Shaking animation won;t work since we're destorying the temp block(.combine()).
        # e.shake(duration=0.5,speed=0.01)

    def mine(self):

        vChange = False
        totalV = 0
        for v in self.builds.model.vertices:
            if (v[0] >=self.bte.x - 0.5 and
                v[0] <=self.bte.x + 0.5 and
                v[1] >=self.bte.y - 0.5 and
                v[1] <=self.bte.y + 0.5 and
                v[2] >=self.bte.z - 0.5 and
                v[2] <=self.bte.z + 0.5):

                v[1] = 9999
                vChange = True
                totalV += 1
                if totalV >= 36: break

        if vChange == True:
            
            whatsHere = self.tDic.get('x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z))
            self.tDic['x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z)] = 'gap'
            if whatsHere != 'b':
                self.mineSpawn()
                self.builds.combine()
            # Update builds model Entity so that we
            # See the gaps -- update vertices
            self.builds.model.generate()
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
                    totalV += 1
                    # The mystery of 36 vertices!! :o
                    # print('TotalV = ' + str(totalV))
                    if totalV==36: break
            if vChange == True:
                self.tDic['x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z)] = 'gap'
                self.mineSpawn()
                # Now that we've spawned what (if anything)
                # we need to, update subset model. Done.
                self.subsets[s].model.generate()
                self.builds.combine()
                return

        totalV = 0
        for s in range(len(self.megasets)):
            vChange = False
            for v in self.megasets[s].model.vertices:
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
                    totalV += 1
                    # The mystery of 36 vertices!! :o
                    # print('TotalV = ' + str(totalV))
                    if totalV==36: break
            if vChange == True:
                self.tDic['x'+str(self.bte.x)+'y'+str(self.bte.y)+'z'+str(self.bte.z)] = 'gap'
                self.mineSpawn()
                # Now that we've spawned what (if anything)
                # we need to, update subset model. Done.
                self.megasets[s].model.generate()
                self.builds.combine()
                return