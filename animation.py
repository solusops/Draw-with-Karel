# animation.py
# This module handles the logic for making the Karels move and tracking the animation state.

class AnimationState:
    def __init__(self):
        self.is_playing = False
        
        # We track different loops and how fast they should be going
        # key: loop head, value: speed (0=slow, 1=fast, 2=super fast)
        self.loop_speeds = {}
        
        # Variables to track the progress of the sliding animation
        # The accumulator counts up to a threshold. When it hits it, the Karels "step".
        self.loop_accumulators = {}
        
        # Visual progress (0.0 to 1.0) for the smooth sliding
        self.visual_progress = {}

def get_speed_threshold(speed):
    """Returns how high the accumulator must count before a Karel takes a step."""
    if speed == 0:
        return 1000  # Slow
    elif speed == 1:
        return 500   # Fast
    else:
        return 200   # Super fast

def toggle_loop_speed(anim_state, head):
    """Cycles the speed of a specific loop: 0 -> 1 -> 2 -> 0"""
    current_speed = anim_state.loop_speeds.get(head, 0)
    anim_state.loop_speeds[head] = (current_speed + 1) % 3

def advance_simulation(world, anim_state, node_to_head, cycle_heads, dt_ms=50):
    """
    Advances the simulation by dt_ms milliseconds.
    If a loop hits its threshold, the Karels in that loop actually take a step.
    Returns True if a step occurred, so the UI knows to redraw the whole board.
    """
    if not anim_state.is_playing:
        return False
        
    # Clean up any loops that disappeared
    keys_to_remove = []
    for h in anim_state.loop_speeds.keys():
        if h not in cycle_heads:
            keys_to_remove.append(h)
    for h in keys_to_remove:
        del anim_state.loop_speeds[h]
        if h in anim_state.loop_accumulators:
            del anim_state.loop_accumulators[h]
            
    step_occurred = False
            
    # Advance each loop independently
    for head in cycle_heads:
        if head not in anim_state.loop_accumulators:
            anim_state.loop_accumulators[head] = 0
            
        anim_state.loop_accumulators[head] += dt_ms
        
        speed = anim_state.loop_speeds.get(head, 0)
        threshold = get_speed_threshold(speed)
        
        # Calculate how far along they should be sliding (0.0 to 1.0)
        anim_state.visual_progress[head] = min(1.0, anim_state.loop_accumulators[head] / threshold)
        
        if anim_state.loop_accumulators[head] >= threshold:
            anim_state.loop_accumulators[head] = 0
            anim_state.visual_progress[head] = 0.0
            
            # They took a step!
            # Move the colors and directions around the cycle to simulate physical movement
            _step_loop(world, head, node_to_head)
            step_occurred = True
            
    return step_occurred

def _step_loop(world, head, node_to_head):
    """
    Moves all Karels in a specific loop forward one step.
    Because the track is fixed, we can just grab all the Karels, look at where they are pointing,
    and shift their data to the next cell!
    """
    from path_finding import find_next_karel_in_line
    from character import get_dir_delta
    
    # First, gather all Karels that belong to this loop's head
    cells_in_loop = []
    for pos in list(world.karels.keys()):
        if node_to_head.get(pos) == head:
            cells_in_loop.append(pos)
            
    # Figure out where each Karel is going
    next_positions = {}
    for pos in cells_in_loop:
        karel_data = world.get_karel(pos[0], pos[1])
        dx, dy = get_dir_delta(karel_data["direction"])
        front_pos = find_next_karel_in_line(world, pos[0], pos[1], dx, dy)
        next_positions[pos] = front_pos
        
    # Create a new dictionary to hold the new state for these cells
    new_data = {}
    
    # Move the Karels!
    for pos in cells_in_loop:
        front_pos = next_positions[pos]
        if front_pos is not None:
            # The Karel at 'pos' moves to 'front_pos'. 
            # But wait, it must adopt the direction of the track at 'front_pos'
            # to stay on the track! It only brings its color.
            current_karel = world.get_karel(pos[0], pos[1])
            target_track = world.get_karel(front_pos[0], front_pos[1])
            
            new_data[front_pos] = {
                "color": current_karel["color"],
                "direction": target_track["direction"],
                "shape": current_karel.get("shape", "Classic Karel")
            }
            
    # Apply the new state
    for pos in cells_in_loop:
        if pos in new_data:
            world.karels[pos] = new_data[pos]
        else:
            # If no Karel moved into this position (e.g. tail of a chain), it becomes empty!
            del world.karels[pos]
