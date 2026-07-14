# Mini Static Timing Analysis (STA) Engine

## Project Overview

The Mini Static Timing Analysis (STA) Engine is a Python-based software tool developed to perform timing analysis on a simplified gate-level Verilog circuit. The program parses a structural Verilog netlist and a cell delay library, constructs the circuit as a Directed Acyclic Graph (DAG), computes the arrival time of each node, identifies the critical path, and generates a timing report.

---

## Features

- Parses a simplified structural Verilog netlist
- Reads gate propagation delays from a JSON library
- Builds a Directed Acyclic Graph (DAG)
- Performs Topological Sorting
- Calculates Arrival Time (AT)
- Calculates Required Time (RT)
- Computes Slack for each node
- Identifies the Critical Path
- Generates a timing analysis report

---

## Project Structure

```
Mini_STA_Engine
│
├── main.py
├── parser.py
├── graph.py
├── timing.py
├── report.py
├── library.json
├── netlist.v
├── timing_report.txt
├── README.md
└── Mini_STA_Report.pdf
```

---

## Software Requirements

- Python 3.14 or later
- Visual Studio Code (Recommended)
- Windows / Linux / macOS
- No external libraries required

---

## Python Modules Used

- json
- re
- collections
- sys

---

## Input Files

### library.json

Contains propagation delays for logic gates.

Example:

```json
{
    "AND2": { "delay_ps": 15.0 },
    "OR2":  { "delay_ps": 12.5 },
    "INV":  { "delay_ps": 8.0 }
}
```

### netlist.v

Contains the simplified structural Verilog description of the digital circuit.

Example:

```verilog
module simple_logic(A,B,C,Y);

input A,B,C;

output Y;

wire w1,w2;

AND2 u1(.A(A),.B(B),.Y(w1));

INV u2(.A(C),.Y(w2));

OR2 u3(.A(w1),.B(w2),.Y(Y));

endmodule
```

---

## How to Run

Open Command Prompt or Terminal.

Navigate to the project folder.

Run the following command:

```bash
python main.py library.json netlist.v
```

---

## Expected Output

The program displays:

- Primary Inputs
- Primary Outputs
- Parsed Gates
- Arrival Time
- Required Time
- Slack
- Worst Case Delay
- Critical Path

A detailed report is also generated in:

```
timing_report.txt
```

---

## Algorithm

1. Read the gate delay library.
2. Parse the Verilog netlist.
3. Build the Directed Acyclic Graph (DAG).
4. Perform Topological Sorting.
5. Calculate Arrival Time (AT).
6. Calculate Required Time (RT).
7. Compute Slack.
8. Identify the Critical Path.
9. Generate the timing report.

---

## Data Structures Used

- Dictionary (Gate Delay Library)
- List (Inputs, Outputs, Gates)
- Directed Acyclic Graph (DAG)
- Adjacency List
- Queue (Topological Sort)
- Dictionary (Arrival Time, Required Time, Slack)

---

## Time Complexity

The overall time complexity is **O(V + E)**, where **V** is the number of gates (vertices) and **E** is the number of wire connections (edges). Each gate and connection is processed only once.

---

## Space Complexity

The overall space complexity is **O(V + E)** because the graph, timing information, and adjacency lists are stored in memory. The required memory grows linearly with the size of the circuit.

---

## Edge Cases Considered

- Empty netlist
- Unknown gate type
- Floating wires
- Missing outputs
- Fan-out connections
- Invalid gate connections
- Combinational loop detection

---

## Output Files

- timing_report.txt
- Terminal Timing Report

---

## Author

**Name:** Chandra

**Project:** Mini Static Timing Analysis (STA) Engine

**Language:** Python 3.14

**Target Role:** VLSI Software / EDA Development Internship
