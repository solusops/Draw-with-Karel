import sys
import os
sys.path.insert(0, os.path.abspath('d:\\GitHub\\Draw-with-Karel'))

from path_finding import detect_loops_and_chains, find_next_karel_in_line
from world import World

w = World(4)

# Recreate Image 2 roughly
w.karels = {
    (0,0): {"direction": "East"},
    (1,0): {"direction": "East"},
    (2,0): {"direction": "East"},
    (3,0): {"direction": "South"},
    
    (1,1): {"direction": "East"},
    (2,1): {"direction": "East"},
    (3,1): {"direction": "South"},
    
    (0,2): {"direction": "East"},
    (1,2): {"direction": "East"},
    (2,2): {"direction": "East"},
    (3,2): {"direction": "South"},
    
    (1,3): {"direction": "East"},
    (2,3): {"direction": "East"},
}

cycles, node_to_head, cycle_heads = detect_loops_and_chains(w)
print("Cycles:")
for c in cycles:
    print(c)
print("Heads:")
print(cycle_heads)
