"""Maze generation and solving toolkit."""

from .animation import AnimationRecorder
from .grid import MazeGrid
from .generators import (
    BinaryTreeGenerator,
    RandomGrowthGenerator,
    SpanningTreeGenerator,
)

from .renderers.ascii import AsciiRenderer
from .solvers import (
    BreadthFirstSolver,
    # DepthFirstSolver,
    # DijkstraSolver,
    MazeSolution,
    SolverStats,
)

__all__ = [
    "AnimationRecorder",
    "MazeGrid",
    "SpanningTreeGenerator",
    "BinaryTreeGenerator",
    "RandomGrowthGenerator",
    "BreadthFirstSolver",
    # "DepthFirstSolver",
    # "DijkstraSolver",
    "MazeSolution",
    "SolverStats",
    "AsciiRenderer",
]
