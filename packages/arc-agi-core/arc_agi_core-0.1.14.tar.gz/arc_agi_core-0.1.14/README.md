# arc-agi-core

```
🚧 Work In Progress...
```

> ## Core research tool-kit for tackling ARC (Abstraction and Reasoning Corpus).

The `arc-agi-core` package serves as the core research tool-kit for tackling the Abstraction and Reasoning Corpus (ARC). It provides the essential data structures and functionalities required to represent, manipulate, and analyze ARC tasks and datasets. Designed as the core component of the broader `arc-agi` ecosystem, it aims to be minimal, well-documented, efficient, extensible, and convenient.

## Minimal Example

```python
import arc_agi_core as arc

dataset = arc.ARC2Traiing.download("dataset/arc-agi-2/training")
task = dataset.sample()
pair = task.train[0]
grid = pair.input
```

**Take a look on `examples/arc-agi-demo/demo.ipynb` for detailed demo notebook.**

## Key Features

- **Core Data Structures:** Robust classes for representing ARC `Grid`s, `Pair`s (input-output examples), `Task`s, and collections of tasks as `Dataset`s.
- **Flexible I/O:** Support for loading and saving ARC data in various formats, including JSON, NumPy (`.npy`), and SVG for visualization.
- **Visualization:** Built-in methods for rendering grids, pairs, and tasks in the terminal (ANSI), in Jupyter/IPython notebooks (HTML), and as scalable vector graphics (SVG).
- **Dataset Management:** Features for handling collections of tasks, including lazy loading from directories, subset selection, sampling, shuffling, and caching.
- **Remote Dataset Access:** Convenient classes for downloading standard ARC datasets (ARC-AGI v1 and ARC Prize 2024) directly from their official GitHub repositories.
- **Minimal Dependencies:** Built on a small set of widely-used libraries (`numpy`, `requests`, `svg-py`).

## Core Data Structures

- `Grid`: Represents the fundamental 2D grid of symbols. Provides methods for conversion, comparison, and saving/loading in JSON, NPY, and SVG formats.
- `Pair`: Encapsulates an input grid and its corresponding output grid. Supports censoring the output (for test pairs) and saving/loading in JSON and SVG formats.
- `Task`: A collection of training and test `Pair`s. Includes utilities for loading/saving JSON, accessing inputs/outputs, creating 'challenge' versions (with censored test outputs), and saving as SVG.
- `Dataset`: Manages a collection of `Task`s. Supports lazy loading from a directory of JSON files, loading/saving to a single JSON file, selecting subsets, sampling, shuffling, and iterating over tasks. Includes subclasses for downloading official ARC datasets.

This package provides the foundational components necessary to build ARC solvers, analyze datasets, and visualize task examples.
