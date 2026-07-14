# These are Python's built-in toolboxes we use for reading data and sorting text.
import json
import re
import collections

# =====================================================================
# 1. EMBEDDED DATABASES (The input data for our circuit)
# =====================================================================

# This string holds the delay database for our gates (AND, OR, NOT).
JSON_DATA = """
{
  "AND2": { "delay": 2.0, "inputs": ["A", "B"], "output": "Y" },
  "OR2":  { "delay": 3.0, "inputs": ["A", "B"], "output": "Y" },
  "NOT":  { "delay": 1.0, "inputs": ["A"],      "output": "Y" }
}
"""

# This string holds the blueprint of our actual circuit connections.
VERILOG_DATA = """
module simple_circuit (
    input wire IN_A,
    input wire IN_B,
    output wire OUT_Z
);
    wire n1;
    wire n2;

    AND2 g1 (.A(IN_A), .B(IN_B), .Y(n1));
    NOT  g2 (.A(IN_B), .Y(n2));
    OR2  g3 (.A(n1), .B(n2), .Y(OUT_Z));
endmodule
"""

# =====================================================================
# 2. STATIC TIMING ANALYSIS ENGINE LOGIC (The math calculator)
# =====================================================================

# This block is the main calculator machine. We name it IntegratedSTAEngine.
class IntegratedSTAEngine:
    
    # This prepares the empty lists and storage buckets when the machine starts.
    def __init__(self, json_string, clock_period=6.0):
        self.clock_period = clock_period  # Sets our time limit (deadline) to 6.0
        self.library = json.loads(json_string)  # Reads the gate delay database text
        
        # Create empty maps to store connections, delays, and calculated times
        self.graph = collections.defaultdict(list)      # Tracks which gate drives what next
        self.rev_graph = collections.defaultdict(list)  # Tracks where a gate gets its inputs from
        self.node_delays = {}    # Storage for cell delays
        self.arrival_times = {}  # Storage for arrival math
        self.required_times = {} # Storage for deadline math
        self.primary_inputs = set()   # List of starting wires
        self.primary_outputs = set()  # List of ending wires
        self.nodes = set()            # List of all unique wires in the circuit

    # This function reads the circuit text and finds all wires and gates.
    def parse_verilog_stream(self, verilog_string):
        # Remove any human comments (lines with // or /*) from the text so code doesn't get confused
        content = re.sub(r'//.*', '', verilog_string)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # Scan the text to find words next to "input" or "output"
        inputs = re.findall(r'input\s+(?:wire\s+)?([A-Za-z0-9_]+)', content)
        outputs = re.findall(r'output\s+(?:wire\s+)?([A-Za-z0-9_]+)', content)
        
        # Save inputs into storage and set their initial wire delay to 0
        for inp in inputs:
            self.primary_inputs.add(inp)
            self.node_delays[inp] = 0.0
            self.nodes.add(inp)
            
        # Save outputs into storage and set their wire delay to 0
        for outp in outputs:
            self.primary_outputs.add(outp)
            self.node_delays[outp] = 0.0
            self.nodes.add(outp)

        # Look for gate descriptions like AND2, NOT, or OR2 inside the text
        gate_pattern = r'([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*\((.*?)\);'
        instances = re.findall(gate_pattern, content, re.DOTALL)

        # Loop through every single gate found in the text file
        for cell_type, inst_name, ports_str in instances:
            if cell_type not in self.library:
                continue  # Ignore the item if it's not a known gate in our database
                
            cell_info = self.library[cell_type]
            out_pin = cell_info['output']
            
            # Find which wires are plugged into the gate pins (e.g., .A(IN_A))
            pin_mappings = re.findall(r'\.([A-Za-z0-9_]+)\s*\(\s*([A-Za-z0-9_]+)\s*\)', ports_str)
            port_dict = {pin: net for pin, net in pin_mappings}
            
            # Find the output wire of this gate and assign its delay from our database
            driving_net = port_dict[out_pin]
            self.node_delays[driving_net] = cell_info['delay']
            self.nodes.add(driving_net)
            
            # Connect the input wires to the output wire to construct the circuit pathway map
            for in_pin in cell_info['inputs']:
                driven_net = port_dict[in_pin]
                self.graph[driven_net].append(driving_net)  # Forward direction wire map
                self.rev_graph[driving_net].append(driven_net)  # Backward direction wire map
                self.nodes.update([driven_net, driving_net])

    # This function executes the core timing calculations.
    def compute_timing(self):
        
        # --- PHASE 1: SORT THE GATES ---
        # Count how many incoming signals each wire is waiting for
        in_degree = {u: 0 for u in self.nodes}
        for u in self.graph:
            for v in self.graph[u]:
                in_degree[v] += 1
                
        # Find the starting wires (wires that don't wait for any gate)
        queue = collections.deque([u for u in self.nodes if in_degree[u] == 0])
        order = []
        
        # Arrange all wires in a perfect line from start to finish so we calculate in order
        while queue:
            u = queue.popleft()
            order.append(u)
            for v in self.graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        
        # --- PHASE 2: FORWARD PASS (Find out when signals actually arrive) ---
        for node in order:
            if node in self.primary_inputs: 
                self.arrival_times[node] = 0.0  # Inputs start counting time at exactly 0.0
            else:
                # Find the slowest incoming path time, then add this gate's delay to get total time
                max_prev = max([self.arrival_times[prev] for prev in self.rev_graph[node]]) if self.rev_graph[node] else 0.0
                self.arrival_times[node] = max_prev + self.node_delays.get(node, 0.0)

        # --- PHASE 3: BACKWARD PASS (Find out the absolute deadlines) ---
        for node in reversed(order):
            if node in self.primary_outputs: 
                self.required_times[node] = self.clock_period  # Final output deadline is our clock limit (6.0)
            else:
                # Work backward: subtract the next gate's delay from its target deadline
                min_next = min([self.required_times[nxt] - self.node_delays.get(nxt, 0.0) for nxt in self.graph[node]]) if self.graph[node] else self.clock_period
                self.required_times[node] = min_next

    # This function prints the final calculated table neatly on the screen.
    def report_timing(self):
        # Print the title row of our table
        print(f"\n{'Net/Node':<12} | {'Cell Delay':<10} | {'Arrival':<10} | {'Required':<10} | {'Slack':<8} | Status")
        print("-" * 68)
        
        # Go through each wire name in alphabetical order and calculate slack space
        for node in sorted(self.nodes):
            arr = self.arrival_times.get(node, 0.0)
            req = self.required_times.get(node, 0.0)
            slack = req - arr  # Slack = Deadline Time minus Actual Arrival Time
            
            # If slack is negative, it's a VIOLATION (bad). If positive, it MET the deadline (good).
            status = 'VIOLATION' if slack < 0 else 'MET'
            
            # Print the formatted row values to the terminal screen
            print(f"{node:<12} | {self.node_delays.get(node, 0.0):<10.2f} | {arr:<10.2f} | {req:<10.2f} | {slack:<8.2f} | {status}")

# =====================================================================
# 3. RUNTIME EXECUTION (The trigger that starts the program)
# =====================================================================
if __name__ == "__main__":
    # 1. Turn on the machine and tell it our clock target speed limit is 6.0
    sta = IntegratedSTAEngine(JSON_DATA, clock_period=6.0)
    
    # 2. Feed the Verilog circuit design text into our parsing text filter
    sta.parse_verilog_stream(VERILOG_DATA)
    
    # 3. Tell the engine to calculate the forward and backward times
    sta.compute_timing()
    
    # 4. Print the final math table out onto our display screen
    sta.report_timing()
