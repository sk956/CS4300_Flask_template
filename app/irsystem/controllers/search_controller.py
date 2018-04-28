from . import *  
import numpy as np 
import pickle 
import numpy as np 
import json
#import zipfile
#import Collections 
from sklearn.preprocessing import normalize
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
####
from app.irsystem.models.words import *
from app.irsystem.models.books import *
import json
import os
import csv
import unicodedata

project_name = "BookRec"
net_id = "Hyun Kyo Jung: hj283"


def db_word_to_closest_books(word, ith, k = 15):
	avg_word = np.zeros(100)
	for w, i in zip(word, ith):
		np_word = np.fromstring(w.vectors, sep= ', ')
		td_np_word = np.reshape(np_word, (100,100))
		np_word = td_np_word[i]
		avg_word += np_word
	avg_word /= len(word)
	print('before query')
	query_result = Books.query.all()
	print('after query')
	dot_products = np.zeros(len(query_result*100))
	print('before processing')
	for book in query_result:
		np_book = np.fromstring(book.vectors, sep = ', ')
		num_books = len(np_book) / 100
		td_np_book = np.reshape(np_book, (num_books, 100))
		dot_prod = np.dot(td_np_book, avg_word)
		for i in range(num_books):
			dot_products[book.start_index + i] = dot_prod[i]
	print('after processing')

	dot_products = np.absolute(dot_products)
	asort = np.argsort(-dot_products)[:k+1]

	top_k_books = []
	top_k_sim_scores = []
	for i in asort[1:]:
		near_names = Books.query.filter_by(start_index = i/100*100).first().names
		name = near_names.split('***')[i % 100]
		name =name.encode('ascii','ignore')
		top_k_books.append(name)
		top_k_sim_scores.append(dot_products[i]/dot_products[asort[0]])
	return top_k_books

def db_book_to_closest_words(book, ith, k = 5):
	np_book = np.fromstring(book.vectors, sep= ', ')
	td_np_book = np.reshape(np_book, (100,100))
	np_book = td_np_book[ith]
	query_result = Words.query.all()
	dot_products = np.zeros(len(query_result*100))
	for word in query_result:
		np_word = np.fromstring(word.vectors, sep = ', ')
		num_words = len(np_word) / 100
		td_np_word = np.reshape(np_word, (num_words, 100))
		dot_prod = np.dot(td_np_word, np_book)
		for i in range(num_words):
			dot_products[word.start_index + i] = dot_prod[i]
	asort = np.argsort(-dot_products)[:k+1]

	top_k_words = []
	for i in asort[1:]:
		near_names = Words.query.filter_by(start_index = i/100*100).first().names
		name = near_names.split('***')[i % 100]
		top_k_words.append((name, dot_products[i]/dot_products[asort[0]]))
	return top_k_words

#Empties out all tables within the postgresql database
def empty_db():
	db.reflect()
	db.drop_all()
	print('database wiped!')

#create all tables in the models folder
def create_tables():
	db.create_all()

#Create a book instance
def put_books_in_db(hash_factor = 100):
	#load the files
	docs_compressed = pickle.load(open("docs.pkl", "rb"))

	index_to_book = json.load(open("index_to_book.json"))
	words_compressed = pickle.load(open("words.pkl", "rb"))
	index_to_word = json.load(open("index_to_word.json"))
	print('files all opened!')

	num_doc = len(docs_compressed)
	row_i = 0
	while row_i < num_doc:
		i = 0
		hundred_vectors = ''
		hundred_names   = ''
		while row_i + i < num_doc and i < hash_factor:
			if i == 0:
				hundred_vectors += str(docs_compressed[row_i + i].tolist())[1:-1]
				hundred_names += index_to_book[str(row_i + i)]
			else:
				hundred_vectors = hundred_vectors + ', ' + str(docs_compressed[row_i + i].tolist())[1:-1]
				hundred_names = hundred_names + '***' + index_to_book[str(row_i + i)]
			i+=1
		b = Books(start_index = row_i, names = hundred_names, vectors = hundred_vectors)
		db.session.add(b)
		row_i += i
	print('done with books!')
	print('last row i was %s' % str(row_i-1))

	num_word = len(words_compressed)
	row_i = 0
	while row_i < num_word:
		i = 0
		hundred_vectors = ''
		hundred_names   = ''
		while row_i + i < num_word and i < hash_factor:
			if i == 0:
				hundred_vectors += str(words_compressed[row_i + i].tolist())[1:-1]
				hundred_names += index_to_word[str(row_i + i)]
			else:
				hundred_vectors = hundred_vectors + ', ' + str(words_compressed[row_i + i].tolist())[1:-1]
				hundred_names = hundred_names + '***' + index_to_word[str(row_i + i)]
			i+=1
		w = Words(start_index = row_i, names = hundred_names, vectors = hundred_vectors)
		db.session.add(w)
		row_i += i
	print('done with words!')

	db.session.commit()
	print('commited!')


# @irsystem.route('/', methods=['GET'])
# def delandadd():
# 	empty_db()
# 	create_tables()
# 	put_books_in_db()
# 	word_cloud_message = ''
# 	top_books_message = ''
# 	word_cloud = ['successfully added']
# 	top_books = ['successfully added']
# 	available_words = []
# 	available_books = []
# 	return render_template('search.html', name=project_name, netid=net_id, word_cloud_message=word_cloud_message, top_books_message=top_books_message, word_cloud=word_cloud, top_books = top_books)
@irsystem.route('/secondpage', methods=['GET'])
def secondpage(): 
	print("enter second page ")
	results = session.get('result', None)
	title_input = session.get('title_input', None) 
	keyword_input = session.get('keyword_input', None)
	top_book_message = title_input.encode('ascii','ignore') + keyword_input.encode('ascii', 'ignore')
	#encode everything to make sure that the output is the correct ouput format 

	for result in results :
		link=result[3].encode('ascii','ignore')
		link ="http://www.goodreads.com/book/show/" + link
		result[1] = result[1].encode('ascii','ignore') 
		result[2] = result[2].encode('ascii','ignore') 
		url = "http://covers.openlibrary.org/b/isbn/" + result[1]  + '-M.jpg'
		url2 = "http://covers.openlibrary.org/b/isbn/" + result[2]  + '-M.jpg'
		url=url.encode('ascii','ignore') 
		url2=url2.encode('ascii','ignore') 
		result[1] = result[1].encode('ascii', 'ignore')
		result[1] = url  
		result[2] = url2 
		result[3] = link 

	return render_template('second.html', name=project_name, netid=net_id, word_cloud_message='', 
		top_books_message=top_book_message, word_cloud=[], top_books = results, avail_keywords = [], avail_books = [])
 

@irsystem.route('/main', methods=['GET'])
def search():
	available_words = json.load(open('words.json'))
	available_words = [unicodedata.normalize('NFKD', w).encode('ascii','ignore') for w in available_words]
	available_books = json.load(open('books.json'))
	available_books = [unicodedata.normalize('NFKD', b).encode('ascii','ignore') for b in available_books]

	title_input = request.args.get('title_search')
	keyword_input = request.args.get('keyword_search') 
	print("first page")

	if title_input is not None or keyword_input is not None :
		w = word_to_closest_books(keyword_input)
		b = book_to_closest_books(title_input)
		result = combine_results(w, b) 
		session["result"] = result 
		session["title_input"]  = title_input 
		session["keyword_input"] = keyword_input
		return redirect(url_for('irsystem.secondpage'))
	return render_template('search.html', name=project_name, netid=net_id, word_cloud_message='', top_books_message='', 
		word_cloud=[], top_books = [], avail_keywords = available_words, avail_books = available_books)

