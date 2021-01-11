#!/usr/bin/python3

import threading
from bs4 import BeautifulSoup
from googlesearch import search 
from pygments import lexers, highlight
from pygments.formatters import TerminalFormatter
import urllib3
import sys
import random
import Algorithmia
import os

class bcolors:
	CYAN = '\033[96m'
	RED = '\033[31m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'

available_sites = ["w3schools", "stackoverflow", "tutorialspoint", "geeksforgeeks", 
	"pypi", "askubuntu", "mathworks"]

try:
	query = sys.argv[1]
except:
	query = input("Give search query: ")

try:
	keyFile = open(os.path.dirname(os.path.realpath(__file__)) + '/api_key', 'r')
	api_key = keyFile.readline().strip()
except:
	print(bcolors.RED)
	print("Please get a free API key by signing up and write it in a ", end="")
	print("file called \"api_key\" in the same folder.")
	print(bcolors.CYAN)
	print("https://algorithmia.com/algorithms/PetiteProgrammer/ProgrammingLanguageIdentification")
	print(bcolors.ENDC)
	exit()

client = Algorithmia.client(api_key)
algo = client.algo('PetiteProgrammer/ProgrammingLanguageIdentification/0.1.3')

print()

num_results = 7
http = urllib3.PoolManager()
mutex = threading.Lock()
total_results = []
threads = []

def find_answer(url):
	site = [x for x in available_sites if url.find(x)!=-1]
	if(len(site)!=0):
		site = site[0]
	else:
		return

	if(site in available_sites):
		response = http.request('GET', url)
		soup = BeautifulSoup(response.data, features="html.parser")

		try:
			if(site == "w3schools"):
				result = soup.find("div", {"class": "w3-code"})
				result = result.get_text(separator="\n").strip()
			elif(site == "stackoverflow"):
				result = soup.find("div", {"class": "accepted-answer"})
				result = result.find("div", {"class": "s-prose"})
				result = result.find("pre").find(text=True)
			elif(site == "tutorialspoint"):
				result = soup.find("div", {"class": "tutorial-content"})
				result = result.find("pre").find(text=True)	
			elif(site == "geeksforgeeks"):
				result = soup.find("td", {"class": "code"})
				result = result.get_text().strip()
			elif(site == "pypi"):
				result = soup.find("span", id="pip-command")
				result = result.text
			elif(site == "askubuntu"):
				result = soup.find("div", {"class": "accepted-answer"})
				result = result.find("div", {"class": "s-prose"})
				result = result.find("pre").find(text=True)
			elif(site == "mathworks"):
				result = soup.find("div", {"class": "codeinput"})
				result = result.get_text(separator="\n").strip()

			result = result.strip()
			if result not in total_results:
				total_results.append(result)
			else:
				return

		except:
			return
    
		try:
			code_lang = algo.pipe(result).result[0]
		except(Algorithmia.errors.AlgorithmException):
			print(bcolors.RED)
			print("API key in file \"api_key\" is wrong, check again")
			print(bcolors.ENDC)
			exit()

		language = code_lang[0]
		probability = code_lang[1]

		with mutex:
			print(bcolors.CYAN + bcolors.BOLD + site + ": " + bcolors.RED + url + bcolors.ENDC) 
			for i in range(min(80, len(site + ": " + url))):
				print(u'\u2501', end="")
			print()

		#	print(bcolors.CYAN + language + " " + 
		#		str(round(probability, 3) * 100) + "% certainty" + bcolors.ENDC)
		#	for i in range(len(language + str(round(probability, 3) * 100)) + 12):
		#		print(u'\u2500', end="")
		#	print()

			if(language == "markdown"):
				language = "md"
			elif(language == "vb"):
				language = "basic"

			lexer = lexers.get_lexer_by_name(language)
			print(highlight(result, lexer, TerminalFormatter()))

once = True

for url in search(query, tld="com", lang='en', num=num_results, stop=num_results, pause=random.uniform(0, 1)): 
	if(once):
		find_answer(url)
		once = False
		continue
	t = threading.Thread(target=find_answer, args=(url,))
	threads.append(t)
	t.start()
