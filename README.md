*This project has been created as part of the 42 curriculum by ypopovyc.*

# Fly-In: Autonomous Drone Swarm Routing Engine

## Description
**Fly-In** is an autonomous drone fleet simulation and pathfinding engine. The core objective is to route multiple drones from a designated starting zone (`start_hub`) to a destination terminal (`end_hub`) across a constrained topological network of hubs and zones in the minimum possible number of discrete simulation turns.

The simulation models real-world multi-agent routing challenges and physical bottlenecks:
- **Spatial Exclusivity:** Intermediate zones enforce strict occupancy limitations (default `max_drones=1`).
- **Edge Concurrency:** Transit links constrain simultaneous bidirectional and pipeline traversal (`max_link_capacity`).
- **Heterogeneous Movement Costs:** Zones feature variable transit dynamics, including standard costs, multi-turn delays in restricted airspace, priority corridors, and impassable obstacles.

In strict compliance with 42 curriculum guidelines, the system is built completely from scratch in **Python 3.10+** without external graph packages (e.g., NetworkX). The codebase adheres to strict object-oriented design (OOP), passes comprehensive static type verification (`mypy --strict`), conforms to PEP 8 / PEP 257 standards, and provides both a headless CLI simulation engine and an interactive 2D graphical visualizer.

---

## Architecture & System Design

The architecture strictly separates responsibilities into modular, decoupled components:

```text
Fly_in/
├── main.py                   # CLI entrypoint and simulation runner
├── Makefile                  # Build, test, and verification automation
├── pyproject.toml            # Project dependencies and tool configurations
├── maps/                     # Benchmark topological maps (easy, medium, hard)
└── fly_in/
    ├── parsing.py            # Map lexer, grammar parser, and syntax validator
    ├── factories.py          # Abstract Factory pattern for polymorphic Zones & Links
    ├── pathfinding.py        # Graph representation and multi-path discovery engine
    ├── simulation.py         # Discrete-event turn scheduler and state evaluator
    └── visualiser.py         # Real-time graphical visualization engine (Pygame)
```

### Class Hierarchy & OOP Modeling
1. **Topological Entities (`Zone` & `Link`):**
   - `Zone` is an Abstract Base Class (`ABC`) defining polymorphic contracts (`can_enter_zone()`, `get_movement_cost()`). Subclasses (`NormalZone`, `PriorityZone`, `RestrictedZone`, `BlockedZone`) encapsulate unique physical constraints.
   - `start_hub` and `end_hub` act as boundless terminal nodes with infinite drone capacity.
2. **Factory Dispatching (`ZoneFactory`):**
   - Implements safe pattern matching (`match-case`) to instantiate concrete zone specializations based on parsed metadata, avoiding type variance conflicts.
3. **Discrete Event Simulation (`Simulation`):**
   - Manages turn-by-turn state progression and active drone registries.
   - Accurately evaluates simultaneous pipeline movements: drones exiting a zone on turn $T$ instantaneously free capacity for arriving drones on that exact turn.

---

## Algorithm Choices & Implementation Strategy

Routing a drone fleet under node- and edge-capacity constraints without collisions or deadlocks is a variation of the **Multi-Commodity Flow** and **Time-Expanded Conflict-Free Routing** problem.

### 1. Multi-Path Discovery Strategy
- **Limitation of Single Shortest Paths:** Standard single-source shortest path routing (such as standard Dijkstra) routes all drones through a single corridor, creating severe queueing delays and violating zone capacities.
- **Disjoint & Overlapping Paths:** The pathfinding module constructs path sets capable of concurrent throughput. When intermediate hub capacities permit, traffic is split across alternate branches (e.g., parallel fork routing).
- **Cost Balancing:** The engine accounts for heterogeneous zone traversal weights:
  - `normal`: 1 turn.
  - `priority`: 1 turn, but prioritized in path assignment heuristics to maximize flow.
  - `restricted`: 2 turns (the drone occupies the incoming link during transit and must land in the destination zone on the subsequent turn).
  - `blocked`: Permanently pruned from the routing graph.

### 2. Turn Scheduling & Deadlock Prevention
- **Reservation Table (Space-Time Scheduling):** To guarantee conflict-free navigation, the scheduler uses space-time tracking `(location, turn)`. A drone only departs if its arrival trajectory respects the node’s `max_drones` capacity at turn $T$ and the connection's `max_link_capacity` during transit.
- **Pipeline Progression (Convoys):** If Zone $A$ contains Drone 1 and Zone $B$ contains Drone 2, Drone 1 can move into Zone $B$ simultaneously as Drone 2 moves into Zone $C$, achieving optimal convoy throughput without stalling.
- **Restricted Corridor Invariant:** A drone is strictly prohibited from entering a restricted transit connection unless the target zone is guaranteed to have available capacity on turn $T + 1$ (hovering or waiting on connections is forbidden).

---

## Instructions

### Prerequisites
- Python 3.10 or higher
- `uv` (recommended modern Python package manager) or `pip`

### Installation
Clone the repository and install all dependencies via `uv`:
```bash
git clone <repository_url> Fly_in
cd Fly_in
make install
```

### Execution

#### 1. Standard Simulation
Run the primary simulation engine against any benchmark map:
```bash
# Default map
make run

# Explicit map selection
make run MAP=maps/easy/02_simple_fork.txt
```

#### 2. Interactive Debugger (`pdb`)
Launch the simulation within Python's interactive debugger:
```bash
make debug MAP=maps/medium/03_priority_puzzle.txt
```


#### 3. Automated Testing & Verification
Execute static code analysis:
```bash

# Standard subject linting (flake8 + mypy)
make lint

# Strict static type check (mypy --strict)
make lint-strict
```

#### 4. Cleanup
```bash
make clean    # Cleans caches and bytecode
make fclean   # Full purge of virtual environment
make re       # Complete clean rebuild
```

---

## Visual Representation

The project includes an interactive graphical visualizer built with **Pygame** to provide intuitive feedback on swarm dynamics and topological states:

- **Dynamic Network Layout:** Graph zones are mapped using coordinate scaling to automatically fit within the window, with color-coded nodes reflecting their functional types:
  - 🟢 **Start Hub** & 🟡 **Goal Hub** (Terminals)
  - ⚪ **Normal Zones** (Standard capacity)
  - 🟣 **Priority Zones** (High-throughput corridors)
  - 🔴 **Restricted Zones** (Hazardous multi-turn areas)
  - ⚫ **Blocked Zones** (Impassable obstacles)
- **Live Occupancy Meters:** Real-time occupancy counters displayed above each hub (`current / max_drones`), highlighting congestion bottlenecks.
- **Flight Vectors:** Visual representation of drones traversing connections, explicitly illustrating mid-flight transit across multi-turn restricted links.
- **Controls:**
  - `SPACE`: Play / Pause simulation.
  - `RIGHT ARROW`: Step forward by one discrete turn.
  - `B`: Reset simulation to Turn 0.
---

## Input & Output Specification

### Input Format (`.txt`)
The input grammar defines fleet size, hubs, and bidirectional connections:
```text
nb_drones: 4
start_hub: start 0 0 [color=green]
end_hub: goal 10 0 [color=yellow]
hub: junction 3 0 [max_drones=2]
hub: path_a 6 2 [zone=normal]
hub: path_b 6 -2 [zone=normal]
connection: start-junction
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

### Expected Simulation Output
Each discrete turn is printed on a separate line. Stationary drones are omitted, and movements are space-separated:
```text
D0-junction D1-junction
D0-path_a D1-path_b D2-junction D3-junction
D0-goal D1-goal D2-path_a D3-path_b
D2-goal D3-goal
```
*Completed in 4 turns (meeting the benchmark target $\le 8$ turns).*

---

## Error Handling & Robustness

In accordance with the **NO CRASHES** policy, the program never terminates with an unhandled exception or raw stack trace:
- **Deterministic Syntax Diagnostics:** The parser identifies line numbers and descriptive causes for syntax violations (e.g., negative coordinates, duplicate edges, invalid zone identifiers containing hyphens).
- **Topological Invariants:** Disconnected graphs, cycles without path to `end_hub`, or maps with unreachable goals are gracefully caught and reported to `sys.stderr` with exit code `1`.
- **Signal Gracefulness:** Clean interception of `SIGINT` (`Ctrl+C`), ensuring safe release of SDL and file descriptor handles without hanging threads or error codes.

---

## Resources & AI Usage

### References & Literature
- https://www.youtube.com/watch?v=AY9MnQ4x3zk
- Python Software Foundation: `typing`, `dataclasses`, `abc`, and `argparse` standard documentation.
- Pygame Community Documentation: Event loops, double buffering, and surface blitting.

### AI Usage Disclosure
In compliance with Chapter II and Chapter VIII of the 42 Subject:
- **Algorithmic Brainstorming:** Used AI as a Socratic dialogue partner to explore the trade-offs between static space-time reservation tables versus dynamic turn-by-turn scheduling for drone traffic coordination.
- **Static Typing & Mypy Strictness:** Leveraged generative assistance to resolve complex structural typing edge cases (e.g., narrowing generic `Callable` signatures in parser command dispatchers and solving covariant type inference for abstract zone factories).
- **Test Matrix Generation:** Used AI to brainstorm edge-case boundary scenarios (e.g., pipeline convoy contention, zero-capacity links, rapid `Ctrl+C` interrupt handling in Pygame).
