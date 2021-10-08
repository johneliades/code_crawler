#!/usr/bin/python3

from bs4 import BeautifulSoup
from googlesearch import search 
from pygments import lexers, highlight
from pygments.formatters import TerminalFormatter
import urllib3
import sys
import random
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from guesslang import Guess

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

print()

num_results = 10
http = urllib3.PoolManager()
total_results = []

guess_flag = False

if "c" in query:
	language = "c"
elif "java" in query:
	language = "java"
elif "python" in query:
	language = "python3"
elif "lua" in query:
	language = "lua"
elif "javascript" in query or "js" in query:
	language = "javascript"
elif "go" in query or "golang" in query:
	language = "go"
elif "cpp" in query or "c++" in query:
	language = "cpp"
elif "matlab" in query:
	language = "matlab"
elif "ruby" in query:
	language = "ruby"
elif "c#" in query  or "csharp" in query:
	language = "csharp"
else:
	guess = Guess()
	guess_flag = True

for url in search(query, tld="com", lang='en', num=num_results, stop=num_results, pause=random.uniform(0, 1)): 
	site = [x for x in available_sites if url.find(x)!=-1]
	if(len(site)!=0):
		site = site[0]
	else:
		continue

	if(site in available_sites):
		try:
			response = http.request('GET', url)
			soup = BeautifulSoup(response.data, features="html.parser")

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
				continue
		except:
			continue

		if guess_flag:
			language = guess.language_name(result)
			probability = guess.probabilities(result)[0][1]

		print(bcolors.CYAN + bcolors.BOLD + site + ": " + bcolors.RED + url + bcolors.ENDC) 
		for i in range(min(80, len(site + ": " + url))):
			print(u'\u2501', end="")
		print()

		# if guess_flag:
		# 	print(bcolors.CYAN + language + " " + 
		# 		str(round(probability, 3) * 100) + "% certainty" + bcolors.ENDC)
		# 	for i in range(len(language + str(round(probability, 3) * 100)) + 12):
		# 		print(u'\u2500', end="")
		# 	print()

		if(language == "Markdown"):
			language = "md"
		elif(language == "vb"):
			language = "basic"		
		elif(language == "Batchfile"):
			language = "batch"

		lexer = lexers.get_lexer_by_name(language)
		print(highlight(result, lexer, TerminalFormatter()))