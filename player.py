from os import path

import pygame
import pygame._sdl2 as sdl2

import settings


class Player:
    POSX = 100
    VELX = 100
    INITIAL_VELY = 0
    UP_VEL = 200
    G_ACC = -500
    WINGS_SOUND_VOL = 0.004
    def __init__(self, screenw, screenh, renderer):
        self.screenw, self.screenh = screenw, screenh
        self.renderer = renderer

        self.pos = pygame.Vector2(self.POSX, self.screenh / 2)
        self.vely = self.INITIAL_VELY

        self.load_texture()
        self.load_sound()

        self.animation_factor  = 0
        self.state = "idle"
        self.score = 0

    def load_texture(self):
        image = pygame.image.load(path.join(settings.ASSETS_PATH, "player.png"))
        self.sprite_sheet = {
        "columns": 4,
        "rows": 1,
        "animation_speed": 8, # In frames/sec
        "sheet": sdl2.Texture.from_surface(self.renderer, image)
        }
        self.rect = pygame.Rect(
            self.POSX,
            0,
            self.sprite_sheet["sheet"].width / self.sprite_sheet["columns"],
            self.sprite_sheet["sheet"].height / self.sprite_sheet["rows"],
            )
        self.rect.centery = self.pos.y

    def load_sound(self):
        self.wings_sound = pygame.mixer.Sound(
            path.join(settings.ASSETS_PATH, "wings.wav")
            )
        self.wings_sound.set_volume(self.WINGS_SOUND_VOL * settings.VOLUME)

    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.state not in ("collided", "died"):
            self.vely = self.UP_VEL
            self.wings_sound.play()
            self.state = "moving"

    def physics(self, dt, base_height):
        if self.state !="idle":
            self.move_vertically(dt)
            self.clamp_pos(base_height)
        if self.state not in ("collided", "died"):
            self.move_horizontally(dt)
        self.animate(dt, self.sprite_sheet)

    def draw(self):
        self.renderer.blit(
            self.sprite_sheet["sheet"],
            self.rect,
            pygame.Rect(*self.get_sprite_pos(self.sprite_sheet), self.rect.w, self.rect.h),
            )

    def reset(self):
        self.animation_factor  = 0
        self.state = "idle"
        self.score = 0

        self.pos = pygame.Vector2(self.POSX, self.screenh / 2)
        self.vely = self.INITIAL_VELY
        self.rect.centery = self.pos.y

    def animate(self, dt, sprite_sheet):
        self.animation_factor = (
            self.animation_factor
            + sprite_sheet["animation_speed"] * dt
            ) % (
            sprite_sheet["rows"] * sprite_sheet["columns"])
        self.animation_index = int(self.animation_factor)

    def get_sprite_pos(self, sprite_sheet):
        row = self.animation_index // sprite_sheet["columns"]
        column = self.animation_index % sprite_sheet["columns"]
        return column * self.rect.w, row * self.rect.h

    def move_vertically(self, dt):
        self.vely += self.G_ACC * dt
        self.pos.y -= self.vely * dt

    def move_horizontally(self, dt):
        self.pos.x += self.VELX * dt

    def clamp_pos(self, base_height):
        self.rect.centery = self.pos.y
        if self.rect.top < 0:
            self.rect.top = 0
            self.pos.y = self.rect.centery
            self.vely = 0
        elif self.rect.bottom > self.screenh - base_height:
            self.rect.bottom = self.screenh - base_height
            self.pos.y = self.rect.centery
            if self.state == "collided":
                self.state = "died"
