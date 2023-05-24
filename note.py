"""
note python
"""
from typing import Any, Dict, Tuple, List, Optional
from enum import Enum
import pygame

# RECT(left, top, width, heigth)
# RECT((left, top), (width, height))

POS = List[int]

class Color(Enum):
    """
    색깔 색
    """
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

class Grade(Enum):
    """
    리듬 판정 enum class
    """
    NONE = -1
    MISS = 0
    GREAT = 1
    PERPECT = 2

def check_height(rect: pygame.Rect, y: float) -> bool:
    """
    y축 확인
    """
    return rect.top <= y and y <= rect.bottom


class Note:
    """
    노트의 추상 클래스
    """
    def __init__(self, object_id: int, note: pygame.Rect, end: POS, velocity: float):
        self.object_id = object_id
        self.note = note
        self.end = end
        self.velocity = velocity

    def check_enter(self) -> Grade:
        """
        키보드를 눌렀을 때, 진입 확인하는 함수
        """
        return Grade.NONE

    def check_exit(self) -> Grade:
        """
        롱노트용
        키보드를 땠을 때, 정상적으로 나가졌는지 확인하는 함수
        """
        return Grade.NONE

    def update(self) -> None:
        """
        위치점을 업데이트 하는 함수
        """
        self.note.move_ip(0, self.velocity)
        return

    def draw(self, screen: Any) -> None:
        """
        노트를 그리는 함수
        """
        pygame.draw.rect(screen, Color.WHITE.value, self.note)
        return

    def __repr__(self):
        return f"{self.object_id}"



class ShortNote(Note):
    """
    일반 노트 클래스
    """
    def __init__(
        self,
        object_id: int,
        line: POS,
        end: POS,
        velocity: float,
        rects: List[pygame.Rect],
        manager: "NoteManager",
        debug: bool = False,
    ):
        super().__init__(object_id, rects[0], end, velocity)
        self.manager = manager
        self.debug = debug
        self.line       = line
        self.perpect    = rects[1]
        self.great      = rects[2]

    def check_enter(self) -> Grade:
        if check_height(self.perpect, self.line[1]):
            self.manager.delete_note(self.object_id)
            return Grade.PERPECT

        elif check_height(self.great, self.line[1]):
            self.manager.delete_note(self.object_id)
            return Grade.GREAT

        return Grade.NONE

    def update(self):
        """
        note update
        """
        super().update()
        self.perpect.move_ip(0, self.velocity)
        self.great.move_ip(0, self.velocity)

        if self.note.y <= self.end[1]:
            return

        self.manager.init_combo()
        self.manager.delete_note(self.object_id)
        return


    def draw(self, screen: Any):
        """
        draw Note
        """
        super().draw(screen)

        if not self.debug:
            return

        pygame.draw.rect(screen, Color.GREEN.value, self.perpect, 2)
        pygame.draw.rect(screen, Color.RED.value, self.great, 2)

class LongNote(Note):
    """
    롱 노트 클래스
    """
    def __init__(
        self,
        object_id: int,
        line: POS,
        end: POS,
        velocity: float,
        rects: List[pygame.Rect],
        manager: "NoteManager",
        debug: bool = False,
    ):
        super().__init__(object_id, rects[0], end, velocity)
        self.manager = manager
        self.debug = debug
        self.line       = line
        self.perpect_enter    = rects[1]
        self.great_enter      = rects[2]

        self.perpect_exit     = rects[3]
        self.great_exit       = rects[4]

        self.is_enter = False

    def check_enter(self) -> Grade:
        if check_height(self.great_enter, self.line[1]):
            self.is_enter = True

            if check_height(self.perpect_enter, self.line[1]):
                return Grade.PERPECT

            return Grade.GREAT

        return Grade.NONE

    def check_exit(self) -> Grade:
        if self.is_enter and check_height(self.great_exit, self.line[1]):
            self.manager.delete_note(self.object_id)
            if check_height(self.perpect_exit, self.line[1]):
                return Grade.PERPECT
            return Grade.GREAT

        self.manager.init_combo()
        self.is_enter = False

        return Grade.NONE


    def update(self):
        """
        note update
        """
        super().update()
        self.perpect_enter.move_ip(0, self.velocity)
        self.great_enter.move_ip(0, self.velocity)

        self.perpect_exit.move_ip(0, self.velocity)
        self.great_exit.move_ip(0, self.velocity)

        if self.note.y <= self.end[1]:
            return

        self.manager.init_combo()
        self.manager.delete_note(self.object_id)
        return


    def draw(self, screen: Any):
        """
        draw Note
        """
        super().draw(screen)

        if not self.debug:
            return

        pygame.draw.rect(screen, Color.GREEN.value, self.perpect_enter, 2)
        pygame.draw.rect(screen, Color.RED.value, self.great_enter, 2)

        pygame.draw.rect(screen, Color.GREEN.value, self.perpect_exit, 2)
        pygame.draw.rect(screen, Color.RED.value, self.great_exit, 2)

class NoteBuilder:
    """
    노트빌더
    """
    def __init__(self, manager: "NoteManager"):
        self.manager = manager

    def build(self, idx: int, append_x: int, length: int) -> Tuple[int, Optional[Note]]:
        """
        노트를 만든다.
        """
        if length == 1:
            short_note_rect = pygame.Rect((append_x, self.manager.rect.top), (50, 10))
            perpect_rect = pygame.Rect(
                (append_x, short_note_rect.top-10),
                (short_note_rect.width, short_note_rect.height + 10 * 2)
            )
            great_rect   = pygame.Rect(
                (append_x, short_note_rect.top-40),
                (short_note_rect.width, short_note_rect.height + 40 * 2)
            )

            short_note = ShortNote(
                self.manager.cand_id,
                [0, self.manager.rect.bottom],
                [0, self.manager.rect.bottom+100],
                self.manager.get_velocity(),
                [short_note_rect, perpect_rect, great_rect],
                self.manager,
                self.manager.debug
            )
            return (idx, short_note)

        long_note_rect = pygame.Rect((append_x, self.manager.rect.top), (50, 10 * length))
        perpect_rect_enter = pygame.Rect(
            (append_x, long_note_rect.bottom-10),
            (long_note_rect.width, 10*2)
        )
        great_rect_enter = pygame.Rect(
            (append_x, long_note_rect.bottom-40),
            (long_note_rect.width, 40*2)
        )
        perpect_rect_exit = pygame.Rect(
            (append_x, long_note_rect.top-10),
            (long_note_rect.width, 10*2)
        )
        great_rect_exit = pygame.Rect(
            (append_x, long_note_rect.top-40),
            (long_note_rect.width, 40*2)
        )

        long_note = LongNote(
            self.manager.cand_id,
            [0, self.manager.rect.bottom],
            [0, self.manager.rect.bottom+100],
            self.manager.get_velocity(),
            [
                long_note_rect,
                perpect_rect_enter,
                great_rect_enter,
                perpect_rect_exit,
                great_rect_exit
            ],
            self.manager,
            self.manager.debug
        )

        return (idx, long_note)


class NoteManager:
    """
    노트 매니저
    """
    def __init__(self, rect: pygame.Rect, bpm: int, fps: int, debug: bool = False):
        self.cand_id = 0
        self.rect = rect
        self.bpm = bpm
        self.fps = fps
        
        self.debug = debug
        self.combo = 0

        self.notes: Dict[int, List[Note]] = {0: [], 1: [], 2:[], 3:[]}
        self.del_cand = []

    def init_combo(self):
        """
        combo 초기화
        """
        self.combo = 0

    def get_velocity(self) -> float:
        """
        BPM에 맞는 스크롤 속도
        """
        return (self.bpm / 60) * (self.rect.height / self.fps)

    def append_note(self, idx: int, note: Note):
        """
        note 추가
        """
        self.cand_id += 1
        self.notes[idx].append(note)

    def enter_note(self, idx: int) -> Grade:
        """
        키보드 입력 컨트롤
        """
        if not self.notes[idx]:
            return Grade.NONE

        grade: Grade = self.notes[idx][0].check_enter()

        if grade == Grade.NONE:
            return grade

        self.combo += 1
        return grade

    def exit_note(self, idx: int) -> Grade:
        """
        키보드 때기 컨트롤
        """
        if not self.notes[idx]:
            return Grade.NONE

        grade: Grade = self.notes[idx][0].check_exit()

        if grade == Grade.NONE:
            return Grade.NONE

        self.combo += 1
        return grade

    def delete_note(self, idx: int):
        """
        delete note
        """
        self.del_cand.append(idx)

    def update(self):
        """
        update notes
        """
        for _, notes in self.notes.items():
            for note in notes:
                note.update()


        for cand in self.del_cand:
            for num, notes in self.notes.items():
                self.notes[num] = [note for note in notes if cand != note.object_id]      

        self.del_cand = []



    def draw(self, screen):
        """
        draw notes
        """
        for _, notes in self.notes.items():
            for note in notes:
                note.draw(screen)
