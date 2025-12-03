"""Генератор лабиринта методом случайного роста (растущее дерево)."""

from __future__ import annotations

import random
from typing import List, Tuple

from ..animation import AnimationRecorder
from ..grid import Cell, MazeGrid, MazeTree
from .base import MazeGenerator


class RandomGrowthGenerator(MazeGenerator):
    """Реализует вариант алгоритма 'растущего дерева' со случайным выбором ячейки."""

    def __init__(self, *, seed: int | None = None):
        # Инициализация генератора случайных чисел
        # Параметр seed позволяет сделать результат воспроизводимым
        self._random = random.Random(seed)

    def generate(
        self,
        grid: MazeGrid,  # Сетка лабиринта
        start: Tuple[int, int],  # Стартовая точка (координаты x, y)
        *,  # Все следующие параметры должны передаваться по ключу
        recorder: AnimationRecorder | None = None,  # Для записи анимации процесса
    ) -> MazeTree:
        # Шаг 1: Подготовка сетки - очистка всех предыдущих связей и стен
        grid.reset()

        # Шаг 2: Получаем стартовую ячейку по координатам
        root = grid.cell(*start)

        # Шаг 3: Список для сохранения порядка посещения ячеек
        # Полезно для анимации и анализа алгоритма
        visit_order: List[Cell] = []

        # Шаг 4: Список "активных" ячеек - это ячейки, которые могут "расти"
        # Активная ячейка имеет хотя бы одного непосещенного соседа
        active: List[Cell] = [root]

        # Шаг 5: Множество посещенных ячеек (храним координаты для быстрого поиска)
        visited = {root.coords}

        # Шаг 6: Счетчик шагов для анимации
        step = 0

        # Шаг 7: Основной цикл алгоритма - продолжается, пока есть активные ячейки
        while active:
            # Шаг 7a: Случайный выбор активной ячейки
            # В отличие от алгоритма Прима, мы не удаляем ячейку сразу
            idx = self._random.randrange(len(active))
            cell = active[idx]

            # Шаг 7b: Записываем текущую ячейку в историю посещений
            visit_order.append(cell)

            # Шаг 7c: Если есть рекордер, записываем активацию ячейки
            if recorder:
                recorder.record(
                    "generate",
                    "activate",
                    cell=list(
                        cell.coords
                    ),  # Преобразуем кортеж в список для сериализации
                    step=step,
                )
            step += 1

            # Шаг 8: Ищем кандидатов для роста
            # Собираем всех непосещенных соседей текущей ячейки
            candidates = [
                neighbor
                for neighbor in grid.neighbors(cell)
                if neighbor.coords not in visited
            ]

            # Шаг 9: Проверяем, есть ли куда расти
            if not candidates:
                # Шаг 9a: Если у ячейки нет непосещенных соседей
                # Удаляем ее из списка активных - она больше не может расти
                active.pop(idx)
                # Переходим к следующей итерации
                continue

            # Шаг 10: Рост - выбираем случайного соседа для присоединения
            neighbor = self._random.choice(candidates)

            # Шаг 10a: Помечаем соседа как посещенного
            visited.add(neighbor.coords)

            # Шаг 10b: Убираем стену между текущей ячейкой и выбранным соседом
            # Это создает проход в лабиринте
            grid.link(cell, neighbor)

            # Шаг 10c: Устанавливаем родительскую связь
            # Текущая ячейка становится родителем соседа в дереве лабиринта
            neighbor.parent = cell

            # Шаг 10d: Добавляем соседа в список детей текущей ячейки
            cell.children.append(neighbor)

            # Шаг 10e: Добавляем соседа в список активных ячеек
            # Теперь он может расти дальше
            active.append(neighbor)

            # Шаг 10f: Если есть рекордер, записываем создание связи
            if recorder:
                recorder.record(
                    "generate",
                    "link",
                    parent=list(cell.coords),
                    child=list(neighbor.coords),
                )

        # Шаг 11: Возвращаем готовый лабиринт в виде дерева
        return MazeTree(grid=grid, root=root, visit_order=visit_order)
