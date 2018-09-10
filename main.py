 #!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""
Created on Sept 9

@author: thiago
""" 

# program to go over all data execute the training 
# and the test, to evaluate our model

import sys
import re
from os import listdir,getcwd
from os.path import isfile, join
import pathlib
from database_pre_process import *
from training_model import training
from test_model import predict

"""
Training 
"""
def training_data(training_folder):

  current_dir = getcwd()
  training_path = current_dir + training_folder
  print(training_path)
  folders = listdir(training_path)

  for author_folder in folders:
    if author_folder != '.DS_Store' and author_folder in ('Dickens','Austen'): # for now, just to see the results from 2 authors
      path = training_path + '/' + author_folder
      books = [book for book in listdir(path) if isfile(join(path, book)) and book != '.DS_Store' ]
      
      path_book = ""

      for book in books:
        path_book = path + '/' + book

        training(path_book)

"""
Test - Classifie 
"""
def test_sample(test_data):
  pred = predict(test_data)
  return pred

def main():
  if len(sys.argv) < 2:
    print("Please provide <test sample>\n")
    sys.exit(1)


  training_folder = "/data/training"
  training_data(training_folder)

  test_data = sys.argv[1]
  pred = test_sample(test_data)

  author = get_author_name(pred[0])

  print(author)


if __name__ == '__main__':
  main()


