# import tkinter
from sortedcontainers import SortedListWithKey
from itertools import permutations, product
from string import ascii_lowercase
from math import ceil

# root = tkinter.Tk(screenName='Test screen', baseName='Test screen')
# root.mainloop()

# board is 15x15
# string value (potential values = " ", "dl", "dw", "tl", "tw")
# TODO FIX THIS TO WORK WITH THE FUCKIANGIN FACEBOOK VERSION
web_board_multiplier = [
    [" ", " ", " ", "tw", " ", " ", "tl", " ", "tl", " ", " ", "tw", " ", " ", " "],
    [" ", " ", "dl", " ", " ", "dw", " ", " ", " ", "dw", " ", " ", "dl", " ", " "],
    [" ", "dl", " ", " ", "dl", " ", " ", " ", " ", " ", "dl", " ", " ", "dl", " "],
    ["tw", " ", " ", "tl", " ", " ", " ", "dw", " ", " ", " ", "tl", " ", " ", "tw"],
    [" ", " ", "dl", " ", " ", " ", "dl", " ", "dl", " ", " ", " ", "dl", " ", " "],
    [" ", "dw", " ", " ", " ", "tl", " ", " ", " ", "tl", " ", " ", " ", "dw", " "],
    ["tl", " ", " ", " ", "dl", " ", " ", " ", " ", " ", "dl", " ", " ", " ", "tl"],
    [" ", " ", " ", "dw", " ", " ", " ", " ", " ", " ", " ", "dw", " ", " ", " "],
    ["tl", " ", " ", " ", "dl", " ", " ", " ", " ", " ", "dl", " ", " ", " ", "tl"],
    [" ", "dw", " ", " ", " ", "tl", " ", " ", " ", "tl", " ", " ", " ", "dw", " "],
    [" ", " ", "dl", " ", " ", " ", "dl", " ", "dl", " ", " ", " ", "dl", " ", " "],
    ["tw", " ", " ", "tl", " ", " ", " ", "dw", " ", " ", " ", "tl", " ", " ", "tw"],
    [" ", "dl", " ", " ", "dl", " ", " ", " ", " ", " ", "dl", " ", " ", "dl", " "],
    [" ", " ", "dl", " ", " ", "dw", " ", " ", " ", "dw", " ", " ", "dl", " ", " "],
    [" ", " ", " ", "tw", " ", " ", "tl", " ", "tl", " ", " ", "tw", " ", " ", " "]
]

facebook_board_multiplier = [
    ["tl", " ", "tw", " ", " ", " ", " ", " ", "tw", " ", "tl"],
    [" ", "dw", " ", " ", " ", "dw", " ", " ", " ", "dw", " "],
    ["tw", " ", "tl", " ", "dl", " ", "dl", " ", "tl", " ", "tw"],
    [" ", " ", " ", "tl", " ", " ", " ", "tl", " ", " ", " "],
    [" ", " ", "dl", " ", " ", " ", " ", " ", "dl", " ", " "],
    [" ", "dw", " ", " ", " ", " ", " ", " ", " ", "dw", " "],
    [" ", " ", "dl", " ", " ", " ", " ", " ", "dl", " ", " "],
    [" ", " ", " ", "tl", " ", " ", " ", "tl", " ", " ", " "],
    ["tw", " ", "tl", " ", "dl", " ", "dl", " ", "tl", " ", "tw"],
    [" ", "dw", " ", " ", " ", "dw", " ", " ", " ", "dw", " "],
    ["tl", " ", "tw", " ", " ", " ", " ", " ", "tw", " ", "tl"]
]

# value of each letter
letter_points = {
    'a': 1, 'b': 4, 'c': 4,  'd': 2, 'e': 1,  'f': 4, 'g': 3,
    'h': 3, 'i': 1, 'j': 10, 'k': 5, 'l': 2,  'm': 4, 'n': 2,
    'o': 1, 'p': 4, 'q': 10, 'r': 1, 's': 1,  't': 1, 'u': 2,
    'v': 5, 'w': 4, 'x': 8,  'y': 3, 'z': 10, '?': 0
}
# USAGE letter_points['a']

word_set = set()
try:
    # shortened word list (already created)
    file_word_list = open("working_word_list.txt", "r")
    for set_word in file_word_list:
        set_word = set_word.rstrip()
        word_set.add(set_word)
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
# max_word = " "
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
    # permutation_set = set(permutations(letters, length))
    permutation_set = set([''.join(p) for p in permutations(letters, length)])
    # You probably want to change this to product instead, because tuples are dumb in this case
    # p = product(*letters, repeat=length)
    # li = list(p)
    # permutation_set = set(li)
    # permutation_set = set(list(product(*letters, repeat=length)))
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


def clear_board(board, added_letters):
    for added_r, added_c in added_letters:
        board[added_r][added_c] = " "


def get_n_best_moves(letters, board, n):
    """
    Finds the "n" best moves that the player can do with their letters
    :param letters: The letters that the player has currently ('?' is blank)
    :param board: The current board
    :param n: How many options you want to see
    :return: List of tuples that are (int, str, int, int, bool) (score, word, start_row, start_column, horizontal)
    The word is the main word stemming from the move (if ambiguous, goes to horizontal)
    """
    # TODO Find out if the board is empty
    is_empty = all(all(value == " " for value in li) for li in board)
    # print("aa" in word_set)
    board_dimension = len(board)
    middle = ceil(board_dimension / 2) - 1
    board_multiplier = [[]]
    if board_dimension == 11:
        board_multiplier = facebook_board_multiplier
    elif board_dimension == 15:
        board_multiplier = web_board_multiplier
    num_tiles = len(letters)
    # (int, str, int, int, bool) (score, word, start_row, start_column, horizontal)
    moves = SortedListWithKey(key=lambda tup: tup[0])
    # Cache for the letter permutations
    letter_permutation_length_dict = {}
    # EXAMPLE USAGE: moves.add((160, "calculator", 1, 2)) (points, word, row, column) {pretty much y, x}

    # This is if you encounter a spot that has a letter, you can skip the spot right and down from it
    # This is going to be a set of tuples
    spots_to_skip = set()

    # iterate through all spaces on the board
    for r in range(0, board_dimension):
        # possibly load the board row here
        # board_row = board[r]
        for c in range(0, board_dimension):
            print("On square [%i, %i]" % (c, r))
            # board[r][c] is the space we are looking at
            # TODO PLEASE MAKE SURE MY LOGIC IS SOUND HERE
            current_board_spot = board[r][c]
            if current_board_spot != " ":
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
                        # Tuple of position to character for the added letters
                        added_letters = {}
                        # The tuple of positions for the beginnings of the offshoot words
                        offshoot_words = []
                        score = 0  # This is the total score for the move
                        # copy_b = copy.deepcopy(board)
                        main_word = ''
                        place_r = r
                        place_c = c
                        is_valid = True
                        is_connected = False
                        # TODO Use this loop to also score the main word
                        # Wherever a letter is added to main_word, more points can be added to score
                        multiplier = 1
                        letter_score = 0
                        for l in p:
                            # TODO This for-loop is poorly constructed for not getting out of range!!!!!!
                            # TODO This is sometimes out of range
                            # You still have to check to make sure that it's not going off the board
                            # Also make sure you're putting it on an empty space
                            while place_c < board_dimension and place_r < board_dimension and board[place_r][place_c] != " ":
                                # This also means that the board is definitely connected
                                is_connected = True
                                board_l = board[place_r][place_c]
                                main_word += board_l
                                # If it's the first turn, being in the middle will also connect it
                                if is_empty and place_r == middle and place_c == middle:
                                    is_connected = True
                                # Add to the scoring
                                # If we're here, we ignore the board multipliers because they were already used
                                letter_score += letter_points[board_l]
                                # Continue iterating through
                                if horizontal:
                                    place_c += 1
                                else:
                                    place_r += 1
                            if place_r > board_dimension - 1 or place_c > board_dimension - 1:
                                is_valid = False
                                break
                            added_letters[(place_r, place_c)] = l
                            board[place_r][place_c] = l
                            main_word += l
                            # Add to the scoring
                            if is_empty and place_r == middle and place_c == middle:
                                is_connected = True
                            multiplier_space = board_multiplier[place_r][place_c]
                            if multiplier_space == "dl":
                                letter_score += 2 * letter_points[l]
                            elif multiplier_space == "tl":
                                letter_score += 3 * letter_points[l]
                            else:
                                letter_score += letter_points[l]
                                if multiplier_space == "dw":
                                    multiplier *= 2
                                elif multiplier_space == "tw":
                                    multiplier *= 3
                            # Continue iterating through
                            if horizontal:
                                place_c += 1
                            else:
                                place_r += 1
                        # TODO Now update the score, word is fully processed
                        score += (letter_score * multiplier)
                        # If it got here because of a premature break, then this permutation isn't gonna work
                        if not is_valid:
                            clear_board(board, added_letters)
                            continue
                        # The copy_b is updated at this point
                        # first make sure that it is connected to the board somehow
                        if not is_connected:
                            # Check perpendicularly from each added letter
                            # You can also use this code to track down which offshoots are words
                            for add_r, add_c in added_letters:
                                if horizontal:
                                    # Then you look along the column
                                    if add_r - 1 >= 0 and board[add_r - 1][add_c] != " ":
                                        # There is proof that this word is connected
                                        is_connected = True
                                        # Then try to find the beginning of the offshoot word!
                                        word_r = add_r - 1
                                        while word_r - 1 >= 0 and board[word_r - 1][add_c] != " ":
                                            word_r -= 1
                                        # At this point, `(word_r - 1, add_c)` is an empty/invalid spot
                                        # Thus, `(word_r, add_c)` is the start of the offshoot word
                                        offshoot_words.append((word_r, add_c))
                                        # continue
                                    # If there was an offshoot word before it, the "offshoot" after it doesn't count
                                    elif add_r + 1 < board_dimension and board[add_r + 1][add_c] != " ":
                                        # There is proof that this word is connected
                                        is_connected = True
                                        # Then you know that `(add_r, add_c)` is the position to add to offshoot
                                        offshoot_words.append((add_r, add_c))
                                        # continue
                                else:
                                    # Then you look along the row
                                    if add_c - 1 >= 0 and board[add_r][add_c - 1] != " ":
                                        # There is proof that this word is connected
                                        is_connected = True
                                        # Then try to find the beginning of the offshoot word!
                                        word_c = add_c - 1
                                        while word_c - 1 >= 0 and board[add_r][word_c - 1] != " ":
                                            word_c -= 1
                                        # At this point, `(add_r, word_c - 1)` is an empty/invalid spot
                                        # Thus, `(add_r, word_c)` is the start of the offshoot word
                                        offshoot_words.append((add_r, word_c))
                                        # continue
                                    elif add_c + 1 < board_dimension and board[add_r][add_c + 1] != " ":
                                        # There is proof that this word is connected
                                        is_connected = True
                                        # Then you know that `(add_r, add_c)` is the position to add to offshoot
                                        offshoot_words.append((add_r, add_c))
                                        # continue

                            if not is_connected:
                                # this is still not connected, this won't work
                                clear_board(board, added_letters)
                                continue

                        # TODO Have a special case for the first move
                        # check to see if main_word is a valid word, then if its off shoots are valid works
                        # go to each **added letter** and make sure the perpendicular routes are words
                        # During that, check to make sure you're not counting one letter words
                        # Once it is determined valid, score it using the method specified above
                        # Then place it into the moves sorted list as (score, word, r, c)

                        if main_word not in word_set:
                            # not a usable word, continue
                            clear_board(board, added_letters)
                            continue
                        # check all of the offshoot words now
                        is_valid = True
                        # TODO Use this to also score all of the offshoot words
                        for word_r, word_c in offshoot_words:
                            # Construct the word one letter at a time
                            multiplier = 1
                            letter_score = 0
                            offshoot_word = board[word_r][word_c]
                            # For scoring, only the letter that is in added letters counts for the multiplier
                            if (word_r, word_c) in added_letters:
                                multiplier_space = board_multiplier[word_r][word_c]
                                if multiplier_space == "dl":
                                    letter_score += 2 * letter_points[offshoot_word]
                                elif multiplier_space == "tl":
                                    letter_score += 3 * letter_points[offshoot_word]
                                else:
                                    letter_score += letter_points[offshoot_word]
                                    if multiplier_space == "dw":
                                        multiplier *= 2
                                    elif multiplier_space == "tw":
                                        multiplier *= 3
                            else:
                                letter_score += letter_points[offshoot_word]

                            # Look at the rest of the letters
                            if horizontal:
                                # Then look along the column
                                word_change_r = word_r
                                while word_change_r + 1 < board_dimension and board[word_change_r + 1][word_c] != " ":
                                    offshoot_l = board[word_change_r + 1][word_c]
                                    offshoot_word += offshoot_l
                                    word_change_r += 1
                                    if (word_change_r, word_c) in added_letters:
                                        multiplier_space = board_multiplier[word_change_r][word_c]
                                        if multiplier_space == "dl":
                                            letter_score += 2 * letter_points[offshoot_l]
                                        elif multiplier_space == "tl":
                                            letter_score += 3 * letter_points[offshoot_l]
                                        else:
                                            letter_score += letter_points[offshoot_l]
                                            if multiplier_space == "dw":
                                                multiplier *= 2
                                            elif multiplier_space == "tw":
                                                multiplier *= 3
                                    else:
                                        letter_score += letter_points[offshoot_l]
                            else:
                                # Then look along the row
                                word_change_c = word_c
                                while word_change_c + 1 < board_dimension and board[word_r][word_change_c + 1] != " ":
                                    offshoot_l = board[word_r][word_change_c + 1]
                                    offshoot_word += offshoot_l
                                    word_change_c += 1
                                    if (word_r, word_change_c) in added_letters:
                                        multiplier_space = board_multiplier[word_r][word_change_c]
                                        if multiplier_space == "dl":
                                            letter_score += 2 * letter_points[offshoot_l]
                                        elif multiplier_space == "tl":
                                            letter_score += 3 * letter_points[offshoot_l]
                                        else:
                                            letter_score += letter_points[offshoot_l]
                                            if multiplier_space == "dw":
                                                multiplier *= 2
                                            elif multiplier_space == "tw":
                                                multiplier *= 3
                                    else:
                                        letter_score += letter_points[offshoot_l]
                            # Then the offshoot word will be complete
                            score += letter_score * multiplier
                            # Score it and then check if it's in the word_set
                            if offshoot_word not in word_set:
                                is_valid = False
                                break
                        if not is_valid:
                            # an offshoot wasn't in the set, so continue
                            clear_board(board, added_letters)
                            continue
                        # Now we know that all of the offshoot words are legit
                        # Now we score the move
                        # The total word positions are in `(r, c)` and `offshoot_words`
                        # Psych, I've already scored the move as well
                        # Last extra adding points thing
                        if placed_letters == 7:
                            score += 35
                        # Now if it got here, add it to the list of moves
                        # (int, str, int, int, bool) (score, word, start_row, start_column, horizontal)
                        # moves.append((score, main_word, r, c, horizontal))
                        moves.add((score, main_word, r, c, horizontal))
                        print("Added %s" % main_word)
                        # TODO Reset board to original state by removing added letters
                        clear_board(board, added_letters)

                # switch the horiz. flag
                horizontal = False

    # TODO Absolutely check this lmao
    print(moves)
    #return list(moves[0:n+1])
    return list(moves[-n:])
    # maybe it's return list(moves[-n:-1])?


# char values
# FACEBOOK is 11, regular is 15
board_dimension_for_the_real_board = 11
main_board = []
# zero the board
for _ in range(0, board_dimension_for_the_real_board):
    line = []
    for _ in range(0, board_dimension_for_the_real_board):
        line.append(" ")
    main_board.append(line)

# Usage of board: board[y][x] or board[r][c]

cleared_board = [
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
]

main_board = [
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "v"],
    [" ", " ", " ", " ", " ", "o", "n", "e", " ", "f", "e"],
    [" ", " ", " ", " ", " ", " ", "a", "m", "b", "e", "r"],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", "t", "a"],
    [" ", " ", " ", " ", " ", " ", " ", " ", "j", "a", " "],
    [" ", " ", " ", " ", " ", "h", "a", "d", "a", "l", " "],
    [" ", " ", " ", " ", " ", " ", "l", "e", "g", " ", " "],
    [" ", " ", " ", " ", " ", "d", "e", "r", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
]

best_moves = get_n_best_moves("qszutyc", main_board, 5)
print(best_moves)


