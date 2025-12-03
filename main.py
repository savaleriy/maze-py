from __future__ import annotations

import argparse
from typing import Dict, Tuple


from src.maze_py import (
    AnimationRecorder,
    AsciiRenderer,
    BinaryTreeGenerator,
    BreadthFirstSolver,
    # DepthFirstSolver,
    # DijkstraSolver,
    MazeSolution,
    MazeGrid,
    RandomGrowthGenerator,
    SpanningTreeGenerator,
)
from src.maze_py.exporters import write_animation_package


GENERATORS = {
    "spanning-tree": SpanningTreeGenerator,
    "binary-tree": BinaryTreeGenerator,
    "random-growth": RandomGrowthGenerator,
}

SOLVERS = {
    "bfs": BreadthFirstSolver,
    # "dfs": DepthFirstSolver,
    # "dijkstra": DijkstraSolver,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and solve mazes.")
    parser.add_argument("--width", type=int, default=20, help="Maze width in cells.")
    parser.add_argument("--height", type=int, default=10, help="Maze height in cells.")
    parser.add_argument(
        "--start",
        type=int,
        nargs=2,
        metavar=("X", "Y"),
        default=(0, 0),
        help="Start cell coordinates.",
    )
    parser.add_argument(
        "--target",
        type=int,
        nargs=2,
        metavar=("X", "Y"),
        default=None,
        help="Target cell coordinates (defaults to bottom-right corner).",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    parser.add_argument(
        "--generator",
        choices=GENERATORS.keys(),
        default="spanning-tree",
        help="Maze generation algorithm.",
    )
    parser.add_argument(
        "--solver",
        choices=SOLVERS.keys(),
        default="bfs",
        help="Solver to drive the visualisation/stat summary ordering.",
    )
    parser.add_argument(
        "--export-json",
        type=str,
        default=None,
        metavar="PATH",
        help="Optional path to save a canvas-friendly animation JSON stream.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    grid = MazeGrid(args.width, args.height)
    generator_cls = GENERATORS[args.generator]
    generator = generator_cls(seed=args.seed)
    recorder = AnimationRecorder() if args.export_json else None
    tree = generator.generate(grid, tuple(args.start), recorder=recorder)

    target: Tuple[int, int]
    if args.target:
        target = tuple(args.target)
    else:
        target = (grid.width - 1, grid.height - 1)

    solver_solutions: Dict[str, MazeSolution] = {}
    for key, solver_cls in SOLVERS.items():
        solver = solver_cls()
        use_recorder = recorder if key == args.solver else None
        solver_solutions[key] = solver.solve(tree, target, recorder=use_recorder)

    solution = solver_solutions[args.solver]

    renderer = AsciiRenderer()
    maze_art = renderer.render(tree, solution)

    print(maze_art)
    if solution.found:
        print(f"\n{args.solver.upper()} path length: {solution.steps} steps")
    else:
        print(f"\n{args.solver.upper()} solver could not reach the target.")

    result = solver_solutions["bfs"]

    stats = result.stats
    status = "Y" if result.found else "N"
    print(
        f"  {key.upper():>8} {status}  "
        f"path={stats.path_length:3d}  "
        f"visited={stats.nodes_expanded:4d}  "
        f"time={stats.runtime_ms:7.2f}ms"
    )

    if args.export_json and recorder:
        output_path = write_animation_package(
            args.export_json,
            grid,
            tree,
            solution,
            recorder,
            start=tuple(args.start),
            target=target,
        )
        print(f"Animation log saved to {output_path}")


if __name__ == "__main__":
    main()
