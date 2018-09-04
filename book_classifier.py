 #!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""
Created on Sun Aug 30 2018

@author: thiago
"""

# Importing the libraries
import sys
import re
import sqlite3

def getauthor(dataset_file):

	out = ""
	try:
		with open(dataset_file,"r") as file:
			for line in file.readlines():
				if (line.find("Author:")) >=0: # skip title 
					line = line.strip()
					line = line.strip('\n')
					line = line.split("Author:")
					line = line[1].split()
					if len(line) ==1:
						out =  line[0].strip().lower()
					elif len(line) >1:
						out =  line[0].strip().lower() + "_" + line[1].strip().lower()
					else:
						print("Missing Author's name in file")
						sys.exit(1)
					break
	except:
		print("usage: {0:s} book name".format(dataset_file))
		sys.exit(1)

	return out

def getbook(dataset_file = None, header_file = None):

	if dataset_file == None and header_file == None:
		print("Need a file or the header of file to get book's name")
		sys.exit(1)

	out = ""
	if header_file is not None:
		try:
			header_file = header_file.strip()
			header_file = header_file.strip('\n')
			header_file = header_file.split("Title:")
			header_file = header_file[1].split()
			out =  header_file[0].strip().lower()
		except:
			print("usage: {0:s} book name".format(dataset_file))
			sys.exit(1)

	elif dataset_file is not None:
		try:
			with open(dataset_file,"r") as file:
				for line in file.readlines():
					if (line.find("Title:")) >=0: # skip title 
						out = getbook(header_file = line)
						continue
		except:
			print("usage: {0:s} book name".format(dataset_file))
			sys.exit(1)
	return out

def data_preprocess(dataset_file):
	words_book = {}
	book = ""
	author = ""
	broken_word = False
	splited_word = ""

	book = getbook(dataset_file = dataset_file)	
	try:
			with open(dataset_file,"r") as file:
				start_book = False
				author = getauthor(dataset_file)
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

def create_tables():

	try:
		conn = sqlite3.connect("../book_classifier.db")
	except:
		print("Database do not exist")
		sys.exit(1)

	try:
		c = conn.cursor()
		c.execute('CREATE TABLE  if not exists {tn} ({nf} {ft} PRIMARY KEY AUTOINCREMENT,{nf2} {ft2} not null)'\
        .format(tn='author', nf='id', ft='INTEGER', nf2='name', ft2='text'))

		c.execute('CREATE TABLE  if not exists {tn} ({nf} {ft} PRIMARY KEY AUTOINCREMENT,{nf2} {ft2} not null, {nf3} {ft3} not null, FOREIGN KEY({nf3}) REFERENCES {nT}({nTf}) )'\
        .format(tn='books', nf='id', ft='INTEGER', nf2='name', ft2='text', nf3='author_id', ft3='INTEGER', nT='author', nTf='id'))

		c.execute('CREATE TABLE  if not exists {tn} ({nf} {ft} PRIMARY KEY AUTOINCREMENT,{nf2} {ft2} not null)'\
        .format(tn='words', nf='id', ft='INTEGER', nf2='name', ft2='text'))

		c.execute('CREATE TABLE  if not exists {tn} ({nf} {ft} PRIMARY KEY AUTOINCREMENT,{nf2} {ft2} not null, {nf3} {ft3} not null, {nf4} {ft4} not null, FOREIGN KEY({nf3}) REFERENCES {nT}({nTf}),FOREIGN KEY({nf4}) REFERENCES {nT2}({nTf2}) )'\
        .format(tn='frequence', nf='id', ft='INTEGER', nf2='freq', ft2='INTEGER', nf3='word_id', ft3='INTEGER', nf4='book_id', ft4='INTEGER', nT='words', nTf='id', nT2='books', nTf2='id'))


		conn.commit()
		conn.close()
	except:
		print("Error while creating tables in database")
		sys.exit(1)


def save_author(author):
	try:
		conn = sqlite3.connect("../book_classifier.db")
	except:
		print("Database do not exist")
		sys.exit(1)

	try:
		c = conn.cursor()
		c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="{aut}"'.\
							format(coi='id', tn='author', cn='name', aut=author))

		id_author = c.fetchone()

		if id_author is None: # if author is not in the database yet
			c.execute('INSERT INTO {tn} ({idf}) VALUES ("{cn}")'.\
								format(tn='author', idf='name', cn=author))

		conn.commit()
		conn.close()

	except:
		print("Error while saving author in database")
		sys.exit(1)


def save_book(book, author):
	try:
		conn = sqlite3.connect("../book_classifier.db")
	except:
		print("Database do not exist")
		sys.exit(1)

	try:
		c = conn.cursor()
		c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="{aut}"'.\
							format(coi='id', tn='books', cn='name', aut=book))

		id_book = c.fetchone()

		if id_book is None: # if book is not in the database yet

			c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="{aut}"'.\
							format(coi='id', tn='author', cn='name', aut=author))

			id_author = c.fetchone()

			if id_author is None:
				print("Author is not in the database. Something is wrong")
				sys.exit(1)

			c.execute('INSERT INTO {tn} ({idf}, {idf2}) VALUES ("{cn}","{cn2}")'.\
								format(tn='books', idf='name',idf2='author_id', cn=book, cn2=int(id_author[0])))

		conn.commit()
		conn.close()

	except:
		print("Error while saving author in database")
		sys.exit(1)

def save_words_freq(words_book, book):
	try:
		conn = sqlite3.connect("../book_classifier.db")
	except:
		print("Database do not exist")
		sys.exit(1)

	try:
		c = conn.cursor()
		# save all words, if not exist in databe
		for word,freq in words_book.items():
			c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="{aut}"'.\
							format(coi='id', tn='words', cn='name', aut=word))

			id_word = c.fetchone()
			if id_word is None: # if it's a new word
				c.execute('INSERT INTO {tn} ({idf}) VALUES ("{cn}")'.\
								format(tn='words', idf='name', cn=word))

			c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="{aut}"'.\
							format(coi='id', tn='words', cn='name', aut=word))

			id_word = c.fetchone()

			c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="{aut}"'.\
							format(coi='id', tn='books', cn='name', aut=book))

			id_book = c.fetchone()

			if id_word is None or id_book is None:
				print("word and book must be in the databse")
				sys.exit(1)
			
			#save frequence as well
			c.execute('INSERT INTO {tn} ({idf},{idf2},{idf3}) VALUES ("{cn}","{cn2}","{cn3}")'.\
								format(tn='frequence', idf='freq', idf2='word_id',idf3='book_id', cn=int(freq),cn2=int(id_word[0]),cn3=int(id_book[0])))

		conn.commit()
		conn.close()

	except:
		print("Error while saving words in database")
		sys.exit(1)

def save_to_data_base(words_book, author, book):
	
	save_author(author)
	save_book(book,author)
	save_words_freq(words_book,book)

def isBookInDatabase(book):

	try:
		conn = sqlite3.connect("../book_classifier.db")
	except:
		print("Database do not exist")
		sys.exit(1)

	isBook = True

	try:
		c = conn.cursor()
		c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="{aut}"'.\
							format(coi='id', tn='books', cn='name', aut=book))


		id_book = c.fetchone()

		if id_book is None:
			isBook = False

	except:
		print("Error while checking book in database")
		sys.exit(1)

	return isBook


def init_dataBase():
		create_tables() # if not exist

def main():	
	if len(sys.argv) < 2:
		print("Please provide <file>\n")
		sys.exit(1)
	
	# run scripts to create tables and others, if not exists
	init_dataBase()
	isBook_database = False

	# book already exists in databse
	if isBookInDatabase(getbook(dataset_file = sys.argv[1])	):
		print("Book " + getbook(dataset_file = sys.argv[1]) + " is already in database...")
		print("Ritriving data....")
		isBook_database = True

	else: # read book, save in database, including the frequence of words
		words_book = {}
		words_book, author, book = data_preprocess(sys.argv[1])

		save_to_data_base(words_book,author,book)

if __name__ == '__main__':
	main()



