import argparse
import curses
import random
import time

from typing import List

DELAY_LIST = [0.003, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.3, 0.4]
DIRECTIONS = {
    "up": (-1, 0),
    "right": (0, 2),
    "down": (1, 0),
    "left": (0, -2)
}
ADJACENT_DIRECTION = {
    "up": ["left", "right", "up"],
    "down": ["left", "right", "down"],
    "left": ["up", "down", "left"],
    "right": ["up", "down", "right"],
}
COLORS = {
    "black": curses.COLOR_BLACK, "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN, "blue": curses.COLOR_BLUE,
    "yellow": curses.COLOR_YELLOW, "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_YELLOW, "white": curses.COLOR_WHITE,
}
COLOR_NAMES = ["red", "green", "blue", "yellow",
               "magenta", "cyan", "black", "white", "random"]
LEAD_COLOR_PAIR = 1
BODY_COLOR_PAIR = 2


def set_lead_color(lead_color: str) -> None:
    if lead_color == "random":
        curses.init_pair(LEAD_COLOR_PAIR, random.randint(1, curses.COLORS),
                         curses.COLOR_BLACK)
    else:
        curses.init_pair(LEAD_COLOR_PAIR, COLORS[lead_color],
                         curses.COLOR_BLACK)


def set_color(body_color: str) -> None:
    if body_color == "random":
        curses.init_pair(BODY_COLOR_PAIR, random.randint(1, curses.COLORS),
                         curses.COLOR_BLACK)
    else:
        curses.init_pair(BODY_COLOR_PAIR, COLORS[body_color],
                         curses.COLOR_BLACK)


def new_cell(head: List[int], direction: str) -> List[int]:
    dy, dx = DIRECTIONS[direction]
    new = [head[0] + dy, head[1] + dx]
    if new[0] < 0:
        new[0] = curses.LINES - 2
    elif new[0] >= curses.LINES - 1:
        new[0] = 0
    elif new[1] < 0:
        new[1] = curses.COLS - 1
    elif new[1] > curses.COLS - 1:
        new[1] = 0
    return new


def next_color(current_color: str) -> str:
    index = COLOR_NAMES.index(current_color)
    if index >= 7:
        index = 0
    else:
        index += 1
    return COLOR_NAMES[index]


def curses_main(screen, args: argparse.Namespace) -> None:
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch().
    curses.use_default_colors()
    set_color(args.color)
    set_lead_color(args.lead_color)
    delay = DELAY_LIST[args.speed]
    snake_body = []
    center_x = curses.COLS // 2
    center_y = curses.LINES // 2
    snake_body.append([
        random.randint(center_y - 5, center_y + 5),
        random.randint(center_x - 5, center_x + 5)
    ])
    new_cell_count = 0
    change_direction = 0
    direction = "down"
    run = True
    while run:
        if change_direction >= random.randint(6, 10):
            direction = random.choice(ADJACENT_DIRECTION[direction])
            change_direction = 0
        else:
            change_direction += 1
        new = new_cell(snake_body[0], direction)
        snake_body.insert(0, new)
        if new_cell_count >= random.randint(9, 16) and len(snake_body) <= 60:
            new_cell_count = 0
        else:
            snake_body.pop(len(snake_body) - 1)
            new_cell_count += 1
        screen.erase()
        for y, x in snake_body[1:]:
            screen.addstr(y, x, "X", curses.color_pair(BODY_COLOR_PAIR))
        screen.addstr(
            snake_body[0][0],
            snake_body[0][1],
            "X",
            curses.color_pair(LEAD_COLOR_PAIR) + curses.A_BOLD
        )
        screen.refresh()

        time.sleep(delay)
        ch = screen.getch()
        if ch in [81, 113]:  # q, Q
            run = False
        elif 48 <= ch <= 57:  # number keys 0 to 9
            delay = DELAY_LIST[int(chr(ch))]
        elif ch == 99:  # c
            args.color = next_color(args.color)
            set_color(args.color)
        elif ch == 108:  # l
            args.lead_color = next_color(args.lead_color)
            set_lead_color(args.lead_color)
        elif ch == 67:  # C
            args.color = "random"
            set_color(args.color)
        elif ch == 76:  # L
            args.lead_color = "random"
            set_lead_color(args.lead_color)
        elif ch == 100:  # d
            args.color = "random"
            args.lead_color = "random"
            delay = DELAY_LIST[5]
            set_color(args.color)
            set_lead_color(args.lead_color)


def positive_int_zero_to_nine(value: str) -> int:
    """
    Used with argparse.
    Checks to see if value is positive int between 0 and 10.
    """
    msg = f"{value} is an invalid positive int value 0 to 9"
    try:
        int_value = int(value)
        if int_value < 0 or int_value >= 10:
            raise argparse.ArgumentTypeError(msg)
        return int_value
    except ValueError:
        raise argparse.ArgumentTypeError(msg)


def color_type(value: str) -> str:
    """
    Used with argparse
    Checks to see if the value is a valid color and returns
    the lower case color name.
    """
    lower_value = value.lower()
    if lower_value in COLOR_NAMES:
        return lower_value
    raise argparse.ArgumentTypeError(f"{value} is an invalid color name")


def argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--color", type=color_type, default="random",
                        help="Set the color. Default random color")
    parser.add_argument("-l", "--lead_color", type=color_type, default="random",
                        help="Set the lead (head) color. Default random color")
    parser.add_argument("-s", "--speed", type=positive_int_zero_to_nine,
                        default=5,
                        help="Set the speed (delay) 0-Fast, 5-Default, 9-Slow")
    return parser.parse_args()


def main() -> None:
    args = argument_parser()
    curses.wrapper(curses_main, args)


if __name__ == "__main__":
    main()
