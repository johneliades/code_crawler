from bs4 import BeautifulSoup
from googlesearch import search 
import urllib3
import sys
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

available_sites = ["w3schools", "stackoverflow", "tutorialspoint", "geeksforgeeks", "pypi"]

try:
	query = sys.argv[1]
except:
	print("Give search query as argument")
	sys.exit()

rows, columns = os.popen('stty size', 'r').read().split()

http = urllib3.PoolManager()
print()

total_results = []
for url in search(query, tld="com", lang='en', num=10, stop=10, pause=1): 
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

		print(bcolors.OKCYAN + site + ": " + bcolors.FAIL + url + bcolors.ENDC) 
		
		for i in range(int(columns)):
			print(u'\u2500', end="")

		print()

		lines = result.splitlines()
		for line in lines:
			print("   " + line)

		if(not line.endswith("\n")):
			print()