 #!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""
Created on Sun Aug 30 2018

@author: thiago
""" 

# Importing the libraries
import sys
import re
from database_pre_process import *

def data_preprocess(dataset_file, lb_wrd, up_wrd):
  words_book = {}
  book = ""
  author = ""
  broken_word = False
  splited_word = ""

  book = getbook_file(dataset_file = dataset_file)  
  try:
      with open(dataset_file,"r") as file:
        start_book = False
        author = getauthor_file(dataset_file)
        for line in file.readlines():
          if not start_book:
            if re.search("^\*\*\*.*START",line):
              start_book = True
            continue
          if re.search("^\*\*\*.*END",line) or re.search("End of Project Gutenberg",line) :
            break

          line = line.strip() # for spaces
          line = line.strip('\n') # for the new line
          line = line.lower() # put all to lower case
          # if there is a broken word from previous line
          if broken_word:
            line = splited_word + line # combine then
            broken_word = False
          words = re.split('[^A-Za-z]+',line)
          for word in words:
            len_word = len(word)
            if len_word >=lb_wrd and len_word<=up_wrd:
              if word not in words_book:
                words_book[word] = 1
              else:
                words_book[word] += 1

          # check for words splited at the end of line, with -
          broken_line = line.split()
          num_strings = len(broken_line)
          if num_strings >0:
            if broken_line[num_strings-1][len(broken_line[num_strings-1])-1] == '-':
              broken_word = True
              splited_word = broken_line[num_strings-1].split('-')[0]

        return words_book,author,book
  except:
    print("Erro during pre-processing data")
    sys.exit(1)

# find out how to do this faster
def set_feature_words(min_freq):
  try: 
    authors = get_authors()
    all_words = get_all_words()
    feautes_in_database = get_idwords_features()

    # do not need to check words that is already in database
    words =[word for word in all_words if word not in feautes_in_database]


    # the idea is to compare 2 authors and find the words that most tell them apart
    # to do that we use the idea that a total freq of word x from author y must be >= than 3/2 of the freq of author z
    # and the min freq of word x in a book t of author y must be >= than the max of author x
    min_freq = 0
    max_freq = 0
    feature_detector = 3/2.0
    word_done = False
    for word in words:
      for author_x in authors:
        # do not need all calculation again for this word, it's alread a feature word
        if word_done:
          word_done = False
          break
        for author_y in authors:
          if word_done:
            break
          # this way, we do not recalculate again for all authors. Just need to find
          # feature words for the new author
          if author_x != author_y:
            # if word appears more in author x than feature_detector % than author y, it may be a feature word
            wrdx = get_total_word_x_author(author_x,word)
            wrdy = get_total_word_x_author(author_y,word)
            if wrdx is None:
              wrdx = 0
              # it should be in all authors book to be a feature
              word_done = True
              break
            if wrdy is None:
              wrdy = 0

            if wrdx < min_freq:
              # should appear at least some amount of time per book
              word_done = True
              break

            if wrdx > feature_detector * wrdy:
              # then, find the min of word x amoung books from author x
              # and find the max of word x amoung books from author y.
              first_word = True
              for book in get_books_author_x(author_x):
                if first_word:
                  first_word = False
                  min_freq = get_total_word_x_book_y(word, book) 
                  if min_freq is None:
                    min_freq = 0
                else:
                  freq_x  = get_total_word_x_book_y(word, book)
                  if freq_x is None:
                    freq_x = float('inf')
                  if freq_x < min_freq:
                    min_freq = freq_x

              first_word = True
              for book in get_books_author_x(author_y):
                if first_word:
                  first_word = False
                  max_freq = get_total_word_x_book_y(word, book)
                  if max_freq is None:
                    max_freq = 0
                else:
                  freq_x  = get_total_word_x_book_y(word, book)
                  if freq_x is None:
                    freq_x = 0
                  if freq_x > max_freq:
                    max_freq = freq_x

              # if min > max, then the word is a feature word for our model 
              if min_freq > max_freq:
                save_feature_word(word)
                word_done = True
  except:
    print("Error while saving new feautures")
    sys.exit(1)


def save_book_database(dataset): 

  # book already exists in databse
  if isBookInDatabase(getbook_file(dataset_file = dataset)  ):
    print("\nBook " + getbook_file(dataset_file = dataset) + " is already in database...\n")

  # training
  else: # read book, save in database, including the frequence of words and probabilities

    print("\nReading book and saving it to database.....")
    words_book = {}
    words_book, author, book = data_preprocess(dataset,5,8)
    if not words_book:
      print("somethig is wrong")
    save_to_data_base(words_book,author,book)
    print("Book "+ book + " from author " + author +" saved into database successfully....\n")

# it's taking a long time
def training(min_freq):
  num_authors = get_num_authors()
  if num_authors is None:
    num_authors = 0

  # has to have at least 2 authors 
  if num_authors >1:
    print("Training --> Updating important words and probabilities.....\n")

    # insert new feature words, based on that new author
    print("Saving new feature words....")
    set_feature_words(min_freq)
    print("Done saving new feature of words")

    # update table of probabilities for all authors
    clean_table("probabilities")
    for author in get_authors():
      dict_probs = get_freq_prob_author(author)
      if dict_probs is None:
        return 
      save_probs_author(author, dict_probs)

    # there is room for improvement for the model
    print("Done with Training.....\n")






