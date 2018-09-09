import sqlite3
import sys 
import re

"""
#functions to get some specific information from file
"""
def getauthor_file(dataset_file):

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

def getbook_file(dataset_file = None, header_file = None):

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
            title = getbook_file(header_file = line)
            continue
    except:
      print("usage: {0:s} book name".format(dataset_file))
      sys.exit(1)
  return title

# function to create tables
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

    c.execute('CREATE TABLE  if not exists {tn} ({nf} {ft} PRIMARY KEY AUTOINCREMENT, {nf3} {ft3} not null, {nf4} {ft4} not null,{nf5} {ft5} not null, FOREIGN KEY({nf3}) REFERENCES {nT}({nTf}),FOREIGN KEY({nf4}) REFERENCES {nT2}({nTf2}) )'\
              .format(tn='probabilities', nf='id', ft='INTEGER', nf3='word_id', ft3='INTEGER', nf4='author_id', ft4='INTEGER',nf5='prob_freq', ft5='REAL', nT='words', nTf='id', nT2='author', nTf2='id'))


    conn.commit()
    conn.close()
  except:
    print("Error while creating tables in database")
    sys.exit(1)

# delete all data from a table  
def clean_table(table):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('DELETE FROM {tn}'.\
              format(tn=table))

    erase = c.fetchall()

    conn.commit()
    conn.close()

  except:
    print("Error while deleting table " + table)
    sys.exit(1)


"""
# functions to save some data into database
"""
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

# save a new book to database
def save_to_data_base(words_book, author, book):
  
  save_author(author)
  save_book(book,author)
  save_words_freq(words_book,book)

# function to save new probabilites from the bag of words, for an author
def save_probs_author(author,dict_probs):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()

    for key,value in dict_probs.items():
      c.execute('INSERT INTO {tn} ({idf}, {idf2},{idf3}) VALUES ("{cn}","{cn2}", "{cn3}")'.\
                format(tn='probabilities', idf='word_id',idf2='author_id',idf3='prob_freq', cn=key, cn2=author, cn3=value))

    conn.commit()
    conn.close()

  except:
    print("Error while saving author in database")
    sys.exit(1)

# create the tables
def init_dataBase():
    create_tables() # if not exist

"""
# Functions to get data from data sets
"""

# check if book exist in database
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

# get all authors from databse
def get_authors():
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT {coi} FROM {tn} '.\
              format(coi='id', tn='author'))


    ids_authors = c.fetchall()
    if ids_authors is None:
      print("There is no author saved on the dataset")
      return None

    ids = [id_aut for id_author in ids_authors for id_aut in id_author]

    return ids
  except:
    print("Error while checking all authors")
    sys.exit(1)

# get author's name from databse
def get_author_name(author_id):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT {coi} FROM {tn} where id = {idn}'.\
              format(coi='name', tn='author', idn=author_id))


    author_name = c.fetchone()
    if author_name is None:
      print("There is no author saved on the dataset")
      return None

    return author_name[0]
  except:
    print("Error while checking all authors")
    sys.exit(1)

# get all frequence & words from an author, order by frequece
def get_freq_words_author(author):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT SUM(freq), word_id FROM frequence where book_id in(select id from books where author_id = {tn}) group by word_id order by freq DESC '.\
              format(tn=author))


    freq_words = c.fetchall()
    if freq_words is None:
      print("There are no words saved on the dataset")
      return None
    return freq_words

  except:
    print("Error while getting all words from author")
    sys.exit(1)

# get total words in database
def get_num_words_database():
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('select count() from {tn} '.\
              format(tn="words"))


    total_words = c.fetchone()
    if total_words is None:
      print("There are no words on the dataset")
      return None
    return total_words[0]

  except:
    print("Error while getting numb of all words in database")
    sys.exit(1)

# get total words from an author in database
def get_num_words_author(author):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT count(word_id) FROM frequence where book_id in(select id from books where author_id = {tn}) group by word_id'.\
              format(tn=author))


    words = c.fetchall()
    num_words = 0
    if words is None:
      print("There are no words saved on the dataset")
      return None
    num_words = len(words)
    return num_words

  except:
    print("Error while getting all words from author")
    sys.exit(1)

# get total of words from an specific book
def get_total_words_book(book):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT count(word_id) FROM frequence where book_id = {tn} group by book_id'.\
              format(tn=book))


    words_book = c.fetchone()
    if words_book is None:
      print("There are no words saved on the dataset")
      return None
    
    return words_book[0]

  except:
    print("Error while getting all words from author")
    sys.exit(1)

# get the total of appereances of word in, in all books from author y
def get_total_word_x_author(author,word):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    total_word = 0
    c = conn.cursor()
    c.execute('select sum(freq) from frequence where book_id in (select id from books where author_id ={aut}) and word_id = {wrd}'.\
              format(aut=author,wrd=word))


    total_word = c.fetchall()
    if total_word is None:
      print("There are no words saved on the dataset")
      return None 

    return total_word[0][0]

  except:
    print("Error while getting count of word "+word+ "from author " +author)
    sys.exit(1)

# get numb of books
def get_num_books():
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT count() FROM {tn}'.\
              format(tn="books"))


    num_books = c.fetchone()
    if num_books is None:
      print("There are no books saved on the dataset")
      return None
    return num_books[0]

  except:
    print("Error while getting num of books")
    sys.exit(1)


# get numb of authors
def get_num_authors():
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT count() FROM {tn}'.\
              format(tn="author"))


    num_authors = c.fetchone()
    if num_authors is None:
      print("There are no author saved on the dataset")
      return None
    return num_authors[0]

  except:
    print("Error while getting num of authors")
    sys.exit(1)

# get words and its frequence(bag of words, based on the frequence and a feature detector)
def get_words_freq_features(feature_detector):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT SUM(freq), word_id FROM frequence where freq > {tn} group by word_id order by freq DESC '.\
              format(tn=feature_detector))


    freq_words = c.fetchall()
    if freq_words is None:
      print("There are no words saved on the dataset")
      return None

    print(len(freq_words),freq_words)
    return freq_words

  except:
    print("Error while getting all words from author")
    sys.exit(1)

# get id words classified as features, based on a feature detecton
def get_idwords_features(feature_detector):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    c = conn.cursor()
    c.execute('SELECT SUM(freq), word_id FROM frequence where freq > {tn} group by word_id order by freq DESC '.\
              format(tn=feature_detector))


    freq_words = c.fetchall()
    if freq_words is None:
      print("There are no words saved on the dataset")
      return None

    words = [y[1] for y in freq_words]
    return words

  except:
    print("Error while getting all words from author")
    sys.exit(1)

# get the actually words classified as features, based on a feature detecton
def get_words_features(feature_detector):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    words_id = get_idwords_features(feature_detector)
    words = ""
    for x in range(len(words_id)-1):
      words += str(words_id[x]) + ','
    words +=str(words_id[len(words_id)-1])

    c = conn.cursor()
    c.execute('SELECT name,id FROM words where id in ({tn}) '.\
              format(tn=words))


    all_words = c.fetchall()
    if all_words is None:
      print("There are no words saved on the dataset")
      return None

    dict_words = {}
    for word in all_words:
      dict_words[word[0]] = word[1]

    return dict_words

  except:
    print("Error while getting all words names")
    sys.exit(1)

# return a dict with key as the id_word and as value its probability calculation for the author
def get_freq_prob_author(author,feature_detector):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:
    prob_wrds = {}
    tot_wrds = get_num_words_author(author) * 1.0
    bag_words = get_idwords_features(feature_detector)
    words = ""
    for x in range(len(bag_words)-1):
      words += str(bag_words[x]) + ','
    words +=str(bag_words[len(bag_words)-1])
    c = conn.cursor()
    c.execute('select word_id,sum(freq)/{twrd} from frequence where book_id in (select id from books where author_id ={aut}) and word_id in ({wrds}) group by word_id;'.\
              format(twrd=tot_wrds,aut=author,wrds=words))


    prob_words = c.fetchall()
    if prob_words is None:
      print("There are no words saved on the dataset")
      return None

    for prob in prob_words:
      prob_wrds[prob[0]] = prob[1]

    return prob_wrds

  except:
    print("Error while getting all probs from author")
    sys.exit(1)

# get the probability of word, from an author
def get_proba_word_author(author,word):
  try:
    conn = sqlite3.connect("../book_classifier.db")
  except:
    print("Database do not exist")
    sys.exit(1)

  try:

    c = conn.cursor()
    c.execute('SELECT prob_freq FROM probabilities where author_id = {tn} and word_id = {wrd} '.\
              format(tn=author,wrd=word))


    prob = c.fetchone()
    if prob is None:
      #print("There are no probabilities saved on the dataset")
      return None

    return prob[0]

  except:
    print("Error while getting prob from word " + word +" and author " +author)
    sys.exit(1)

"""
select sum(freq),word_id from frequence where freq >= 20 group by word_id;

select sum(freq),word_id from frequence where freq >= 20 and book_id in (select id from books where author_id = 2) group by word_id;

"""







