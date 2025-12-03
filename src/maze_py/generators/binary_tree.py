"""Генератор лабиринта методом бинарного дерева."""

from __future__ import annotations

import random
from typing import List, Tuple

from ..animation import AnimationRecorder
from ..grid import Cell, MazeGrid, MazeTree
from .base import MazeGenerator


class BinaryTreeGenerator(MazeGenerator):
    """Создает проходы, соединяя каждую ячейку либо с восточной, либо с южной соседкой."""

    def __init__(self, *, seed: int | None = None):
        # Инициализация генератора случайных чисел
        # Параметр seed обеспечивает воспроизводимость результатов
        self._random = random.Random(seed)

    def generate(
        self,
        grid: MazeGrid,  # Сетка лабиринта
        start: Tuple[int, int],  # Стартовая точка (используется как корень дерева)
        *,  # Все следующие параметры должны передаваться по ключу
        recorder: AnimationRecorder | None = None,  # Для записи анимации процесса
    ) -> MazeTree:
        # Шаг 1: Сброс состояния сетки - удаление всех существующих связей
        grid.reset()

        # Шаг 2: Список для сохранения порядка обработки ячеек
        visit_order: List[Cell] = []

        # Шаг 3: Получение стартовой ячейки (корня дерева)
        root = grid.cell(*start)

        # Шаг 4: Основной двойной цикл - проход по всем ячейкам сетки
        # Проходим по строкам (y) и столбцам (x) в порядке от левого верхнего угла
        # к правому нижнему
        for y in range(grid.height):
            for x in range(grid.width):
                # Шаг 4a: Получаем текущую ячейку
                cell = grid.cell(x, y)

                # Шаг 4b: Добавляем ячейку в список посещенных
                visit_order.append(cell)

                # Шаг 4c: Если есть рекордер, записываем обработку ячейки
                if recorder:
                    recorder.record(
                        "generate",
                        "activate",
                        cell=[x, y],
                        step=len(visit_order),  # Используем длину списка как номер шага
                    )

                # Шаг 5: Определяем возможные направления для соединения
                # Инициализируем список кандидатов
                choices = []

                # Шаг 5a: Проверяем возможность соединения с восточным соседом (x+1)
                if grid.contains(x + 1, y):
                    choices.append(grid.cell(x + 1, y))

                # Шаг 5b: Проверяем возможность соединения с южным соседом (y+1)
                if grid.contains(x, y + 1):
                    choices.append(grid.cell(x, y + 1))

                # Шаг 6: Проверяем, есть ли доступные соседи
                # Для ячеек в правом нижнем углу список choices будет пуст
                if not choices:
                    # Пропускаем эту ячейку - она уже соединена или является угловой
                    continue

                # Шаг 7: Выбираем случайного соседа из доступных вариантов
                neighbor = self._random.choice(choices)

                # Шаг 8: Создаем проход между ячейками
                # Убираем стену между текущей ячейкой и выбранным соседом
                grid.link(cell, neighbor)

                # Шаг 9: Устанавливаем связи в дереве лабиринта
                # Сосед становится ребенком текущей ячейки
                neighbor.parent = cell
                cell.children.append(neighbor)

                # Шаг 10: Если есть рекордер, записываем создание связи
                if recorder:
                    recorder.record(
                        "generate",
                        "link",
                        parent=[cell.x, cell.y],
                        child=[neighbor.x, neighbor.y],
                    )

        # Шаг 11: Возвращаем готовый лабиринт в виде дерева
        return MazeTree(grid=grid, root=root, visit_order=visit_order)
