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
from transformers import TextClassificationPipeline,RobertaForSequenceClassification,RobertaTokenizer
from time import time

CODEBERTA_LANGUAGE_ID = "huggingface/CodeBERTa-language-id"

code_tokenizer = RobertaTokenizer.from_pretrained(CODEBERTA_LANGUAGE_ID)
code_classifier = RobertaForSequenceClassification.from_pretrained(
	"./code_classifier/CodeBERT-github-code-snippet-tiny")

pipeline = TextClassificationPipeline(
    model= code_classifier,
    tokenizer= code_tokenizer
)

start = time()

class bcolors:
	CYAN = '\033[96m'
	RED = '\033[31m'
	NEW = '\033[32m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'

available_sites = ["w3schools", "stackoverflow", "tutorialspoint", 
				"geeksforgeeks", "pypi", "askubuntu", "mathworks",
				"stackexchange", "unrealengine", "microsoft"]

try:
	query = sys.argv[1]
	if("\"" not in query and "'" not in query):
		query = ' '.join(sys.argv[1:])
except:
	query = input("Give search query: ")

print()

num_results = 6
http = urllib3.PoolManager(ca_certs=certifi.where(), cert_reqs='REQUIRED')
total_results = []

for url in search(query, tld="com", lang='en', num=num_results, stop=num_results, pause=random.uniform(0, 0.5)): 
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
				result = result.get_text(separator="\n").strip()
			elif site == "stackoverflow" or site == "askubuntu" or site == "stackexchange":
				result = soup.find("div", {'class': ['answer', 'accepted-answer']})
				result = result.find("div", {"class": "answercell"})
				result = result.find("div", {"class": "s-prose"})
				result = result.find("pre").text
			elif site == "tutorialspoint":
				result = soup.find("div", {"class": "tutorial-content"})
				result = result.find("pre").text	
			elif site == "geeksforgeeks":
				result = soup.find("td", {"class": "code"})
				results = result.find_all(class_="line")
				
				result = ""
				for line in results:
					result += line.getText() + "\n"

			elif site == "pypi":
				result = soup.find("span", id="pip-command")
				result = result.get_text().strip()
			elif site == "mathworks":
				result = soup.find("div", {"class": "codeinput"})
				result = result.find("pre").text	
			elif site == "unrealengine":
				result = soup.find("div", {'class': ['answer', 'accepted-answer']})
				result = result.find("div", {"class": "answer-body"})
				result = result.find("pre").text	
			elif site == "microsoft":
				result = soup.find("code")
				result = result.get_text().strip()

			result = result.strip() + "\n"
			if result not in total_results:
				total_results.append(result)
			else:
				continue
		except:
			continue

		possible_lexer_names = [lexer[1][0] for lexer in lexers.get_all_lexers() if len(lexer[1]) > 0]
		lexer = None
		for cur_lexer in possible_lexer_names:
			if(cur_lexer.lower() in query.lower().split(' ')):
				lexer = lexers.get_lexer_by_name(cur_lexer)
				break

		print(bcolors.CYAN + bcolors.BOLD + site + ": " + bcolors.RED + url + bcolors.ENDC, end="")

		if(lexer == None):
			prediction = pipeline(result)
			lexer = lexers.get_lexer_by_name(prediction[0]["label"])

			print(bcolors.NEW + " (" + prediction[0]["label"] + " " + 
				str(round(prediction[0]["score"]*100, 2)) + "%)" + bcolors.ENDC) 
		else:
			print(bcolors.ENDC)
		
		for i in range(min(80, len(site + ": " + url))):
			print(u'\u2501', end="")
		print()

		if(lexer!=None):
			print(highlight(result,  lexers.get_lexer_by_name("TSV"), TerminalFormatter()))
		else:
			print(result)