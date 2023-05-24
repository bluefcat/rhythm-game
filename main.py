"""
main python
"""
from optparse import OptionParser
from typing import Any, Callable, Dict, List
from random import randint
import pygame

from note import Note, ShortNote, LongNote, NoteBuilder, NoteManager, Grade
from keyboard import KeyboardController

class Game:
    """
    Object for main Game controlled
    """
    def __init__(self, rect: pygame.Rect, fps: int, debug: bool = False):
        pygame.init()

        self.rect = rect
        self.screen: Any = pygame.display.set_mode((self.rect.width, self.rect.height))
        self.fps: int = fps
        self.debug = debug

        self.fps_clock: Any = pygame.time.Clock()

        self.running: bool = True

        self.event: Dict[Any, Callable[[Any], Any]] = {
            pygame.QUIT: self.quit,
            pygame.KEYDOWN: self.keydown,
            pygame.KEYUP: self.keyup
        }

        bpm: float = 60
        self.note_manager = NoteManager(
            pygame.Rect((0, 0), (self.rect.width, self.rect.height-50)),
            bpm,
            self.fps,
            debug
        )
        self.note_builder = NoteBuilder(
            self.note_manager
        )

        self.keyboard_controller = KeyboardController()

        self.keyboard_controller.append_down('d', lambda: self.enter_note(0))
        self.keyboard_controller.append_up('d', lambda: self.note_manager.exit_note(0))
        self.keyboard_controller.append_down('f', lambda: self.enter_note(1))
        self.keyboard_controller.append_up('f', lambda: self.note_manager.exit_note(1))
        self.keyboard_controller.append_down('j', lambda: self.enter_note(2))
        self.keyboard_controller.append_up('j', lambda: self.note_manager.exit_note(2))
        self.keyboard_controller.append_down('k', lambda: self.enter_note(3))
        self.keyboard_controller.append_up('k', lambda: self.note_manager.exit_note(3))

        self.effect = pygame.image.load('resource/image/effect.png')

        self.combo_image = [pygame.image.load(f'resource/image/{i}.png') for i in range(0, 10)]

        self.p = None

        self.p_image = {
            Grade.NONE: None,
            Grade.MISS: pygame.image.load('resource/image/miss.png'),
            Grade.GREAT: pygame.image.load('resource/image/great.png'),
            Grade.PERPECT: pygame.image.load('resource/image/perfect.png')
        }

    def enter_note(self, i):
        self.p = self.note_manager.enter_note(i)
        


    def keydown(self) -> None:
        """
        keydown
        """
        self.keyboard_controller.keydown()

    def keyup(self):
        """
        keyup
        """
        self.keyboard_controller.keyup()

    def run(self) -> None:
        """
        run game
        """

        count = 0
        idx = randint(0, 3)
        self.note_manager.append_note(*self.note_builder.build(idx, 10 + idx * 60, 1))

        while self.running:
            #
            # Screen Update START
            #
            
            self.screen.fill(0)
            # combo drawing 

            if self.p != None and self.p_image[self.p] != None:
                image = self.p_image[self.p]
                a = self.rect.width/2 - image.get_width()/2
                self.screen.blit(image, (a, 100))

            combo: str = f"{self.note_manager.combo}"
            margin = 47
            init_x, init_y = 0, self.rect.height / 2 - self.combo_image[0].get_height()- 100

            for idx, c in enumerate(combo):
                n: int = int(c, base=10)

                image = self.combo_image[n]
                x = init_x + idx * (self.combo_image[0].get_width() - margin)
                y = init_y

                self.screen.blit(image, (x, y))
            # combo drawing end

            if count > 20:
                count = 0
                idx = randint(0, 3)
                self.note_manager.append_note(*self.note_builder.build(idx, 10 + idx * 60, 1))

            if self.keyboard_controller.is_pressed('d'):
                self.screen.blit(self.effect, (10, self.rect.bottom-50-self.effect.get_height()))

            if self.keyboard_controller.is_pressed('f'):
                self.screen.blit(self.effect, (70, self.rect.bottom-50-self.effect.get_height()))

            if self.keyboard_controller.is_pressed('j'):
                self.screen.blit(self.effect, (130, self.rect.bottom-50-self.effect.get_height()))

            if self.keyboard_controller.is_pressed('k'):
                self.screen.blit(self.effect, (190, self.rect.bottom-50-self.effect.get_height()))

            self.note_manager.draw(self.screen)

            pygame.draw.line(
                self.screen,
                (255, 0, 0),
                (0, self.rect.bottom-50),
                (250, self.rect.bottom-50),
                1
            )


            #
            # Screen Update END
            #

            count += 1
            self.fps_clock.tick(self.fps)
            self.note_manager.update()
            self.handle_event()

            pygame.display.update()

        return

    def handle_event(self) -> None:
        """
        handle game
        """
        for event in pygame.event.get():
            func = self.event.get(event.type, None)

            if not func:
                continue
            func()

    def quit(self):
        """
        quit game
        """
        self.running = False
        pygame.quit()

def main():
    """
    main entry
    """
    parser: OptionParser = OptionParser()
    parser.add_option("--DEBUG", action="store_true", default=False)
    parser.add_option("-F", "--FPS", action="store", default=60, type="int")
    (options, _) = parser.parse_args()

    Game(pygame.Rect(0, 0, 480, 600), options.FPS, options.DEBUG).run()
    exit(0)

if __name__ == "__main__":
    main()