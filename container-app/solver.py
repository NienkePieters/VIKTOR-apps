from rectpack import newPacker
import rectpack.packer as packer

import numpy as np
from collections import deque

def solver_3d(boxes, container):
    container_width, container_length, container_height = container

    # Sort boxes by volume (largest first)
    sorted_boxes = sorted(boxes, key=lambda b: b['length'] * b['width'] * b['height'] * b['quantity'], reverse=True)

    # Initialize container space
    space = np.zeros((container_width, container_length, container_height), dtype=bool)

    placed_boxes = []
    empty_spaces = deque([(0, 0, 0)])

    for box in sorted_boxes:
        for _ in range(int(box['quantity'])):
            placed = False
            for _ in range(len(empty_spaces)):
                x, y, z = empty_spaces.popleft()
                if (x + box['length'] <= container_width and
                    y + box['width'] <= container_length and
                    z + box['height'] <= container_height and
                    not np.any(space[x:x+box['length'], y:y+box['width'], z:z+box['height']])):
                    
                    space[x:x+box['length'], y:y+box['width'], z:z+box['height']] = True
                    placed_boxes.append({
                        'x': x, 'y': y, 'z': z,
                        'length': box['length'], 'width': box['width'], 'height': box['height']
                    })
                    placed = True

                    # Add new empty spaces
                    empty_spaces.append((x + box['length'], y, z))
                    empty_spaces.append((x, y + box['width'], z))
                    empty_spaces.append((x, y, z + box['height']))
                    break
                else:
                    empty_spaces.append((x, y, z))

            if not placed:
                raise ValueError("Not all boxes could fit in the container")

    return placed_boxes

def solver(boxes, bins):
    container_width, container_length, container_height = bins[0]

    try:
        placed_boxes = solver_3d(boxes, (container_width, container_length, container_height))
    except ValueError as e:
        return str(e), None

    return placed_boxes, None