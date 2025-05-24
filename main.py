import pygame 
import random

pygame.init()
pygame.display.set_caption("Worm")

WIDTH, HEIGHT = 850, 775

WHITE = 255, 255, 255
BLACK = 0, 0, 0
GREEN = 0, 255, 0
RED = 255, 0, 0
BLUE = 0, 0, 255
ORANGE = 234, 181, 11

FPS = 60

EMPTY = 0
FRUIT = -1
SNAKE_HEAD = 1

MOVE_SNAKE = pygame.USEREVENT + 1

def change_direction(k, grid, row_head, col_head):
    head = grid[row_head][col_head]
    direction = grid[row_head][col_head]["direction"]
    if k == pygame.K_d and direction != "left":
        head["direction"] = "right"
    elif k == pygame.K_a and direction != "right":
        head["direction"] = "left"
    elif k == pygame.K_w and direction != "down":
        head["direction"] = "up"
    elif k == pygame.K_s and direction != "up":
        head["direction"] = "down"

# Call this first time passing in tail coords

def find_next_seg(grid, r, c, value):
    if c + 1 < len(grid[0]) and grid[r][c + 1]["value"] == value + 1:
        return r, c + 1
    elif c - 1 >= 0 and grid[r][c - 1]["value"] == value + 1:
        return r, c - 1
    elif r - 1 >= 0 and grid[r - 1][c]["value"] == value + 1:
        return r - 1, c
    elif r + 1 < len(grid) and grid[r + 1][c]["value"] == value + 1:
        return r + 1, c

def move(grid, r, c, length, new_direction):
    value = grid[r][c]["value"]
    old_direction = grid[r][c]["direction"]

    if old_direction == "left":
        grid[r][c - 1]["value"] = value
        grid[r][c - 1]["direction"] = new_direction
        r_head, c_head = r, c - 1
    elif old_direction == "right":
        grid[r][c + 1]["value"] = value
        grid[r][c + 1]["direction"] = new_direction
        r_head, c_head = r, c + 1
    elif old_direction == "up":
        grid[r - 1][c]["value"] = value
        grid[r - 1][c]["direction"] = new_direction
        r_head, c_head = r - 1, c
    elif old_direction == "down":
        grid[r + 1][c]["value"] = value
        grid[r + 1][c]["direction"] = new_direction
        r_head, c_head = r + 1, c

    if value < length:
        new_r, new_c = find_next_seg(grid, r, c, value)
        move(grid, new_r, new_c, length, old_direction)
    else:
        grid[r][c]["value"] = EMPTY
        del grid[r][c]["direction"]

    if value == 1:
        return r_head, c_head


def found_fruit(row_fruit, col_fruit, row_head, col_head):
    if row_fruit == row_head and col_fruit == col_head:
        return True
    return False

def gen_fruit(grid):
    generate_again = True

    while generate_again:
        r = random.randint(0, 14)
        c = random.randint(0, 16)
        # Checks if fruit would be placed on empty space 
        if grid[r][c]["value"] == EMPTY:
            generate_again = False
    return r, c

def find_tail_coords(grid, row, col, length):
    value = grid[row][col]["value"]
    if value == length:
        return row, col
    
    if col + 1 < len(grid[0]) and grid[row][col + 1]["value"] == value + 1:   
        return find_tail_coords(grid, row, col + 1, length)
    elif col - 1 >= 0 and grid[row][col - 1]["value"] == value + 1:
        return find_tail_coords(grid, row, col - 1, length)
    elif row - 1 >= 0 and grid[row - 1][col]["value"] == value + 1:
        return find_tail_coords(grid, row - 1, col, length)
    elif row + 1 < len(grid) and grid[row + 1][col]["value"] == value + 1:
        return find_tail_coords(grid, row + 1, col, length)

def increase_snake_len(grid, row_tail, col_tail, snake_len):
    direction = grid[row_tail][col_tail]["direction"]
    if direction == "right":
        grid[row_tail][col_tail - 1]["value"] = snake_len + 1
        grid[row_tail][col_tail - 1]["direction"] = direction 
    elif direction == "left":
        grid[row_tail][col_tail + 1]["value"] = snake_len + 1
        grid[row_tail][col_tail + 1]["direction"] = direction 
    elif direction == "up":
        grid[row_tail + 1][col_tail]["value"] = snake_len + 1
        grid[row_tail + 1][col_tail]["direction"] = direction
    else:
        grid[row_tail - 1][col_tail]["value"] = snake_len + 1
        grid[row_tail - 1][col_tail]["direction"] = direction

# Pass in coords of snake head
def check_loss(grid, r, c):
    direction = grid[r][c]["direction"]

    if direction == "right" and (c + 1 >= len(grid[0]) or grid[r][c + 1]["value"] > SNAKE_HEAD):
        return True
    elif direction == "left" and (c - 1 < 0 or grid[r][c - 1]["value"] > SNAKE_HEAD):
        return True
    elif direction == "up" and (r - 1 < 0 or grid[r - 1][c]["value"] > SNAKE_HEAD):
        return True
    elif direction == "down" and (r + 1 >= len(grid) or grid[r + 1][c]["value"] > SNAKE_HEAD):
        return True

    return False

def draw(window, grid, square, score_txt, lost_txt, lost):
    window.fill(WHITE)
    window.blit(score_txt, (425, 5))

    square.x, square.y = 0, 25
    for row in grid:
        for tile in row:
            pygame.draw.rect(window, BLACK, square, 1)
            if tile["value"] == 1:
                pygame.draw.rect(window, ORANGE, square)
            elif tile["value"] > 1:
                pygame.draw.rect(window, GREEN, square)
            elif tile["value"] == FRUIT:
                pygame.draw.rect(window, RED, square)
            square.x += 50
        square.y += 50
        square.x = 0
    
    if lost:
        window.blit(lost_txt, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    # Initializes grid 
    grid = [[{"value" : EMPTY} for _ in range(17)] for _ in range(15)]

    # Snake
    row_head, col_head = 0, 0
    grid[row_head][col_head] = {"value": 1, "direction": "right"}
    snake_len = 1

    # Fruit 
    row_fruit, col_fruit = gen_fruit(grid)
    grid[row_fruit][col_fruit] = {"value" : FRUIT}

    # lost
    lost = False

    square = pygame.Rect(0, 0, 50, 50)
    row_tail, col_tail = row_head, col_head

    comic_sans = pygame.font.SysFont("comicsans", 15)
    lost_font = pygame.font.SysFont("comicsans", 40)
    lost_txt = lost_font.render("Good game!", True, BLUE)

    pygame.time.set_timer(MOVE_SNAKE, 200)

    while run:
        clock.tick(FPS)

        score_txt = comic_sans.render(str(snake_len), True, BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == MOVE_SNAKE:
                lost = check_loss(grid, row_head, col_head)
                if lost is False:
                    row_head, col_head = move(grid, row_head, col_head, snake_len, grid[row_head][col_head]["direction"])

            if event.type == pygame.KEYDOWN:
                key = event.key
                change_direction(key, grid, row_head, col_head)
        
        if lost is False:
            row_tail, col_tail = find_tail_coords(grid, row_head, col_head, snake_len)
            if found_fruit(row_fruit, col_fruit, row_head, col_head):
                row_fruit, col_fruit = gen_fruit(grid)
                grid[row_fruit][col_fruit]["value"] = FRUIT
                increase_snake_len(grid, row_tail, col_tail, snake_len)
                snake_len += 1
    

        draw(window, grid, square, score_txt, lost_txt, lost)
        if lost:
            run = False
            pygame.time.wait(3000)
           
if __name__ == "__main__":
    main()
    pygame.quit()   