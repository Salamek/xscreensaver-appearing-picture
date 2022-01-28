import random
import signal
import os
import sys
from typing import Callable
from pathlib import Path

# Disable stupid pygame message on import
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame


class BouncingText(pygame.sprite.Sprite):
    picture = None
    picture_dimensions = None

    def __init__(self):
        super(BouncingText, self).__init__()
        self.rect = pygame.Rect((1, 1), (1, 1))

    def set_picture(self, picture_path: Path):
        self.picture = pygame.image.load(picture_path.absolute())
        self.picture_dimensions = (self.picture.get_width(), self.picture.get_height())
        self.update_image(0)

    def update_image(self, alpha: int = 255):
        if not self.picture or not self.picture_dimensions:
            raise ValueError('No picture was set')
        # A transparent surface onto which we blit the text surfaces.
        self.image = pygame.Surface(self.picture_dimensions, pygame.SRCALPHA)
        self.image.fill((255, 255, 255, alpha))
        self.image.blit(self.picture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # Get a new rect (if you maybe want to make the text clickable).
        self.rect = self.image.get_rect(topleft=self.rect.topleft)


class Screensaver:
    def __init__(self,
                 picture_path_callable: Callable[[], Path],
                 full_screen: bool = False,
                 show_fps: bool = False,
                 background_color: str = '#000000',
                 animation_speed: int = 1,
                 display_time: int = 1,
                 fps: int = 60,
                 window_id: str = None
                 ):
        self.picture_path_callable = picture_path_callable
        self.show_fps = show_fps
        self.background_color = pygame.Color(background_color)
        self.animation_speed = animation_speed
        self.display_time = display_time
        self.fps = fps
        signal.signal(signal.SIGTERM, self.handle_term)

        window_id = os.environ.get('XSCREENSAVER_WINDOW', window_id)
        if window_id:
            os.environ['SDL_WINDOWID'] = window_id

        pygame.init()
        pygame.display.set_caption('Appearing picture screensaver')
        pygame.mouse.set_visible(False)
        info_object = pygame.display.Info()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if full_screen else pygame.display.set_mode((info_object.current_w, info_object.current_h))

        self.width, self.height = self.screen.get_size()
        self.fps_font = pygame.font.Font(None, 40)

    def handle_term(self, signal=None, frame=None):
        pygame.quit()
        sys.exit(0)

    def update_fps(self):
        fps = 'FPS: {}'.format(int(self.clock.get_fps()))
        fps_text = self.fps_font.render(fps, True, pygame.Color("coral"))
        return fps_text

    def run(self):
        appearing_picture = BouncingText()
        all_sprites = pygame.sprite.Group(appearing_picture)

        timer_event = pygame.USEREVENT + 1

        max_alpha = 255
        min_alpha = 0
        picture_alpha = 0
        fading_in = True
        fading_out = False

        def _place_picture():
            appearing_picture.set_picture(self.picture_path_callable())
            if self.width > appearing_picture.rect.width:
                position_x = random.randint(0, self.width - appearing_picture.rect.width)
            elif self.width < appearing_picture.rect.width:
                position_x = random.randint(0, appearing_picture.rect.width - self.width)
            else:
                position_x = 0

            if self.height > appearing_picture.rect.height:
                position_y = random.randint(0, self.height - appearing_picture.rect.height)
            elif self.height < appearing_picture.rect.height:
                position_y = random.randint(0, appearing_picture.rect.height - self.height)
            else:
                position_y = 0
            appearing_picture.rect.x = position_x
            appearing_picture.rect.y = position_y

        _place_picture()
        pygame.time.set_timer(timer_event, self.display_time * 1000)  # display_time is in seconds, set_timer accepts ms, that's why *1000
        while True:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_term()

                elif event.type == timer_event:
                    fading_out = True

            if fading_in:
                if picture_alpha < max_alpha:
                    picture_alpha += self.animation_speed

                # Since we can have configurable speed we need to check for overflow
                if picture_alpha > max_alpha:
                    picture_alpha = max_alpha

                if picture_alpha == max_alpha:
                    fading_in = False

            elif fading_out:
                if picture_alpha > min_alpha:
                    picture_alpha -= self.animation_speed

                # Since we can have configurable speed we need to check for underflow
                if picture_alpha < min_alpha:
                    picture_alpha = min_alpha

                if picture_alpha == min_alpha:
                    fading_out = False
                    _place_picture()
                    fading_in = True

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

            if fading_in or fading_out:
                appearing_picture.update_image(picture_alpha)

            self.screen.fill(self.background_color)
            if self.show_fps:
                self.screen.blit(self.update_fps(), (10, 0))
            all_sprites.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.fps)
