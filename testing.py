import pygame
import pyopencl as cl
import numpy as np
import pygame
import sys
import time
import math

# ========== OpenCL Setup ==========

# Create OpenCL context and queue
ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

# OpenCL kernel code for moving the player toward the target
kernel_code = """
__kernel void move_towards(
    __global const float *current,
    __global const float *target,
    __global float *step,
    const float speed
)
{
    float dx = target[0] - current[0];
    float dy = target[1] - current[1];
    float dist = sqrt(dx * dx + dy * dy);
    if (dist > 0.01f) {
        step[0] = speed * dx / dist;
        step[1] = speed * dy / dist;
    } else {
        step[0] = 0.0f;
        step[1] = 0.0f;
    }
}
"""
program = cl.Program(ctx, kernel_code).build()

# ========== Pygame Setup ==========

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Maze + OpenCL Movement")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Font setup
font = pygame.font.SysFont(None, 30)

# Player settings
player_radius = 15
player_pos = [60.0, 60.0]
player_speed = 3.75

# Goal settings
goal_pos = [540, 540]
goal_size = 30

# Maze walls setup
walls = [
    pygame.Rect(0, 0, 600, 30),
    pygame.Rect(0, 0, 30, 600),
    pygame.Rect(0, 570, 600, 30),
    pygame.Rect(570, 0, 30, 600),
    pygame.Rect(90, 90, 420, 30),
    pygame.Rect(90, 90, 30, 300),
    pygame.Rect(480, 150, 30, 420),
    pygame.Rect(180, 360, 300, 30),
]

# Charges and movement state
charges = []
moving = False
target_charge = None

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Function to check for collision with walls
def check_collision(pos):
    player_rect = pygame.Rect(pos[0] - player_radius, pos[1] - player_radius, player_radius * 2, player_radius * 2)
    return any(player_rect.colliderect(wall) for wall in walls)

# CPU-only movement function with added complexity
def cpu_move_towards(current, target, speed):
    # Basic movement logic
    dx = target[0] - current[0]
    dy = target[1] - current[1]
    dist = math.hypot(dx, dy)

    # Simulate a computationally intensive operation
    result = 0
    for i in range(1000000):  # Adding a large number of iterations
        result += math.sin(i) * math.cos(i) * math.sqrt(i)

    # Return the movement step
    if dist > 0.01:
        return [speed * dx / dist, speed * dy / dist]
    else:
        return [0.0, 0.0]

# ========== Main Game Loop ==========

frame_counter = 0  # To count frames and print time every 10 frames

while True:
    # Fill the screen with white background
    screen.fill(WHITE)

    # Draw the maze walls
    for wall in walls:
        pygame.draw.rect(screen, BLACK, wall)

    # Draw the goal
    pygame.draw.rect(screen, GREEN, (*goal_pos, goal_size, goal_size))

    # Draw the player
    pygame.draw.circle(screen, RED, (int(player_pos[0]), int(player_pos[1])), player_radius)
    neg_text = font.render("−", True, WHITE)
    screen.blit(neg_text, (player_pos[0] - 6, player_pos[1] - 10))

    # Draw the charges
    for (x, y, q) in charges:
        pygame.draw.circle(screen, BLUE, (x, y), 12)
        text = font.render("+", True, WHITE)
        screen.blit(text, (x - 6, y - 8))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if not moving and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            mouse_rect = pygame.Rect(mx - 5, my - 5, 10, 10)
            if not any(mouse_rect.colliderect(wall) for wall in walls):
                charges.append((mx, my, 1))
                target_charge = (mx, my)
                moving = True

    # Initialize timings
    opencl_time, cpu_time = 0, 0

    # Move the player using OpenCL and CPU
    if moving and target_charge:
        # Convert player and target positions to numpy arrays
        current_np = np.array(player_pos, dtype=np.float32)
        target_np = np.array(target_charge, dtype=np.float32)
        step_np = np.zeros(2, dtype=np.float32)

        # OpenCL memory buffers
        mf = cl.mem_flags
        current_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=current_np)
        target_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=target_np)
        step_buf = cl.Buffer(ctx, mf.WRITE_ONLY, step_np.nbytes)

        # === OpenCL timing ===
        t1 = time.perf_counter()
        program.move_towards(queue, (1,), None, current_buf, target_buf, step_buf, np.float32(player_speed))
        cl.enqueue_copy(queue, step_np, step_buf)
        t2 = time.perf_counter()
        opencl_time = (t2 - t1) * 1e6  # µs

        # === CPU-only timing ===
        t3 = time.perf_counter()
        cpu_step = cpu_move_towards(player_pos, target_charge, player_speed)
        t4 = time.perf_counter()
        cpu_time = (t4 - t3) * 1e6  # µs

        # Apply OpenCL movement step
        new_pos = [player_pos[0] + step_np[0], player_pos[1] + step_np[1]]
        if not check_collision(new_pos):
            player_pos = new_pos

        # Check if the player reached the target charge
        if math.hypot(player_pos[0] - target_charge[0], player_pos[1] - target_charge[1]) < player_radius:
            moving = False
            target_charge = None

        # Print the timings every 10 frames
        frame_counter += 1
        if frame_counter % 10 == 0:
            print(f"OpenCL Time: {opencl_time:.2f} µs")
            print(f"CPU Time: {cpu_time:.2f} µs")

    # Update the display
    pygame.display.flip()
    
    # Control the frame rate
    clock.tick(60)