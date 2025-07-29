# Loynaz: Approximate Edge Dominating Set Solver

![Honoring the Memory of Dulce Maria Loynaz (A renowned Cuban poet and key figure in Cuban literature, she won the Miguel de Cervantes Prize.)](docs/loynaz.jpg)

This work builds upon [Efficient Edge Dominating Set Approximation for Sparse Graphs](https://dev.to/frank_vega_987689489099bf/efficient-edge-dominating-set-approximation-for-sparse-graphs-56d7).

---

# Edge Dominating Set Problem - Overview

## Definition

The **Edge Dominating Set (EDS)** problem is a classical problem in graph theory and combinatorial optimization. Given an undirected graph $G = (V, E)$, an edge dominating set is a subset $D \subseteq E$ such that every edge not in $D$ is adjacent to at least one edge in $D$.

### Formal Definition:

A set $D \subseteq E$ is an **edge dominating set** if for every edge $e \in E \setminus D$, there exists an edge $d \in D$ such that $e$ and $d$ share a common vertex.

## Objective

Find an edge dominating set $D$ of **minimum cardinality** (smallest possible size).

## Computational Complexity

- **NP-Hard**: The decision version of EDS ("Does a graph $G$ have an edge dominating set of size $k$?") is NP-complete.
- **Approximation**: There exists a 2-approximation algorithm for EDS (i.e., a solution at most twice the optimal size).
- **Exact Solutions**: Solvable in exponential time via brute-force or more efficient algorithms like branch-and-bound.

## Applications

- Network design and fault tolerance.
- Wireless sensor networks (efficient coverage).
- Scheduling and resource allocation problems.

## Variants

- **Weighted Edge Dominating Set**: Edges have weights, and the goal is to minimize the total weight of $D$.
- **Connected Edge Dominating Set**: Requires $D$ to induce a connected subgraph.
- **Efficient Edge Dominating Set**: Imposes additional constraints on the structure of $D$.

## Related Problems

- **Vertex Cover**: A vertex cover indirectly dominates edges, while EDS directly dominates them.
- **Dominating Set**: A vertex-based variant where vertices dominate neighboring vertices.

## Example

Consider a graph $G$ with edges $E = \{(1,2), (2,3), (3,4)\}$:

- A minimal edge dominating set: $D = \{(2,3)\}$, since:
  - Edge (1,2) is adjacent to (2,3).
  - Edge (3,4) is adjacent to (2,3).

## Algorithms

1. **Greedy Approach**: Iteratively select edges covering the most undominated edges.
2. **Integer Linear Programming (ILP)**: Formulate EDS as an optimization problem.
3. **Fixed-Parameter Tractability (FPT)**: Solvable in $O^*(c^k)$ time for some constant $c$.

## Open Problems

- Finding improved approximation ratios or exact algorithms for special graph classes (e.g., planar graphs, bipartite graphs).
- Investigating parameterized complexity further.

## References

- Garey & Johnson, _Computers and Intractability_ (1979).
- G. F. Italiano et al., _Exact and Approximate Algorithms for Edge Dominating Set_.

---

## Problem Statement

Input: A Boolean Adjacency Matrix $M$.

Answer: Find a Minimum Edge Dominating Set.

### Example Instance: 5 x 5 matrix

|        | c1  | c2  | c3  | c4  | c5  |
| ------ | --- | --- | --- | --- | --- |
| **r1** | 0   | 0   | 1   | 0   | 1   |
| **r2** | 0   | 0   | 0   | 1   | 0   |
| **r3** | 1   | 0   | 0   | 0   | 1   |
| **r4** | 0   | 1   | 0   | 0   | 0   |
| **r5** | 1   | 0   | 1   | 0   | 0   |

The input for undirected graph is typically provided in [DIMACS](http://dimacs.rutgers.edu/Challenges) format. In this way, the previous adjacency matrix is represented in a text file using the following string representation:

```
p edge 5 4
e 1 3
e 1 5
e 2 4
e 3 5
```

This represents a 5x5 matrix in DIMACS format such that each edge $(v,w)$ appears exactly once in the input file and is not repeated as $(w,v)$. In this format, every edge appears in the form of

```
e W V
```

where the fields W and V specify the endpoints of the edge while the lower-case character `e` signifies that this is an edge descriptor line.

_Example Solution:_

Edge Dominating Set Found `(3, 5), (2, 4)`: Edges `(3, 5)`, and `(2, 4)` constitute an optimal solution.

---

# Compile and Environment

## Prerequisites

- Python ≥ 3.10

## Installation

```bash
pip install loynaz
```

## Execution

1. Clone the repository:

   ```bash
   git clone https://github.com/frankvegadelgado/loynaz.git
   cd loynaz
   ```

2. Run the script:

   ```bash
   edge -i ./benchmarks/testMatrix1
   ```

   utilizing the `edge` command provided by Loynaz's Library to execute the Boolean adjacency matrix `loynaz\benchmarks\testMatrix1`. The file `testMatrix1` represents the example described herein. We also support `.xz`, `.lzma`, `.bz2`, and `.bzip2` compressed text files.

   **Example Output:**

   ```
   testMatrix1: Edge Dominating Set Found (3, 5), (2, 4)
   ```

   This indicates edges `(3, 5), (2, 4)` form a edge dominating set.

---

## Edge Dominating Set Size

Use the `-c` flag to count the edges in the edge dominating set:

```bash
edge -i ./benchmarks/testMatrix2 -c
```

**Output:**

```
testMatrix2: Edge Dominating Set Size 3
```

---

# Command Options

Display help and options:

```bash
edge -h
```

**Output:**

```bash
usage: edge [-h] -i INPUTFILE [-a] [-b] [-c] [-v] [-l] [--version]

Compute the Approximate Edge Dominating Set for undirected graph encoded in DIMACS format.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the edge dominating set
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Batch Execution

Batch execution allows you to solve multiple graphs within a directory consecutively.

To view available command-line options for the `batch_edge` command, use the following in your terminal or command prompt:

```bash
batch_edge -h
```

This will display the following help information:

```bash
usage: batch_edge [-h] -i INPUTDIRECTORY [-a] [-b] [-c] [-v] [-l] [--version]

Compute the Approximate Edge Dominating Set for all undirected graphs encoded in DIMACS format and stored in a directory.

options:
  -h, --help            show this help message and exit
  -i INPUTDIRECTORY, --inputDirectory INPUTDIRECTORY
                        Input directory path
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the edge dominating set
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Testing Application

A command-line utility named `test_edge` is provided for evaluating the Algorithm using randomly generated, large sparse matrices. It supports the following options:

```bash
usage: test_edge [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-a] [-b] [-c] [-w] [-v] [-l] [--version]

The Loynaz Testing Application using randomly generated, large sparse matrices.

options:
  -h, --help            show this help message and exit
  -d DIMENSION, --dimension DIMENSION
                        an integer specifying the dimensions of the square matrices
  -n NUM_TESTS, --num_tests NUM_TESTS
                        an integer specifying the number of tests to run
  -s SPARSITY, --sparsity SPARSITY
                        sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the edge dominating set
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Code

- Python implementation by **Frank Vega**.

---

# License

- MIT License.
