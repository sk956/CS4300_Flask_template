############
#This file contains functions that drive user's search by querying the database
############

from . import *  
import numpy as np 
import pickle 
import numpy as np 
import json
from sklearn.preprocessing import normalize
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.words import *
from app.irsystem.models.books import *
from app.irsystem.models.authors import *
from app.irsystem.controllers.db_change import *
from app.irsystem.controllers.db_query import *
import json
import os
import csv
import unicodedata


#words: user's keyword input! 
def inputs_to_scores(words, books, length = 61082, k =100):


	vector_sum = np.zeros(k)
	word_inputs = words.split('**')
	book_inputs = books.split('**')
	for word in word_inputs:
		if word == '':
			del word_inputs[0]
			break
		vector_sum += np.fromstring(Words.query.filter_by(name = word).first().vector, sep=', ')
	for book in book_inputs:
		if book == '':
			del book_inputs[0]
			break
		vector_sum += np.fromstring(Books.query.filter_by(name = book).first().vector, sep=', ')
	if len(word_inputs) + len(book_inputs) == 0:
		return None
	vector_sum /= len(word_inputs) + len(book_inputs)

	sum_sim_scores = np.zeros(length)
	for book in Books.query.all():
		index = book.index
		ith_book_vector = np.fromstring(book.vector, sep=', ')
		sum_sim_scores[index] = ith_book_vector.dot(vector_sum)

	return sum_sim_scores

# #book: user's book title input
# def book_to_closest_books(books, length = 61082):
# 	if books == '':
# 		return np.zeros(length)
# 	book_query_objects = [Books.query.filter_by(name=book).first() for book in books.split('**')]
# 	book_vector = np.fromstring(book_query_object.vector, sep=', ')
# 	sim_scores = np.zeros(length)
# 	for book in Books.query.all():
# 		index = book.index
# 		ith_book_vector = np.fromstring(book.vector, sep = ', ')
# 		for book_q_obj in book_query_objects:
# 			sim_scores[index] += ith_book_vector.dot(np.fromstring(book_q_obj.vector, sep = ', '))
# 	return sim_scores / len(book_query_objects)

def scores_to_asort(scores, k = 15):	
	asort = np.argsort(-scores)
	start_index = 0
	#Get rid of the first few with sim score veryvery close to 1 
	if round(scores[asort[0]], 2) == 1.0: 
		start_index += 1
	asort_score_tup = []
	for i in asort[start_index:start_index+k]:
		asort_score_tup.append((i, round(scores[i],4)*100))
	return asort_score_tup

def get_books(asorted_list):
	top_k_books = []
	for tup in asorted_list:
		book_list = []
		book_query_object = Books.query.filter_by(index = tup[0]).first()
		book_list.append(book_query_object.name)							##1. Bookname
		book_list.append(book_query_object.isbn10)							##2. ISBN10
		book_list.append(book_query_object.isbn13)							##3. ISBN13
		book_list.append(book_query_object.link)							##4. Link
		book_list.append(book_query_object.author)							##5. author
		book_list.append(book_query_object.description)						##6. description
		#add word cloud ([('warm', 95), ('cold', 7)])
		book_list.append(book_to_closest_words(book_query_object))			##7. word cloud
		book_list.append(book_query_object.avg_rating)						##8. average rating
		book_list.append(tup[1])											##9. Similarity Score
		top_k_books.append(book_list)
	return top_k_books

def book_to_closest_words(book, k = 50, length = 5260):
	book_vector = book.vector

	sim_scores = np.zeros(length)
	for word in Words.query.all():
		index = word.index
		ith_word_vector = np.fromstring(word.vector, sep=', ')
		sim_scores[index] = ith_word_vector.dot(np.fromstring(book_vector,sep=', '))
	word_score_tup_list = []
	for i in np.argsort(-sim_scores)[:k]:
		word_name = unicodedata.normalize('NFKD', Words.query.filter_by(index=i).first().name).encode('ascii', 'ignore')
		word_score_tup_list.append((word_name, round(sim_scores[i],4)*100))
	return word_score_tup_list
