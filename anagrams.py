#!/usr/bin/env python3

"""
anagrams.py - Given a word, returns a list of words of anagrams for it.
"""

from collections import Counter

EN_DICITONARY = 'ciphers/utils/en_dictionary.txt'

def main():
  dictionary = load_dictionary(EN_DICITONARY)
  user_input = take_user_input('Type in a word: ')
  anagram_list = find_anagrams(dictionary, user_input)

  if len(anagram_list) == 0:
    print('No matches found!')
  else:
    print('Anagrams found:', *anagram_list, sep='\n')


def find_anagrams(list_of_words, target):
  return [w for w in list_of_words if Counter(w.lower()) == Counter(target)]


def take_user_input(prompt_text):
  res = input(prompt_text)
  while len(res) == 0:
    print('You must type at least one word')
    res = input(prompt_text)
  return res


def load_dictionary(path_to_dict):
  dictionary = []
  with open(path_to_dict) as f:
    for word in f:
      dictionary.append(word.strip())
  return dictionary


if __name__ == '__main__':
  main()