#!/usr/bin/env python3
# chmod u+x
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
from training_model import training,save_book_database
from test_model import predict

#import matplotlib.pyplot as plt

"""
Training 
"""
def save_data(training_folder):

  current_dir = getcwd()
  training_path = current_dir + training_folder
  folders = listdir(training_path)

  for author_folder in folders:
    if author_folder != '.DS_Store': # and author_folder in ('Austen','Dickens'): # for now, just to see the results from 2 authors
      path = training_path + '/' + author_folder
      books = [book for book in listdir(path) if isfile(join(path, book)) and book != '.DS_Store' ]
      
      path_book = ""

      for book in books:
        path_book = path + '/' + book

        save_book_database(path_book)

"""
Test - Classifie 
"""
# if a folder is passed, we run the test for all test cases
# if a file, it runs the test for that file
def test_sample(file = None, folder = None):
  if file is None and folder is None:
    print("Please, provide test file or test folder")
    sys.exit(1)

  pred = []
  if file is not None:
    pred.append(predict(file))
  else:
    current_dir = getcwd()
    test_path = current_dir + folder
    folders = listdir(test_path)

    for author_folder in folders:
      if author_folder != '.DS_Store': # and author_folder in ('Austen','Dickens'): # for now, just to see the results from 2 authors
        path = test_path + '/' + author_folder
        books = [book for book in listdir(path) if isfile(join(path, book)) and book != '.DS_Store' ]
        
        path_book = ""

        for book in books:
          path_book = path + '/' + book 
          y_ = predict(path_book)
          author_ = get_author_name(y_[0])

          pred.append([author_folder.lower(),author_])

  return pred

def display_dristribution():
  feature_detector = (10 * get_num_books() ) + get_num_authors()
  freq_features = get_freq_features(feature_detector)

  # plot a distribution, to see the correlatiion
  plt.figure(figsize = (6,6))
  plt.hist(freq_features)
  plt.show()

def main():

  # run scripts to create tables and others, if not exists
  init_dataBase()

  """ ##### Training #####
  """

  training_folder = "/data/training"
  #save_data(training_folder)

  """ ##### Test #####
  """
  num_authors = get_num_authors()
  if num_authors is None:
    num_authors = 0
  if num_authors <2:
    print("Model has just one author. Please, insert more")
    sys.exit(1)

  single_test = None
  if len(sys.argv) >= 2:
    single_test = sys.argv[1]

  """
    For a test of a single file
  """
  if single_test is not None:
    test_data = sys.argv[1]
    print("\n#\t#\t#\t#\t#\t#\nTesting model with sample " + sys.argv[1]+"\n#\t#\t#\t#\t#\t#")
    pred = test_sample(file=test_data)

    author = get_author_name(pred[0][0])
    print(author)

  else:

      # after all data is saved, time for training --> Find the feature of words
    for x in(0,5,10,15,20,25,30,45,40):
      clean_table("feature_words")
      print("Training for min freq of " + str(x))
      training(x) 

      """
        For a test of all test files in the test bataset
      """
      test_folder = "/data/test"
      print("\n#\t#\t#\t#\t#\t#\t#\t#\t#\nTesting model with all test cases in the dataset "+test_folder+"\n#\t#\t#\t#\t#\t#\t#\t#\t#")
      # get all predictions
      pred = test_sample(folder=test_folder) 
      print(pred)
      # calculate our matrix consution, with [correct outputs, wrong outputs]
      matrix_confusion = [0,0]
      for output in pred:
        correct = False
        names = re.split('[^A-Za-z]+',output[0])
        for name in names:
          if output[1].find(name.lower()) >=0:
            matrix_confusion[0] +=1
            correct = True
            break

        if not correct:
          matrix_confusion[1] +=1
      

      print("\nThe accurancy of this model is "+ str( (matrix_confusion[0]/(matrix_confusion[0] + matrix_confusion[1]))*100) +' %\n' )

  #display_dristribution()


if __name__ == '__main__':
  main()


