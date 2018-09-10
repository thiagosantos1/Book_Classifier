# Book Author Classifier
A Machine Learning implemented using Gaussian Multinomial to give a probability of who is the author of a book.

# Main Idea
Our goal is to create a table of probability of each word, based on the frequence of it in all books. This probability gives us an idea of how often such word appears in books from an specific author.

# Database
Since we may run the same example many times, for analyses, we will create a sqlite database. Therefore, we will save all books, all words and its frequences for each book. This will speed up the data pre-processing time.

# How to execute 
	* You must save all data inside of folder data, separated by training and test folder and separated by author
	* To execute for all data
		* You can run ./main.py 
	* To test for an especific test sample
		* You can run ./main.py <name of file to test>


