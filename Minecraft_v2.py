from random import randrange
from numpy.core.shape_base import block
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor,abs,sin,cos,radians
import time
from perlin_noise import PerlinNoise
from nMap import nMap
from cave_system import Caves
from tree_system import Trees
from mining_system1 import Mining_system

app = Ursina()

# Our main character.
subject = FirstPersonController()
subject.cursor.visible = True
subject.gravity = 0
grav_speed = 0
grav_acc = 0.1
subject.x = subject.z = 5
subject.y = 32
prevZ = subject.z
prevX = subject.x
origin = subject.position # Vec3 object? .x .y .z

# Load in texutre and model
grassStokeTex = 'grass_14.png'
monoTex = 'stroke_mono.png'
stoneTex = 'grass_mono.png'

cubeTex = 'block_texture.png'
cubeModel = 'MoonCube'

axoTex = 'axolotl.png'
axoModel = 'axolotl.obj'

axeModel = 'Diamond-Pickaxe'
axeTex = 'diamond_axe_tex'

# Important variables
noise = PerlinNoise(octaves=1, seed=int(randrange(99,111)))
seedMouth = Text(text='<white><bold>Your seed, today, sir, is ' +str(noise.seed), background=True)
seedMouth.scale *= 1.4
seedMouth.background.color = color.blue
seedMouth.x = -0.52
seedMouth.y = 0.4
seedMouth.appear(speed=0.15)
# print('seed is ' + str(noise.seed))

megasets = []
subsets = []
subCubes = []
# New variables :)
generating = 1 # -1 if off.
canGenerate = 1 # -1 if off.
genSpeed = 0
perCycle = 64
currentCube = 0
currentSubset = 0
currentMegaset = 0
numSubCubes = 64
numSubsets = 10 # I.e. how many combined into a megaset?
theta = 0
rad = 0
subDic = {}

def createTerrainEntities():
    for i in range(numSubCubes):
        bud = Entity(model=cubeModel,texture=cubeTex)
        bud.scale *= 0.99999
        bud.rotation_y = random.randint(1,4)*90
        bud.disable()
        subCubes.append(bud)

    # Instantiate our empty subset.
    for i in range(numSubsets):
        bud = Entity(model=cubeModel)
        bud.texture = cubeTex
        bud.disable()
        subsets.append(bud)

    # Instantiate our empty megasets.
    for i in range(99):
        bud = Entity(model=cubeModel)
        bud.texture = cubeTex
        bud.scale *= 0
        bud.disable()
        megasets.append(bud)

createTerrainEntities()

# save and load file functions :D
def save():
    global subDic, megasets, subsets, subCubes, noise
    import pickle, os, sys
    # Create a new entity that combiens all our
    # subsets and megasets, which we can
    # place onto a file.

    # First, let's open/create a file in the
    # folder we are working in (working directory)
    # that we can save to
    path = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(path)
    with open('pickling.txt','wb') as f:
        e = Entity()
        for s in subsets:
            if s.enabled == True:
                s.parent = e
        for m in megasets:
            if m.enabled == True:
                m.parent = e
        e.combine(auto_destroy=False)
        terrainModel = [    e.model.vertices,
                            e.model.triangles,
                            e.model.colors,
                            e.model.uvs]
        buildsModel = [ varch.builds.model.vertices,
                        varch.builds.model.triangles,
                        varch.builds.model.colors,
                        varch.builds.model.uvs]
        for s in subsets:
            s.parent = scene
        for m in megasets:
            m.parent = scene
        destroy(e)

        newlist = [ subject.position,
                    varch.tDic,
                    subDic,
                    terrainModel,
                    noise,
                    buildsModel
                    ]

        # Write game state objects to file.
        pickle.dump(newlist, f)
        # Clear out temporary lists.
        newlist.clear()
        terrainModel.clear()

def load():
    import pickle, sys, os
    global subDic, rad, theta, currentSubset
    global currentCube, currentMegaset, noise
    global canGenerate, generating

    # Open main module directory for correct file
    path = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(path)

    with open('pickling.txt', 'rb') as f:
        nd = pickle.load(f)

        # Populate our familiar terrain variables
        # with data from the saved file

        subject.position = copy(nd[0])
        varch.tDic = copy(nd[1])
        subDic = copy(nd[2])
        tm = copy(nd[3])
        noise = copy(nd[4])
        bm = copy(nd[5])

        # Now, let's delete all the current terrain
        # And builds!
        for s in subCubes:
            destroy(s)
        for s in subsets:
            destroy(s)
        for m in megasets:
            destroy(m)
        destroy(varch.builds)
        subCubes.clear()
        subsets.clear()
        megasets.clear()

        createTerrainEntities()
        # Reset terrain generation variables.

        megasets[0] = Entity(model=Mesh(
                        vertices=tm[0],
                        triangles=tm[1],
                        colors=tm[2],
                        uvs=tm[3]),
                        texture=cubeTex)

        varch.builds = Entity(model=Mesh(
                        vertices=bm[0],
                        triangles=bm[1],
                        colors=bm[2],
                        uvs=bm[3]),
                        texture=cubeTex)
        
        currentCube = 0
        currentMegaset = 1
        currentSubset = 0
        rad = 0
        theta = 0
        generating = -1
        canGenerate = -1
        subject.rotation_x = 0.0

# Our pickaxe :D
pickaxe = Entity(model=axeModel,texture=axeTex,scale=0.07,position=subject.position,always_on_top=True)
pickaxe.x -= 3
pickaxe.z -= 2.2
pickaxe.y -= subject.y
pickaxe.rotation_z = 90
pickaxe.rotation_y = 180

pickaxe.parent=camera
 
anush = Caves()
sol4r = Trees()

# And again, but for out mining system (built tools etc.).
varch = Mining_system(subject, pickaxe, camera, subsets, megasets)

window.color = color.rgb(0,200,211)
window.exit_button.visible = False

prevTime = time.time()

scene.fog_color = color.rgb(0,222,0)
scene.fog_density = 0.02

def input(key):
    global generating, canGenerate

    # Deal with mining system's key inputs. Thanks.
    varch.input(key) 

    if key == 'q' or key == 'escape':
        quit()
    if key == 'g': 
        generating *= -1
        canGenerate *= -1
    if varch.buildMode == 1:
        generating = -1
        canGenerate = -1

    if key == 'b':
        save()

    if key == 'n':
        load()

def update():
    global prevZ, prevX, prevTime, genSpeed, perCycle
    global rad, origin, generating, canGenerate, theta
    if abs(subject.z - prevZ) > 1 or \
        abs(subject.x - prevX) > 1:
        origin = subject.position
        rad = 0
        theta = 0
        generating = 1 * canGenerate
        prevZ = subject.z
        prevX = subject.x

            
    generateShell()

    if time.time() - prevTime > genSpeed:
        for i in range(perCycle):
            genTerrain()
        prevTime = time.time()

    vincent.look_at(subject, 'forward')
    # vincent.rotation_x = 0

    # Controls mining and building function
    varch.buildTool()

for i in range(numSubCubes):
    bud = Entity(model=cubeModel,texture=cubeTex)
    bud.scale *= 0.99999
    bud.rotation_y = random.randint(1,4)*90
    bud.disable()
    subCubes.append(bud)

def genPerlin(_x, _z, plantTree=False):
    y = 0
    freq = 64
    amp = 42
    y += ((noise([_x/freq,_z/freq]))*amp)
    freq = 32
    amp = 21
    y += ((noise([_x/freq,_z/freq]))*amp)

    # is there are cave-gap here?
    # if so, lower the cube by 32...or something ;)
    whatCaveHeight = anush.checkCave(_x, _z)
    if whatCaveHeight != None:
        y=whatCaveHeight
    elif plantTree==True:
        sol4r.checkTree(_x, y, _z)
    return floor(y)

def genTerrain():
    global currentCube, theta, rad, currentSubset
    global generating, currentMegaset

    if generating == -1: return

    # Decide where to place new terrain cube!!!!!!!!
    x = floor(origin.x + sin(radians(theta)) * rad)
    z = floor(origin.x + cos(radians(theta)) * rad)
    # Check whether there is terrain here already
    if subDic.get('x' + str(x) + 'z' + str(z)) != 'i':
        subCubes[currentCube].enable()
        subCubes[currentCube].x = x
        subCubes[currentCube].z = z
        subCubes[currentCube].parent = subsets[currentSubset]
        y = subCubes[currentCube].y = genPerlin(x,z,True)
        subDic['x' + str(x) + 'z'+str(z)] = 'i'
        varch.tDic['x'+str(x)+'y'+str(y)+'z'+str(z)]=y
        # OK -- time to decide colors :D
        c = nMap(y, -8, 21, 132, 212)
        c += random.randint(-32, 32)
        subCubes[currentCube].color = color.rgb(c, c, c)
        subCubes[currentCube].disable()
        currentCube += 1

        # Ready to build a subset?
        if currentCube==numSubCubes:
            subsets[currentSubset].combine(auto_destroy=False)
            subsets[currentSubset].enable()
            currentSubset+=1
            currentCube=0
            
            # And ready to build a megaset?
            if currentSubset==numSubsets:
                # Parent all subsets to our new megaset.
                for s in subsets:
                    s.parent=megasets[currentMegaset]
                # In case user has Ursina version 3.6.0.
                # safe_combine(megasets[-1],auto_destroy=False)
                megasets[currentMegaset].combine(auto_destroy=False)
                for s in subsets:
                    s.parent=scene
                    # Invisible? Delete this line :)
                    # s.disable()
                currentSubset=0
                currentMegaset+=1
                print('Megaset #' + str(len(megasets))+'!')


    else:
        pass
        # There was terrain already there, so
        # continue rotation to find new terrain spot.
    
    if rad > 0:
        theta += 45/rad
    else: rad += 0.5

    if theta >= 360:
        theta = 0
        rad += 0.5

# for i in range(terrainWidth*terrainWidth):
#     bud = Entity(model='cube',color=color.green)
#     bud.x = floor(i/terrainWidth)
#     bud.z = floor(i%terrainWidth)
#     bud.y = floor((noise([bud.x/freq,bud.z/freq]))*amp)
#     bud.parent = terrain

# terrain.combine()
# terrain.collider = 'mesh'
# terrain.texture = grassStokeTex

def generateShell():
    global subject, grav_speed, grav_acc

    # New 'new' system :D
    # How high or low can we step/drop?
    step_height = 3
    gravityON = True
    
    target_y = subject.y

    for i in range(step_height,-step_height,-1):
        # What y is the terrain at this position?
        # terra = genPerlin(subject.x,subject.z)
        terra = varch.tDic.get( 'x'+str((floor(subject.x)))+
                                'y'+str((floor(subject.y+i)))+
                                'z'+str((floor(subject.z+0.5))))
        terraTop = varch.tDic.get( 'x'+str((floor(subject.x)))+
                                   'y'+str((floor(subject.y+i+1)))+
                                   'z'+str((floor(subject.z+0.5))))
        if terra != None and terra != 'gap':
            gravityON = False
            if terraTop == None or terraTop == 'gap':
                # print('TERRAIN FOUND! ' + str(terra + 2))
                target_y = floor(subject.y+i)# + 2
                break

            subject.x -= 0.6
            subject.z -= 0.6

    if gravityON==True:
        # This means we're falling!
        grav_speed += (grav_acc * time.dt)
        subject.y -= grav_speed
    else:
        subject.y = lerp(subject.y, target_y, 9.807*time.dt)
        grav_speed = 0 # Reset gravity speed: gfloored.


    # 'new' old system
    """
    # How high or low can we step/drop?
    step_height = 5

    # What y is the terrain at this position
    target_y = genPerlin(subject.x, subject.z)
    # Check if target is too high...
    # How far are we from the target y?
    target_dist = target_y - subject.y
    #Can we step up or down?
    if target_dist < step_height and target_dist > -step_height:
        subject.y = lerp(subject.y, target_y, 9.807*time.dt)
    elif target_dist < -step_height:
        # This means we're falling!
        grav_speed += grav_acc * time.dt
        subject.y -= grav_speed
    """

    # global shellWidth
    # for i in range(len(shellies)):
    #     x = shellies[i].x = floor((i/shellWidth) + subject.x - 0.5*shellWidth)
    #     z = shellies[i].z = floor((i%shellWidth) + subject.z - 0.5*shellWidth)
    #     shellies[i].y = genPerlin(x,z)

chickenModel = load_model('chicken.obj')
vincent = Entity(model=chickenModel,scale=1,x=22,z=16,y=4,texture='chicken.png',double_sided=True)

vincent2 = Entity(model=chickenModel,scale=1,x=99,z=16,y=4,texture='chicken.png',double_sided=True)

cyan_axolotl = Entity(model=axoModel,scale=10,x=-22,z=16,y=4,texture=axoTex,double_sided=True)

cyan2_axolotl = Entity(model=axoModel,scale=10,x=-99,z=16,y=4,texture=axoTex,double_sided=True)

generateShell()

app.run()