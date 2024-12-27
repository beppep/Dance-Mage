import pygame
import time
import random
import os
import math

clock = pygame.time.Clock()
SOUND_PATH = os.path.join("assets", "sounds")
pygame.init()
pygame.display.init()

infoObject = pygame.display.Info()
SCREENSIZE = (infoObject.current_w, infoObject.current_h)
FRAMERATE = 60
GRIDSIZE = 64
ANIMATION_MULTIPLIER = 1

gameDisplay = pygame.display.set_mode(SCREENSIZE)
#gameDisplay = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("Dance Mage")
pygame.display.set_icon(pygame.image.load(os.path.join("assets", "textures", "player", "player.png")))

def blitRotate(image, pos, originPos, angle = 0):
    if angle == 0:
        gameDisplay.blit(image, (pos[0]-originPos[0], pos[1]-originPos[1]))

    # calcaulate the axis aligned bounding box of the rotated image
    w, h       = image.get_size()
    box        = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box    = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box    = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

    # calculate the translation of the pivot 
    pivot        = pygame.math.Vector2(originPos[0], -originPos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move   = pivot_rotate - pivot

    # calculate the upper left origin of the rotated image
    origin = (int(pos[0] - originPos[0] + min_box[0] - pivot_move[0] + game.currentScreenShake[0]), int(pos[1] - originPos[1] - max_box[1] + pivot_move[1] + game.currentScreenShake[1]))

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    gameDisplay.blit(rotated_image, origin)

def AtoV(a):
    return [(1,0),(0,-1),(-1,0),(0,1)][a//90]
def VtoA(v):
    return [(1,0),(0,-1),(-1,0),(0,1)].index(v)*90
def applySymmetry(vector, symmetry): # a symmetry = (rotation_angle, mirrored)
    if vector == (0,0):
        return (0,0)
    else:
        ang = (VtoA(vector)*symmetry[1] + symmetry[0])%360
        return AtoV(ang)

def changeTextbox(dabox, datext):
    dabox.html_text=str(datext)
    dabox.rebuild()

def loadImage(path, dims = (1,1)):
    image = pygame.image.load(os.path.join("assets", "textures", path))
    
    image = pygame.transform.scale(image, (GRIDSIZE*dims[0], GRIDSIZE*dims[1]))
    return image

def initSound():
    volume = 0.5
    music_volume = 0
    pygame.font.init() # you have to call this at the start, 
                           # if you want to use this module.
    pygame.mixer.init(buffer=32)

    Sound.crushSounds = []
    Sound.wallSounds = []
    for i in range(10):
        Sound.crushSounds.append(pygame.mixer.Sound(os.path.join(SOUND_PATH, "crush"+str(i+1)+".wav")))
        Sound.crushSounds[i].set_volume(volume*1)
    for i in range(4):
        Sound.wallSounds.append(pygame.mixer.Sound(os.path.join(SOUND_PATH, "wall"+str(i+1)+".wav")))
        Sound.wallSounds[i].set_volume(volume*1)
    
    pygame.mixer.music.load(os.path.join(SOUND_PATH, "crushing music.wav")) #must be wav 16bit and stuff?
    pygame.mixer.music.set_volume(music_volume*0.5)
    pygame.mixer.music.play(-1)

def changeVolume(volume):
    for i in range(10):
        Sound.crushSounds[i].set_volume(volume*1)
    for i in range(4):
        Sound.wallSounds[i].set_volume(volume*1)

def playCrushSound():
    sound = random.choice(Sound.crushSounds)
    #sound.set_volume(vol*(i+1))
    sound.play()
def playWallSound():
    sound = random.choice(Sound.wallSounds)
    #sound.set_volume(vol*(i+1))
    sound.play()
def makeSmokeCloud(x,y,nr, particleName = "smoke"):
    for i in range(nr):
        particle = Particle(x, y, random.random()*360, particleName, random.randint(20,24))
        particle.xv = (random.random()-0.5)*0.1
        particle.yv = (random.random()-0.5)*0.1
        game.particles.append(particle)

class Sound():
    0

initSound()

class Game():

    def __init__(self):
        self.playerClass = None # given by some start menu idk

        # player data
        self.wavesWon = 0
        self.spellBook = [None]
        self.relics = [] #[relic() for relic in ALLRELICS] #[random.choice(ALLRELICS)()]

        # logic
        self.mode = "playing"
        self.playerActionable = True # whether the player can press a button. (no spellstack, enemy actions, animation time)
        self.spellStack = []
        self.enemyStack = []

        #visual
        self.particles = []
        self.animationTime = 0
        self.screenshake = 0
        self.currentScreenShake = (0,0)
        self.screenshakeDir = (0,0)
        self.level_over_animation = False

    def beginResolveTurn(self):
        self.playerActionable = False
        self.enemyStack = self.arena.entities[:] # randomizing turn order is not very important. can be removed
        random.shuffle(self.enemyStack)
        self.enemyStack.sort(key = lambda x: hasattr(x, "state") and x.state=="normal")

    def update(self):

        # TURN LOGIC
        
        if self.animationTime > 0:
            self.animationTime -= 1/ANIMATION_MULTIPLIER
        elif self.spellStack:
            self.spellStack[0].decoratedActivate(self.player, AtoV(self.player.angle))
            self.spellStack.pop(0)
        elif self.enemyStack:
            if self.enemyStack[0] in self.arena.entities:
                self.enemyStack[0].decoratedAct()
            self.enemyStack.pop(0)
        else:
            self.playerActionable = True
            if self.player.shield > 0:
                self.player.shield -= 1

            # ROUND CLEARED LOGIC
            
            if self.mode == "playing" or self.mode == "practice":
                if len([enemy for enemy in self.arena.entities if isinstance(enemy, Enemy)])==0:
                    if self.mode=="playing":
                        self.wavesWon += 1
                        self.mode = "rewards"
                        self.generateRewards()
                    else:
                        self.startWave()

        # VISUAL LOGIC
        
        if self.screenshake>0:
            ampl = 2
            self.currentScreenShake = [(random.random()-0.5)*2*self.screenshake*ampl, ((random.random()-0.5)*2*self.screenshake*ampl)]
            self.currentScreenShake[0] += self.screenshake*ampl*self.screenshakeDir[0]
            self.currentScreenShake[1] += self.screenshake*ampl*self.screenshakeDir[1]
            self.screenshake -= 0.5
        else:
            self.screenshake = 0

        for particle in self.particles:
            particle.update()

    def generateRewards(self):
        self.rewardOptions = []
        rewardOptions = ALLSPELLS + ALLRELICS
        random.shuffle(rewardOptions)
        for i in range(3):
            self.rewardOptions.append(rewardOptions[i]())

    def selectReward(self, n):
        reward = self.rewardOptions[n]
        if isinstance(reward, Spell):
            self.spellBook.append(reward)
        elif isinstance(reward, Relic):
            self.relics.append(reward)
            ALLRELICS.remove(reward.__class__)
            reward.obtained()
        self.startPractice()

    def startPractice(self):
        self.mode = "practice"
        self.arena = Arena(8,8)
        self.player = self.playerClass((3,3))
        self.arena.entities.append(StartCrystal((3,1)))

    def startWave(self):
        self.mode = "playing"
        w = random.randint(0, self.wavesWon)
        h = self.wavesWon - w
        self.arena = Arena(4 + w, 4 + h)
        self.player = self.playerClass((3,3))
        self.arena.generateWave(3 + self.wavesWon*5)

    def draw(self):
        gameDisplay.fill((0,0,0))
        self.arena.draw()
        self.player.draw()

        for particle in self.particles:
            particle.draw()

        if self.mode == "rewards":
            MARGINS = 100
            pygame.draw.rect(gameDisplay, (100,100,120), (MARGINS,MARGINS,SCREENSIZE[0]-MARGINS*2,SCREENSIZE[1]-MARGINS*2))
            for i in range(len(self.rewardOptions)):
                self.rewardOptions[i].drawBig(i)
        if self.mode == "playing":
            bigtext = "Wave "+str(self.wavesWon+1)
        elif self.mode == "practice":
            bigtext = "Practice!"
        else:
            bigtext = "Choose Reward:"
        myfont = pygame.font.SysFont('Calibri', 64)
        textsurface = myfont.render(bigtext, True, (220, 220, 220))
        blitRotate(textsurface, (SCREENSIZE[0]//2, 50), (textsurface.get_width()//2, textsurface.get_height()//2))    

        self.player.drawUI()

        for i in range(len(self.relics)):
            self.relics[i].draw(i)

    def shakeScreen(self, amount, dPos):
        self.screenshake = max(self.screenshake, amount)
        self.screenshakeDir = dPos

    controls = {
        pygame.K_a : (-1,0), pygame.K_d : (1,0), pygame.K_w : (0,-1), pygame.K_s : (0,1), 
        pygame.K_LEFT : (-1,0), pygame.K_RIGHT : (1,0), pygame.K_UP : (0,-1), pygame.K_DOWN : (0,1), pygame.K_SPACE : (0,0)
    }

class Arena():

    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.entities = []

    def randomLocation(self, empty = False, fat=1):
        loc = (random.randint(0,self.width-fat), random.randint(0,self.height-fat))
        if empty==False:
            return loc
        else:
            while self.entity_at(*loc, fat=fat):
                loc = (random.randint(0,self.width-fat), random.randint(0,self.height-fat))
            return loc

    def inbounds(self, x, y, fat=1):
        return 0<=x and x+fat-1<=self.width-1 and 0<=y and y+fat-1<=self.height-1

    def enemy_at(self, x, y, fat=1, ignore = None): # non - player entity
        for enemy in self.entities:
            if enemy.x <= x+fat-1 and x <= enemy.x + enemy.fat-1 and enemy.y <= y+fat-1 and y <= enemy.y + enemy.fat-1:
                if not ignore == enemy:
                    return enemy
        return None

    def entity_at(self, x, y, fat=1, ignore = None):
        if game.player.x <= x+fat-1 and x <= game.player.x + game.player.fat-1 and game.player.y <= y+fat-1 and y <= game.player.y + game.player.fat-1:
            if not ignore == game.player:
                return game.player
        return self.enemy_at(x, y, fat=fat, ignore = ignore)

    def get_topleft(self):

        x = SCREENSIZE[0]//2 - game.player.x*GRIDSIZE - GRIDSIZE//2
        y = SCREENSIZE[1]//2 - game.player.y*GRIDSIZE - GRIDSIZE//2

        return x,y

    def generateWave(self, difficultyLevel):
        while difficultyLevel > 0:
            available_enemies = [e for e in ALLENEMIES if e.powerLevel<=difficultyLevel]
            if len(available_enemies)>0:
                #SELECT ENEMY
                enemy = random.choice(available_enemies)
                difficultyLevel -= enemy.powerLevel

                #SPAWN ENEMY
                pos = self.randomLocation(empty = True, fat = enemy.fat)
                self.entities.append(enemy(pos))
            else:
                return
        return

    def draw(self):
        topleft = self.get_topleft()

        for x in range(-1, self.width+1):
            for y in range(-1, self.height+1):
                if x==-1 or y==-1 or x==self.width or y==self.height:
                    image = self.images["rock"]
                else:
                    image = self.images["sand"]
                #rotated_image = pygame.transform.rotate(image, 0)
                #blitRotate(image, (topleft[0] + x*GRIDSIZE +GRIDSIZE//2, topleft[1] + y*GRIDSIZE +GRIDSIZE//2), (GRIDSIZE//2,GRIDSIZE//2), 0)
                blitRotate(image, (topleft[0] + x*GRIDSIZE, topleft[1] + y*GRIDSIZE), (0,0))

        for enemy in self.entities:
            enemy.draw()

    images = {}
    for i in ["sand","wood","rock","obsidian","diamond"]:
        images[i] = loadImage(os.path.join("blocks", i+".png"))

class Spell():

    def __init__(self, recipe = None):
        self.recipe = recipe
        self.current_alignment = (0,(0,1)) # (alignment_length, (degrees, mirrored))
        if self.recipe == None:
            self.generateRecipe(self.powerLevel)

    def generateRecipe(self, length):
        self.recipe = []
        for i in range(length):
            self.recipe.append(random.choice([(1,0),(-1,0),(0,1),(0,-1),(0,0)]))
        return self.recipe

    def decoratedActivate(self, player, dPos):
        self.activate(player, dPos)

        # thunder relic # lightning after can hit bomb. lightning before can change dash
        for i in range(game.player.RNG_lightnings):
            game.animationTime = 8
            pos = game.arena.randomLocation()
            while game.arena.entity_at(*pos)==player:
                pos = game.arena.randomLocation()
            entity = game.arena.enemy_at(*pos)
            if entity:
                entity.hurt(1)
            lightning = Particle(pos[0], pos[1], 0, "lightning", 8)
            game.particles.append(lightning)
            playCrushSound()

    def drawRecipe(self, position, brighted_length, symmetry):
        for i in range(len(self.recipe)):
            brighted_symbol = (brighted_length>i)
            if self.recipe[i] == (0,0):
                img = [self.darkDotImage, self.dotImage][brighted_symbol]
                angle = 0
            else:
                img = [self.darkArrowImage, self.arrowImage][brighted_symbol]
                angle = VtoA(applySymmetry(self.recipe[i], symmetry))
            blitRotate(img, (position[0]+i*GRIDSIZE,position[1]), (GRIDSIZE//2, GRIDSIZE//2), angle)

    def draw(self, height):
        blitRotate(Particle.images[self.displayIcon], (50,150+height*GRIDSIZE), (GRIDSIZE//2, GRIDSIZE//2), 0)
        self.drawRecipe((50+GRIDSIZE,150+height*GRIDSIZE), *self.current_alignment)

    def drawBig(self, rwrdNr):
        SPACING = 400
        centerPos = (SCREENSIZE[0]//2 - SPACING + SPACING*rwrdNr, SCREENSIZE[1]//2)
        
        myfont = pygame.font.SysFont('Calibri', 64)
        textsurface = myfont.render(self.displayName, True, (0, 0, 0))
        blitRotate(textsurface, (centerPos[0], centerPos[1] - SPACING//2), (textsurface.get_width()//2, textsurface.get_height()//2))

        blitRotate(Particle.images[self.displayIcon], centerPos, (GRIDSIZE//2, GRIDSIZE//2), 0)

        x = centerPos[0] - (GRIDSIZE*len(self.recipe))//2 + GRIDSIZE//2
        y = centerPos[1] + SPACING//2
        self.drawRecipe((x,y), 999, (0,1))

    arrowImage = loadImage(os.path.join("particles", "arrow.png"))
    darkArrowImage = loadImage(os.path.join("particles", "darkarrow.png"))
    dotImage = loadImage(os.path.join("particles", "dot.png"))
    darkDotImage = loadImage(os.path.join("particles", "darkdot.png"))

class StabSpell(Spell):

    powerLevel = 2
    displayName = "Slice"
    displayIcon = "slice"

    def activate(self, player, dPos):
        game.animationTime = 8
        x = player.x + dPos[0]
        y = player.y + dPos[1]
        enemy = game.arena.enemy_at(x, y)
        if enemy:
            enemy.hurt(1)
        arrow = Particle(x, y, player.angle, "slice", 10)
        game.particles.append(arrow)
        playCrushSound()
class DashSpell(Spell):

    powerLevel = 3
    displayName = "Dash/Ramm"
    displayIcon = "swoosh"

    def activate(self, player, dPos):
        game.animationTime = 10
        stopped = False
        steps_moved = 0
        while not stopped:
            if game.arena.inbounds(player.x+dPos[0], player.y+dPos[1]):
                enemy = game.arena.enemy_at(player.x+dPos[0], player.y+dPos[1])
                if enemy:
                    #enemy.hurt(1+steps_moved)
                    enemy.hurt(1)
                    #enemy.forcedMovement(dPos, steps_moved)
                    playCrushSound()
                    makeSmokeCloud(player.x+dPos[0]/2, player.y+dPos[1]/2, 3+steps_moved)
                    game.shakeScreen(3+steps_moved, dPos)
                    stopped = True
                else:
                    # SMOKE AND TRAIL
                    trail = Particle(player.x, player.y, player.angle, "swoosh", steps_moved+8)
                    game.particles.append(trail)

                    smoke = Particle(player.x +dPos[0]*random.random(), player.y +dPos[1]*random.random(), player.angle, "smoke", random.randint(5,30))
                    smoke.xv = (dPos[0] + random.random() -0.5)*0.01
                    smoke.yv = (dPos[1] + random.random() -0.5)*0.01
                    game.particles.append(smoke)

                    # MoVE
                    player.x += dPos[0]
                    player.y += dPos[1]
                    steps_moved += 1
            else:
                stopped = True
                playWallSound()
                game.shakeScreen(5, dPos)
class FireSpell(Spell):

    powerLevel = 3
    displayName = "Fire Spear" # make this a fireball?
    displayIcon = "fire"

    def activate(self, player, dPos):
        game.animationTime = 16
        #game.player.nr_of_fireSpell_casts += 1
        for i in range(1,4):# + FireSpell.nr_of_fireSpell_casts):
            x = player.x + dPos[0]*i
            y = player.y + dPos[1]*i
            enemy = game.arena.enemy_at(x, y)
            if enemy:
                enemy.hurt(1)
            smoke = Particle(x, y, player.angle, "smoke", 20+5*i)
            game.particles.append(smoke)
            flame = Particle(x, y, player.angle, "fire", 12+2*i)
            game.particles.append(flame)
        playCrushSound()
class ExplosionSpell(Spell):

    powerLevel = 4
    displayName = "Explode"
    displayIcon = "fire"

    def activate(self, player, dPos):
        game.animationTime = 16
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                x = player.x + dx
                y = player.y + dy
                enemy = game.arena.enemy_at(x, y)
                if enemy:
                    enemy.hurt(1)
        makeSmokeCloud(player.x, player.y, 5, particleName = "smoke")
        makeSmokeCloud(player.x, player.y, 10, particleName = "fire")
        playCrushSound()
class BlazeSpell(Spell):

    powerLevel = 4
    displayName = "Blaze"
    displayIcon = "fire"

    def activate(self, player, dPos):
        game.animationTime = 20
        def aoeIndeces(dz):
            if dz:
                aoe = [dz,2*dz]
            else:
                aoe = [-1,0,1]
            return aoe
        for dx in aoeIndeces(dPos[0]):
            for dy in aoeIndeces(dPos[1]):
                x = player.x + dx
                y = player.y + dy
                enemy = game.arena.enemy_at(x, y)
                if enemy:
                    enemy.hurt(2)
                smoke = Particle(x, y, player.angle, "smoke", 24)
                game.particles.append(smoke)
                flame = Particle(x, y, player.angle, "fire", 16)
                game.particles.append(flame)
        playCrushSound()
class PushSpell(Spell):

    powerLevel = 2
    displayName = "Push"
    displayIcon = "smoke"

    def activate(self, player, dPos):
        game.animationTime = 10
        for dPos in [(0,1),(-1,0),(0,-1),(1,0)]:
            x = player.x + dPos[0]
            y = player.y + dPos[1]
            enemy = game.arena.enemy_at(x, y)
            if enemy:
                enemy.forcedMovement(dPos, 1)
            arrow = Particle(x, y, VtoA(dPos), "arrow", 16)
            arrow.xv, arrow.yv = (dPos[0]*0.02, dPos[1]*0.02)
            game.particles.append(arrow)
        playWallSound()
class FreezeSpell(Spell):

    powerLevel = 3
    displayName = "Ice Blast"
    displayIcon = "ice"

    def activate(self, player, dPos):
        game.animationTime = 10
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                x = player.x + dx + dPos[0]*2
                y = player.y + dy + dPos[1]*2
                enemy = game.arena.enemy_at(x, y)
                if enemy:
                    enemy.freeze(2 + game.player.freezePower)
                    #enemy.hurt(1)
                arrow = Particle(x, y, player.angle, "ice", 10)
                game.particles.append(arrow)
        playCrushSound()
class ShieldSpell(Spell):
    powerLevel = 2
    displayName = "Shield"
    displayIcon = "shield"

    def activate(self, player, dPos):
        game.animationTime = 8
        game.player.shield += 1
        print(game.player.shield)
        playWallSound()
class RockSpell(Spell):

    powerLevel = 3
    displayName = "Fortify"
    displayIcon = "rocks"

    def activate(self, player, dPos):
        game.animationTime = 8
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                x = player.x + dx
                y = player.y + dy
                entity = game.arena.entity_at(x, y)
                if not entity and not abs(dx)+abs(dy)==2:
                    game.arena.entities.append(Rock((x,y)))
        makeSmokeCloud(player.x, player.y, 5, particleName = "rocks")
        playCrushSound()
class BombSpell(Spell):

    powerLevel = 2
    displayName = "Bomb"
    displayIcon = "bomb"

    def activate(self, player, dPos):
        game.animationTime = 8
        newX = player.x + dPos[0]
        newY = player.y + dPos[1]
        if game.arena.inbounds(newX, newY):
            entity = game.arena.enemy_at(newX, newY)
            if entity:
                entity.forcedMovement(dPos, 1)
            entity = game.arena.enemy_at(newX, newY)
            if not entity:
                game.arena.entities.append(Bomb((newX, newY)))
            playWallSound()
class LightningSpell(Spell):

    powerLevel = 2
    displayName = "Lightning" # make this a fireball?
    displayIcon = "lightning"

    def activate(self, player, dPos):
        game.animationTime = 16
        x = player.x + dPos[0]*2
        y = player.y + dPos[1]*2
        entity = game.arena.enemy_at(x, y)
        if entity:
            entity.hurt(1)
        lightning = Particle(x, y, 0, "lightning", 8)
        game.particles.append(lightning)
        playCrushSound()
class HealSpell(Spell):

    powerLevel = 3
    displayName = "Heal" # make this a fireball?
    displayIcon = "heart"

    def activate(self, player, dPos):
        game.animationTime = 16
        game.player.health = min(game.player.health+1, game.player.maxhealth)
        makeSmokeCloud(player.x, player.y, 3, particleName = "heart")

#double next spell
#hookshot
#teleport
#knockback
#defensive stuff
#create blocks, bombs, totems etc
#casting, healing totem
# one time use spells.
# charge one time use cannonSpell.

ALLSPELLS = [DashSpell, FireSpell, ExplosionSpell, BlazeSpell, PushSpell, FreezeSpell, ShieldSpell, RockSpell, BombSpell, LightningSpell, HealSpell]

class Entity():

    fat = 1

    def __init__(self, position):
        self.x = position[0]
        self.y = position[1]
        self.angle = 0 # 0 is right. 1 is up.
        self.frozen = 0
        self.shield = 0
        self.health = self.maxhealth
        self.image = self.standingImage

    def move(self, vector): # returns all kinds of shit (entity, "wall", False)
        if vector == (0,0):
            print("WARNING: Entity.move() called with (0,0) step.")
        else:
            self.angle = VtoA(vector)
        if game.arena.inbounds(self.x + vector[0], self.y+vector[1], fat = self.fat):
            whats_there = game.arena.entity_at(self.x + vector[0], self.y+vector[1], fat = self.fat, ignore = self)
            if whats_there: # lol
                if isinstance(self, Player):
                    playWallSound()
                return whats_there
            else:
                self.x += vector[0]
                self.y += vector[1]
                return False
        else:
            if isinstance(self, Player):
                playWallSound()
            return "wall"

    def hurt(self, dmg):
        game.shakeScreen(4,(0,0))
        if isinstance(self, Player):
            game.shakeScreen(16,(0,0))
        if self.shield>0:
            self.shield -= 1
        else:
            self.health -= dmg
            if self.health <= 0:
                self.die()

    def freeze(self, n):
        self.frozen = max(self.frozen, n)

    def forcedMovement(self, dPos, distance):
        for i in range(distance):
            if game.arena.inbounds(self.x+dPos[0], self.y+dPos[1], fat = self.fat):
                if not game.arena.entity_at(self.x+dPos[0], self.y+dPos[1], fat = self.fat, ignore = self):
                    self.x += dPos[0]
                    self.y += dPos[1]
            else:
                playWallSound()

    def decoratedAct(self):
        if self.frozen:
            self.frozen -= 1
        else:
            return self.act()

    def act(self):
        pass

    def die(self):
        if self in game.arena.entities:
            game.arena.entities.remove(self)
        else:
            print("Why am i already deleted?")

    def draw(self):
        topleft = game.arena.get_topleft()
        x = topleft[0] + self.x*GRIDSIZE + GRIDSIZE//2
        y = topleft[1] + self.y*GRIDSIZE + GRIDSIZE//2
        if self.frozen>0:
            blitRotate(self.iceImage, (x, y), (GRIDSIZE//2, GRIDSIZE//2), 0)
        if self.shield>0:
            blitRotate(self.shieldImage, (x, y), (GRIDSIZE//2, GRIDSIZE//2), 0)
        blitRotate(self.image, (x, y), (GRIDSIZE//2, GRIDSIZE//2), self.angle)

    iceImage = loadImage(os.path.join("particles", "ice.png"))
    shieldImage = loadImage(os.path.join("particles", "shield.png"))

class Player(Entity):

    def __init__(self, position):
        super().__init__(position)
        self.moveHistory = []
        
        # RELIC STUFF
        self.RNG_lightnings = 0
        self.freezePower = 0
        self.rockCrushPower = 0
        self.bomb_immune = 0

        for relic in game.relics:
            relic.start_of_round(self)

    def die(self):
        print("GAME OVER")

    def move(self, vector):
        game.animationTime = 8
        if self.frozen:
            self.frozen -= 1
            self.moveHistory.append(vector) #?
        else:
            if vector != (0,0):
                super().move(vector = vector)
            self.moveHistory.append(vector)
            self.castSpells()
        game.beginResolveTurn()

    def castSpells(self):
        for spell in game.spellBook:
            spell.current_alignment = self.checkRecipe(spell)
            #print(spell.current_alignment)
            if spell.current_alignment[0] == len(spell.recipe):
                game.spellStack.append(spell)

    def checkRecipe(self, spell):
        recipeLength = len(spell.recipe)
        for L in range(recipeLength):
            alignment_length = recipeLength - L
            if len(self.moveHistory)<alignment_length:
                continue
            for symmetry in [(0,1), (90,1), (180,1), (270,1)]:#, (0,-1), (90,-1), (180,-1), (270,-1)]:
                success = True
                for i in range(alignment_length):
                    ith_last_movement_vector = self.moveHistory[-1-i]
                    ith_last_required = applySymmetry(spell.recipe[alignment_length-1-i], symmetry)
                    if ith_last_movement_vector==ith_last_required: 
                        continue
                    else:
                        success = False
                        break
                if success:
                    return (alignment_length, symmetry)
        return (0, (0,1))

    def drawUI(self):
        for i in range(self.maxhealth):
            if i<self.health:
                img = self.heartImage
            else:
                img = self.darkHeartImage
            gameDisplay.blit(img, (20+60*i,20))
        for i in range(len(game.spellBook)):
            game.spellBook[i].draw(i)

    heartImage = loadImage(os.path.join("particles", "heart.png"))
    darkHeartImage = loadImage(os.path.join("particles", "darkheart.png"))

class Dasher(Player):

    maxhealth = 3

    def __init__(self, position):
        super().__init__(position)
        game.spellBook[0] = DashSpell()
        game.spellBook[0].recipe = [(0,-1),(0,1),(0,-1)]
class Rogue(Player):

    maxhealth = 2

    def __init__(self, position):
        super().__init__(position)
        game.spellBook[0] = StabSpell()
        game.spellBook[0].recipe = [(0,0)]

    def draw(self):
        topleft = game.arena.get_topleft()
        x = topleft[0] + self.x*GRIDSIZE
        y = topleft[1] + self.y*GRIDSIZE
        super().draw()
        img = [self.standingImage, self.standingUpImage, self.standingLeftImage, self.standingDownImage][self.angle//90]
        blitRotate(img, (x, y), (0,0))

    standingImage = loadImage(os.path.join("player", "player.png"))
    standingLeftImage = pygame.transform.flip(loadImage(os.path.join("player", "player.png")),True,False)
    standingDownImage = loadImage(os.path.join("player", "player_down.png"))
    standingUpImage = loadImage(os.path.join("player", "player_up.png"))

class Enemy(Entity):

    def __init__(self, position):
        super().__init__(position)
        self.state = "normal"

    def moveRandom(self):
        guess = random.choice([(0,1),(0,-1),(-1,0),(1,0)])
        move_collision = self.move(guess)
        if move_collision and move_collision != game.player:
            return self.move((-guess[0],-guess[1]))
        else:
            return move_collision

    def directionTowardsPlayer(self):
        dx = 0
        dy = 0
        if game.player.x > self.x:
            dx = 1
        if game.player.x < self.x:
            dx = -1
        if game.player.y > self.y:
            dy = 1
        if game.player.y < self.y:
            dy = -1
        if dx and dy:
            if random.random() < 0.5:
                dx = 0
            else:
                dy = 0
        return VtoA((dx,dy))
    
    def draw(self):
        super().draw()

        if self.health<self.maxhealth:
            topleft = game.arena.get_topleft()
            x = topleft[0] + self.x*GRIDSIZE
            y = topleft[1] + self.y*GRIDSIZE
            pygame.draw.rect(gameDisplay, (100,0,0), (x,y,GRIDSIZE,4), 0)
            pygame.draw.rect(gameDisplay, (0,200,0), (x,y,GRIDSIZE*self.health/self.maxhealth,4), 0)
    

    standingImage = loadImage(os.path.join("enemies", "ghost", "ghost.png"))
# rework enemy health so that it can be calculated (displayed/small values/1 hit)
class StartCrystal(Enemy):

    maxhealth = 1

    def act(self):
        pass

    standingImage = loadImage(os.path.join("enemies", "crystal.png"))
class Ghost(Enemy):

    powerLevel = 2
    maxhealth = 1

    def act(self):
        decided_to_walk = random.random() < 0.8 and self.state=="normal"
        if decided_to_walk:
            move_collision = self.moveRandom()
        if (not decided_to_walk) or move_collision: # else-or-if moment. nu har vi decided_to_walk istället
            if self.state == "normal":
                self.state = "preExplode"
                self.image = self.preExplodeImage
            else:
                game.animationTime = 8
                makeSmokeCloud(self.x, self.y, 15, particleName = "electrics")
                for dx in [-1,0,1]:
                    for dy in [-1,0,1]:
                        entity = game.arena.entity_at(self.x + dx, self.y + dy)
                        if isinstance(entity, Player) or isinstance(entity, Egg):
                            entity.hurt(1)
                self.image = self.standingImage
                self.state = "normal"
        self.angle = 0

    standingImage = loadImage(os.path.join("enemies", "ghost", "ghost.png"))
    preExplodeImage = loadImage(os.path.join("enemies", "ghost", "preExplode.png"))
class Armadillo(Enemy):

    powerLevel = 4
    maxhealth = 1

    def act(self):
        decided_to_walk = random.random() < 0.8 and self.state=="normal"
        if decided_to_walk:
            self.angle = self.directionTowardsPlayer()
            walk_collision = self.move(AtoV(self.angle))
        if (not decided_to_walk) or (walk_collision == game.player): # else-or-if moment. nu har vi decided_to_walk istället
            if self.state == "normal":
                self.state = "preDash"
                self.image = self.preDashImage
                self.shield = 999
            else:
                self.shield = 0
                game.animationTime = 8
                stopped = False
                steps_moved = 0
                smokeParticles = []
                dPos = AtoV(self.angle)
                while not stopped:
                    if game.arena.inbounds(self.x+dPos[0], self.y+dPos[1]):
                        entity = game.arena.entity_at(self.x+dPos[0], self.y+dPos[1])
                        if entity == game.player:
                            stopped = True
                            entity.hurt(1)
                            playCrushSound()
                            makeSmokeCloud(self.x, self.y, 10, "rocks")
                            game.shakeScreen(10, dPos)
                        elif entity:
                            stopped = True
                            entity.hurt(0)
                            playWallSound()
                            game.shakeScreen(2, dPos)
                        else:
                            smoke = Particle(self.x, self.y, self.angle, "smoke", random.randint(5,10))
                            smoke.xv = (dPos[0] + random.random() -0.5)*0.01
                            smoke.yv = (dPos[1] + random.random() -0.5)*0.01
                            game.particles.append(smoke)

                            self.x += dPos[0]
                            self.y += dPos[1]
                            steps_moved += 1
                    else:
                        stopped = True
                        playWallSound()
                        game.shakeScreen(2, dPos)
                self.image = self.standingImage
                self.state = "normal"

    standingImage = loadImage(os.path.join("enemies", "armadillo", "armadillo.png"))
    preDashImage = loadImage(os.path.join("enemies", "armadillo", "dash.png"))
class Troll(Enemy):

    powerLevel = 1
    maxhealth = 1

    def act(self):
        decided_to_walk = random.random() < 0.8 and self.state=="normal"
        if decided_to_walk:
            self.angle = self.directionTowardsPlayer()
            walk_collision = self.move(AtoV(self.angle))
        if (not decided_to_walk) or (walk_collision and not isinstance(walk_collision, Enemy)): # else-or-if moment. nu har vi decided_to_walk istället
            if self.state == "normal":
                self.state = "prePunch"
                self.image = self.prePunchImage
            else:
                game.animationTime = 8
                dPos = AtoV(self.angle)
                if game.arena.inbounds(self.x+dPos[0], self.y+dPos[1]):
                    entity = game.arena.entity_at(self.x+dPos[0], self.y+dPos[1])
                    if entity == game.player:
                        entity.hurt(1)
                        entity.forcedMovement(dPos, 1)
                        playCrushSound()
                        game.shakeScreen(10, dPos)
                    else:
                        if entity:
                            entity.hurt(1)
                        playWallSound()
                        game.shakeScreen(2, dPos)
                makeSmokeCloud(self.x+dPos[0], self.y+dPos[1], 10, "planks")
                self.image = self.standingImage
                self.state = "normal"

    standingImage = loadImage(os.path.join("enemies", "troll", "troll.png"))
    prePunchImage = loadImage(os.path.join("enemies", "troll", "swing.png"))
class MotherGhost(Enemy):

    powerLevel = 15
    maxhealth = 10
    fat = 2

    def act(self):
        if self.state=="normal" and random.random()<0.8:
            self.state = random.choice(["preexplode","preexplode","eggs"])
        if self.state == "normal":
            move_collision = self.moveRandom()
            #print(move_collision)
            self.angle = 0
            if move_collision:
                self.state == "preexplode"
        elif self.state == "preexplode":
            self.state = "explode"
            self.image = self.preExplodeImage
        elif self.state == "explode":
            game.animationTime = 8
            makeSmokeCloud(self.x  , self.y  , 8, particleName = "electrics")
            makeSmokeCloud(self.x+1, self.y  , 8, particleName = "electrics")
            makeSmokeCloud(self.x  , self.y+1, 8, particleName = "electrics")
            makeSmokeCloud(self.x+1, self.y+1, 8, particleName = "electrics")
            for dx in range(-1,3):
                for dy in range(-1,3):
                    entity = game.arena.entity_at(self.x + dx, self.y + dy)
                    if isinstance(entity, Player) or isinstance(entity, Egg):
                        entity.hurt(1)
            self.image = self.standingImage
            self.state = "normal"
        elif self.state == "eggs":
            game.animationTime = 8
            for x in range(self.x-1,self.x+3):
                for y in range(self.y-1,self.y+3):
                    entity = game.arena.entity_at(x, y)
                    if (not entity) and random.random()<0.2 and game.arena.inbounds(x,y):
                        game.arena.entities.append(Egg((x, y)))
            self.state = "normal"
        else:
            print("ERROR: unknown state in mother ghost")

    standingImage = loadImage(os.path.join("enemies", "mother ghost", "mother ghost.png"), (2,2))
    preExplodeImage = loadImage(os.path.join("enemies", "ghost", "preExplode.png"), (2,2))
class Droid(Enemy):

    powerLevel = 20
    maxhealth = 10

    def act(self):
        if self.state=="normal":
            if random.random()<0.5 and self.shield <= 0:
                self.shield = 1
            else:
                self.angle = self.directionTowardsPlayer()
                if (self.x == game.player.x or self.y == game.player.y):
                    self.state = "preshoot"
                    self.image = self.preShootImage
                else:
                    walk_collision = self.move(AtoV(self.angle))
        elif self.state == "preshoot":
            game.animationTime = 8
            laser_len = 1
            dPos = AtoV(self.angle)
            while 1:
                query_X = self.x+dPos[0]*laser_len
                query_Y = self.y+dPos[1]*laser_len
                if game.arena.inbounds(query_X, query_Y):
                    entity = game.arena.entity_at(query_X, query_Y)
                    if entity == game.player:
                        entity.hurt(1)
                        game.shakeScreen(10, dPos)
                        break
                    elif entity:
                        entity.hurt(0)
                        game.shakeScreen(2, dPos)
                        break
                    else:
                        trail = Particle(query_X, query_Y, self.angle, "swoosh", 8)
                        game.particles.append(trail)
                        laser_len += 1
                else:
                    game.shakeScreen(2, dPos)
                    break
            else:
                print("ERROR: unknown state in droid")
            playCrushSound()
            self.image = self.standingImage
            self.state = "normal"

    standingImage = loadImage(os.path.join("enemies", "droid", "droid.png"))
    preShootImage = loadImage(os.path.join("enemies", "droid", "droid2.png"))
class Bishop(Enemy):

    powerLevel = 7
    maxhealth = 1

    def act(self):
        dx = random.choice([-1,1])
        dy = random.choice([-1,1])
        if game.player.x > self.x:
            dx = 1
        if game.player.x < self.x:
            dx = -1
        if game.player.y > self.y:
            dy = 1
        if game.player.y < self.y:
            dy = -1
        while 1:
            if game.arena.inbounds(self.x + dx, self.y + dy):
                entity = game.arena.entity_at(self.x + dx, self.y + dy)
                if entity == game.player:
                    entity.hurt(1)
                    makeSmokeCloud(entity.x, entity.y, 5)
                    game.shakeScreen(10, (0,0))
                elif not entity:
                    self.x += dx
                    self.y += dy
                    if random.random()<0.9:
                        continue
            break

    standingImage = loadImage(os.path.join("enemies", "bishop.png"))

class Bomb(Entity):

    powerLevel = 0
    maxhealth = 1
    
    def __init__(self, pos):
        super().__init__(pos)
        self.age = 0

    def act(self):
        self.age += 1
        if self.age == 1:
            self.image = self.standing2Image
        elif self.age == 2:
            self.image = self.standing3Image
        else:
            self.die()

    def die(self):
        super().die()
        playCrushSound()
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                x = self.x + dx
                y = self.y + dy
                entity = game.arena.entity_at(x, y)
                if entity:
                    if not (entity == game.player and game.player.bomb_immune):
                        entity.hurt(1)
        makeSmokeCloud(self.x,self.y,10)

    standingImage = loadImage(os.path.join("enemies","bomb", "bomb1.png"))
    standing2Image = loadImage(os.path.join("enemies","bomb", "bomb2.png"))
    standing3Image = loadImage(os.path.join("enemies","bomb", "bomb3.png"))
class Egg(Entity):

    powerLevel = 1
    maxhealth = 1

    def die(self):
        super().die()
        game.arena.entities.append(Ghost((self.x,self.y)))

    standingImage = loadImage(os.path.join("entities", "egg.png"))
class Rock(Entity):

    powerLevel = 0
    maxhealth = 1

    def die(self):
        super().die()
        if game.player.rockCrushPower == 0:
            playWallSound()
            makeSmokeCloud(self.x,self.y,3, "rocks")
        else:
            playCrushSound()
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    x = self.x + dx
                    y = self.y + dy
                    entity = game.arena.enemy_at(x, y)
                    if entity and isinstance(entity, Enemy):
                        entity.hurt(1)
            makeSmokeCloud(self.x,self.y,8, "rocks")
            makeSmokeCloud(self.x,self.y,8)

    standingImage = loadImage(os.path.join("entities", "rock.png"))

class Relic():

    image = None
    explain_text = "???"
    displayName = "?"

    def draw(self, height):
        MYFONT = pygame.font.SysFont('Calibri', 32)
        blitRotate(self.image, (SCREENSIZE[0]-50-GRIDSIZE,50+height*GRIDSIZE), (0, 0), 0)
        # duplicate relic count?
        """
        textsurface = MYFONT.render(some nr, True, (0, 0, 0))
        blitRotate(textsurface, (centerPos[0], centerPos[1] - SPACING//2), (textsurface.get_width()//2, textsurface.get_height()//2))
        """
        mouse_pos = pygame.mouse.get_pos()
        if SCREENSIZE[0]-50-GRIDSIZE < mouse_pos[0] < SCREENSIZE[0]-50 and 50+height*GRIDSIZE < mouse_pos[1] < 50+(height+1)*GRIDSIZE:
            textsurface = MYFONT.render(self.explain_text, True, (255, 200, 155))
            blitRotate(textsurface, (mouse_pos[0] - textsurface.get_width(), mouse_pos[1]), (0,0))
        
    def drawBig(self, rwrdNr):
        SPACING = 400
        centerPos = (SCREENSIZE[0]//2 - SPACING + SPACING*rwrdNr, SCREENSIZE[1]//2)
        
        myfont = pygame.font.SysFont('Calibri', 64)
        myfont2 = pygame.font.SysFont('Calibri', 32)
        textsurface = myfont.render(self.displayName, True, (0, 0, 0))
        blitRotate(textsurface, (centerPos[0], centerPos[1] - SPACING//2), (textsurface.get_width()//2, textsurface.get_height()//2))

        blitRotate(self.image, centerPos, (GRIDSIZE//2, GRIDSIZE//2), 0)
        
        textsurface = myfont2.render(self.explain_text, True, (0, 0, 0))
        blitRotate(textsurface, (centerPos[0], centerPos[1] + SPACING//2), (textsurface.get_width()//2, textsurface.get_height()//2))

        
    def obtained(self):
        pass

    def start_of_round(self, player):
        pass

class ThunderRelic(Relic):

    image = loadImage(os.path.join("particles", "lightning.png"))
    explain_text = "Lighting strikes when casting spells"
    displayName = "Thunderstorm"

    def start_of_round(self, player):
        player.RNG_lightnings += 1
class HeartRelic(Relic):

    image = loadImage(os.path.join("particles", "heart.png"))
    explain_text = "+1 HP"
    displayName = "Heart Container"

    def start_of_round(self, player):
        player.maxhealth += 1
        player.health += 1
class FreezeTimeRelic(Relic):

    image = loadImage(os.path.join("particles", "ice.png"))
    explain_text = "Enemies remain frozen longer"
    displayName = "Ice Time..."

    def start_of_round(self, player):
        player.freezePower += 1
class RockCrushRelic(Relic):

    image = loadImage(os.path.join("particles", "rocks.png"))
    explain_text = "Crushing rocks hurts enemies"
    displayName = "Rock CRUSH!"

    def start_of_round(self, player):
        player.rockCrushPower += 1
class BombImmunityRelic(Relic):

    image = loadImage(os.path.join("particles", "shield.png"))
    explain_text = "Bomb immunity"
    displayName = "Blast Resistor"

    def start_of_round(self, player):
        player.bomb_immune += 1
class UpgradeRelic(Relic):

    image = loadImage(os.path.join("particles", "fire.png"))
    explain_text = "Removes random dance step."
    displayName = "Upgrade Spell"

    def obtained(self):
        try:
            upgradedSpell = random.choice([s for s in game.spellBook if len(s.recipe)>1])
            upgradedSpell.recipe.remove(random.choice(upgradedSpell.recipe))
        except:
            print("ERROR: nothing to upgrade")

ALLRELICS = [ThunderRelic, HeartRelic, RockCrushRelic, FreezeTimeRelic, UpgradeRelic]
# summoner
# healer
# shielded
# freezer?
# regelkandidat
# mario weeping angel
# env hazards?

ALLENEMIES = [Ghost, Armadillo, Troll, Egg, Rock, MotherGhost, Droid, Bishop]

class Particle():

    def __init__(self, x,y,a, img, lt):
        self.x = x
        self.y = y
        self.xv = 0
        self.yv = 0
        self.angle = a
        self.image = self.images[img]
        self.lifetime = lt

    def update(self):
        self.x += self.xv/ANIMATION_MULTIPLIER
        self.y += self.yv/ANIMATION_MULTIPLIER
        self.lifetime -= 1/ANIMATION_MULTIPLIER
        if self.lifetime <= 0:
            if self in game.particles:
                game.particles.remove(self)
            else:
                print("?!?!?")

    def draw(self):
        topleft = game.arena.get_topleft()
        x = topleft[0] + self.x*GRIDSIZE + GRIDSIZE//2
        y = topleft[1] + self.y*GRIDSIZE + GRIDSIZE//2
        blitRotate(self.image, (x, y), (GRIDSIZE//2,GRIDSIZE//2), self.angle)


    images = {}
    for i in ["rocks","smoke","planks","electrics","swoosh","fire","arrow","darkarrow","slice","ice","swoosh","shield","lightning","bomb","heart","darkheart"]:
        images[i] = loadImage(os.path.join("particles", i+".png"))


game = Game()
game.playerClass = Rogue
game.startPractice()


jump_out = False
while jump_out == False:
    time_delta = clock.tick(FRAMERATE)/1000.0

    
    #pygame.event.get()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True

        if event.type == pygame.KEYDOWN:
            if game.mode in ["playing", "practice"]:
                if event.key in game.controls.keys():
                    if game.playerActionable:
                        game.player.move(game.controls[event.key])
                if event.key == pygame.K_2:
                    game.arena.entities = []
            if game.mode == "rewards":
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    game.selectReward([pygame.K_1, pygame.K_2, pygame.K_3].index(event.key))

    game.update()
    game.draw()

    pygame.display.flip()
    
    
pygame.quit()
#quit() #bad for pyinstaller
