 #!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""
Created on Sun Aug 30 2018

@author: thiago
"""

# Importing the libraries
import sys
import re


def data_preprocess(dataset_file):
	try:
			with open(sys.argv[1],"r") as file:
			  for line in file.readlines():
			    words = re.split('[^A-Za-z]+',line)
			    for w in words:
			      if(len(w) >=5 && len(w)<=10) :
			        lcw = w.lower()               # convert to all lower case
			        if lcw not in wordlist:       # is the word in the dictionary
			          if lcw not in badlist:      # if not, have we seen it already?
			            badlist[lcw] = 1          # if not, set count to 1
			          else:
			            badlist[lcw] += 1         # otherwise increment count
			printdictionary(badlist)           
		except:
			print("usage: {0:s} textfile".format(sys.argv[0]))

def main():	
	if len(sys.argv) < 2:
		print("Please provide <file>\n")
		sys.exit(1)
	
	data_preprocess(sys.argv[1])


if __name__ == '__main__':
	main()