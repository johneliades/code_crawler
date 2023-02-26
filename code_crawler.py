#!/usr/bin/python3

from bs4 import BeautifulSoup
from googlesearch import search 
from pygments import lexers, highlight
from pygments.formatters import TerminalFormatter
import urllib3
import sys
import random
import os
import certifi
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import threading

def import_transformers():
	global pipeline

	from transformers import TextClassificationPipeline, RobertaForSequenceClassification, RobertaTokenizer

	code_tokenizer = RobertaTokenizer.from_pretrained("huggingface/CodeBERTa-language-id")

	code_classifier = RobertaForSequenceClassification.from_pretrained(
		"./code_classifier/CodeBERT-github-code-snippet-tiny")

	pipeline = TextClassificationPipeline(
		model= code_classifier,
		tokenizer= code_tokenizer
	)

def choose_lexer(query):
	possible_lexer_names = [lexer[1][0] for lexer in lexers.get_all_lexers() if len(lexer[1]) > 0]

	predict = True
	chosen_lexer = None
	for cur_lexer in possible_lexer_names:
		if(cur_lexer.lower() in query.lower().split(' ')):
			chosen_lexer = lexers.get_lexer_by_name(cur_lexer)
			predict = False
			break

	return chosen_lexer, predict

class bcolors:
	CYAN = '\033[96m'
	RED = '\033[31m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'

available_sites = ["w3schools", "stackoverflow", "tutorialspoint", 
				"geeksforgeeks", "pypi", "askubuntu", "mathworks",
				"stackexchange", "unrealengine", "microsoft"]

if(len(sys.argv)==1):
	# Create a new thread to import libraries
	import_thread = threading.Thread(target=import_transformers)
	import_thread.start()

	query = input("Give search query: ")

	chosen_lexer, predict = choose_lexer(query)
else:
	query = sys.argv[1]
	if("\"" not in query and "'" not in query):
		query = ' '.join(sys.argv[1:])

	chosen_lexer, predict = choose_lexer(query)
	if(predict):
		import_thread = threading.Thread(target=import_transformers)
		import_thread.start()

columns, _ = os.get_terminal_size()

half_width = columns - len(" Crawling started ")

print(bcolors.CYAN, end="")
for i in range(half_width//2):
	print(u'\u2501', end="")
print(" Crawling started ", end="")
for i in range(half_width//2):
	print(u'\u2501', end="")
print("\n")

num_search_results = 7
http = urllib3.PoolManager(ca_certs=certifi.where(), cert_reqs='REQUIRED')
code_blocks = []

for url in search(query, tld="com", lang='en', 
	num=num_search_results, stop=num_search_results, pause=random.uniform(0, 0.5)): 
	
	site = [x for x in available_sites if url.find(x)!=-1]
	if(len(site)!=0):
		site = site[0]
	else:
		continue

	if(site in available_sites):
		response = http.request('GET', url)
		soup = BeautifulSoup(response.data, features="html.parser")
		try:
			if site == "w3schools":
				result = soup.find("div", {"class": "w3-code"})
				cur_code_block = result.get_text(separator="\n").strip()
			elif site == "stackoverflow" or site == "askubuntu" or site == "stackexchange":
				result = soup.find("div", {'class': ['answer', 'accepted-answer']})
				result = result.find("div", {"class": "answercell"})
				result = result.find("div", {"class": "s-prose"})
				cur_code_block = result.find("pre").text
			elif site == "tutorialspoint":
				result = soup.find("div", {"class": "tutorial-content"})
				cur_code_block = result.find("pre").text	
			elif site == "geeksforgeeks":
				result = soup.find("td", {"class": "code"})
				results = result.find_all(class_="line")

				cur_code_block = ""
				for line in results:
					cur_code_block += line.getText() + "\n"

			elif site == "pypi":
				result = soup.find("span", id="pip-command")
				cur_code_block = result.get_text().strip()
			elif site == "mathworks":
				result = soup.find("div", {"class": "codeinput"})
				cur_code_block = result.find("pre").text	
			elif site == "unrealengine":
				result = soup.find("div", {'class': ['answer', 'accepted-answer']})
				result = result.find("div", {"class": "answer-body"})
				cur_code_block = result.find("pre").text	
			elif site == "microsoft":
				result = soup.find("code")
				result = result.get_text().strip()

			cur_code_block = cur_code_block.strip() + "\n"
			if cur_code_block not in code_blocks:
				code_blocks.append(cur_code_block)
			else:
				print(bcolors.RED + "Duplicate codeblock ignored" + bcolors.ENDC)
				continue
		except:
			continue

		url_parts = url.split(site)
		print(bcolors.RED + bcolors.BOLD + url_parts[0] + bcolors.CYAN + site + 
			bcolors.RED + url_parts[1] + bcolors.ENDC, end="")

		if(predict):
			import_thread.join()

			prediction = pipeline(cur_code_block)
			chosen_lexer = lexers.get_lexer_by_name(prediction[0]["label"])

			if(prediction[0]["score"]*100>50):
				print(bcolors.GREEN + " (" + prediction[0]["label"] + " " + 
					str(round(prediction[0]["score"]*100, 2)) + "%)" + bcolors.ENDC) 
			else:
				print(bcolors.YELLOW + " (" + prediction[0]["label"] + " " + 
					str(round(prediction[0]["score"]*100, 2)) + "%)" + bcolors.ENDC) 
		else:
			print(bcolors.ENDC)

		for i in range(min(len(url_parts[0] + site + url_parts[1]), columns)):
			print(u'\u2501', end="")
		print()

		if(chosen_lexer!=None):
			print(highlight(cur_code_block, chosen_lexer, TerminalFormatter()))
		else:
			print(cur_code_block)
