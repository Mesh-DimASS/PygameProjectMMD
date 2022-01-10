import pygame
import os
import sys
import random

spawn_flag = False
pygame.init()
size = width, height = 1500, 800
screen = pygame.display.set_mode(size)
background_rect = screen.get_rect()
air_x = 0
font_name = pygame.font.match_font('arial')


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

    def done_par(self):
        screen.blit(screen, background_rect)
        draw_text(screen, 'Survivors:' + str(self.done), 18, width / 2, 10)


class Airplane(pygame.sprite.Sprite):
    image = load_image("airplane.png", -1)

    def __init__(self):
        super().__init__(all_sprites)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.image = Airplane.image

    def update(self):
        self.rect = self.rect.move(5, 0)
        if self.rect.bottomleft[0] % 100 == 0 and self.rect.bottomleft[0] < 1000:
            Parachutist(self.rect.bottomleft[0], mountain)
        if self.rect.center[0] > 4000:
            self.rect.x = 0
            self.rect.y = 0


class Parachutist(pygame.sprite.Sprite):
    image = load_image("parach.png", -1)

    def __init__(self, air_x, mountain):
        super().__init__(all_sprites)
        self.image = Parachutist.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = air_x
        self.rect.y = random.choice(range(10))

    def update(self):
        if not pygame.sprite.collide_mask(self, mountain):
            self.rect = self.rect.move(0, 1)
        else:
            mountain.done += 1
            self.kill()


def terminate():
    pygame.quit()
    sys.exit()


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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(fps)


all_sprites = pygame.sprite.Group()
mountain = Mountain()
running = True
clock = pygame.time.Clock()
fps = 60
start_screen()
Airplane()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(fps)
    screen.fill((0, 191, 255))
    mountain.done_par()
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()