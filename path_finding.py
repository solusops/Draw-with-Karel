# path_finding.py
# This file contains the logic to figure out if our Karels are arranged in a loop!

from character import get_dir_delta

def find_next_karel_in_line(world, col, row, dx, dy):
    """
    Looks forward in the direction (dx, dy) to find the next Karel.
    Stops at the edge of the board (No Pac-Man).
    """
    curr_col = col + dx
    curr_row = row + dy
    
    while 0 <= curr_col < world.logical_grid_cols and 0 <= curr_row < world.logical_grid_rows:
        # Check if there is a Karel at this position
        if world.get_karel(curr_col, curr_row) is not None:
            return (curr_col, curr_row)
            
        # Move forward one more step
        curr_col += dx
        curr_row += dy
        
    return None

def detect_loops_and_chains(world):
    """
    Detects loops (4 or more Karels pointing to each other) and chains 
    (Karels pointing into a loop).
    Returns a tuple: (cycles, node_to_head, cycle_heads)
    """
    cycles = []
    cycle_heads = []
    node_to_head = {}
    visited_global = [] # Using a simple list so beginners can understand
    
    # Check every Karel on the board
    for start_pos in list(world.karels.keys()):
        if start_pos in visited_global:
            continue
            
        path = []
        curr = start_pos
        
        while curr is not None:
            if curr in path:
                # We found a loop!
                # Find where the loop started in our path
                cycle_start_idx = 0
                for i in range(len(path)):
                    if path[i] == curr:
                        cycle_start_idx = i
                        break
                        
                cycle = path[cycle_start_idx:]
                
                # Check if the loop has at least 4 Karels
                if len(cycle) >= 4:
                    cycles.append(cycle)
                    # The "head" of the loop is the top-left-most cell in the loop
                    head = cycle[0]
                    for pos in cycle:
                        if pos[1] < head[1] or (pos[1] == head[1] and pos[0] < head[0]):
                            head = pos
                    cycle_heads.append(head)
                    
                    # Mark all nodes in the cycle as belonging to this head
                    for pos in cycle:
                        node_to_head[pos] = head
                
                break
                
            if curr in visited_global:
                # We ran into an already processed path
                break
                
            path.append(curr)
            
            # Find the next Karel in the line of sight
            karel_data = world.get_karel(curr[0], curr[1])
            dx, dy = get_dir_delta(karel_data["direction"])
            curr = find_next_karel_in_line(world, curr[0], curr[1], dx, dy)
            
        # Mark all the nodes we just checked as visited
        for node in path:
            if node not in visited_global:
                visited_global.append(node)
                
    # Now that we found cycles, let's find the chains that connect into them
    # A chain is a Karel pointing directly at a Karel that is already moving.
    moving = list(node_to_head.keys())
    changed = True
    while changed:
        changed = False
        for pos in list(world.karels.keys()):
            if pos in moving:
                continue
                
            karel_data = world.get_karel(pos[0], pos[1])
            dx, dy = get_dir_delta(karel_data["direction"])
            front_pos = find_next_karel_in_line(world, pos[0], pos[1], dx, dy)
            
            if front_pos is not None and front_pos in moving:
                front_data = world.get_karel(front_pos[0], front_pos[1])
                # Only connect if they are facing the same direction
                if front_data["direction"] == karel_data["direction"]:
                    node_to_head[pos] = node_to_head[front_pos]
                    moving.append(pos)
                    changed = True
                    
    return cycles, node_to_head, cycle_heads
