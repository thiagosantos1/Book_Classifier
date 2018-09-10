 #!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""
Created on Sept 7

@author: thiago
""" 

# Importing the libraries
import sys
import re
from database_pre_process import *
from math import log

# Gaussian multinomial model

# read words from text, and consider just the important one(based on training)
def data_preprocess(dataset_file, lb_wrd, up_wrd,feature_words):
  broken_word = False
  splited_word = ""
  test_words = {}
  try:
    with open(dataset_file,"r") as file:
      for line in file.readlines():
        line = line.strip() # for spaces
        line = line.strip('\n') # for the new line
        line = line.lower() # put all to lower case
        # if there is a broken word from previous line
        if broken_word:
          line = splited_word + line # combine then
          broken_word = False
        words = re.split('[^A-Za-z]+',line)
        for word in words:
          if word in feature_words:
            len_word = len(word)
            if len_word >=lb_wrd and len_word<=up_wrd:
              if word not in test_words:
                test_words[word] = 1
              else:
                test_words[word] += 1

        # check for words splited at the end of line, with -
        broken_line = line.split()
        num_strings = len(broken_line)
        if num_strings >0:
          if broken_line[num_strings-1][len(broken_line[num_strings-1])-1] == '-':
            broken_word = True
            splited_word = broken_line[num_strings-1].split('-')[0]

      return test_words
  except:
    print("Erro during pre-processing sample test")
    sys.exit(1)


# get the probability of the giving book was written from author
def get_prob_author(author):
  pass

# wrd1 * log(porb_wrd1) + wrd2 * log(porb_wrd2) + ...... wrdn * log(porb_wrdn)
def classifie(feature_words,test_words):
  hig_prob = 0.0 # list with id of the author and the highest prob that the book was written from an author y
  prob_aut = 0.0 # prob the book was written for author y
  num_wrd_x = 0 # numb of times wrd x appenas in the sample book
  prob_wrd_x =0
  first_author = True
  for author in get_authors():
    for ft_wrd,id_ft in feature_words.items():
      prob_wrd_x = get_proba_word_author(author,id_ft)
      if ft_wrd in test_words and prob_wrd_x is not None: # if none, result from log X 0 is zero
        num_wrd_x = test_words[ft_wrd]
        prob_aut += num_wrd_x * (log(prob_wrd_x))
    
    if prob_aut !=0: 
      if first_author:
        hig_prob = [author,prob_aut]
        first_author = False
      elif prob_aut > hig_prob[1]:
        hig_prob = [author,prob_aut]

    prob_aut = 0.0

  return hig_prob



def predict(dataset): 

  feature_detector = (5 * get_num_books() ) + get_num_authors()
  # feature words, done over training
  feature_words = get_words_features(feature_detector)

  # colect the data, with frequence, based if the word is a feature word
  test_words = data_preprocess(dataset,5,8, feature_words)

  # based on all gaussian multinomial probabilities
  # we get a list with the author id and it's probability(the highest among all)
  y_ = classifie(feature_words,test_words)

  return y_





