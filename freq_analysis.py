#!/usr/bin/env python3

'''
A small script that provides several utility functions to analyze a piece of
text and determine what the most (and least) frequently repeated letters are.
Frequency analysis is used among other things to break encryption ciphers that
rely on letter substitution such as the Vigenere cipher.

'ETAOIN' are the six most common letters used in the English language.

WORK IN PROCESS!
TODO: Create possible key combinations
'''

ETAOIN='ETAOINSHRDLCUMWFGYPBVKJXQZ'
LETTERS='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
MAX_KEY_LENGTH = 16

from vigenere_cipher import decrypt
from is_lang import is_english
from concurrent.futures import ProcessPoolExecutor
import itertools
import time
import pprint
import re

only_letters = re.compile(r'[^a-zA-Z]')

def main():
    # ciphertext = 'Ai seh pvxo xffbxzl elt fzghip cs yhglp xgjnfw. Ganjbrp ftwez bfjs gr lmyk awbx ulgg nqw pzwt hytu ezwylmc mirollf sd GUHEPQMHV. phv amiyg txwipgk ybpj wawh hpie rvisiqgvrg mq rdh hnjx qwajbrr ichzkfpw. Wavmilh dt hnjxrwaj, ai seh dvktitsehw eyh qsvg ulc tergx xec cw mimq pnqw, fcmcuzgh yq ozdsmyk esiypvkoafxw es ivzl eew. huh yvfwifrmjsl cs qhx dsjbubok rvr ztc jsj ijxe xm, oag wmdxpwe yssk tnql ass loem imk pbrmio ecr ttox ydcuxgteis nabx fs vv ysc xws stoh uchow hpjtok fpwr drripp. Qn tropvghr yhglpxgk hg ejz glfi lrs ap kppc abgxp.'
    # uppercased = 'AISEHPVXOXFFBXZLELTFZGHIPCSYHGLPXGJNFWGANJBRPFTWEZBFJSGRLMYKAWBXULGGNQWPZWTHYTUEZWYLMCMIROLLFSDGUHEPQMHVPHVAMIYGTXWIPGKYBPJWAWHHPIERVISIQGVRGMQRDHHNJXQWAJBRRICHZKFPWWAVMILHDTHNJXRWAJAISEHDVKTITSEHWEYHQSVGULCTERGXXECCWMIMQPNQWFCMCUZGHYQOZDSMYKESIYPVKOAFXWESIVZLEEWHUHYVFWIFRMJSLCSQHXDSJBUBOKRVRZTCJSJIJXEXMOAGWMDXPWEYSSKTNQLASSLOEMIMKPBRMIOECRTTOXYDCUXGTEISNABXFSVVYSCXWSSTOHUCHOWHPJTOKFPWRDRRIPPQNTROPVGHRYHGLPXGKHGEJZGLFILRSAPKPPCABGXP'
    # ciphertext = 'Sm nhl frpv zokshrp zox vvyoky hj izkgs bwffmy. Pfettvk ixmar ihsx xb dqtn emxp bnpl eao tuzx xulb gibpveg hlvehdm um LLRWTLPLL. lzc cvnpq lbrltwg qirs brgz lkli hrazkzlmby ql uhx dfqz zbrttvm lgxvcmrf. Brfemgk hj dfqzabrt, sm nhl trcakcxvro itk uiry bnl yvbyb shg ss epoz ueao, jxpgkvyo az tqnkqtn iieqwxttrppa zv mlvd lgf. mlr qzazmvnequu hj azb yvnrqtvm aai jlg evn yfpl zv, trq oqyatma qzut yead env peae pot usbemj hgh plvz hitepkohmi jsiz ox mf qwx aai olvj dhyyo lkmxeg xwya iibatk. Tr jngwxpmi izkgsbwg zn gse xvxm guw ql cwrl fsqpt.'
    # 'He has been through the ringer of vocal issues. Imagine being able to sing like this and lose that ability because of SHELLFISH. you would atleast fall into deep depression if not quit singing entirely. Instead of quitting, he has persevered and been the front man of this band, bringing us amazing performances to this day. the frustration of not sounding the way you used to, and distain from fans who want him booted and cant appreciate what he is for the band would defeat most people. My favorite vocalist of all time and my role model.'
    # teleportbeyond

    # BEFORE!!!
    uppercased = 'PPQCA XQVEKG YBNKMAZU YBNGBAL JON I TSZM JYIM. VRAG VOHT VRAU C TKSG. DDWUO XITLAZU VAVV RAZ C VKB QP IWPOU'
    uppercased = only_letters.sub('', uppercased)

    # List of numbers, potential key lengths
    pattern_distances = kasiski_key_lengths(uppercased)
    print(pattern_distances)

    potential_key_lengths = get_common_factors(pattern_distances)
    print(potential_key_lengths)

    interval_string = get_letter_at_interval(uppercased, 4)
    print(interval_string)

    potential_subkeys = []

    for subtext in interval_string:
        highest_subkey_score = 0
        highest_subkeys = []
        for subkey in LETTERS:
            decrypted = decrypt(subtext, subkey)
            letter_count = count_letters(decrypted)
            sorted_by_frequency = sort_by_frequency(letter_count)
            score = get_english_score(sorted_by_frequency)

            # If score is high enough add a new subkey as potential match
            if score == highest_subkey_score:
                highest_subkeys.append(subkey)

            # If score is the highest so far, current subkey takes precedence
            if score > highest_subkey_score:
                highest_subkeys = [subkey]
                highest_subkey_score = score

        potential_subkeys.extend(highest_subkeys)

    print(potential_subkeys)

    return

    for key in potential_key_lengths:
        # (big) list of strings taken at regular intervals
        interval_string = get_letter_at_interval(uppercased, key)

        # This will include all letter combinations for a potential key
        potential_subkeys = []

        # Decrypt each string using all possible letters (subkeys)
        for subtext in interval_string:
            print(subtext)
            # Keep track of each decryption attempt and the score
            highest_subkey_score = 0
            highest_subkeys = []

            for subkey in LETTERS:
                decryption_attempt = decrypt(subtext, subkey)

                # Analyze letter frequency and score each decrypted result
                letter_count = count_letters(decryption_attempt)
                sorted_by_frequency = sort_by_frequency(letter_count)
                score = get_english_score(sorted_by_frequency)
                # print(f'English probability score: {score}')

                # If score is high enough add a new subkey as potential match
                if score == highest_subkey_score:
                    highest_subkeys.append(subkey)

                # If score is the highest so far, current subkey takes precedence
                if score > highest_subkey_score:
                    highest_subkeys = [subkey]
                    highest_subkey_score = score

            # Keep only subkeys with high probability
            potential_subkeys.append(highest_subkeys)

        print(potential_subkeys)
        return

        # Finally with all possible letters found, calculate all possible
        # key combinations

        # --------------CAUTION--------------
        # Bugs ahead do not run this code yet :/

        # possible_key_combinations = itertools.product(potential_subkeys, repeat=key)
        # print(f'Trying {len(list(possible_key_combinations))} keys...')
        #
        # for key_try in possible_key_combinations:
        #     cleartext = decrypt(ciphertext, key_try)
        #     if is_english(cleartext):
        #         print('Potential key match found!')
        #         print(f'{cleartext[:100]}...')
        #         print('Continue decryption? y/n')
        #         response = input()
        #         if not response.lower().startswith('y'):
        #             print(f'Decryption key: {key_try}')
        #             print(cleartext)
        #             print('Exiting program...')
        #             sys.exit()


def count_letters(text):
    '''
    Counts the letters in a string of text and returns a dictionary with the
    number of times each letter appears in it.
    '''

    letter_frequency = {
        'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0, \
        'I': 0, 'J': 0, 'K': 0, 'L': 0, 'M': 0, 'N': 0, 'O': 0, 'P': 0, \
        'Q': 0, 'R': 0, 'S': 0, 'T': 0, 'U': 0, 'V': 0, 'W': 0, 'X': 0, \
        'Y': 0, 'Z': 0
    }
    for letter in text.upper():
        if letter in letter_frequency:
            letter_frequency[letter] += 1
    return letter_frequency


def sort_by_frequency(letter_freq):
    '''
    Takes a dictionary of 26 items representing each letter associated with a
    number, which represents the number of times it appears on a given text.

    Returns a string sorted from most frequently repeated to least.
    '''

    result = {}

    # Groupt letters by their frequency
    for k, v in letter_freq.items():
        result.setdefault(v, [])
        result[v].append(k)

    # Sort each frequency group by ETAOIN (to avoid false positives)
    for k, v in result.items():
        v = sorted(v, key=ETAOIN.find, reverse=True)
        result[k] = ''.join(v)

    # Join each group as a string, and then all groups to return final result
    result = [x[1] for x in sorted(result.items(), key=lambda x: x[0], reverse=True)]
    return ''.join(result)


def get_english_score(frequency_list):

    score = 0

    # Compare most common letters in English against most common from text
    for letter in ETAOIN[:6]:
            if letter in frequency_list[:6]:
                score += 1

    # Same with the least commons, used as well to build the confidence score
    for letter in ETAOIN[-6:]:
        if letter in frequency_list[-6:]:
            score += 1

    return score


def kasiski_key_lengths(ciphertext):
    '''
    Using the Kasiski's examination of the ciphertext we can find sequences of
    repeated patterns at specific intervals. Those intervals will be used to
    find the length of the encryption key.

    Takes a ciphertext and returns a list of numbers.
    '''

    # Remove non-letters and make uppercase
    ciphertext = only_letters.sub('', ciphertext).upper()
    print(ciphertext)

    msg_length = len(ciphertext)
    sequences = {}

    # Extract patterns at "i" intervals, of 3 letters long
    for j in range(0, msg_length):
        pattern = ciphertext[j:j+3]
        sequences.setdefault(pattern, [])
        sequences[pattern].append(j + 3)

    # Retrieve the distance between repeating patterns
    distances = []

    for sequence in sequences.values():
        # Skip patterns that dont repeat
        if len(sequence) < 2:
            continue

        # For every element, look at other elements lower than current and get
        # the difference. This provides all distance values for all matches.
        for x in sequence:
            for y in sequence:
                if y < x:
                    distances.append(x - y)

    return distances


def get_common_factors(distances):
    '''
    Takes a list of numbers representing the distance between found patterns
    in a ciphertext. This will calculate the factors of each of those numbers,
    and return those that are more likely based on how after they are repeated
    '''

    # Get factor of each pattern distances, representing a potential key length
    factors = []
    [factors.extend(find_factors(d)) for d in distances]

    # Count how often each factor number appears
    factor_count = {}
    for f in factors:
        factor_count[f] = factors.count(f)

    # Return those that are repeated most often (may be one or multiple numbers)
    most_common = max(factor_count.values())
    most_likely_factors = [k for k,v in factor_count.items() if v == most_common]

    return most_likely_factors


def find_factors(number, max=MAX_KEY_LENGTH):
    '''
    Calculates all factors for the number provided. Returns a list of all
    factors found, above 1 and up to the specified maximum.
    '''

    factors = []

    # Find all factors (above 1) for the given number.
    for idx in range(2, max + 1):
        if number % idx == 0:
            factors.append(idx)

            # We can also add as factor any number we know is valid divided by 2
            other_factors = idx // 2
            if other_factors > 1 and other_factors < max:
                factors.append(other_factors)

    # Avoid returning duplicate factors
    return set(factors)


def get_letter_at_interval(text, interval):
    '''
    Given a string of text and a number, it will return a list of strings
    containing letters at a specified interval. Starting at index 0 and repeat
    at index 1, index 2, index n...
    '''

    letters = []

    # Extract the nth letter from text starting at indexes 0, 1, 2, ...n
    for i in range(interval):

        current_index_string = []
        # Extract the nth letter from text at interval specified
        for j in range(i, len(text), interval):
            current_index_string.append(text[j])
        letters.append(''.join(current_index_string))

    return letters


if __name__ == '__main__':
    main()
