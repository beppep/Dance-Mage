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

gameDisplay = pygame.display.set_mode(SCREENSIZE)
#gameDisplay = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("Dance Mage")
pygame.display.set_icon(pygame.image.load(os.path.join("assets", "textures", "player", "player.png")))

def blitRotate(surf,image, pos, originPos, angle):

    #ifx rad ddeg
    #angle = angle*180/math.pi

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
    surf.blit(rotated_image, origin)

def AtoV(a):
    return [(1,0),(0,-1),(-1,0),(0,1)][a//90]
def VtoA(v):
    return [(1,0),(0,-1),(-1,0),(0,1)].index(v)*90

def changeTextbox(dabox, datext):
    dabox.html_text=str(datext)
    dabox.rebuild()

def loadImage(path):
    image = pygame.image.load(os.path.join("assets", "textures", path))
    
    image = pygame.transform.scale(image, (GRIDSIZE, GRIDSIZE))
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
        self.mode = "playing"
        self.player = Rogue((4,4))
        self.arena = Arena(8,8)
        self.playerActionable = True # the player can press a button. (not spellstack, enemy actions, animation time)
        self.spellStack = []
        self.enemyStack = []
        self.wavesWon = 0

        self.particles = []

        self.animationTime = 0
        self.screenshake = 0
        self.currentScreenShake = (0,0)
        self.screenshakeDir = (0,0)
        self.level_over_animation = False

    def beginResolveTurn(self):
        self.playerActionable = False
        random.shuffle(self.arena.enemies)
        self.arena.enemies.sort(key = lambda x: x.state=="normal")
        self.enemyStack = self.arena.enemies[:]

    def update(self):

        # TURN LOGIC
        
        if self.animationTime > 0:
            self.animationTime -= 1
        elif self.spellStack:
            self.spellStack[0].activate(self.player, *self.player.moveHistory[-1])
            self.spellStack.pop(0)
        elif self.enemyStack:
            if self.enemyStack[0].health > 0:
                self.enemyStack[0].act()
            self.enemyStack.pop(0)
        else:
            self.playerActionable = True

            # ROUND CLEARED LOGIC
            
            if self.mode == "playing":
                if len(self.arena.enemies) == 0:
                    self.wavesWon += 1
                    self.mode = "rewards"
                    self.generateRewards()

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
        random.shuffle(ALLSPELLS)
        for i in range(3):
            self.rewardOptions.append(ALLSPELLS[i]())

    def selectReward(self, n):
        self.player.spellBook.append(self.rewardOptions[n])
        self.mode = "practice"
        self.arena = Arena(8,8)

    def startWave(self):
        self.arena.generateWave(self.wavesWon*5)
        self.player.health = 3
        self.player.moveHistory = []
        self.mode = "playing"

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

    def shakeScreen(self, amount, dPos):
        self.screenshake = max(self.screenshake, amount)
        self.screenshakeDir = dPos

    controls = {
        pygame.K_a : ((-1,0),180), pygame.K_d : ((1,0),0), pygame.K_w : ((0,-1),90), pygame.K_s : ((0,1),270), 
        pygame.K_LEFT : ((-1,0),180), pygame.K_RIGHT : ((1,0),0), pygame.K_UP : ((0,-1),90), pygame.K_DOWN : ((0,1),270)
    }

class Arena():

    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.enemies = []

    def inbounds(self, x, y):
        return 0<=x<self.width and 0<=y<self.height

    def enemy_at(self, x, y):
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return enemy
        return None

    def entity_at(self, x, y):
        if game.player.x == x and game.player.y == y:
            return game.player
        return self.enemy_at(x, y)

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
                x = random.randint(0,self.width-1)
                y = random.randint(0,self.height-1)
                while self.entity_at(x,y):
                    x = random.randint(0,self.width-1)
                    y = random.randint(0,self.height-1)
                self.enemies.append(enemy((x,y)))
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
                #blitRotate(gameDisplay, image, (topleft[0] + x*GRIDSIZE +GRIDSIZE//2, topleft[1] + y*GRIDSIZE +GRIDSIZE//2), (GRIDSIZE//2,GRIDSIZE//2), 0)
                gameDisplay.blit(image, (topleft[0] + x*GRIDSIZE, topleft[1] + y*GRIDSIZE))

        for enemy in self.enemies:
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
        for i in range(length-1):
            self.recipe.append(90*random.randint(0,3))
        self.recipe.append(90)
        return self.recipe

    def activate(self, player, dPos, ang):
        pass

    def draw(self, height):
        current_symmetry = self.current_alignment[1]
        for i in range(len(self.recipe)):
            if self.current_alignment[0]>i:
                img = self.arrowImage
            else:
                img = self.darkArrowImage
            angle = (self.recipe[i]*current_symmetry[1] + current_symmetry[0])
            blitRotate(gameDisplay, img, (50+(i+1)*GRIDSIZE,150+height*GRIDSIZE), (GRIDSIZE//2, GRIDSIZE//2), angle)
        blitRotate(gameDisplay, Particle.images[self.displayIcon], (50,150+height*GRIDSIZE), (GRIDSIZE//2, GRIDSIZE//2), 0)

    def drawBig(self, rwrdNr):
        SPACING = 400
        centerPos = (SCREENSIZE[0]//2 - SPACING + SPACING*rwrdNr, SCREENSIZE[1]//2)

        for i in range(len(self.recipe)):
            img = self.arrowImage
            angle = self.recipe[i]
            x = centerPos[0] - (GRIDSIZE*len(self.recipe))//2 + i*GRIDSIZE + GRIDSIZE//2
            y = centerPos[1] + SPACING//2
            blitRotate(gameDisplay, img, (x, y), (GRIDSIZE//2, GRIDSIZE//2), angle)

        blitRotate(gameDisplay, Particle.images[self.displayIcon], centerPos, (GRIDSIZE//2, GRIDSIZE//2), angle)
        myfont = pygame.font.SysFont('Calibri', 100)
        textsurface = myfont.render(self.displayName, True, (0, 0, 0))
        gameDisplay.blit(textsurface, (centerPos[0] - textsurface.get_width()//2, centerPos[1] - SPACING//2 - textsurface.get_height()//2))

    arrowImage = loadImage(os.path.join("particles", "arrow.png"))
    darkArrowImage = loadImage(os.path.join("particles", "darkarrow.png"))

class StabSpell(Spell):

    displayIcon = "slice"

    def __init__(self):
        super().__init__([0,90])

    def activate(self, player, dPos, ang):
        game.animationTime = 8
        x = player.x + dPos[0]
        y = player.y + dPos[1]
        enemy = game.arena.enemy_at(x, y)
        if enemy:
            enemy.hurt(2)
        arrow = Particle(x, y, player.angle, "slice", 10)
        game.particles.append(arrow)
        playCrushSound()
class DashSpell(Spell):

    def __init__(self):
        super().__init__([90,270,90])

    def activate(self, player, dPos, ang):
        game.animationTime = 16
        player.angle = ang
        stopped = False
        steps_moved = 0
        while not stopped:
            if game.arena.inbounds(player.x+dPos[0], player.y+dPos[1]):
                enemy = game.arena.enemy_at(player.x+dPos[0], player.y+dPos[1])
                if enemy:
                    #enemy.hurt(1+steps_moved)
                    enemy.hurt(4)
                    #enemy.forcedMovement(dPos, steps_moved)
                    playCrushSound()
                    makeSmokeCloud(player.x, player.y, random.randint(1+steps_moved,5+steps_moved))
                    game.shakeScreen(steps_moved+5, dPos)
                    stopped = True
                else:
                    player.x += dPos[0]
                    player.y += dPos[1]
                    steps_moved += 1

                    # SMOKE AND TRAIL
                    trail = Particle(player.x, player.y, player.angle, "swoosh", steps_moved+8)
                    game.particles.append(trail)

                    smoke = Particle(player.x +dPos[0]*random.random(), player.y +dPos[1]*random.random(), player.angle, "smoke", random.randint(5,30))
                    smoke.xv = (dPos[0] + random.random() -0.5)*0.01
                    smoke.yv = (dPos[1] + random.random() -0.5)*0.01
                    game.particles.append(smoke)
            else:
                stopped = True
                playWallSound()
                game.shakeScreen(5, dPos)

class FireSpell(Spell):

    powerLevel = 3
    displayName = "Fire Spear"
    displayIcon = "fire"

    def activate(self, player, dPos, ang):
        game.animationTime = 16
        for i in range(1,4):
            x = player.x + dPos[0]*i
            y = player.y + dPos[1]*i
            enemy = game.arena.enemy_at(x, y)
            if enemy:
                enemy.hurt(4)
            smoke = Particle(x, y, player.angle, "smoke", 20+5*i)
            game.particles.append(smoke)
            flame = Particle(x, y, player.angle, "fire", 12+2*i)
            game.particles.append(flame)
        playCrushSound()
class ExplosionSpell(Spell):

    powerLevel = 4
    displayName = "Explode"
    displayIcon = "fire"

    def activate(self, player, dPos, ang):
        game.animationTime = 16
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                x = player.x + dx
                y = player.y + dy
                enemy = game.arena.enemy_at(x, y)
                if enemy:
                    enemy.hurt(3)
        makeSmokeCloud(player.x, player.y, 5, particleName = "smoke")
        makeSmokeCloud(player.x, player.y, 10, particleName = "fire")
        playCrushSound()
class BlazeSpell(Spell):

    powerLevel = 5
    displayName = "Blaze"
    displayIcon = "fire"

    def activate(self, player, dPos, ang):
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
                    enemy.hurt(6)
                smoke = Particle(x, y, player.angle, "smoke", 24)
                game.particles.append(smoke)
                flame = Particle(x, y, player.angle, "fire", 16)
                game.particles.append(flame)
        playCrushSound()
class PushSpell(Spell):

    powerLevel = 2
    displayName = "Push"
    displayIcon = "smoke"

    def activate(self, player, dPos, ang):
        game.animationTime = 10
        x = player.x + dPos[0]
        y = player.y + dPos[1]
        enemy = game.arena.enemy_at(x, y)
        if enemy:
            enemy.hurt(2)
            enemy.forcedMovement(dPos, 1)
        arrow = Particle(x, y, player.angle, "arrow", 16)
        arrow.xv, arrow.yv = (dPos[0]*0.02, dPos[1]*0.02)
        game.particles.append(arrow)
        playCrushSound()
class FreezeSpell(Spell):

    powerLevel = 4
    displayName = "Ice Blast"
    displayIcon = "ice"

    def activate(self, player, dPos, ang):
        game.animationTime = 10
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                x = player.x + dx + dPos[0]*2
                y = player.y + dy + dPos[1]*2
                enemy = game.arena.enemy_at(x, y)
                if enemy:
                    enemy.frozen = max(enemy.frozen, 2)
                    enemy.hurt(1)
                arrow = Particle(x, y, player.angle, "ice", 10)
                game.particles.append(arrow)
        playCrushSound()
#double next spell
#hookshot
#knockback

ALLSPELLS = [FireSpell, ExplosionSpell, BlazeSpell, PushSpell, FreezeSpell]

class Entity():

    def __init__(self, position):
        self.x = position[0]
        self.y = position[1]
        self.angle = 0 # 0 is right. 1 is up.
        self.frozen = 0

    def move(self, dPos, ang):
        self.angle = ang
        if game.arena.inbounds(self.x + dPos[0], self.y+dPos[1]):
            if game.arena.entity_at(self.x + dPos[0], self.y+dPos[1]):
                if isinstance(self, Player):
                    playWallSound()
                return False
            else:
                self.x += dPos[0]
                self.y += dPos[1]
                return True
        else:
            if isinstance(self, Player):
                playWallSound()
            return False

    def draw(self):
        topleft = game.arena.get_topleft()
        x = topleft[0] + self.x*GRIDSIZE + GRIDSIZE//2
        y = topleft[1] + self.y*GRIDSIZE + GRIDSIZE//2
        if self.frozen>0:
            blitRotate(gameDisplay, self.iceImage, (x, y), (GRIDSIZE//2, GRIDSIZE//2), 0)
        blitRotate(gameDisplay, self.image, (x, y), (GRIDSIZE//2, GRIDSIZE//2), self.angle)

    iceImage = loadImage(os.path.join("particles", "ice.png"))

class Player(Entity):

    def __init__(self, position):
        super().__init__(position)

        self.image = self.standingImage
        self.moveHistory = []

    def hurt(self, dmg=1):
        self.health -= dmg
        if self.health <= 0:
            print("GAME OVER")

    def move(self, dPos, ang):
        game.animationTime = 8
        if self.frozen:
            self.frozen -= 1
            self.moveHistory.append((dPos, ang)) #?
        else:
            super().move(dPos, ang)
            self.moveHistory.append((dPos, ang))
            self.castSpells()
        game.beginResolveTurn()

    def castSpells(self):
        for spell in self.spellBook:
            spell.current_alignment = self.checkRecipe(spell)
            print(spell.current_alignment)
            if spell.current_alignment[0] == len(spell.recipe):
                game.spellStack.append(spell)

    def checkRecipe(self, spell):
        recipeLength = len(spell.recipe)
        for L in range(recipeLength):
            alignment_length = recipeLength - L
            if len(self.moveHistory)<alignment_length:
                continue
            for symmetry in [(0,1), (90,1), (180,1), (270,1), (0,-1), (90,-1), (180,-1), (270,-1)]:
                success = True
                for i in range(alignment_length):
                    ith_last_movement_angle = self.moveHistory[-1-i][1]
                    ith_last_required = (spell.recipe[alignment_length-1-i]*symmetry[1]+symmetry[0])%360 # flip first or last?
                    if ith_last_movement_angle==ith_last_required: 
                        continue
                    else:
                        success = False
                        break
                if success:
                    return (alignment_length, symmetry)
        return (0, (0,1))
        #print("ERROR: no trivial alignment") # happens when no movements are done

    def update(self):
        pass#pressed = pygame.get_pressed()
        if random.random()<0.02:
            self.image = self.standingImages[self.color]

    def draw(self):
        super().draw()
        #blitRotate(gameDisplay, self.image, (SCREENSIZE[0]//2, SCREENSIZE[1]//2), (GRIDSIZE//2,GRIDSIZE//2), self.angle)
        for i in range(self.health):
            gameDisplay.blit(self.standingImage, (20+60*i,20))
        for i in range(len(self.spellBook)):
            self.spellBook[i].draw(i)

    standingImage = loadImage(os.path.join("player", "player2.png"))

class Dasher(Player):
    def __init__(self, position):
        super().__init__(position)
        self.health = 3
        self.spellBook = [DashSpell()]
class Rogue(Player):
    def __init__(self, position):
        super().__init__(position)
        self.health = 3
        self.spellBook = [StabSpell()]

class Enemy(Entity):

    def __init__(self, position):
        super().__init__(position)
        self.image = self.standingImage
        self.health = self.maxhealth

    def moveAggro(self):
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
        return self.move((dx, dy), VtoA((dx,dy)))

    def hurt(self, dmg):
        self.health -= dmg
        #self.frozen = max(self.frozen, 1) # inflict stun/ kb always??
        if self.health <= 0:
            if self in game.arena.enemies:
                game.arena.enemies.remove(self)
            else:
                print("Why am i already deleted?")

    def forcedMovement(self, dPos, distance):
        for i in range(distance):
            if game.arena.inbounds(self.x+dPos[0], self.y+dPos[1]):
                if not game.arena.entity_at(self.x+dPos[0], self.y+dPos[1]):
                    self.x += dPos[0] 
                    self.y += dPos[1]
            else:
                playWallSound()

    def act(self):
        game.animationTime = 2
        if self.frozen>0:
            self.frozen -= 1
            return True
        return False
        #self.move(*random.choice(list(game.controls.values())))

    def draw(self):
        super().draw()

        topleft = game.arena.get_topleft()
        x = topleft[0] + self.x*GRIDSIZE
        y = topleft[1] + self.y*GRIDSIZE
        pygame.draw.rect(gameDisplay, (100,0,0), (x,y,GRIDSIZE,4), 0)
        pygame.draw.rect(gameDisplay, (0,200,0), (x,y,GRIDSIZE*self.health/self.maxhealth,4), 0)

    standingImage = loadImage(os.path.join("enemies", "ghost", "ghost.png"))

class Ghost(Enemy):

    powerLevel = 1
    maxhealth = 7

    def __init__(self, position):
        super().__init__(position)
        self.image = self.standingImage
        self.state = "normal"

    def act(self):
        if super().act(): # return if frozen hacky code. use decorator?
            return

        decided_to_walk = random.random() < 0.8 and self.state=="normal"
        if decided_to_walk:
            successful = self.move(*random.choice(list(game.controls.values())))
        if (not decided_to_walk) or (not successful): # else-or-if moment. nu har vi decided_to_walk istället
            if self.state == "normal":
                self.state = "preExplode"
                self.image = self.preExplodeImage
            else:
                game.animationTime = 5
                makeSmokeCloud(self.x, self.y, 15, particleName = "planks")
                if -1 <= game.player.x - self.x <= 1 and -1 <= game.player.y - self.y <= 1:
                    game.player.hurt(1)
                self.image = self.standingImage
                self.state = "normal"

    standingImage = loadImage(os.path.join("enemies", "ghost", "ghost.png"))
    preExplodeImage = loadImage(os.path.join("enemies", "ghost", "preExplode.png"))
class Armadillo(Enemy):

    powerLevel = 2
    maxhealth = 6

    def __init__(self, position):
        super().__init__(position)
        self.image = self.standingImage
        self.state = "normal"

    def act(self):
        if super().act():
            return
        decided_to_walk = random.random() < 0.8 and self.state=="normal"
        if decided_to_walk:
            successful = self.moveAggro()
        if (not decided_to_walk) or (not successful): # else-or-if moment. nu har vi decided_to_walk istället
            if self.state == "normal":
                self.state = "preDash"
                self.image = self.preDashImage
            else:
                game.animationTime = 8
                stopped = False
                steps_moved = 0
                smokeParticles = []
                dPos = AtoV(self.angle)
                while not stopped:
                    if game.arena.inbounds(self.x+dPos[0], self.y+dPos[1]):
                        entity = game.arena.entity_at(self.x+dPos[0], self.y+dPos[1])
                        if entity == game.player:
                            entity.hurt(1)
                            playCrushSound()
                            makeSmokeCloud(self.x, self.y, 10, "rocks")
                            game.shakeScreen(10, dPos)
                            stopped = True
                        elif entity:
                            stopped = True
                            entity.hurt(2)
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

    powerLevel = 4
    maxhealth = 16

    def __init__(self, position):
        super().__init__(position)
        self.image = self.standingImage
        self.state = "normal"

    def act(self):
        if super().act():
            return
        decided_to_walk = random.random() < 0.8 and self.state=="normal"
        if decided_to_walk:
            successful = self.moveAggro()
        if (not decided_to_walk) or (not successful): # else-or-if moment. nu har vi decided_to_walk istället
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
                        playCrushSound()
                        game.shakeScreen(10, dPos)
                        stopped = True
                    else:
                        if entity:
                            entity.hurt(4)
                        stopped = True
                        playWallSound()
                        game.shakeScreen(2, dPos)
                makeSmokeCloud(self.x+dPos[0], self.y+dPos[1], 10, "planks")
                self.image = self.standingImage
                self.state = "normal"

    standingImage = loadImage(os.path.join("enemies", "troll", "troll.png"))
    prePunchImage = loadImage(os.path.join("enemies", "troll", "swing.png"))
# summoner
# healer
# shielded
# freezer?

# env hazards?

ALLENEMIES = [Ghost, Armadillo, Troll]

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
        self.x += self.xv
        self.y += self.yv
        self.lifetime -= 1
        if self.lifetime <= 0:
            if self in game.particles:
                game.particles.remove(self)
            else:
                print("?!?!?")

    def draw(self):
        topleft = game.arena.get_topleft()
        x = topleft[0] + self.x*GRIDSIZE + GRIDSIZE//2
        y = topleft[1] + self.y*GRIDSIZE + GRIDSIZE//2
        blitRotate(gameDisplay, self.image, (x, y), (GRIDSIZE//2,GRIDSIZE//2), self.angle)


    images = {}
    for i in ["rocks","smoke","planks","diamonds","swoosh","fire","arrow","darkarrow","slice","ice"]:
        images[i] = loadImage(os.path.join("particles", i+".png"))


game = Game()
game.arena.generateWave(0)


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
                        game.player.move(*game.controls[event.key])
            if game.mode == "practice":
                if event.key == pygame.K_SPACE:
                    game.startWave()
            if game.mode == "rewards":
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    game.selectReward([pygame.K_1, pygame.K_2, pygame.K_3].index(event.key))

    game.update()
    game.draw()

    pygame.display.flip()
    
    
pygame.quit()
#quit() #bad for pyinstaller
