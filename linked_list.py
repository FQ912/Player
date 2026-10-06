"""Модуль связного списка и плейлиста.

Содержит классы:
    Composition      — музыкальная композиция;
    LinkedListItem   — элемент двусвязного списка;
    LinkedList       — базовый кольцевой двусвязный список;
    PlayList         — плейлист, наследник LinkedList.
"""

from __future__ import annotations

from typing import Any, Iterator, Optional


class Composition:
    """Музыкальная композиция.

    Attributes:
        title: Название композиции.
        artist: Исполнитель.
        file_path: Путь к аудиофайлу.
    """

    def __init__(self, title: str, artist: str, file_path: str) -> None:
        """Инициализирует композицию.

        Args:
            title: Название композиции.
            artist: Исполнитель.
            file_path: Путь к аудиофайлу.
        """
        self.title: str = title
        self.artist: str = artist
        self.file_path: str = file_path

    def __str__(self) -> str:
        """Возвращает строковое представление композиции."""
        return f"{self.artist} — {self.title}"

    def __repr__(self) -> str:
        """Возвращает отладочное представление композиции."""
        return (
            f"Composition({self.title!r}, {self.artist!r}, "
            f"{self.file_path!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Сравнивает две композиции по всем полям."""
        if not isinstance(other, Composition):
            return NotImplemented
        return (
            self.title == other.title
            and self.artist == other.artist
            and self.file_path == other.file_path
        )

    def __hash__(self) -> int:
        """Хэш композиции."""
        return hash((self.title, self.artist, self.file_path))


class LinkedListItem:
    """Элемент двусвязного списка.

    Сеттеры ``next_item`` / ``previous_item`` автоматически поддерживают
    двустороннюю связь между соседними элементами.

    Attributes:
        data: Полезная нагрузка элемента.
    """

    def __init__(self, data: Any = None) -> None:
        """Инициализирует элемент списка.

        Args:
            data: Данные элемента.
        """
        self._next: Optional[LinkedListItem] = None
        self._previous: Optional[LinkedListItem] = None
        self.data: Any = data

    @property
    def next_item(self) -> Optional[LinkedListItem]:
        """Следующий элемент списка."""
        return self._next

    @next_item.setter
    def next_item(self, value: Optional[LinkedListItem]) -> None:
        """Устанавливает следующий элемент и обратную ссылку.

        Args:
            value: Новый следующий элемент.
        """
        self._next = value
        # pylint: disable=protected-access
        if value is not None and value._previous is not self:
            value._previous = self
        # pylint: enable=protected-access

    @property
    def previous_item(self) -> Optional[LinkedListItem]:
        """Предыдущий элемент списка."""
        return self._previous

    @previous_item.setter
    def previous_item(self, value: Optional[LinkedListItem]) -> None:
        """Устанавливает предыдущий элемент и обратную ссылку.

        Args:
            value: Новый предыдущий элемент.
        """
        self._previous = value
        # pylint: disable=protected-access
        if value is not None and value._next is not self:
            value._next = self
        # pylint: enable=protected-access

    def __repr__(self) -> str:
        """Отладочное представление элемента."""
        return f"LinkedListItem({self.data!r})"


class LinkedList:
    """Кольцевой двусвязный список.

    Attributes:
        first_item: Первый элемент списка.
    """

    def __init__(self, first_item: Optional[LinkedListItem] = None) -> None:
        """Инициализирует список.

        Args:
            first_item: Первый элемент списка (или None).
        """
        self.first_item: Optional[LinkedListItem] = first_item
        self._iter_node: Optional[LinkedListItem] = None
        self._iter_count: int = 0

    # ------------------------------------------------------------------ #
    #                          Внутренние методы                          #
    # ------------------------------------------------------------------ #

    def _find_node(self, item: Any) -> Optional[LinkedListItem]:
        """Находит узел по данным.

        Args:
            item: Искомые данные.

        Returns:
            Найденный узел или None.
        """
        node = self.first_item
        for _ in range(len(self)):
            if node is not None and node.data == item:
                return node
            if node is None:
                break
            node = node.next_item
        return None

    # ------------------------------------------------------------------ #
    #                              Свойства                               #
    # ------------------------------------------------------------------ #

    @property
    def last(self) -> Optional[LinkedListItem]:
        """Последний элемент списка (или None для пустого)."""
        if self.first_item is None:
            return None
        node = self.first_item
        for _ in range(len(self) - 1):
            node = node.next_item  # type: ignore[assignment]
        return node

    def last_item(self) -> Optional[LinkedListItem]:
        """Возвращает последний элемент списка.

        Метод-алиас свойства ``last`` — добавлен для формального
        соответствия формулировке задания, где ``last`` описан как метод.

        Returns:
            Последний элемент списка или None для пустого списка.
        """
        return self.last

    # ------------------------------------------------------------------ #
    #                       Добавление / удаление                         #
    # ------------------------------------------------------------------ #

    def append_left(self, item: Any) -> None:
        """Добавляет элемент в начало списка.

        Args:
            item: Данные для добавления.
        """
        new_item = LinkedListItem(item)
        if self.first_item is None:
            new_item.next_item = new_item
            new_item.previous_item = new_item
            self.first_item = new_item
            return
        last = self.last
        first = self.first_item
        new_item.next_item = first
        new_item.previous_item = last
        last.next_item = new_item  # type: ignore[union-attr]
        self.first_item = new_item

    def append_right(self, item: Any) -> None:
        """Добавляет элемент в конец списка.

        Args:
            item: Данные для добавления.
        """
        new_item = LinkedListItem(item)
        if self.first_item is None:
            new_item.next_item = new_item
            new_item.previous_item = new_item
            self.first_item = new_item
            return
        first = self.first_item
        last = self.last
        new_item.next_item = first
        new_item.previous_item = last
        last.next_item = new_item  # type: ignore[union-attr]

    def append(self, item: Any) -> None:
        """Алиас для append_right.

        Args:
            item: Данные для добавления.
        """
        self.append_right(item)

    def remove(self, item: Any) -> None:
        """Удаляет элемент из списка.

        Args:
            item: Данные для удаления.

        Raises:
            ValueError: Если элемент отсутствует в списке.
        """
        node = self._find_node(item)
        if node is None:
            raise ValueError("Элемент не найден в списке")
        if len(self) == 1:
            self.first_item = None
            return
        prev = node.previous_item
        nxt = node.next_item
        prev.next_item = nxt       # type: ignore[union-attr]
        if node is self.first_item:
            self.first_item = nxt
        if prev is nxt:
            prev.next_item = prev       # type: ignore[union-attr]
            prev.previous_item = prev   # type: ignore[union-attr]

    def insert(self, previous: Any, item: Any) -> None:
        """Вставляет item после элемента с данными previous.

        Args:
            previous: Данные узла, после которого вставляем.
            item: Данные для вставки.

        Raises:
            ValueError: Если элемент previous не найден.
        """
        node = self._find_node(previous)
        if node is None:
            raise ValueError("Элемент previous не найден")
        new_item = LinkedListItem(item)
        nxt = node.next_item
        new_item.previous_item = node
        new_item.next_item = nxt
        node.next_item = new_item
        if nxt is not None:
            nxt.previous_item = new_item

    # ------------------------------------------------------------------ #
    #                         Магические методы                           #
    # ------------------------------------------------------------------ #

    def __len__(self) -> int:
        """Возвращает длину списка."""
        if self.first_item is None:
            return 0
        count = 1
        node = self.first_item.next_item
        while node is not None and node is not self.first_item:
            count += 1
            node = node.next_item
        return count

    def __iter__(self) -> LinkedList:
        """Возвращает итератор — сам объект списка.

        Итерация реализована через поля ``_iter_node`` / ``_iter_count``,
        что позволяет явно определить ``__next__``.
        """
        self._iter_node = self.first_item
        self._iter_count = 0
        return self

    def __next__(self) -> LinkedListItem:
        """Возвращает следующий узел итератора.

        Returns:
            Очередной узел списка.

        Raises:
            StopIteration: Когда все элементы пройдены.
        """
        if self._iter_count >= len(self):
            raise StopIteration
        node = self._iter_node
        if node is None:
            raise StopIteration
        self._iter_node = node.next_item
        self._iter_count += 1
        return node

    def __getitem__(self, index: int) -> Any:
        """Возвращает данные по индексу.

        Args:
            index: Индекс (поддерживаются отрицательные значения).

        Returns:
            Данные узла по индексу.

        Raises:
            IndexError: Если индекс вне диапазона.
        """
        length = len(self)
        if index < 0:
            index += length
        if index < 0 or index >= length:
            raise IndexError("Индекс вне диапазона")
        node = self.first_item
        for _ in range(index):
            node = node.next_item  # type: ignore[union-attr]
        return node.data  # type: ignore[union-attr]

    def __contains__(self, item: Any) -> bool:
        """Проверяет наличие данных в списке."""
        return self._find_node(item) is not None

    def __reversed__(self) -> Iterator[Any]:
        """Возвращает обратный итератор по данным списка.

        Yields:
            Данные узлов в порядке от последнего к первому.
        """
        node = self.last
        for _ in range(len(self)):
            if node is None:
                break
            yield node.data
            node = node.previous_item

    def __repr__(self) -> str:
        """Отладочное представление списка."""
        return f"{self.__class__.__name__}({[n.data for n in self]!r})"


class PlayList(LinkedList):
    """Плейлист — кольцевой двусвязный список с текущим треком.

    Attributes:
        current_item: Текущий элемент плейлиста.
    """

    def __init__(self) -> None:
        """Инициализирует пустой плейлист."""
        super().__init__()
        self.current_item: Optional[LinkedListItem] = None

    def play_all(self, item: Composition) -> Composition:
        """Начинает воспроизведение с указанной композиции.

        Args:
            item: Композиция, с которой начинаем.

        Returns:
            Текущая композиция.

        Raises:
            ValueError: Если композиция не найдена в плейлисте.
        """
        node = self._find_node(item)
        if node is None:
            raise ValueError("Композиция не найдена в плейлисте")
        self.current_item = node
        return node.data

    def next_track(self) -> Composition:
        """Переходит к следующему треку (по кольцу).

        Returns:
            Следующая композиция.

        Raises:
            ValueError: Если воспроизведение не начато.
        """
        if self.current_item is None:
            raise ValueError("Воспроизведение не начато")
        self.current_item = self.current_item.next_item
        return self.current_item.data  # type: ignore[union-attr]

    def previous_track(self) -> Composition:
        """Переходит к предыдущему треку (по кольцу).

        Returns:
            Предыдущая композиция.

        Raises:
            ValueError: Если воспроизведение не начато.
        """
        if self.current_item is None:
            raise ValueError("Воспроизведение не начато")
        self.current_item = self.current_item.previous_item
        return self.current_item.data  # type: ignore[union-attr]

    @property
    def current(self) -> Optional[Composition]:
        """Текущая композиция (или None)."""
        if self.current_item is None:
            return None
        return self.current_item.data
        
