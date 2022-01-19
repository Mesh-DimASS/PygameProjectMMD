import pygame
import os
import sys
import random
from os import path
import sqlite3
import datetime as dt
import time

spawn_flag = False
pygame.init()
size = width, height = 1500, 800
screen = pygame.display.set_mode(size)
background_rect = screen.get_rect()
air_x = 0
font_name = pygame.font.match_font('arial')
shots = 0


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Mountain(pygame.sprite.Sprite):
    image = load_image("theme.png", -1)

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Mountain.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height
        self.done = 0
        self.kil = 0

    def done_par(self):
        screen.blit(screen, background_rect)
        draw_text(screen, 'Выжившие:' + str(self.done), 30, 880, 10)
        draw_text(screen, 'Подбитые:' + str(self.kil), 30, 670, 10)


class Airplane(pygame.sprite.Sprite):
    image = load_image("airplane.png", -1)

    def __init__(self):
        super().__init__(all_sprites)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.image = Airplane.image

    def update(self):
        self.rect = self.rect.move(10, 0)
        if self.rect.bottomleft[0] % 200 == 0 and self.rect.bottomleft[0] < 1600:
            Parachutist(self.rect.bottomleft[0])
            if time < 400 and random.choice(range(10)) in range(2):
                Bomb(self.rect.bottomleft[0])
            if 800 > time > 600 and random.choice(range(10)) in range(4):
                Bomb(self.rect.bottomleft[0])
            if time > 800 and random.choice(range(10)) in range(7):
                Bomb(self.rect.bottomleft[0])

        if self.rect.center[0] > 2000:
            self.rect.x = 0
            self.rect.y = 0


class CaughtParach(pygame.sprite.Sprite):
    image = load_image("kil_par.png", -1)

    def __init__(self, par_coord):
        super().__init__(all_sprites)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = par_coord
        self.image = CaughtParach.image

    def update(self):
        if not pygame.sprite.collide_mask(self, mountain):
            self.rect = self.rect.move(0, 12)
        else:
            mountain.kil += 1
            self.kill()


class Boom(pygame.sprite.Sprite):
    image = load_image("Boom.png", -1)

    def __init__(self, par_coord):
        super().__init__(all_sprites)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = par_coord
        self.image = Boom.image

    def update(self):
        if time % 60 == 0:
            self.kill()


class Bomb(pygame.sprite.Sprite):
    image = load_image("bomb.png", -1)

    def __init__(self, air_x):
        super().__init__(all_sprites)
        self.image = Bomb.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = air_x + random.choice(range(-200, 10))
        self.rect.y = random.choice(range(100))

    def update(self):
        if not pygame.sprite.collide_mask(self, mountain):
            self.rect = self.rect.move(0, 10)
        elif pygame.sprite.collide_mask(self, mountain):
            Boom((self.rect.x, self.rect.y))
            self.kill()
        for sprite in friendly_buildings_squad:
            if pygame.sprite.collide_mask(self, sprite):
                DeadGun((sprite.rect.x, sprite.rect.y))
                self.kill()
                sprite.kill()


class DeadGun(pygame.sprite.Sprite):
    image = load_image("destr_gun.png", -1)

    def __init__(self, par_coord):
        super().__init__(all_sprites)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = par_coord
        self.image = DeadGun.image
        end_screen_lose()


class Net(pygame.sprite.Sprite):
    image = load_image("web.png", -1)

    def __init__(self, gun_x):
        super().__init__(all_sprites)
        self.rect = self.image.get_rect()
        self.image = Net.image
        self.rect.x = gun_x - 20
        self.rect.y = 540
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect = self.rect.move(0, -13)
        for sprite in parach_squad:
            if pygame.sprite.collide_mask(self, sprite):
                self.kill()
                CaughtParach((sprite.rect.x, sprite.rect.y))
                sprite.kill()


class Gun(pygame.sprite.Sprite):
    image = load_image("gun.png", -1)

    def __init__(self):
        super().__init__(all_sprites)
        self.rect = self.image.get_rect()
        self.rect.y = 600
        self.image = Gun.image
        friendly_buildings_squad.add(self)

    def update(self):
        self.rect.x = pygame.mouse.get_pos()[0] - 71


class AnimatedSprite(pygame.sprite.Sprite):
    img = load_image('animated_helicopter.png')

    def __init__(self, img, columns, rows):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(img, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(0, 0)

    def cut_sheet(self, img, columns, rows):
        self.rect = pygame.Rect(0, 0, img.get_width() // columns,
                                img.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(img.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(10, 0)
        if self.rect.bottomleft[0] % 200 == 0 and self.rect.bottomleft[0] < 1600:
            Parachutist(self.rect.bottomleft[0])
            if time < 400 and random.choice(range(10)) in range(2):
                Bomb(self.rect.bottomleft[0])
            if 800 > time > 600 and random.choice(range(10)) in range(4):
                Bomb(self.rect.bottomleft[0])
            if time > 800 and random.choice(range(10)) in range(7):
                Bomb(self.rect.bottomleft[0])

        if self.rect.center[0] > 2000:
            self.rect.x = 0
            self.rect.y = 0


class Parachutist(pygame.sprite.Sprite):
    image = load_image("parach.png", -1)

    def __init__(self, air_x):
        super().__init__(all_sprites)
        self.image = Parachutist.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = air_x + random.choice(range(-200, 10))
        self.rect.y = random.choice(range(100))
        parach_squad.add(self)

    def update(self):
        if not pygame.sprite.collide_mask(self, mountain):
            self.rect = self.rect.move(0, 5)
        else:
            mountain.done += 1
            self.kill()


class Cursor(pygame.sprite.Sprite):
    image = load_image("aim.png", -1)

    def __init__(self):
        super().__init__(mouse_sprite)
        self.image = Cursor.image
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)

    def update(self):
        self.rect.center = (pygame.mouse.get_pos()[0] + 5, pygame.mouse.get_pos()[1])


def terminate():
    pygame.quit()
    sys.exit()


def pause_screen():
    pygame.mouse.set_visible(True)
    with open(os.path.join('data', 'pause_text'), encoding="UTF-8") as a:
        pause_text = list(map(str.strip, a.readlines()))
        fon = pygame.transform.scale(load_image('fon.jpg'), size)
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 70)
        text_coord = 30
        for line in pause_text:
            string_rendered = font.render(line, 2, pygame.Color('black'))
            pause_rect = string_rendered.get_rect()
            text_coord += 10
            pause_rect.top = text_coord
            pause_rect.x = 520
            text_coord += pause_rect.height + 50
            screen.blit(string_rendered, pause_rect)
        font = pygame.font.Font(None, 50)
        text = font.render("Начать заново", True, (100, 255, 100))
        text_x = 50
        text_y = 550
        text_w = text.get_width()
        text_h = text.get_height()
        pygame.draw.rect(screen, (255, 255, 255), (text_x - 10, text_y - 10,
                                                   text_w + 20, text_h + 20), 0)
        screen.blit(text, (text_x, text_y))

        text = font.render("Продолжить", True, (100, 255, 100))
        text_x = 1250
        text_y = 550
        text_w = text.get_width()
        text_h = text.get_height()
        pygame.draw.rect(screen, (255, 255, 255), (text_x - 10, text_y - 10,
                                                   text_w + 20, text_h + 20), 0)
        screen.blit(text, (text_x, text_y))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.set_volume(0.4)
                    pygame.mouse.set_visible(False)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return
                pygame.display.flip()
                clock.tick(fps)


def end_screen_win():
    con = sqlite3.connect('history.db')
    cur = con.cursor()
    cur.execute("""INSERT INTO hist_tab (day, time, score) VALUES (?, ?
                , ?)""", (
        dt.datetime.now().date().strftime("%d.%m.%Y"), dt.datetime.now().time().strftime("%H:%M"), mountain.kil))
    con.commit()
    with open(os.path.join('data', 'win_text'), encoding="UTF-8") as a:
        intro_text = list(map(str.strip, a.readlines()))
    fon = pygame.transform.scale(load_image('win_fon.jpg'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 100
        intro_rect.top = text_coord
        intro_rect.x = 400
        text_coord += intro_rect.height + 5
        screen.blit(string_rendered, intro_rect)

    snd_dir = path.join(path.dirname(__file__), 'snd')
    pygame.mixer.music.load(path.join(snd_dir, 'start_music.ogg'))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(loops=-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(fps)


def end_screen_lose():
    con = sqlite3.connect('history.db')
    cur = con.cursor()
    cur.execute("""INSERT INTO hist_tab (day, time, score) VALUES (?, ?
            , ?)""", (
        dt.datetime.now().date().strftime("%d.%m.%Y"), dt.datetime.now().time().strftime("%H:%M"), mountain.kil))
    con.commit()
    with open(os.path.join('data', 'lose_text'), encoding="UTF-8") as a:
        intro_text = list(map(str.strip, a.readlines()))
    fon = pygame.transform.scale(load_image('lose_fon.jpg'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 100
        intro_rect.top = text_coord
        intro_rect.x = 400
        text_coord += intro_rect.height + 5
        screen.blit(string_rendered, intro_rect)

    snd_dir = path.join(path.dirname(__file__), 'snd')
    pygame.mixer.music.load(path.join(snd_dir, 'start_music.ogg'))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(loops=-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(fps)


def start_screen():
    with open(os.path.join('data', 'intro_text'), encoding="UTF-8") as a:
        intro_text = list(map(str.strip, a.readlines()))

    fon = pygame.transform.scale(load_image('fon.jpg'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height + 50
        screen.blit(string_rendered, intro_rect)

    snd_dir = path.join(path.dirname(__file__), 'snd')
    pygame.mixer.music.load(path.join(snd_dir, 'start_music.ogg'))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(loops=-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(path.join(snd_dir, 'rock2.mp3'))
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(loops=-1)
                return
        pygame.display.flip()
        clock.tick(fps)


def reload():
    screen.blit(screen, background_rect)
    draw_text(screen, 'Перегрев орудия!!!', 30, 1300, 600)


mouse_sprite = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
parach_squad = pygame.sprite.Group()
friendly_buildings_squad = pygame.sprite.Group()
mountain = Mountain()
running = True
clock = pygame.time.Clock()
fps = 30
shots = 0
reloading = False
start_screen()
Gun()
Cursor()
AnimatedSprite(load_image("animated_helicopter.png", -1), 1, 4)
time = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if shots <= 10:
            if event.type == pygame.MOUSEBUTTONDOWN:
                Net(event.pos[0])
                shots += 1
                reloading = False
        if shots == 11:
            reloading = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mixer.music.set_volume(0)
            pause_screen()
    time += 1
    clock.tick(fps)
    if time % 240 == 0:
        shots = 0
        reloading = False
    screen.fill((0, 191, 255))
    mountain.done_par()
    all_sprites.draw(screen)
    all_sprites.update()
    mouse_sprite.draw(screen)
    mouse_sprite.update()
    if reloading:
        reload()
    if mountain.kil == 50:
        end_screen_win()

    if mountain.done == 5:
        end_screen_lose()
    pygame.display.flip()
    pygame.display.flip()
