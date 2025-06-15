import pygame
import sys
import math

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BBox Arena")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# Constants
SPEED = 5
HANDLE_SIZE = 10
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
HANDLE_COLOR = (100, 100, 255)

# Initial box positions
initial_box1 = pygame.Rect(100, 100, 150, 100)
initial_box2 = pygame.Rect(400, 300, 150, 100)
box1 = initial_box1.copy()
box2 = initial_box2.copy()

selected_box = None
resize_mode = None
mouse_offset = (0, 0)

# Functions for metrics
def draw_text(text, x, y):
    img = font.render(text, True, WHITE)
    screen.blit(img, (x, y))

def iou(a, b):
    xA, yA = max(a.left, b.left), max(a.top, b.top)
    xB, yB = min(a.right, b.right), min(a.bottom, b.bottom)
    inter = max(0, xB - xA) * max(0, yB - yA)
    return inter / float(a.width * a.height + b.width * b.height - inter + 1e-6)

def giou(a, b):
    i = iou(a, b)
    xC, yC = min(a.left, b.left), min(a.top, b.top)
    xD, yD = max(a.right, b.right), max(a.bottom, b.bottom)
    convex = (xD - xC) * (yD - yC)
    inter = i * (a.width * a.height + b.width * b.height - i)
    union = a.width * a.height + b.width * b.height - inter
    return i - (convex - union) / (convex + 1e-6)

def diou(a, b):
    i = iou(a, b)
    cxA, cyA = a.center
    cxB, cyB = b.center
    center_dist = (cxA - cxB) ** 2 + (cyA - cyB) ** 2
    xC, yC = min(a.left, b.left), min(a.top, b.top)
    xD, yD = max(a.right, b.right), max(a.bottom, b.bottom)
    diag = (xD - xC) ** 2 + (yD - yC) ** 2
    return i - center_dist / (diag + 1e-6)

def ciou(a, b):
    i = iou(a, b)
    d = diou(a, b)
    w1, h1 = a.width, a.height
    w2, h2 = b.width, b.height
    v = (4 / math.pi ** 2) * (math.atan(w2 / h2) - math.atan(w1 / h1)) ** 2
    alpha = v / (1 - i + v + 1e-6) if v != 0 else 0
    return d - alpha * v

def draw_resize_handles(rect, color):
    pygame.draw.rect(screen, color, rect, 2)
    for x in [rect.left, rect.right - HANDLE_SIZE]:
        for y in [rect.top, rect.bottom - HANDLE_SIZE]:
            pygame.draw.rect(screen, HANDLE_COLOR, (x, y, HANDLE_SIZE, HANDLE_SIZE))

def get_resize_handle(rect, pos):
    mx, my = pos
    corners = {
        'tl': pygame.Rect(rect.left, rect.top, HANDLE_SIZE, HANDLE_SIZE),
        'tr': pygame.Rect(rect.right - HANDLE_SIZE, rect.top, HANDLE_SIZE, HANDLE_SIZE),
        'bl': pygame.Rect(rect.left, rect.bottom - HANDLE_SIZE, HANDLE_SIZE, HANDLE_SIZE),
        'br': pygame.Rect(rect.right - HANDLE_SIZE, rect.bottom - HANDLE_SIZE, HANDLE_SIZE, HANDLE_SIZE),
    }
    for key, area in corners.items():
        if area.collidepoint(mx, my):
            return key
    return None

def resize_box(rect, mode, mouse_pos):
    if mode == 'tl':
        rect.width += rect.left - mouse_pos[0]
        rect.height += rect.top - mouse_pos[1]
        rect.left = mouse_pos[0]
        rect.top = mouse_pos[1]
    elif mode == 'tr':
        rect.width = mouse_pos[0] - rect.left
        rect.height += rect.top - mouse_pos[1]
        rect.top = mouse_pos[1]
    elif mode == 'bl':
        rect.width += rect.left - mouse_pos[0]
        rect.left = mouse_pos[0]
        rect.height = mouse_pos[1] - rect.top
    elif mode == 'br':
        rect.width = mouse_pos[0] - rect.left
        rect.height = mouse_pos[1] - rect.top

# Main Loop
mouse_down = False
while True:
    screen.fill((0, 0, 0))
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            box1 = initial_box1.copy()
            box2 = initial_box2.copy()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True
            for box in [box1, box2]:
                mode = get_resize_handle(box, (mx, my))
                if mode:
                    selected_box = box
                    resize_mode = mode
                    break
            else:
                if box1.collidepoint(mx, my):
                    selected_box = box1
                    resize_mode = None
                    mouse_offset = (mx - box1.x, my - box1.y)
                elif box2.collidepoint(mx, my):
                    selected_box = box2
                    resize_mode = None
                    mouse_offset = (mx - box2.x, my - box2.y)
                else:
                    selected_box = None
                    resize_mode = None

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False
            selected_box = None
            resize_mode = None

    if mouse_down and selected_box:
        if resize_mode:
            resize_box(selected_box, resize_mode, (mx, my))
        else:
            new_x = mx - mouse_offset[0]
            new_y = my - mouse_offset[1]
            selected_box.topleft = (new_x, new_y)

    # Keyboard movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: box1.x -= SPEED
    if keys[pygame.K_RIGHT]: box1.x += SPEED
    if keys[pygame.K_UP]: box1.y -= SPEED
    if keys[pygame.K_DOWN]: box1.y += SPEED
    if keys[pygame.K_a]: box2.x -= SPEED
    if keys[pygame.K_d]: box2.x += SPEED
    if keys[pygame.K_w]: box2.y -= SPEED
    if keys[pygame.K_s]: box2.y += SPEED

    # Draw boxes and handles
    draw_resize_handles(box1, GREEN)
    draw_resize_handles(box2, RED)

    # Compute metrics
    draw_text(f"IoU:  {iou(box1, box2):.3f}", 10, 10)
    draw_text(f"GIoU: {giou(box1, box2):.3f}", 10, 40)
    draw_text(f"DIoU: {diou(box1, box2):.3f}", 10, 70)
    draw_text(f"CIoU: {ciou(box1, box2):.3f}", 10, 100)
    draw_text("Press 'R' to reset", WIDTH - 200, 10)

    pygame.display.flip()
    clock.tick(60)
