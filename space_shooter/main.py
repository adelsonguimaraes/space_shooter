import pgzrun
import math
import random

WIDTH = 800
HEIGHT = 600
MARGIN = 30
GAME_ON = False
SOUND_ON = True

class Menu():
    menus = [{
        'name': 'Start Game',
        'posx': WIDTH//2,
        'posy': 250
    },{
        'name': f'Toggle Sound',
        'posx': WIDTH//2,
        'posy': 300
    },{
        'name': 'Quit',
        'posx': WIDTH//2,
        'posy': 350
    }]
    selected = 0
    default_color = 'white'
    selected_color = 'yellow'

    def draw(self):
        if not GAME_ON:
            screen.draw.text('Space Shooter', center=(WIDTH//2, 200), color='red', fontsize=40)

            for index, option in enumerate(self.menus):
                color = self.selected_color if index == self.selected else self.default_color
                if index == 1:
                    sound_status = "ON" if SOUND_ON else "OFF"
                    screen.draw.text(f'{option.get("name")}: {sound_status}', center=(option.get('posx'), option.get('posy')), color=color, fontsize=40)
                else:
                    screen.draw.text(option.get('name'), center=(option.get('posx'), option.get('posy')), color=color, fontsize=40)
        
    def navigate(self, key):
        global GAME_ON, SOUND_ON

        if key == key.ESCAPE:
                GAME_ON = not GAME_ON

        if not GAME_ON:
            if key == keys.UP:
                if self.selected > 0:
                    self.selected -= 1
            elif key == keys.DOWN:
                if self.selected < 2:
                    self.selected += 1
            elif key == keys.RETURN:
                if self.selected == 0:
                    GAME_ON = True
                elif self.selected == 1:
                    SOUND_ON = not SOUND_ON
                    if SOUND_ON:
                        music.play('space_sound')
                    else:
                        music.stop()
                else:
                    exit()


class Laser():
    visible = False
    laser = Actor('laser_blue')
    meteor: 'Meteor' = None
    player: 'Player' = None

    def start(self):
        if self.visible:
            self.laser.y -= 5

            if self.laser.y < 0:
                self.visible = False

            self.colision()

    def shoot(self, x, y, meteor: 'Meteor', player: 'Player'):
        if not self.visible and keyboard.space:
            self.visible = True
            self.laser.x = x
            self.laser.y = y
            self.meteor = meteor
            self.player = player

            if SOUND_ON:
                sounds.sfx_laser2.play()

    def draw(self):
        if self.visible:
            self.laser.draw()

    def colision(self):
        if self.laser.colliderect(self.meteor.instance):
            meteor.destroy()
            self.destroy()
            self.player.incrementPoints()

    def destroy(self):
        self.visible = False


class Life:
    def __init__(self, total):
        self.total = total
        self.icons = []
        self.icon_spacing = 40
        self.icon_y = 20
        self.mount()

    def mount(self):
        self.icons = []

        for i in range(self.total):
            x = Actor('powerup_red_shield')
            x.pos = (20 + i * self.icon_spacing, self.icon_y)
            self.icons.append(x)

    def draw(self):
        for icon in self.icons:
            icon.draw()

    def decrement(self):
        if self.icons:
            self.total -= 1
            self.mount()

    def reset(self):
        self.total = 3
        self.mount()
            

class Player():
    points = 0
    instance = Actor('player')

    def __init__(self, laser: Laser, life: 'Life'):
        self.laser = laser
        self.life = life
        self.reset()

    def draw(self):
        self.instance.draw()
        self.PointsDisplay()

    def move(self):
        if keyboard.left:
            self.instance.x -= 3
        if keyboard.right:
            self.instance.x += 3
        if keyboard.up:
            self.instance.y -= 3
        if keyboard.down:
            self.instance.y += 3

        self.instance.x = max(MARGIN, min(WIDTH - MARGIN, self.instance.x))
        self.instance.y = max(MARGIN, min(HEIGHT - MARGIN, self.instance.y))

    def shoot(self, meteor: 'Meteor'):
        if keyboard.space:
            laser.shoot(self.instance.x, self.instance.y, meteor, self)

    def incrementPoints(self):
        self.points += 1

    def damage(self):
        self.life.decrement()
        
        if SOUND_ON:
            sounds.sfx_lose.play()

    def PointsDisplay(self):
        screen.draw.text(f'Points: {self.points}', topleft=(WIDTH-120, 20))

    def start(self):
        self.move()

    def reset(self):
        self.instance.y = 550
        self.instance.x = WIDTH/2


class Meteor():
    visible = False
    frames_elapsed = 0
    instance = Actor('meteor_grey_big', (0, 0))

    def __init__(self, player: 'Player'):
        self.player = player

    def setX(self, value):
        self.instance.x = value
        
    def setY(self, value, increment=False):
        if increment:
            self.instance.y += value
        else:
            self.instance.y = value

    def setAngle(self, value):
        self.instance.angle = value

    def start(self):
        if not self.visible:
            self.setY(0)
            self.setX(random.randint(0, WIDTH - 30))
            self.visible = True
        else:
            self.drop()
            self.colision()

    def drop(self):
        if self.visible:
            self.setY(2, True)
        
            self.frames_elapsed += 1

            if self.frames_elapsed >= 3 * 4:
                self.frames_elapsed = 0
                self.setAngle(random.randint(-90, 90))
            
            if self.instance.y > HEIGHT:
                self.visible = False

    def colision(self):
        if self.instance.colliderect(self.player.instance):
            self.destroy()
            self.player.damage()

    def draw(self):
        if self.visible:
            self.instance.draw()

    def destroy(self):
        self.visible = False
        
        if SOUND_ON:
            sounds.impact_metal_003.play()


class Message():

    def gameOver(self):
        screen.draw.text('GAME OVER', center=(WIDTH/2, HEIGHT/2), color='red', fontsize=40.0)

menu = Menu()
laser = Laser()
life = Life(3)
player = Player(laser, life)
meteor = Meteor(player)
message = Message()

music.play('space_sound')

def update():
    if GAME_ON:
        meteor.start()
        player.start()
        laser.start()
        player.shoot(meteor)

def on_key_down(key, mod, unicode):
    menu.navigate(key)

def draw():
    global GAME_ON

    screen.clear()
    menu.draw()

    if GAME_ON:
        if life.total > 0:
            screen.clear()
            player.draw()
            meteor.draw()
            laser.draw()
            life.draw()
        else:
            GAME_ON = False
            life.reset()
            player.reset()
