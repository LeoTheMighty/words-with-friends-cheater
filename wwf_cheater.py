# import tkinter
import numpy as np
from sortedcontainers import SortedListWithKey
from itertools import permutations, product
from string import ascii_lowercase

# root = tkinter.Tk(screenName='Test screen', baseName='Test screen')
# root.mainloop()

# board is 15x15
# string value (potential values = "", "dl", "dw", "tl", "tw")
board_multiplier = [
    ["", "", "", "tw", "", "", "tl", "", "tl", "", "", "tw", "", "", ""],
    ["", "", "dl", "", "", "dw", "", "", "", "dw", "", "", "dl", "", ""],
    ["", "dl", "", "", "dl", "", "", "", "", "", "dl", "", "", "dl", ""],
    ["tw", "", "", "tl", "", "", "", "dw", "", "", "", "tl", "", "", "tw"],
    ["", "", "dl", "", "", "", "dl", "", "dl", "", "", "", "dl", "", ""],
    ["", "dw", "", "", "", "tl", "", "", "", "tl", "", "", "", "dw", ""],
    ["tl", "", "", "", "dl", "", "", "", "", "", "dl", "", "", "", "tl"],
    ["", "", "", "dw", "", "", "", "", "", "", "", "dw", "", "", ""],
    ["tl", "", "", "", "dl", "", "", "", "", "", "dl", "", "", "", "tl"],
    ["", "dw", "", "", "", "tl", "", "", "", "tl", "", "", "", "dw", ""],
    ["", "", "dl", "", "", "", "dl", "", "dl", "", "", "", "dl", "", ""],
    ["tw", "", "", "tl", "", "", "", "dw", "", "", "", "tl", "", "", "tw"],
    ["", "dl", "", "", "dl", "", "", "", "", "", "dl", "", "", "dl", ""],
    ["", "", "dl", "", "", "dw", "", "", "", "dw", "", "", "dl", "", ""],
    ["", "", "", "tw", "", "", "tl", "", "tl", "", "", "tw", "", "", ""]
]

# value of each letter
letter_points = {
    'a': 1, 'b': 4, 'c': 4,  'd': 2, 'e': 1,  'f': 4, 'g': 3,
    'h': 3, 'i': 1, 'j': 10, 'k': 5, 'l': 2,  'm': 4, 'n': 2,
    'o': 1, 'p': 4, 'q': 10, 'r': 1, 's': 1,  't': 1, 'u': 2,
    'v': 5, 'w': 4, 'x': 8,  'y': 3, 'z': 10, '?': 0
}

word_set = set()
try:
    # shortened word list (already created)
    file_word_list = open("working_word_list.txt", "r")
    for word in file_word_list:
        word_set.add(word)
except FileNotFoundError:
    # Make a new working list from the back up file
    file_word_list = open("words_with_friends_word_list.txt", "r")
    working_file = open("working_word_list.txt", "w+")
    word_list = []
    for line in file_word_list:
        length_of_word = len(line) - 1
        if length_of_word < 16:  # Word can't be fragmented so only working words
            working_file.write(line)
            word_set.add(line)

# max_length = 0
# max_word = ""
# num_too_long = 0
# total = 0
# for line in file_word_list:
    # total += 1
    # length = len(line) - 1
    # if length < 16:  # Word can't be fragmented so only working words
        # word_list.append(line)
    # else:
        # num_too_long += 1
        #    max_length = length
        #    max_word = line

# print("There are %i words that are too big out of %i" % (num_too_long, total))  # 4272 out of 173122
# print("The biggest word is %s with %i letters" % (max_word, max_length))

# SCORING RULES
# Remember that words can only be going down and right!!!
# Each word created is scored separately
# First update the values of the letters based on the "double/triple letter" spaces
# For each word, add up the values of all letters together
# Then for each letter in that word that is on a "double/triple word space" double/triple word value
# if all 7 tiles are used in that turn, then award 35 extra points


def permutations_of_length(letters, length):
    """
    Gets the permutations of the letters of length, but adds permutations of wildcards
    :param letters: The letters to create the permutations (including '?')
    :param length: The length of each permutation we want
    :return: Set of tuples of length *length* representing the permutations
    """
    # using set to avoid duplicates
    permutation_set = set(permutations(letters, length))
    # You probably want to change this to product instead, because tuples are dumb in this case
    # permutation_set = set(product(*letters, repeat=length)) TODO
    add_set = set()
    remove_list = []
    for p in permutation_set:
        if '?' in p:
            # This will store the possible letters for the wildcards to choose from
            lower_case_letter_list = []
            # get a list of indexes where the wild cards are
            wild_index_list = [i for i, ltr in enumerate(p) if ltr == '?']
            num_wild = len(wild_index_list)
            for _ in range(0, num_wild):  # Thankfully, this will only get up to 2 at most
                # Add another version of the ascii_lowercase for each new wildcard
                # (so that you can have 'aa' as wildcard choices, for instance)
                lower_case_letter_list += ascii_lowercase
            wild_card_permutation_set = set(permutations(lower_case_letter_list, num_wild))
            # Add each wild_card permutation into the whole set
            for w_p in wild_card_permutation_set:
                copy_p = list(p)  # list version of the tuple permutation
                i = 0  # the index of the wild card tuple
                for w_i in wild_index_list:
                    copy_p[w_i] = w_p[i]  # replace the tuple's '?''s with lowercase letters
                    # Can't add to the permutation_set while still iterating through it
                    add_set.add(tuple(copy_p))
                    i += 1
            # Can't add to the permutation_set while still iterating through it ya goofball
            remove_list.append(p)
    permutation_set.update(add_set)
    for p in remove_list:
        permutation_set.remove(p)
    return permutation_set


def get_n_best_moves(letters, board, n):
    """
    Finds the "n" best moves that the player can do with their letters
    :param letters: The letters that the player has currently ('?' is blank)
    :param board: The current board
    :param n: How many options you want to see
    :return: List of tuples that are (int, str, int, int) (score, word, start_row, start_column)
    The word is the main word stemming from the move (if ambiguous, goes to horizontal)
    """
    num_tiles = len(letters)
    moves = SortedListWithKey(key=lambda tup: tup[0])
    # Cache for the letter permutations
    letter_permutation_length_dict = {}
    # EXAMPLE USAGE: moves.add((160, "calculator", 1, 2)) (points, word, row, column) {pretty much y, x}

    # This is if you encounter a spot that has a letter, you can skip the spot right and down from it
    # This is going to be a set of tuples
    spots_to_skip = set()

    # iterate through all spaces on the board
    for r in range(0, 15):
        # possibly load the board row here
        # board_row = board[r]
        for c in range(0, 15):
            # board[r][c] is the space we are looking at
            # TODO PLEASE MAKE SURE MY LOGIC IS SOUND HERE
            current_board_spot = board[r][c]
            if current_board_spot != '':
                spot1 = (r + 1, c)
                spot2 = (r, c + 1)
                spots_to_skip.add(spot1)
                spots_to_skip.add(spot2)
            # If you're skipping but it still has a character in it, then you still get to skip next one
            if (r, c) in spots_to_skip:
                continue
            # run this space twice, once for horizontal letter placing and once for vertical
            horizontal = True
            for _ in range(0, 2):
                # iterate for the number of letters that you will place (1 or all of them)
                for placed_letters in range(1, num_tiles + 1):
                    # You are going to try to put down *placed_letters* amount of letters

                    # first do checks to avoid as much computation as you can :)

                    # if it's just gonna go off the board, don't do it my guy
                    if r + placed_letters > 14 or c + placed_letters > 14:
                        continue

                    # All the different permutations of how you can place your letters
                    if placed_letters in letter_permutation_length_dict:
                        letter_permutations = letter_permutation_length_dict[placed_letters]
                    else:
                        letter_permutations = permutations_of_length(letters, placed_letters)
                        letter_permutation_length_dict[placed_letters] = letter_permutations

                    # Check each potential word that you could possibly do!
                    for p in letter_permutations:
                        # TODO if the first spot has a letter, you don't need to check the spots in front of it
                        # Tuple to character for the added letters
                        added_letters = {}
                        copy_b = board.deepcopy()
                        main_word = ""
                        place_r = r
                        place_c = c
                        is_valid = True
                        is_connected = False
                        for l in p:
                            board_l = board[place_r][place_c]
                            # You still have to check to make sure that it's not going off the board
                            # Also make sure you're putting it on an empty space
                            while place_c < 15 and place_r < 15 and board_l != '':
                                # This also means that the board is definitely connected
                                is_connected = True
                                main_word += board_l
                                if horizontal:
                                    place_c += 1
                                else:
                                    place_r += 1
                            if place_r > 14 or place_c > 14:
                                is_valid = False
                                break
                            added_letters[(place_r, place_c)] = l
                            copy_b[place_r][place_c] = l
                            main_word += l
                            if horizontal:
                                place_c += 1
                            else:
                                place_r += 1
                        # If it got here because of a premature break, then this permutation isn't gonna work
                        if not is_valid:
                            continue
                        # The copy_b is updated at this point
                        # first make sure that it is connected to the board somehow
                        if not is_connected:
                            # Check perpendicularly from each added letter

                        # TODO Have a special case for the first move
                        # check to see if main_word is a valid word, then if its off shoots are valid works
                        # go to each **added letter** and make sure the perpendicular routes are words
                        # During that, check to make sure you're not counting one letter words
                        # Once it is determined valid, score it using the method specified above
                        # Then place it into the moves sorted list as (score, word, r, c)

                # switch the horiz. flag
                horizontal = False

    # TODO Absolutely check this lmao
    return list(moves[0:n])
    # maybe it's return list(moves[-n:-1])?


# char values
main_board = []
# zero the board
for _ in range(0, 15):
    line = []
    for _ in range(0, 15):
        line.append('')
    main_board.append(line)

# Usage of board: board[y][x] or board[r][c]


