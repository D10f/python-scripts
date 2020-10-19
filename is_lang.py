#!/usr/bin/python3

'''
is_lang.py - this script will evaluate an input string of text and assert if it
is a valid English

USAGE: is_lang.py text [word_percent]

TODO: Add letter by letter verification
TODO: Add support for more languages
'''

import logging

def load_dictionary(lang):

    '''Reads the contents of file which is expected to have all words from a
    language. Expects the file to be in the named as "lang_dictionary.txt".'''

    dictionary = {}
    with open(f'{lang}_dictionary.txt') as file:
        for word in file:
            dictionary[word.strip()] = None
    return dictionary


def is_english(text, word_percent=60):

    '''Evalutes if the provided text is written in English'''

    # A dictionary with over 45,000 English words
    en_dictionary = load_dictionary('en')

    # Clean up the text sample by removing non-letter characters
    not_letters = ',.; "\'?!@#$%^&*()_+=-{}[]0123456789'
    sample = text.strip(not_letters).upper().split()

    # Searches the text for words in the dictionary
    words_found = 0
    for word in sample:
        if word in en_dictionary:
            words_found += 1

    # If no words were found at all then is not English
    if words_found == 0:
        return False

    # Ratio of words in text and words matched in dictionary
    total_words = len(sample)
    confidence = (words_found / total_words) * 100

    logging.debug(f'total_words: {total_words}')
    logging.debug(f'words_found: {words_found}')
    logging.debug(f'confidence: {confidence}%')

    # If the confidence of the algorithm is greater than the minimum expected
    # for this function call it returns True
    if confidence >= word_percent:
        logging.debug('match')
        return True
    else:
        logging.debug('no match')
        return False
