import sqlite3
import sys
import re

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
						out =  line[0].strip().lower() + " " + line[1].strip().lower()
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

	title = ""
	title = ""
	if header_file is not None:
		try:
			header_file = header_file.strip()
			header_file = header_file.strip('\n')
			header_file = header_file.split("Title:")
			header_file = header_file[1].split()
			for word in header_file:
				title += word.strip().lower()
				title +=" "
			title = title.strip()

		except:
			print("usage: {0:s} book name".format(dataset_file))
			sys.exit(1)

	elif dataset_file is not None:
		try:
			with open(dataset_file,"r") as file:
				for line in file.readlines():
					if (line.find("Title:")) >=0: # skip title 
						title = getbook(header_file = line)
						continue
		except:
			print("usage: {0:s} book name".format(dataset_file))
			sys.exit(1)
	return title

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