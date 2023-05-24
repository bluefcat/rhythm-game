from typing import Any, Callable, Dict, List
import pygame

class KeyboardController:
    """
    키보드 컨트롤러
    """
    def __init__(self):
        self.key: Dict[str, bool] = {
            "d": False,
            "f": False,
            "j": False,
            "k": False
        }

        self.key_down_function: Dict[str, Callable[[Any], Any]] = {}
        self.key_up_function: Dict[str, Callable[[Any], Any]] = {}

    def append_down(self, name: str, function: Callable[[Any], Any]):
        """
        키함수 등록
        """
        self.key_down_function[name] = function

    def append_up(self, name: str, function: Callable[[Any], Any]):
        """
        키함수 등록
        """
        self.key_up_function[name] = function

    def keydown(self):
        """
        키 누르기
        """
        pressed = self.get_pressed()
        for k, v in self.key.items():
            if v or k not in pressed:
                continue

            function = self.key_down_function.get(k, None)
            self.key[k] = True

            if function:
                function()


    def keyup(self):
        """
        키 떼기
        """
        pressed = self.get_pressed()

        for k, v in self.key.items():
            if not v or k in pressed:
                continue

            function = self.key_up_function.get(k, None)
            self.key[k] = False

            if function:
                function()

    def is_pressed(self, name: str) -> bool:
        """
        특정 키가 눌러져있는지 확인
        """
        return self.key.get(name, False)

    def get_pressed(self) -> List[str]:
        """
        눌린 키를 구하는 함수
        """
        keys = pygame.key.get_pressed()
        result = [pygame.key.name(idx + 93) for idx, key in enumerate(keys) if key ]
        return result