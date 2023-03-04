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
import threading

def import_transformers():
	global pipeline

	from transformers import TextClassificationPipeline, RobertaForSequenceClassification, RobertaTokenizer

	code_tokenizer = RobertaTokenizer.from_pretrained("huggingface/CodeBERTa-language-id")

	try:
		code_classifier = RobertaForSequenceClassification.from_pretrained(
			"./code_classifier/CodeBERT-github-code-snippet-tiny")
	except:
		print("Download pytorch_model.bin from "
			"https://drive.google.com/file/d/1VxrJ8zUZuNA-ojTA-z1FQuvPseqYQOJE/view "
			"and put it in code_classifier\CodeBERT-github-code-snippet-tiny")
		os._exit(1)

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
	GREEN_UNDERLINED = "\033[32;4m"
	YELLOW_UNDERLINED = '\033[33;4m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'

available_sites = ["w3schools", "stackoverflow", "tutorialspoint", 
				"geeksforgeeks", "pypi", "askubuntu", "mathworks",
				"stackexchange", "unrealengine", "microsoft", 
				"futurestud", "unity"]

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
print(bcolors.ENDC + "\n")

num_search_results = 7
http = urllib3.PoolManager(ca_certs=certifi.where(), cert_reqs='REQUIRED')
code_blocks = []

for url in search(query, tld="com", lang='en', 
	num=num_search_results, stop=num_search_results, pause=random.uniform(0, 0.5)): 
	
	site = [x for x in available_sites if url.find(x)!=-1]
	if(len(site)!=0):
		site = site[0]
	else:
		print(bcolors.RED + "Site not crawled: " + bcolors.CYAN + url + bcolors.ENDC + "\n")
		continue

	try:
		response = http.request('GET', url)
		soup = BeautifulSoup(response.data, features="html.parser")
		
		if site == "w3schools":
			w3_code = soup.find("div", {"class": "w3-code"})
			cur_code_block = w3_code.get_text(separator="\n").strip()
		elif site == "stackoverflow" or site == "askubuntu" or site == "stackexchange":
			accepted_answer = soup.find("div", {'class': ['answer', 'accepted-answer']})
			answercell = accepted_answer.find("div", {"class": "answercell"})
			s_prose = answercell.find("div", {"class": "s-prose"})
			cur_code_block = s_prose.find("pre").get_text()
		elif site == "tutorialspoint":
			tutorial_content = soup.find("div", {"class": "tutorial-content"})
			cur_code_block = tutorial_content.find("pre").get_text()	
		elif site == "geeksforgeeks":
			code = soup.find("td", {"class": "code"})
			lines = code.find_all(class_="line")

			cur_code_block = ""
			for line in lines:
				cur_code_block += line.get_text() + "\n"

		elif site == "pypi":
			pip_command = soup.find("span", id="pip-command")
			cur_code_block = pip_command.get_text().strip()
		elif site == "mathworks":
			codeinput = soup.find("div", {"class": "codeinput"})
			cur_code_block = codeinput.find("pre").get_text()	
		elif site == "unrealengine":
			accepted_answer = soup.find("div", {'class': ['answer', 'accepted-answer']})
			answer_body = accepted_answer.find("div", {"class": "answer-body"})
			cur_code_block = answer_body.find("pre").get_text()	
		elif site == "microsoft":
			code = soup.find("code")
			cur_code_block = code.get_text().strip()
		elif site == "futurestud":
			cur_code_block = soup.find("pre").get_text()
		elif site == "unity":
			answer_body = soup.find('div', {'class': 'answer-body'})
			cur_code_block = answer_body.find('pre').get_text()

		cur_code_block = cur_code_block.strip() + "\n"
		if cur_code_block not in code_blocks:
			code_blocks.append(cur_code_block)
		else:
			continue
	except:
		print(bcolors.RED + "Code not found: " + bcolors.CYAN + url + bcolors.ENDC + "\n")
		continue

	url_parts = url.split(site)
	print(bcolors.RED + bcolors.BOLD + url_parts[0] + bcolors.CYAN + site + 
		bcolors.RED + url_parts[1] + bcolors.ENDC, end="")

	if(predict):
		import_thread.join()

		prediction = pipeline(cur_code_block)
		chosen_lexer = lexers.get_lexer_by_name(prediction[0]["label"])
		print()
	else:
		print(bcolors.ENDC)

	for i in range(min(len(url_parts[0] + site + url_parts[1]), columns)):
		print(u'\u2501', end="")
	print()

	print(bcolors.CYAN + "Prediction: " + bcolors.ENDC, end="")
	if(predict):
		if(prediction[0]["score"]*100>50):
			print(bcolors.GREEN_UNDERLINED + prediction[0]["label"] + " " + 
				str(round(prediction[0]["score"]*100, 1)) + "%" + bcolors.ENDC) 
		else:
			print(bcolors.YELLOW_UNDERLINED + prediction[0]["label"] + " " + 
				str(round(prediction[0]["score"]*100, 1)) + "%" + bcolors.ENDC) 

	print()

	if(chosen_lexer!=None):
		print(highlight(cur_code_block, chosen_lexer, TerminalFormatter()))
	else:
		print(cur_code_block)
