"""Генератор лабиринта на основе случайного остовного дерева."""

from __future__ import annotations

import random
from typing import List, Tuple

from ..animation import AnimationRecorder
from ..grid import Cell, MazeGrid, MazeTree
from .base import MazeGenerator


class SpanningTreeGenerator(MazeGenerator):
    """Генерирует равномерное остовное дерево, используя подход, подобный алгоритму Прима."""

    def __init__(self, *, seed: int | None = None):
        # Инициализация генератора случайных чисел с возможностью указания seed
        # (для воспроизводимости результатов)
        self._random = random.Random(seed)

    def generate(
        self,
        grid: MazeGrid,  # Сетка, представляющая лабиринт
        start: Tuple[int, int],  # Начальная точка (x, y) для построения лабиринта
        *,  # Означает, что следующие параметры должны передаваться по ключу
        recorder: AnimationRecorder | None = None,  # Опциональный рекордер для анимации
    ) -> MazeTree:
        # Шаг 1: Сброс состояния сетки (очистка стен и связей между ячейками)
        grid.reset()

        # Шаг 2: Получаем стартовую ячейку по координатам
        root = grid.cell(*start)
        root.parent = None  # Устанавливаем корень дерева (родителя нет)

        # Шаг 3: Список для сохранения порядка посещения ячеек (для отладки/анимации)
        visit_order: List[Cell] = []

        # Шаг 4: Инициализация "фронта" - списка ячеек, которые уже посещены,
        # но имеют непосещенных соседей. Фронт начинает с одной ячейки - корня
        frontier: List[Cell] = [root]

        # Шаг 5: Множество для быстрой проверки, посещена ли ячейка
        # Храним координаты для эффективного сравнения
        visited = {root.coords}

        # Шаг 6: Счетчик шагов для анимации/отладки
        step = 0

        # Шаг 7: Основной цикл алгоритма - продолжается, пока есть ячейки во фронте
        while frontier:
            # Шаг 7a: Случайным образом выбираем индекс ячейки во фронте
            # Это ключевое отличие от стандартного алгоритма Прима:
            # мы выбираем не ближайшую, а случайную ячейку из фронта
            idx = self._random.randrange(len(frontier))

            # Шаг 7b: Извлекаем ячейку по случайному индексу
            cell = frontier.pop(idx)

            # Шаг 7c: Добавляем ячейку в список посещенных по порядку
            visit_order.append(cell)

            # Шаг 7d: Если есть рекордер, записываем активацию ячейки
            if recorder:
                recorder.record(
                    "generate",
                    "activate",
                    cell=list(cell.coords),
                    step=step,
                )
            step += 1

            # Шаг 8: Исследуем всех соседей текущей ячейки
            for neighbor in grid.neighbors(cell):
                # Шаг 8a: Если сосед уже посещен, пропускаем его
                if neighbor.coords in visited:
                    continue

                # Шаг 8b: Помечаем соседа как посещенного
                visited.add(neighbor.coords)

                # Шаг 8c: Убираем стену между текущей ячейкой и соседом
                # Это создает проход в лабиринте
                grid.link(cell, neighbor)

                # Шаг 8d: Устанавливаем родительскую связь в дереве
                # Текущая ячейка становится родителем соседа
                neighbor.parent = cell

                # Шаг 8e: Добавляем соседа в список детей текущей ячейки
                cell.children.append(neighbor)

                # Шаг 8f: Добавляем соседа во фронт
                # Теперь эта ячейка будет рассмотрена на следующих итерациях
                frontier.append(neighbor)

                # Шаг 8g: Если есть рекордер, записываем создание связи
                if recorder:
                    recorder.record(
                        "generate",
                        "link",
                        parent=list(cell.coords),
                        child=list(neighbor.coords),
                    )

        # Шаг 9: Возвращаем результат - дерево лабиринта
        # Содержит сетку, корень и порядок посещения ячеек
        return MazeTree(grid=grid, root=root, visit_order=visit_order)
