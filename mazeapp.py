import cv2
import numpy as np
from pyzbar.pyzbar import decode
from queue import PriorityQueue

# A* Pathfinding
def astar(maze, start, end):
    rows, cols = maze.shape
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while not open_set.empty():
        _, current = open_set.get()

        if current == end:
            return reconstruct_path(came_from, current)

        neighbors = get_neighbors(current, rows, cols)
        for neighbor in neighbors:
            if maze[neighbor] == 1:  # Wall
                continue
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                open_set.put((f_score[neighbor], neighbor))

    return []  # No path found

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def get_neighbors(node, rows, cols):
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        x, y = node[0] + dx, node[1] + dy
        if 0 <= x < rows and 0 <= y < cols:
            neighbors.append((x, y))
    return neighbors

# QR Code Detection
def detect_qr_codes(frame):
    decoded_objects = decode(frame)
    car_qr, target_qr = None, None
    for obj in decoded_objects:
        data = obj.data.decode("utf-8")
        if "car" in data.lower():
            car_qr = obj
        elif "target" in data.lower():
            target_qr = obj
    return car_qr, target_qr

# Process Frame
def process_frame(frame, maze, car_position, target_position):
    bw_view = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bw_view = cv2.Canny(bw_view, 50, 150)

    walls = maze == 1
    path = astar(maze, car_position, target_position)

    # Highlight maze walls and path in black-and-white view
    color_bw_view = cv2.cvtColor(bw_view, cv2.COLOR_GRAY2BGR)
    color_bw_view[walls] = [255, 0, 0]  # Blue for walls
    for x, y in path:
        color_bw_view[x, y] = [255, 255, 255]  # White for path

    return color_bw_view, path

# Draw Mini-Map
def draw_mini_map(maze, car_position, target_position, path):
    mini_map = np.zeros((maze.shape[0] * 10, maze.shape[1] * 10, 3), dtype=np.uint8)
    for x in range(maze.shape[0]):
        for y in range(maze.shape[1]):
            color = (0, 0, 0) if maze[x, y] == 0 else (0, 0, 255)
            cv2.rectangle(mini_map, (y * 10, x * 10), ((y + 1) * 10, (x + 1) * 10), color, -1)

    # Draw path
    for x, y in path:
        cv2.circle(mini_map, (y * 10 + 5, x * 10 + 5), 3, (255, 255, 255), -1)

    # Draw car and target
    car_x, car_y = car_position
    target_x, target_y = target_position
    cv2.putText(mini_map, "🚗", (car_y * 10, car_x * 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(mini_map, "🏁", (target_y * 10, target_x * 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    return mini_map

# Main Loop
def main():
    cap = cv2.VideoCapture(0)
    maze = np.zeros((20, 20), dtype=np.uint8)  # Example empty maze
    car_position = (10, 10)
    target_position = (5, 5)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        car_qr, target_qr = detect_qr_codes(frame)
        if car_qr:
            car_position = (int(car_qr.rect.top // 10), int(car_qr.rect.left // 10))
        if target_qr:
            target_position = (int(target_qr.rect.top // 10), int(target_qr.rect.left // 10))

        bw_view, path = process_frame(frame, maze, car_position, target_position)
        mini_map = draw_mini_map(maze, car_position, target_position, path)

        # Display views
        cv2.imshow("Top-to-Bottom View", frame)
        cv2.imshow("Black-and-White View", bw_view)
        cv2.imshow("Mini-Map", mini_map)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
