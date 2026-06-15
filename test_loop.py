def get_dir_delta(direction):
    if direction == "East": return 1, 0
    elif direction == "West": return -1, 0
    elif direction == "North": return 0, -1
    elif direction == "South": return 0, 1
    return 0, 0

logical_grid_size = 3
karels = {
    (0,0): {"direction": "East"},
    (1,0): {"direction": "East"},
    (2,0): {"direction": "North"},
    (0,1): {"direction": "South"},
    (1,1): {"direction": "East"},
    (2,1): {"direction": "West"}
}

cycles = []
node_to_head = {}
visited_global = set()

for start in list(karels.keys()):
    if start in visited_global:
        continue
    path = []
    visited_local = {}
    curr = start
    while curr in karels:
        if curr in visited_local:
            cycle_start_idx = visited_local[curr]
            cycle = path[cycle_start_idx:]
            if len(cycle) >= 4:
                cycles.append(set(cycle))
            break
        if curr in visited_global:
            break
        visited_local[curr] = len(path)
        path.append(curr)
        col, row = curr
        data = karels[curr]
        dx, dy = get_dir_delta(data["direction"])
        curr = ((col + dx) % logical_grid_size, (row + dy) % logical_grid_size)
    for node in path:
        visited_global.add(node)

print("Cycles:", cycles)
