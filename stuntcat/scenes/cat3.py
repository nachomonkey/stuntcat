import pygame
import math
import random
from pygame.locals import *

from .scene import Scene
from .. resources import gfx, sfx, music

from pygame.sprite import DirtySprite, LayeredDirty

def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


class LayeredDirtyAppend(LayeredDirty):
    """ Like a group, except it has append and extend methods like a list.
    """
    def append(self, x):
        self.add(x)
    def extend(self, alist):
        for x in alist:
            self.add(x)

class Elephant(DirtySprite):
    def __init__(self, scene):
        DirtySprite.__init__(self)
        self.scene = scene
        self.width = scene.width
        self.height = scene.height
        self.state = 0
        self.states = {
            0: 'offscreen',
            1: 'poise left',
            2: 'stomp left',
            3: 'offscreen',
            4: 'poise right',
            5: 'stomp right',
        }
        self.last_state = 0
        self.just_happened = None


        self.time_between_stomps = 1500 #ms
        # self.time_between_stomps = 1000 #ms
        self.time_of_poise = 1500 #ms
        self.time_of_stomp = 1500 #ms
        self.last_animation = 0 #ms

        # stamp.
        sfx('foot_elephant.ogg')

        self.rect = pygame.Rect([0, 0, self.width//2, self.height])
        self.image = pygame.Surface((self.rect[2], self.rect[3])).convert()
        self.image.fill((255, 0, 0))
        #self.image = gfx('foot.png', convert_alpha=True)
        # gfx('foot_part.png').convert_alpha()
        #self.rect = self.image.get_rect()
        self.rect.x = -1000
        self.rect.y = -1000


    def update(self):
        # if self.just_happened is not None:
        #     print(self.just_happened)
        from_top = 100

        if self.just_happened == 'offscreen':
            self.dirty = True
            self.rect.x = -1000
            self.rect.y = -1000
            sfx('foot_elephant.ogg', stop=1)
        elif self.just_happened == 'poise left':
            self.rect.x = 0
            self.rect.y = from_top - self.height
            self.dirty = True
            sfx('foot_elephant.ogg', play=1)
        elif self.just_happened == 'stomp left':
            self.rect.y = self.scene.cat_wire_height - self.height#(self.height - self.image.get_height()) - self.scene.cat_wire_height
            self.rect.x = 0
            self.dirty = True

            if pygame.sprite.collide_rect(self, self.scene.cat):
                self.scene.reset_on_death()
                self.dirty = True

        elif self.just_happened == 'poise right':
            self.rect.x = self.width//2
            self.rect.y = from_top - self.height
            self.dirty = True
            sfx('foot_elephant.ogg', play=1)
        elif self.just_happened == 'stomp right':
            self.rect.x = self.width//2
            self.rect.y = self.scene.cat_wire_height - self.height
            self.dirty = True
            if pygame.sprite.collide_rect(self, self.scene.cat):
                self.scene.reset_on_death()
                self.dirty = True


    def animate(self, total_time):
        state = self.states[self.state]
        start_state = self.state
        if state == 'offscreen':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None
            if total_time > self.last_animation + self.time_between_stomps:
                self.state += 1
                self.last_animation = total_time
        elif state == 'poise left' or state == 'poise right':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None

            if total_time > self.last_animation + self.time_of_poise:
                self.state += 1
                self.last_animation = total_time
        elif state == 'stomp left' or state == 'stomp right':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None

            if total_time > self.last_animation + self.time_of_stomp:
                self.state += 1
                if self.state == max(self.states.keys()) + 1:
                    self.state = 0
                self.last_animation = total_time

        self.last_state = start_state


    def render(self, screen, width, height):
        if self.state == 1: #poise left
            pygame.draw.polygon(
                screen,
                [255, 0, 0],
                [
                    [0.1 * width, 0],
                    [0.5 * width, 0],
                    [0.5 * width, 100],
                    [0.1 * width, 100],
                ],
            )
        if self.state == 2: #stomp left
            pygame.draw.polygon(
                screen,
                [255, 0, 0],
                [
                    [0.1 * width, 0],
                    [0.5 * width, 0],
                    [0.5 * width, height - 100],
                    [0.1 * width, height - 100],
                ],
            )
        if self.state == 4: #poise right
            pygame.draw.polygon(
                screen,
                [255, 0, 0],
                [
                    [0.5 * width, 0],
                    [0.9 * width, 0],
                    [0.9 * width, 100],
                    [0.5 * width, 100],
                ],
            )
        if self.state == 5: #stomp right
            pygame.draw.polygon(
                screen,
                [255, 0, 0],
                [
                    [0.5 * width, 0],
                    [0.9 * width, 0],
                    [0.9 * width, height - 100],
                    [0.5 * width, height - 100],
                ],
            )


    def collide(self, scene, width, height, cat_head_location):
        #pass
        state = self.states[self.state]
        if state == 'stomp left':
            if self.scene.cat_head_location[0] < width/2:
                self.scene.reset_on_death()
                self.dirty = True
        if state == 'stomp right':
            if self.scene.cat_head_location[0] > width/2:
                self.scene.reset_on_death()
                self.dirty = True


class Lazer(DirtySprite):
    def __init__(self, parent, container, width, height):
        DirtySprite.__init__(self, container)
        self.rect = pygame.Rect([150, parent.laser_height - 5, width, 10])
        self.image = pygame.transform.scale(gfx('shark_laser.png', convert_alpha=True), self.rect.size)


class Shark(DirtySprite):
    def __init__(self, container, scene, width, height):
        DirtySprite.__init__(self, container)
        self.container = container
        self.scene = scene
        self.width, self.height = width, height

        self.state = 0 #
        self.states = {
            0: 'offscreen',
            1: 'about_to_appear',
            2: 'poise',
            3: 'aiming',
            4: 'fire laser',
            5: 'leaving',
        }
        self.last_state = 0
        self.just_happened = None
        self.lazered = False # was the cat hit?
        self.lazer = None
        self.laser_height = height - 150 #where should the laser be on the screen?

        #TODO: to make it easier to test the shark
#        self.time_between_appearances = 1000 #ms
        self.time_between_appearances = 5000 #ms

        self.time_of_about_to_appear = 1000#ms
        self.time_of_poise = 1000 #ms
        self.time_of_aiming = 500 #ms
        self.time_of_laser = 200 #ms
        self.time_of_leaving = 1000 #ms
        self.last_animation = 0 #ms

        self.applaud = True

        sfx('default_shark.ogg')
        sfx('shark_appear.ogg')
        sfx('shark_gone.ogg')
        sfx('shark_lazer.ogg')
        sfx('applause.ogg')
        sfx('cat_shot.ogg')
        sfx("boo.ogg")

        self.image = gfx('shark.png', convert_alpha=True)
        # gfx('foot_part.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = -1000
        self.rect.y = (self.height - self.image.get_height())

    def update(self):
        debug = False

        if debug and self.just_happened:
            print(self.just_happened)

        if self.just_happened == 'offscreen':
            sfx('shark_gone.ogg', stop=1)

            self.rect.x = -1000
            self.dirty = True

        elif self.just_happened == 'about_to_appear':
            music(stop=True)
            self.applaud = True
            sfx('shark_appear.ogg', play=1)

        elif self.just_happened == 'poise':
            sfx('shark_attacks.ogg', play=1)

            self.rect.x = -30
            self.dirty = True

        elif self.just_happened == 'fire laser':
            self.lazer = Lazer(self, self.container, self.width, self.height)

            sfx('shark_lazer.ogg', play=1)

            if self.scene.cat_location[1] >  self.scene.cat_wire_height - 3:
                sfx('cat_shot.ogg', play=1)

                self.lazered = True
            else:
                self.lazered = False

        elif self.just_happened == 'leaving':
            sfx('shark_appear.ogg', fadeout=3500)
            sfx('shark_attacks.ogg', stop=1)
            sfx('shark_gone.ogg', play=1)
            self.dirty = True
            if self.lazered:
                sfx("boo.ogg", play=True)
                self.scene.reset_on_death()
                self.lazered = False
                self.scene.annoy_crowd()
            elif self.applaud:
                sfx('applause.ogg', play=1)
            if self.lazer:
                self.lazer.kill()
                self.lazer = None

    def animate(self, total_time):
        # print('update', self.states[self.state], self.states[self.last_state])
        state = self.states[self.state]
        start_state = self.state

        if state == 'offscreen':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None

            if total_time > self.last_animation + self.time_between_appearances:
                self.state += 1
                self.last_animation = total_time

        elif state == 'about_to_appear':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None

            if total_time > self.last_animation + self.time_of_about_to_appear:
                self.state += 1
                self.last_animation = total_time

        elif state == 'poise':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None

            #smoothly animate upwards
            self.rect.y = (self.height - self.image.get_height()) + 0.2*(self.last_animation + self.time_of_poise - total_time)
            self.dirty = True 

            if total_time > self.last_animation + self.time_of_poise:
                self.state += 1
                self.last_animation = total_time

        elif state == 'aiming':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None

            if total_time > self.last_animation + self.time_of_aiming:
                self.state += 1
                self.last_animation = total_time

        elif state == 'fire laser':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None

            if total_time > self.last_animation + self.time_of_laser:
                self.state += 1
                self.last_animation = total_time

        elif state == 'leaving':
            just_happened = self.state != self.last_state
            if just_happened:
                self.just_happened = state
            else:
                self.just_happened = None

            #smoothly animate downwards
            self.rect.y = (self.height - self.image.get_height()) + 0.2*(total_time - self.last_animation)
            self.dirty = True 

            if total_time > self.last_animation + self.time_of_leaving:
                self.state += 1
                if self.state == max(self.states.keys()) + 1:
                    self.state = 0
                self.last_animation = total_time

        self.last_state = start_state

    #set the state number from the name
    def set_state(self, new_state):
        self.state = list(self.states.values()).index(new_state)

    def get_state(self):
        return self.states[self.state]

    #this function does nothing now I think
    def render(self, screen, width, height):
        state = self.states[self.state]

        if state == 'poise':
            pygame.draw.polygon(
                screen,
                [255, 255, 0],
                [
                    [0, self.laser_height],
                    [0.2 * width, self.laser_height],
                    [0.2 * width, height],
                    [0, height],
                ],
            )
        if state == 'fire laser':
            pygame.draw.polygon(
                screen,
                [255, 255, 0],
                [
                    [0, self.laser_height],
                    [0.2 * width, self.laser_height],
                    [0.2 * width, height],
                    [0, height],
                ],
            )
            pygame.draw.polygon(
                screen,
                [255, 0, 0],
                [
                    [0.2 * width, self.laser_height],
                    [width, self.laser_height],
                    [width, self.laser_height + 10],
                    [0.2 * width, self.laser_height],
                ],
            )


    def collide(self, scene, width, height, cat_location):
        pass
        #TODO: this doesn't work. It means the laser never fires.
        # if self.state == 2:
        #     if cat_location[1] > height - 130:
        #         print('shark collide')
        #         scene.reset_on_death()


class Cat(DirtySprite):
    def __init__(self, cat_holder):
        DirtySprite.__init__(self)
        self.cat_holder = cat_holder
        self.image = gfx('cat_unicycle1.png', convert_alpha=True)
        self.rect = self.image.get_rect()
        sfx('cat_jump.ogg')

        self.images = []
        self.flipped_images = []

        self.last_location = [0, 0]
        self.last_direction = True #right is true
        self.last_rotation = -1
        self.last_frame = None

        self.frame = 1
        self.frame_rate = 750 # time passed in ms before frame changes
        self.frame_time = 0
        self.frame_direction = True # True = increasing, False = decreasing

        self.num_frames = 4

        for i in range(self.num_frames):
            img = gfx('cat_unicycle%d.png' % (i+1), convert_alpha=True)
            self.images.append(img)
            self.flipped_images.append(pygame.transform.flip(img, 1, 0))

    def get_image(self):
        return (self.images, self.flipped_images)[self.cat_holder.cat_speed[0] < 0][self.frame - 1]

    def animate(self, dt):
        self.frame_time += dt
        if self.frame_time >= self.frame_rate:
            if self.frame_direction:
                self.frame += 1
            else:
                self.frame -= 1
            self.frame_time = 0
            if self.frame == self.num_frames or self.frame == 1:
                self.frame_direction = not self.frame_direction

    def update(self):
        direction = self.cat_holder.cat_speed[0] > 0
        # location = self.cat_holder.cat_location
        location = self.cat_holder.cat_head_location
        rotation = self.cat_holder.cat_angle
        #if self.last_location != location:
        #    self.dirty = True
        #    self.rect.x = int(location[0])
        #    self.rect.y = int(location[1])
        if self.last_direction != direction:
            self.dirty = True
            self.image = self.get_image()

        if self.last_rotation != rotation or self.last_location != location or self.last_frame != self.frame:
#            self.image = pygame.transform.rotate(self.image_direction[int(direction)], -self.cat_holder.cat_angle*180/math.pi)
            self.image = pygame.transform.rotate(self.get_image(), -self.cat_holder.cat_angle*180/math.pi)
            size = self.image.get_rect().size
            self.dirty = True
            self.rect.x = int(location[0]) - size[0]*0.5
            self.rect.y = int(location[1]) - size[1]*0.5

        self.last_location == location[:]
        self.last_direction = direction
        self.last_rotation = rotation
        self.last_frame = self.frame

        # draw cat
        # pygame.draw.line(
        #     screen, [0, 0, 255], self.cat_location, self.cat_head_location, 20
        # )
        # pygame.draw.circle(screen, [0, 0, 255], self.cat_head_location, 50, 1)
        # pygame.draw.circle(screen, [0, 255, 0], self.cat_head_location, 100, 1)

class Fish(DirtySprite):
    colors = ["red", "yellow", "green"]

    def __init__(self, group, x, y, vx, vy):
        DirtySprite.__init__(self, group)
        self.image = gfx("fish_" + random.choice(Fish.colors) + ".png", convert_alpha=True)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = pygame.math.Vector2(vx, vy)

        self.last_pos = [x, y]
        self.pos = [x,y]

    def update(self):
        if self.last_pos != self.pos[:2]:
            self.dirty = True
            self.rect.x = self.pos[0] - 25
            self.rect.y = self.pos[1] - 25
        self.last_pos = self.pos[:2]

class NotFish(DirtySprite):
    def __init__(self, group, x, y, vx, vy):
        DirtySprite.__init__(self, group)
        self.image = gfx('ring.png', convert_alpha=True)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = pygame.math.Vector2(vx, vy)

        self.last_pos = [x, y]
        self.pos = [x,y]

    def update(self):
        if self.last_pos != self.pos[:2]:
            self.dirty = True
            self.rect.x = self.pos[0] - 25
            self.rect.y = self.pos[1] - 25
        self.last_pos = self.pos[:2]

SCORE_TEXT_CENTER = (472, 469)

class Score(DirtySprite):
    def __init__(self, score_holder):
        """
        score_holder has a 'score' attrib.
        """
        DirtySprite.__init__(self)
        self.score_holder = score_holder
        self.myfont = pygame.font.SysFont("monospace", 30, bold=True)
        self.image = self.myfont.render(str(self.score_holder.score), True, [0, 0, 0])
        self.update_rect()
        self.last_score = self.score_holder.score

    def update_rect(self):
        self.rect = self.image.get_rect()
        self.rect.center = SCORE_TEXT_CENTER

    def update(self):
        if self.last_score != self.score_holder.score:
            self.dirty = True
            self.image = self.myfont.render(str(self.score_holder.score), True, [0,0,0])
            self.update_rect()
        self.last_score = self.score_holder.score


class DeadZone(DirtySprite):
    def __init__(self, points):
        """
        score_holder has a 'score' attrib.
        """
        DirtySprite.__init__(self)
        color = [255, 0, 0]

        # draw dead zones
        surf = pygame.display.get_surface()
        rect = pygame.draw.polygon(
            surf,
            color,
            points
        )
        self.image = surf.subsurface(rect.clip(surf.get_rect())).copy()
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y


CAT_MAX_JUMPING_TIME = 600 #ms
CAT_JUMP_SPEED = 0.07

JOY_JUMP_BUTTONS = (0, 1)
JOY_LEFT_BUTTONS = (4,)
JOY_RIGHT_BUTTONS = (5,)
JOY_TILT_LEFT_AXIS = 2
JOY_TILT_RIGHT_AXIS = 5
JOY_SENSE = 0.5  # Joystick sensitivity for movement

class CatUniScene(Scene):
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        (width, height) = (1920//2, 1080//2)
        self.width, self.height = width, height

        # Loading screen should always be a fallback active scene
        self.active = False
        self.first_render = True

        self.myfont = pygame.font.SysFont("monospace", 20)

        self.background = gfx('background.png', convert=True)
        # self.cat_unicycle = gfx('cat_unicycle.png').convert_alpha()
        # self.fish = gfx('fish.png').convert_alpha()
        # self.foot = gfx('foot.png').convert_alpha()
        # self.foot_part = gfx('foot_part.png').convert_alpha()
        # self.shark = gfx('shark.png').convert_alpha()

        sfx('cat_jump.ogg')
        sfx('eatfish.ogg')
        sfx('splash.ogg')
        sfx('cat_crash.ogg')

        self.meow_names = ['cat_meow01.ogg', 'cat_meow02.ogg', 'cat_meow03.ogg']
        self.last_meow = None

        self.touching_ground = True
        self.jumping = False
        self.jumping_time = 0
        self.jump_key = None

        for meow_name in self.meow_names:
            sfx(meow_name)

        self.boing_names = ['boing1.ogg', 'boing2.ogg', 'boing3.ogg']
        for boing_name in self.boing_names:
            sfx(boing_name)

        #cat variables
        self.cat_wire_height = height - 100
        self.cat_location = [width / 2, height - 100]
        self.cat_speed = [0, 0]
        self.cat_speed_max = 8
        self.cat_fall_speed_max = 16
        self.cat_roll_speed = .01
        self.cat_angle = 0
        self.cat_angular_vel = 0
        self.cat_head_location = [
            int(self.cat_location[0] + 100 * math.cos(self.cat_angle - math.pi / 2)),
            int(self.cat_location[1] + 100 * math.sin(self.cat_angle - math.pi / 2)),
        ]

        self.people_mad = False
        self.people_mad_duration = 3000 #ms
        self.people_mad_current_time = 0
        self.next_notfish = 0
        self.notfish_time = 0

        self.last_joy_right_tilt = 0
        self.last_joy_left_tilt = 0

        self.left_pressed = False
        self.right_pressed = False

        self.score = 0

        #timing
        self.dt_scaled = 0
        self.total_time = 0

        #elephant and shark classes
        self.elephant = Elephant(self)
        self.shark_active = False #is the shark enabled yet
        self.elephant_active = False
        self.cat = Cat(self)
        self.score_text = Score(self)

        self.deadzones = []

        # self.deadzones = [
        #     DeadZone(
        #         [
        #             [0, height - 100],
        #             [0.1 * width, height - 100],
        #             [0.1 * width, height],
        #             [0, height],
        #         ],
        #     ),
        #     DeadZone(
        #         [
        #             [0.9 * width, height - 100],
        #             [width, height - 100],
        #             [width, height],
        #             [0.9 * width, height],
        #         ],
        #     ),
        # ]

        self.init_sprites()

        # lists of things to catch by [posx, posy, velx, vely]
        # self.fish = [[0, height / 2, 10, -5]]
        self.fish = LayeredDirtyAppend()
        self.fish.extend([Fish(self.allsprites, 0, height / 2, 10, -5)])

        self.not_fish = LayeredDirtyAppend()
                
        self.unicycle_sound = sfx('unicycle.ogg', play=True, loops=-1, fadein=500)

        self.reset_meow()

        #difficulty varibles
        self.number_of_not_fish = 0

    def reset_meow(self):
        self.next_meow = random.uniform(5000, 10000)

    def meow(self):
        # Play a meow sound, but not the same one twice in a row
        meow_names = self.meow_names[:]
        if self.last_meow in self.meow_names:
            meow_names.remove(self.last_meow)
        self.last_meow = random.choice(meow_names)
        sfx(self.last_meow, play=1)
        self.reset_meow()

    def init_sprites(self):
        """temp, this will go in the init.
        """
        sprite_list = [
            self.elephant,
            self.cat,
            self.score_text
        ]
        sprite_list += self.deadzones
        self.allsprites = LayeredDirty(
            sprite_list,
            _time_threshold=1000/10.0
        )
        scene = self
        self.shark = Shark(self.allsprites, scene, self.width, self.height)
        self.allsprites.add(self.shark)
        self.allsprites.clear(self.screen, self.background)


    #what to do when you die, reset the level
    def reset_on_death(self):
        self.cat_location = [self.width / 2, self.height - 100]
        self.cat_speed = [0, 0]
        self.cat_angle = 0
        self.cat_angular_vel = 0
        self.score = 0
        self.total_time = 0

        self.elephant.last_animation = 0
        self.elephant.state = 0
        self.elephant.just_happened = None
        self.elephant.dirty = 1
        self.elephant_active = False
        self.elephant.animate(self.total_time)

        #make the shark leave
        self.shark_active = False
        self.shark.last_animation = 0
        self.shark.dirty = True

        if self.shark.get_state() in ('aiming', 'fire laser'):
            self.shark.just_happenend = None
            self.shark.set_state('leaving')
            self.shark.applaud = False
        else:
            self.shark.just_happenend = None
            self.shark.set_state('offscreen')
            self.shark.animate(self.total_time)

        sfx('shark_appear.ogg', fadeout=1000)

        if self.shark.lazer:
            self.shark.lazer.kill()

    #periodically increase the difficulty
    def increase_difficulty(self):
        self.number_of_not_fish = 0
        if self.score > 3:
            self.number_of_not_fish = 1
        if self.score > 9:
            self.number_of_not_fish = 1
        if self.score > 15:
            self.number_of_not_fish = 2
        if self.score > 19:
            self.number_of_not_fish = 1
        if self.score > 25:
            self.number_of_not_fish = 2
        if self.score > 35:
            self.number_of_not_fish = 3
        if self.score >= 50:
            self.number_of_not_fish = int((self.score - 20)/10)

        #TODO: to make it easier to test.
        # if self.score >= 15:
        #     self.shark_active = True
        if self.score >= 10:
            self.shark_active = True

        #TODO: to make it easier to test.

        # Elephant doesn't work yet, so let's not use it
#        if self.score >= 20:
#            self.elephant_active = True

    def annoy_crowd(self):
        self.people_mad = True
        self.people_mad_current_time = 0

    def render_sprites(self):
        rects = []
        self.allsprites.update()
        rects.extend(self.allsprites.draw(self.screen))
        return rects

    def render(self):
        rects = []
        if self.first_render:
            self.first_render = False
            rects.append(self.screen.get_rect())
        rects.extend(self.render_sprites())
        return rects

    def tick(self, dt):
        self.increase_difficulty()

        self.cat.animate(dt)

        self.total_time += dt #keep track of the total number of ms passed during the game
        dt_scaled = dt/17
        self.dt_scaled = dt_scaled
        width, height = self.width, self.height

        ##cat physics
        self.cat_angular_vel *= 0.9**dt_scaled #max(0.9/(max(0.1,dt_scaled)),0.999)

        #make the cat slide in the direction it's rotated
        self.cat_speed[0] += math.sin(self.cat_angle) * (dt_scaled * self.cat_roll_speed)

        # add gravity
        self.cat_speed[1] = min(self.cat_speed[1] + (1 * dt_scaled), self.cat_fall_speed_max)

        self.unicycle_sound.set_volume(abs(self.cat_speed[0] / self.cat_speed_max))

        # accelerate the cat left or right
        if self.right_pressed:
            self.cat_speed[0] = min(
                self.cat_speed[0] + 0.3 * dt_scaled, self.cat_speed_max
            )
            self.cat_angle -= 0.003 * dt_scaled

        if self.left_pressed:
            self.cat_speed[0] = max(
                self.cat_speed[0] - 0.3 * dt_scaled, -self.cat_speed_max
            )
            self.cat_angle += 0.003 * dt_scaled

        # make the cat fall
        angle_sign = 1 if self.cat_angle > 0 else -1
        self.cat_angular_vel += 0.0002 * angle_sign * dt_scaled
        self.cat_angle += self.cat_angular_vel * dt_scaled
        if (self.cat_angle > math.pi / 2 or self.cat_angle < -math.pi / 2) and self.cat_location[1] > height - 160:
            sfx('cat_crash.ogg', play=1)
            self.reset_on_death()

        # move cat
        self.cat_location[0] += self.cat_speed[0] * dt_scaled
        self.cat_location[1] += self.cat_speed[1] * dt_scaled
        if self.cat_location[1] > self.cat_wire_height and self.cat_location[0] > 0.25 * width:
            self.touching_ground = True
            self.cat_location[1] = self.cat_wire_height
            self.cat_speed[1] = 0
        else:
            self.touching_ground = False

        if self.cat_location[1] > height:
            sfx('splash.ogg', play=1)
            self.meow()
            self.reset_on_death()
        if self.cat_location[0] > width:
            self.cat_location[0] = width
            if self.cat_angle > 0:
                self.cat_angle *= 0.7
        self.cat_head_location = [
            int(self.cat_location[0] + 100 * math.cos(self.cat_angle - math.pi / 2)),
            int(self.cat_location[1] + 100 * math.sin(self.cat_angle - math.pi / 2)),
        ]

        # check for out of bounds
        if self.cat_location[0] > 0.98 * width and self.cat_location[1] > self.cat_wire_height - 30:
            #bump the cat back in
            self.meow()
            sfx(random.choice(self.boing_names), play=True)
            self.cat_angular_vel -= 0.01*dt_scaled
            self.cat_speed[0] = -5
            self.cat_speed[1] = -20
            #self.reset_on_death()
        if self.cat_location[0] < 0.25 * width and self.cat_location[1] > self.cat_wire_height - 30:
            pass

        #check for collision with the elephant stomp
        if self.elephant_active:
            self.elephant.animate(self.total_time)
            self.elephant.collide(self, width, height, self.cat_head_location)
        if self.shark_active or self.shark.states[self.shark.state] == 'leaving':
            self.shark.animate(self.total_time)
            self.shark.collide(self, width, height, self.cat_location)

        #jumping physics
        if self.jumping:
            self.cat_speed[1] -= dt * ((CAT_MAX_JUMPING_TIME - self.jumping_time) / CAT_MAX_JUMPING_TIME) * CAT_JUMP_SPEED
            self.jumping_time += dt
            if self.jumping_time >= CAT_MAX_JUMPING_TIME:
                self.jumping = False

        ##meow timing
        if self.next_meow <= 0:
            self.meow()
        self.next_meow -= dt

        ##angry people (increased throwing of not-fish)
        if self.people_mad:
            self.people_mad_current_time += dt
            self.notfish_time += dt
            if self.notfish_time >= self.next_notfish:
                self.next_notfish = random.randint(100, 400)
                self.notfish_time = 0
                self.SpawnNotFish()
            if self.people_mad_current_time >= self.people_mad_duration:
                self.people_mad = False

        ##object physics

        # move fish and not fish
        for f in reversed(self.fish.sprites()):
            f.pos[0] += f.velocity[0] * dt_scaled  # speed of the throw
            f.velocity[1] += 0.2 * dt_scaled  # gravity
            f.pos[1] += f.velocity[1] * dt_scaled # y velocity
            # check out of bounds
            if f.pos[1] > height:
                self.fish.remove(f)
                f.kill()
        for f in reversed(self.not_fish.sprites()):
            f.pos[0] += f.velocity[0] * dt_scaled # speed of the throw
            f.velocity[1] += 0.2 * dt_scaled  # gravity
            f.pos[1] += f.velocity[1] * dt_scaled  # y velocity
            # check out of bounds
            if f.pos[1] > height:
                self.not_fish.remove(f)
                f.kill()

        # check collision with the cat
        for f in reversed(self.fish.sprites()):
            if distance([f.rect[0], f.rect[1]], self.cat_head_location) < 100:
                self.score += 1
                self.fish.remove(f)
                sfx('eatfish.ogg', play=1)
                f.kill()
        for f in reversed(self.not_fish.sprites()):
            if distance([f.rect[0], f.rect[1]], self.cat_head_location) < 50:
                self.not_fish.remove(f)
                f.kill()
                self.angle_to_not_fish = (
                    math.atan2(
                        self.cat_head_location[1] - f.rect[1],
                        self.cat_head_location[0] - f.rect[0],
                    )
                    - math.pi / 2
                )
                side = 1 if self.angle_to_not_fish < 0 else -1
                self.cat_angular_vel += side * random.uniform(0.08, 0.15)
                sfx(random.choice(self.boing_names), play=True)

        # refresh lists
        while len(self.fish) < 1 and not self.people_mad:
            # choose a side of the screen
            if random.choice([0, 1]) == 0:
                self.fish.append(
                    Fish(self.allsprites,
                        0,
                        height/2,#random.randint(0, height / 2),
                        random.randint(3, 7),
                        -random.randint(5, 12),
                    )
                )
            else:
                self.fish.append(
                    Fish(self.allsprites,
                        width,
                        height/2,#random.randint(0, height / 2),
                        -random.randint(3, 7),
                        -random.randint(5, 12),
                    )
                )
        while len(self.not_fish) < self.number_of_not_fish:
            self.SpawnNotFish()

    def SpawnNotFish(self):
        # choose a side of the screen
        velocity_multiplier = 1
        x_pos = 0
        if random.randint(0, 1):
            velocity_multiplier *= -1
            x_pos = self.width
        self.not_fish.append(
                NotFish(self.allsprites,
                    x_pos,
                    self.height / 2,
                    random.randint(3, 7) * velocity_multiplier,
                    -random.randint(5, 12),
                )
        )

    def start_jump(self, key):
        self.jump_key = key
        if self.touching_ground and not self.jumping:
            self.jumping = True
            self.jumping_time = 0
            self.cat_speed[1] -= 12.5
            sfx('cat_jump.ogg', play=1)

    def stop_jump(self):
        self.jumping = False
        sfx('cat_jump.ogg', fadeout=50)

    def tilt_left(self):
        self.cat_angular_vel -= random.uniform(0.01 * math.pi, 0.03 * math.pi)

    def tilt_right(self):
        self.cat_angular_vel += random.uniform(0.01 * math.pi, 0.03 * math.pi)

    def event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                self.right_pressed = True
            elif event.key == K_LEFT:
                self.left_pressed = True
            elif event.key == K_a:
                self.tilt_left()
            elif event.key == K_d:
                self.tilt_right()
            elif event.key in (K_UP, K_SPACE):
                self.start_jump(event.key)
        elif event.type == KEYUP:
            if event.key == self.jump_key:
                self.stop_jump()
            elif event.key == K_RIGHT:
                self.right_pressed = False
            elif event.key == K_LEFT:
                self.left_pressed = False

        if event.type == JOYBUTTONDOWN:
            if event.button in JOY_JUMP_BUTTONS:
                self.start_jump("JOY" + str(event.button))
            if event.button in JOY_LEFT_BUTTONS:
                self.tilt_left()
            if event.button in JOY_RIGHT_BUTTONS:
                self.tilt_right()

        if event.type == JOYBUTTONUP:
            if "JOY" + str(event.button) == self.jump_key:
                self.stop_jump()

        if event.type == JOYAXISMOTION:
            if event.axis == 0:
                if event.value >= JOY_SENSE:
                    self.right_pressed = True
                    self.left_pressed = False
                elif event.value <= -JOY_SENSE:
                    self.right_pressed = False
                    self.left_pressed = True
                else:
                    self.right_pressed = False
                    self.left_pressed = False
            if event.axis == JOY_TILT_RIGHT_AXIS:
                if self.last_joy_right_tilt < JOY_SENSE and event.value >= JOY_SENSE:
                    self.tilt_right()
                self.last_joy_right_tilt = event.value
            if event.axis == JOY_TILT_LEFT_AXIS:
                if self.last_joy_left_tilt < JOY_SENSE and event.value >= JOY_SENSE:
                    self.tilt_left()
                self.last_joy_left_tilt = event.value
