 #!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""
Created on Sun Aug 30 2018

@author: thiago
""" 

# Importing the libraries
import sys
import re
from database_process import *

def data_preprocess(dataset_file):
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
					if (line.find("*** START OF THIS PROJECT")) >=0: # skip title 
						start_book = True
						continue
					elif not start_book:
						continue

					if (line.find("*** END OF THIS PROJECT")) >=0: # skip botton
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
						if(len(word) >=5 and len(word)<=10) :
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

def main():	
	if len(sys.argv) < 2:
		print("Please provide <file>\n")
		sys.exit(1)
	
	# run scripts to create tables and others, if not exists
	init_dataBase()

	# book already exists in databse
	if isBookInDatabase(getbook_file(dataset_file = sys.argv[1])	):
		print("\nBook " + getbook_file(dataset_file = sys.argv[1]) + " is already in database...\n")

	else: # read book, save in database, including the frequence of words
		print("\nReading book and saving it to database.....")
		words_book = {}
		words_book, author, book = data_preprocess(sys.argv[1])

		save_to_data_base(words_book,author,book)
		print("Book saved into database successfully....\n")

		print("Training --> Updating probabilities.....\n")

		print("Done with Training.....\n")

if __name__ == '__main__':
	main()



