from bs4 import BeautifulSoup
from googlesearch import search 
from pygments import lexers, highlight
from pygments.formatters import TerminalFormatter
import urllib3
import sys
import random
import Algorithmia

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

client = Algorithmia.client('simPbzpOSX4A7ZK6Y4oQjeSGpZ61')
algo = client.algo('PetiteProgrammer/ProgrammingLanguageIdentification/0.1.3')

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
				continue

		except:
			continue

		print(bcolors.CYAN + bcolors.BOLD + site + ": " + bcolors.RED + url + bcolors.ENDC) 
		for i in range(min(80, len(site + ": " + url))):
			print(u'\u2501', end="")
		print()

		code_lang = algo.pipe(result).result[0]
		language = code_lang[0]
		probability = code_lang[1]

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
