from . import *
import numpy as np
import pickle
import numpy as np
import json
from sklearn.preprocessing import normalize
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.word import *
from app.irsystem.models.books import *
from app.irsystem.models.authors import *
from app.irsystem.controllers.db_change import *
from app.irsystem.controllers.db_query import *
import json
import os
import csv
import unicodedata

project_name = "BookRec"
net_id = "Hyun Kyo Jung: hj283"

# @irsystem.route('/', methods=['GET'])
# def delandadd():
# 	empty_db()
# 	create_tables()
# 	put_words_in_db()
# 	put_books_in_db()
# 	word_cloud_message = ''
# 	top_books_message = ''
# 	word_cloud = ['successfully added']
# 	top_books = ['successfully added']
# 	available_words = []
# 	available_books = []
# 	return render_template('search.html', name=project_name, netid=net_id, word_cloud_message=word_cloud_message, top_books_message=top_books_message, word_cloud=word_cloud, top_books = top_books)

# @irsystem.route('/', methods=['GET'])
# def add_words_chunks():
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
	top_book_message = ""
	if title_input is not None : 
		title_input = title_input.encode('ascii', 'gignore')
		top_book_message += title_input 
	if keyword_input is not None: 
		keyword_input = keyword_input.encode('ascii', 'ignore')
		top_book_message += keyword_input
	
	#encode everything to make sure that the output is the correct ouput format 

	for result in results :
		for i in range(4):
			if result[i] is None:
				result[i] = ''
			else: 
				result[i] = result[i].encode('ascii','ignore')
		result[3] = "http://www.goodreads.com/book/show/" + result[3]
		result[2] = "http://covers.openlibrary.org/b/isbn/" + result[2] + "-M.jpg"
		result[1] = "http://covers.openlibrary.org/b/isbn/" + result[1] + "-M.jpg"


	return render_template('secondpage.html', name=project_name, netid=net_id, word_cloud_message='', 
		top_books_message=top_book_message, word_cloud=[], top_books = results, avail_keywords = [], avail_books = [])
 
	
@irsystem.route('/main', methods=['GET'])
def search():
	available_words = json.load(open('words.json'))
	available_words = [unicodedata.normalize('NFKD', w).encode('ascii','ignore') for w in available_words]
	available_books = json.load(open('books.json'))
	available_books = [unicodedata.normalize('NFKD', b).encode('ascii','ignore') for b in available_books]

	#author_input = request.args.get('author_search')
	title_input = request.args.get('title_search')
	keyword_input = request.args.get('keyword_search')
	title_input = request.args.get('title_search')
	keyword_input = request.args.get('keyword_search') 
	print("first page")

	if title_input is not None or keyword_input is not None :
		print(title_input)
		print(keyword_input)
		#w = word_to_closest_books(keyword_input)
		#b = book_to_closest_books(title_input)
		#result = combine_results(w, b) 
		#session["result"] = result 
		session["title_input"]  = title_input 
		session["keyword_input"] = keyword_input
		return redirect(url_for('irsystem.secondpage'))
	return render_template('search.html', name=project_name, netid=net_id, word_cloud_message='', top_books_message='', 
		word_cloud=[], top_books = [], avail_keywords = available_words, avail_books = available_books)

	#print(len(Word.query.all()))
