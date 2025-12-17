# Hashiwokakero

This project implements an Artificial Intelligence system to solve the **Hashiwokakero** logic puzzle. It features a comparative study of four different algorithmic approaches, ranging from naive search to advanced SAT solvers, with automated batch processing and performance analysis.

## 📂 Project Structure

The project is organized into modular components for parsing, solving, and rendering:

```text
Source/
│
├── CNF/                        # Modules for SAT Solver conversion
│   ├── CNF_Generator.py        # Generates CNF clauses from the Puzzle
│   ├── Parser.py               # Reads input text files into Puzzle objects
│   └── Solution_Decoder.py     # Decodes SAT model results back to Bridges
│
├── Core/                       # Core data structures and utilities
│   ├── Bridge.py               # Class representing a bridge connection
│   └── Renderer.py             # Visualization and file export logic
│
├── Inputs/                     # Input puzzle files
│   ├── input-01.txt
│   ├── ...
│   └── input-10.txt
│
├── Outputs/                    # Generated solutions (auto-created)
│   ├── AStar/
|   |   ├── output-01.txt
|   |   ├── output-02.txt
|   |   └── ...
│   ├── Backtracking/
|   |   ├── output-01.txt
|   |   ├── output-02.txt
|   |   └── ...
│   ├── BruteForce/
|   |   ├── output-01.txt
|   |   ├── output-02.txt
|   |   └── ...
│   └── PySAT/
|       ├── output-01.txt
|       ├── output-02.txt
|       └── ...
│
├── Solver/                     # Algorithm implementations
│   ├── AStar_Solver.py         # A* Search with heuristics
│   ├── Backtracking_Solver.py  # Backtracking with pruning & conflict maps
│   ├── BruteForce_Solver.py    # Naive Recursive Search
│   └── PySAT_Solver.py         # SAT Solver wrapper (using python-sat)
│
└── main.py                     # Entry point (Batch processing & Timeout handling)
```

## 🚀 Algorithms Implemented

This project solves the puzzle using the following strategies:

### 1. Brute Force (`BruteForce_Solver.py`)
*   **Method:** Naive recursive search.
*   **Logic:** Tries every combination of bridge counts (0, 1, 2) for every possible connection sequentially.
*   **Use Case:** Baseline for performance comparison. Very slow on maps larger than 7x7.

### 2. Backtracking (`Backtracking_Solver.py`)
*   **Method:** Recursive search with **Constraint Propagation** and **Pruning**.
*   **Key Optimizations:** 
    *   **Conflict Map:** Pre-computes crossing bridges to check validity in $O(1)$ time.
    *   **Pruning:** Immediately stops a branch if a node exceeds capacity or bridges cross.
    *   **Connectivity Check:** Verifies graph connectivity at leaf nodes.

### 3. A* Search (`AStar_Solver.py`)
*   **Method:** Heuristic Search using a Priority Queue.
*   **Heuristic ($h$):** Estimates the remaining capacity of islands to guide the search towards the goal.
*   **Logic:** Prioritizes states that are most likely to lead to a solution based on $f(n) = g(n) + h(n)$.

### 4. PySAT (`PySAT_Solver.py`)
*   **Method:** Reduction to Boolean Satisfiability (SAT).
*   **Logic:** Encodes the rules of Hashiwokakero (Bridge capacity, Non-crossing, Connected graph) into CNF clauses and solves them using the Glucose/Minisat solver.
*   **Performance:** Typically the fastest and most scalable approach for this NP-complete problem.

## 🛠️ Installation & Requirements

Ensure you have **Python 3.x** installed. You need to install the following dependencies:

```bash
# Library for SAT solving
pip install python-sat

# Library for handling execution timeouts
pip install func-timeout
```

## ▶️ Usage

To run the project, navigate to the `Source` directory and execute `Main.py`.

The script will:
1.  Iterate through all input files (`input-01.txt` to `input-10.txt`).
2.  Run all 4 algorithms for each puzzle sequentially.
3.  Enforce a **30-second timeout** per algorithm to prevent hanging on large maps.
4.  Print the resulting map and performance statistics to the console.
5.  Save the solution to text files in the `Outputs/` directory.

```bash
cd Source
python main.py
```

## 📝 Input Format
The input files in `Inputs/` follow a simple matrix format:
*   Numbers `1-8`: Represent islands with that specific capacity.
*   `0`: Represents water (empty space).

**Example:**
```text
2, 0, 0, 2
0, 0, 0, 0
2, 0, 0, 2
```

## 📊 Output & Statistics
For every run, the system logs the following metrics:
*   **Time (ms):** Total execution time.
*   **Expanded/Recursion:** Number of states visited (for Search algorithms).
*   **Clauses/Variables:** Problem complexity size (for SAT).
*   **Total Bridges:** The sum of bridges in the valid solution.

Results are saved as:
`Outputs/{Algorithm}/output-{xx}.txt`