import os
import pickle
import random
from math import sqrt, log
import neat
import pygame

# TODO: Make a "Play Human" global.
#  [] Use a "feedforward-default" file, and load
#  in the generation size automatically.
#  [] Add additional info to the GUI
#  Are boards winning for tying? I don't get it...

generation = 0

BLACK = (0, 0, 0)
GREY_1 = (64, 64, 64)
GREY_2 = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (198, 79, 79)
YELLOW = (211, 205, 91)

pygame.font.init()
COMIC_SANS = pygame.font.SysFont('Comic Sans MS', 30)

X_COLOR = RED
O_COLOR = YELLOW

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_MARGIN = 16
INNER_BOARD_MARGIN = 8
BOARD_LINE_WIDTH = 8
PIECE_THICKNESS = 16
SQUARE_WIDTH = ((SCREEN_WIDTH - (2 * SCREEN_MARGIN) - (2 * BOARD_LINE_WIDTH))
                / 3)
SQUARE_HEIGHT = ((SCREEN_HEIGHT - (2 * SCREEN_MARGIN) - (2 * BOARD_LINE_WIDTH))
                 / 3)
PIECE_WIDTH = SQUARE_WIDTH - (2 * INNER_BOARD_MARGIN)
PIECE_HEIGHT = SQUARE_HEIGHT - (2 * INNER_BOARD_MARGIN)
NUM_SQUARES = 9


def draw_board_squares(square_pygame, square_screen):
    if True:
        for loc in range(NUM_SQUARES):
            x_loc = loc % 3
            y_loc = loc // 3
            x_coord = SCREEN_MARGIN + (
                    x_loc * (BOARD_LINE_WIDTH + SQUARE_WIDTH))
            y_coord = SCREEN_MARGIN + (
                    y_loc * (BOARD_LINE_WIDTH + SQUARE_HEIGHT))
            square_pygame.draw.rect(square_screen, GREY_1,
                                    square_pygame.Rect(x_coord,
                                                       y_coord,
                                                       SQUARE_WIDTH,
                                                       SQUARE_HEIGHT))
            x = SCREEN_MARGIN + INNER_BOARD_MARGIN + (
                    x_loc * (SQUARE_WIDTH + BOARD_LINE_WIDTH))
            y = SCREEN_MARGIN + INNER_BOARD_MARGIN + (
                    y_loc * (SQUARE_WIDTH + BOARD_LINE_WIDTH))
            square_pygame.draw.rect(square_screen, GREY_2,
                                    square_pygame.Rect(x, y, PIECE_WIDTH,
                                                       PIECE_HEIGHT))


def draw_grid(board_pygame, board_screen):
    # Draw horizontal lines
    x = SCREEN_MARGIN + SQUARE_WIDTH
    y = SCREEN_MARGIN
    board_line_length = SCREEN_HEIGHT - (SCREEN_MARGIN * 2)
    board_pygame.draw.rect(board_screen, WHITE,
                           board_pygame.Rect(x, y, BOARD_LINE_WIDTH,
                                             board_line_length))

    x += SQUARE_WIDTH + BOARD_LINE_WIDTH
    board_pygame.draw.rect(board_screen, WHITE,
                           board_pygame.Rect(x, y, BOARD_LINE_WIDTH,
                                             board_line_length))

    board_line_length = SCREEN_WIDTH - (SCREEN_MARGIN * 2)
    x = SCREEN_MARGIN
    y = SCREEN_MARGIN + SQUARE_HEIGHT
    board_pygame.draw.rect(board_screen, WHITE,
                           board_pygame.Rect(x, y, board_line_length,
                                             BOARD_LINE_WIDTH))

    y += SQUARE_HEIGHT + BOARD_LINE_WIDTH
    board_pygame.draw.rect(board_screen, WHITE,
                           board_pygame.Rect(x, y, board_line_length,
                                             BOARD_LINE_WIDTH))


def draw_X(x_pygame, x_screen, loc):
    x, y = calc_top_left(loc)

    offset = sqrt((PIECE_THICKNESS ** 2) / 2)
    points = [(x + offset, y),
              (x, y + offset),
              (x + PIECE_WIDTH - offset, y + PIECE_HEIGHT),
              (x + PIECE_WIDTH, y + PIECE_HEIGHT - offset)]
    x_pygame.draw.polygon(x_screen, X_COLOR, points)
    points = [(x + PIECE_WIDTH - offset, y),
              (x + PIECE_WIDTH, y + offset),
              (x + offset, y + PIECE_HEIGHT),
              (x, y + PIECE_HEIGHT - offset)]
    x_pygame.draw.polygon(x_screen, X_COLOR, points)


def draw_O(o_pygame, o_screen, loc):
    x, y = calc_top_left(loc)

    radius = (PIECE_WIDTH / 2)
    x += radius
    y += radius
    o_pygame.draw.circle(o_screen, YELLOW, (x, y), radius)

    small_radius = radius - PIECE_THICKNESS
    o_pygame.draw.circle(o_screen, BLACK, (x, y), small_radius)


def find_space(mouse_pos):
    x = mouse_pos[0]
    y = mouse_pos[1]

    top_lefts = [calc_top_left(i) for i in range(NUM_SQUARES)]
    bottom_rights = [calc_bottom_right(i) for i in range(NUM_SQUARES)]

    for tl, br in zip(top_lefts, bottom_rights):
        if tl[0] < x < br[0] and tl[1] < y < br[1]:
            return top_lefts.index(tl)
    return -1


def calc_top_left(loc):
    x = SCREEN_MARGIN + INNER_BOARD_MARGIN + (
            loc % 3 * (SQUARE_WIDTH + BOARD_LINE_WIDTH))
    y = SCREEN_MARGIN + INNER_BOARD_MARGIN + (
            loc // 3 * (SQUARE_WIDTH + BOARD_LINE_WIDTH))
    return x, y


def calc_bottom_right(loc):
    x, y = calc_top_left(loc)
    return x + PIECE_WIDTH, y + PIECE_HEIGHT


def draw_everything(everything_pygame, everything_screen):
    draw_grid(everything_pygame, everything_screen)
    draw_board_squares(everything_pygame, everything_screen)
    for i in range(NUM_SQUARES):
        draw_O(everything_pygame, everything_screen, i)
        draw_X(everything_pygame, everything_screen, i)


def draw_board(board_pygame, board_screen, board_list):
    for i in range(len(board_list)):
        if board_list[i] == 0:
            draw_X(board_pygame, board_screen, i)
        elif board_list[i] == 1:
            draw_O(board_pygame, board_screen, i)
    return


def check_winner(board):
    winning_combos = [[0, 1, 2],
                      [3, 4, 5],
                      [6, 7, 8],
                      [0, 3, 6],
                      [1, 4, 7],
                      [2, 5, 8],
                      [0, 4, 8],
                      [2, 4, 6]]
    for combo in winning_combos:
        values = [board[i] for i in combo]
        if -1 not in values and values[1:] == values[:-1]:
            return True
    return False


def display_winner(winner_pygame, winner_screen, winner_winner):
    width = SCREEN_WIDTH * .8
    height = SCREEN_HEIGHT * .2
    center = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
    coord = center[0] - width / 2, center[1] - height / 2
    winner_pygame.draw.rect(winner_screen, WHITE,
                            winner_pygame.Rect(coord[0], coord[1], width,
                                               height))

    # apply it to text on a label
    if winner_winner != -1:
        winner_text = f"Player {winner_winner + 1} is the winner!"
    else:
        winner_text = f"CAT!"
    label = COMIC_SANS.render(winner_text, True, BLACK)
    # put the label object on the screen at point x=100, y=100
    winner_screen.blit(label, (coord[0] + 20, center[1]))


def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    players and sets their fitness based their # wins
    (Let's just do a round robin)
    """

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        ge.append(genome)
    players = [{"genome": genome, "net": net} for genome, net in zip(ge, nets)]
    # print(players)
    game_logic(players)


def game_logic(players):
    pygame.init()
    # Initialize pygame
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    games = create_normal_tourney(players)
    current_game = None
    winner_list = []

    is_running = True
    current_player = "p1"
    game_over_countdown = -1
    is_game_start = True
    board_spaces = []
    is_generation_over = False

    while is_running:
        # Event checkers
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            # if event.type == pygame.MOUSEBUTTONUP:
            #     space_index = find_space(pygame.mouse.get_pos())
            #     if space_index != -1 and board_spaces[space_index] == -1:
            #         board_spaces[space_index] = current_player
            #         current_player = (current_player + 1) % 2

        # Reset board if part of new game
        if is_game_start:
            # Reset visual board
            screen.fill(BLACK)
            draw_grid(pygame, screen)

            # Reset logic
            board_spaces = [-1] * NUM_SQUARES
            current_player = "p1"
            is_game_start = False
            game_over_countdown = -1

            # Pull a new generation
            if len(games) != 0:
                current_game = games.pop()
            elif len(winner_list) != 0 and len(winner_list) != 1:
                games = create_normal_tourney(winner_list)
                current_game = games.pop()
                winner_list = []
            else:
                is_running = False
                is_generation_over = True
                break

        # If generation is over
        if is_generation_over:
            break
        # if game is still going
        elif game_over_countdown == -1:
            # Give the ai the current board

            info = board_spaces[:]
            info.insert(0, get_player_num(current_player))

            net = current_game[current_player]["net"]
            results = net.activate(tuple(info))
            indexed_results = [[i, r] for i, r in enumerate(results)]
            indexed_results.sort(key=sort_func, reverse=True)
            for i, results in enumerate(indexed_results):
                # Pick first valid output
                if board_spaces[results[0]] == -1:
                    board_spaces[results[0]] = get_player_num(current_player)
                    # If the hightest output *is* valid, give a little treat
                    if i == 0:
                        current_game[current_player]["genome"].fitness += .1
                    break
            current_player = get_other_player(current_player)

            draw_board(pygame, screen, board_spaces)
            # See if someone won
            if check_winner(board_spaces):
                # Flip the player back
                current_player = get_other_player(current_player)
                winner = get_player_num(current_player)
                current_game[current_player]["genome"].fitness += 10
                winner_list.append(current_game[current_player])
                display_winner(pygame, screen, winner)
                game_over_countdown = 2
            # Or tied
            elif -1 not in board_spaces:
                # Tie!
                winner = -1
                display_winner(pygame, screen, winner)
                current_game[current_player]["genome"].fitness += 3
                # winner_list.append(current_game[current_player])
                current_game[get_other_player(current_player)][
                    "genome"].fitness += 3
                # winner_list.append(current_game[get_other_player(current_player)])

                game_over_countdown = 2
        # If game and coutndown are over
        elif game_over_countdown == 0:
            is_game_start = not is_game_start
            # is_running = False
            # break
        # If game is over but countdown is not
        else:
            game_over_countdown -= 1

        # Refresh visuals
        pygame.display.flip()
        # clock.tick(4)

    global generation
    players.sort(reverse=True, key=fitness_sorter)
    pickle.dump(players[0]["net"],
                open(f"pickles/best{generation}.pickle", "wb"))
    generation += 1


def game_vs_ai():
    pygame.init()
    # Initialize pygame
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    is_running = True
    current_player = get_rand_player()
    game_over_countdown = -1
    is_game_start = True
    board_spaces = []

    # Load in network
    pickle_file = open("pickles/best49.pickle", "rb")
    net = pickle.load(pickle_file)
    while is_running:
        # Event checkers
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.MOUSEBUTTONUP:
                space_index = find_space(pygame.mouse.get_pos())
                if space_index != -1 and board_spaces[space_index] == -1:
                    board_spaces[space_index] = get_player_num(current_player)
                    current_player = get_other_player(current_player)

        # Reset board if part of new game
        if is_game_start:
            # Reset visual board
            screen.fill(BLACK)
            draw_grid(pygame, screen)

            # Reset logic
            board_spaces = [-1] * NUM_SQUARES
            current_player = get_rand_player()
            is_game_start = False
            game_over_countdown = -1
        # if game is still going
        elif game_over_countdown == -1:
            # Let the AI play
            if current_player == "p1":
                info = board_spaces[:]
                info.insert(0, get_player_num(current_player))
                results = net.activate(tuple(info))

                indexed_results = [[i, r] for i, r in enumerate(results)]
                indexed_results.sort(key=sort_func, reverse=True)
                for i, results in enumerate(indexed_results):
                    # Pick first valid output
                    if board_spaces[results[0]] == -1:
                        board_spaces[results[0]] = get_player_num(
                            current_player)
                        break
                current_player = get_other_player(current_player)

            draw_board(pygame, screen, board_spaces)
            # See if someone won
            if check_winner(board_spaces):
                # Flip the player back
                current_player = get_other_player(current_player)
                winner = get_player_num(current_player)
                display_winner(pygame, screen, winner)

                game_over_countdown = 180
            # Or tied
            elif -1 not in board_spaces:
                # Tie!
                winner = -1
                display_winner(pygame, screen, winner)

                game_over_countdown = 180
        # If game and coutndown are over
        elif game_over_countdown == 0:
            is_game_start = not is_game_start
        # If game is over but countdown is not
        else:
            game_over_countdown -= 1

        # Refresh visuals
        pygame.display.flip()
        clock.tick(60)


def fitness_sorter(o):
    return o["genome"].fitness


def get_other_player(player_str):
    if player_str == "p1":
        return "p2"
    elif player_str == "p2":
        return "p1"
    else:
        Exception("get_other_player: Exception raised")


def sort_func(o):
    return o[1]


def get_player_num(p):
    if p == "p1":
        return 0
    elif p == "p2":
        return 1
    else:
        Exception("num_player: Exception raised")


def get_rand_player():
    if bool(random.getrandbits(1)):
        return "p1"
    else:
        return "p2"


def create_round_robin_tourney(player_list):
    # Creates a "round robin" sort of deal
    tourney_list = []
    for i in range(len(player_list)):
        for j in range(i + 1, len(player_list)):
            if bool(random.getrandbits(1)):
                tourney_list.append(
                    {"p1": player_list[i], "p2": player_list[j]})
            else:
                tourney_list.append(
                    {"p1": player_list[j], "p2": player_list[i]})
    return tourney_list


def create_normal_tourney(player_list):
    # Sorts by most fit, and limits to a power of 2
    player_list.sort(reverse=True, key=fitness_sorter)
    if not len(player_list) % 2 == 0:
        player_list.pop()

    # Shuffles remaining players and puts them in new brackets
    random.shuffle(player_list)
    p1s = player_list[::2]
    p2s = player_list[1::2]
    return [{"p1": p1, "p2": p2}
            for p1, p2 in zip(p1s, p2s)]


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    play_ai = True
    if play_ai:
        game_vs_ai()
    else:
        run(config_path)
