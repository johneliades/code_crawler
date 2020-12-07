from bs4 import BeautifulSoup
from googlesearch import search 
import urllib3
import sys
import os
import random
import re

class bcolors:
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	CYAN = '\033[96m'
	MAGENTA = '\033[33m'
	RED = '\033[31m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

available_sites = ["w3schools", "stackoverflow", "tutorialspoint", "geeksforgeeks", "pypi"]

programming_keywords_cyan = \
[
	"auto", "long", "enum", "register", "typedef", "extern", "union", "char", 
	"float", "short", "unsigned", "const", "signed", "void", "goto", "sizeof", 
	"bool",	"do", "int", "struct", "_Packed", "double",	"boolean", "byte", 
	"catch", "class", "extends", "instanceof", "interface", "native", 
	"private", "super", "this", "throws", "def", "len",	"lambda", "exit"
]

programming_keywords_magenta = \
[
	"break", "if", "else", "pass", "try", "except", "for", "import", "and", "not", "or",
	"del", "in", "is", "elif", "yield", "with", "from", "print", "raise", "global", 
	"continue", "finally", "while", "assert", "return", "+", "-", "/", "^", "*", "=",
	"exec", "switch", "case", "volatile", "default", "static", "abstract", "final", 
	"implements", "new", "package", "protected", "public", "strictfp", "synchronized", 
	"throw", "transient", 
]

programming_keywords_blue = \
[
	"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
]

try:
	query = sys.argv[1]
except:
	print("Give search query as argument")
	sys.exit()

rows, columns = os.popen('stty size', 'r').read().split()

http = urllib3.PoolManager()
print()

total_results = []
for url in search(query, tld="com", lang='en', num=10, stop=10, pause=random.uniform(0, 1)): 
	site = [x for x in available_sites if url.find(x)!=-1]
	if(len(site)!=0):
		site = site[0]
	else:
		continue

	if(site in available_sites):
		response = http.request('GET', url)
		soup = BeautifulSoup(response.data, features="lxml")

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
		except:
			continue

		if result not in total_results:
			total_results.append(result)
		else:
			continue

		result = "".join([bcolors.BLUE + x + bcolors.ENDC
			if x>="0" and x<="9" else x for x in result])

		result = re.findall('.*?[\n\t (]', result)

		result = [bcolors.CYAN + x + bcolors.ENDC
			if any(substring in x and len(substring)+2 >= len(x)
				for substring in programming_keywords_cyan)
			else x for x in result]

		result = [bcolors.MAGENTA + x + bcolors.ENDC
			if any(substring in x and len(substring)+2 >= len(x)
				for substring in programming_keywords_magenta)
			else x for x in result]

		result = "".join(result)

		print(bcolors.BLUE + site + ": " + bcolors.RED + url + bcolors.ENDC) 
		
		for i in range(int(columns)):
			print(u'\u2500', end="")

		print()

		lines = result.splitlines()
		for line in lines:
			print("   " + line)

		if(not line.endswith("\n")):
			print()