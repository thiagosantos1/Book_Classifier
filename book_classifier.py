 #!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""
Created on Sun Aug 30 2018

@author: thiago
"""

# Importing the libraries
import sys
import re

def getauthor(dataset_file):
	file = dataset_file.split('.')
	return file[0]

def getbook(line):
	try:
		line = line.strip()
		line = line.strip('\n')
		line = line.split("EBOOK")
		line = line[1].split(' ')
		return line[1]
	except:
		print("usage: {0:s} book name".format(dataset_file))
		sys.exit(1)

def data_preprocess(dataset_file):
	words_book = {}
	book = ""
	author = ""
	try:
			with open(dataset_file,"r") as file:
				start_book = False
				author = getauthor(dataset_file)
				for line in file.readlines():
					if (line.find("*** START OF THIS PROJECT")) >=0: # skip title 
						start_book = True
						book = getbook(line)
						continue
					elif not start_book:
						continue

					if (line.find("*** END OF THIS PROJECT")) >=0: # skip botton
						break

					line = line.strip() # for spaces
					line = line.strip('\n') # for the new line
					line = line.lower() # put all to lower case
					words = re.split('[^A-Za-z]+',line)
					for word in words:
						if(len(word) >=5 and len(word)<=10) :
							if word not in words_book:
								words_book[word] = 1
							else:
								words_book[word] += 1

				return words_book,author,book
	except:
		print("usage: {0:s} textfile".format(sys.argv[0]))
		sys.exit(1)

def save_to_data_base(words_book, author, book):
	
	pass

def main():	
	if len(sys.argv) < 2:
		print("Please provide <file>\n")
		sys.exit(1)
	
	words_book = {}
	words_book, author, book = data_preprocess(sys.argv[1])

	save_to_data_base(words_book,author,book)

if __name__ == '__main__':
	main()