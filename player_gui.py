"""Графический интерфейс простого плеера на PyQt5 + pygame."""

# pylint: disable=no-name-in-module
# pylint: disable=too-many-instance-attributes
# pylint: disable=wrong-import-position

from __future__ import annotations

import os
import sys
from typing import Optional

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from linked_list import Composition, PlayList


class PlayerWindow(QWidget):
    """Окно плеера.

    Attributes:
        playlist: Единственный плейлист приложения.
    """

    def __init__(self) -> None:
        """Инициализирует окно плеера."""
        super().__init__()
        self.playlist: PlayList = PlayList()
        self.setWindowTitle("Плеер")
        self.resize(560, 420)

        pygame.mixer.init()

        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_end)
        self._timer.start(1000)

    # ------------------------------------------------------------------ #
    #                              UI                                     #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        """Создаёт элементы интерфейса."""
        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.play_selected)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_remove = QPushButton("Удалить")
        self.btn_up = QPushButton("Вверх")
        self.btn_down = QPushButton("Вниз")
        self.btn_play = QPushButton("Играть")
        self.btn_prev = QPushButton("Пред.")
        self.btn_next = QPushButton("След.")
        self.btn_stop = QPushButton("Стоп")

        for btn in (
            self.btn_add,
            self.btn_remove,
            self.btn_up,
            self.btn_down,
            self.btn_play,
            self.btn_prev,
            self.btn_next,
            self.btn_stop,
        ):
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.btn_add.clicked.connect(self.add_track)
        self.btn_remove.clicked.connect(self.remove_track)
        self.btn_up.clicked.connect(lambda: self._move_track(-1))
        self.btn_down.clicked.connect(lambda: self._move_track(1))
        self.btn_play.clicked.connect(self.play_selected)
        self.btn_prev.clicked.connect(self.play_previous)
        self.btn_next.clicked.connect(self.play_next)
        self.btn_stop.clicked.connect(self.stop_music)

    # ------------------------------------------------------------------ #
    #                          Вспомогательные                            #
    # ------------------------------------------------------------------ #

    def _refresh(self) -> None:
        """Обновляет список в интерфейсе."""
        self.list_widget.clear()
        for node in self.playlist:
            self.list_widget.addItem(str(node.data))

    def _selected(self) -> Optional[Composition]:
        """Возвращает выбранную композицию или None."""
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.playlist):
            return None
        return self.playlist[row]

    def _start_music(self, comp: Composition) -> None:
        """Запускает воспроизведение композиции.

        Args:
            comp: Композиция для воспроизведения.
        """
        try:
            pygame.mixer.music.load(comp.file_path)
            pygame.mixer.music.play()
        except pygame.error as exc:  # pylint: disable=no-member
            QMessageBox.critical(self, "Ошибка воспроизведения", str(exc))

    # ------------------------------------------------------------------ #
    #                            Действия                                 #
    # ------------------------------------------------------------------ #

    def add_track(self) -> None:
        """Добавляет трек в плейлист."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите аудиофайл",
            "",
            "Audio (*.mp3 *.ogg *.wav)",
        )
        if not path:
            return
        title, ok1 = QInputDialog.getText(self, "Название", "Введите название:")
        if not ok1 or not title:
            return
        artist, ok2 = QInputDialog.getText(
            self, "Исполнитель", "Введите исполнителя:"
        )
        if not ok2:
            return
        self.playlist.append(Composition(title, artist, path))
        self._refresh()

    def remove_track(self) -> None:
        """Удаляет выбранный трек.

        Если удаляется текущий трек — воспроизведение останавливается.
        """
        comp = self._selected()
        if comp is None:
            return
        is_current = self.playlist.current == comp
        try:
            self.playlist.remove(comp)
        except ValueError as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return
        if is_current:
            pygame.mixer.music.stop()
            self.playlist.current_item = None
        self._refresh()

    def _move_track(self, direction: int) -> None:
        """Перемещает выбранный трек на позицию вверх/вниз.

        Args:
            direction: -1 — вверх, 1 — вниз.
        """
        comp = self._selected()
        if comp is None:
            return
        row = self.list_widget.currentRow()
        new_row = row + direction
        if new_row < 0 or new_row >= len(self.playlist):
            return
        self.playlist.remove(comp)
        if new_row == 0:
            self.playlist.append_left(comp)
        else:
            self.playlist.insert(self.playlist[new_row - 1], comp)
        self._refresh()
        self.list_widget.setCurrentRow(new_row)

    def play_selected(self) -> None:
        """Запускает выбранный трек."""
        comp = self._selected()
        if comp is None:
            QMessageBox.warning(self, "Ошибка", "Выберите трек")
            return
        try:
            self.playlist.play_all(comp)
        except ValueError as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return
        self._start_music(comp)

    def play_next(self) -> None:
        """Запускает следующий трек."""
        try:
            comp = self.playlist.next_track()
        except ValueError as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return
        self._start_music(comp)

    def play_previous(self) -> None:
        """Запускает предыдущий трек."""
        try:
            comp = self.playlist.previous_track()
        except ValueError as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))
            return
        self._start_music(comp)

    def stop_music(self) -> None:
        """Останавливает воспроизведение и сбрасывает текущий трек."""
        pygame.mixer.music.stop()
        self.playlist.current_item = None

    def _check_end(self) -> None:
        """Автопереход после завершения трека."""
        if self.playlist.current_item is None:
            return
        if not pygame.mixer.music.get_busy():
            try:
                comp = self.playlist.next_track()
            except ValueError:
                return
            self._start_music(comp)


def main() -> None:
    """Точка входа приложения."""
    app = QApplication(sys.argv)
    window = PlayerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    