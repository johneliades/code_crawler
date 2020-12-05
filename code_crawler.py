from bs4 import BeautifulSoup
from googlesearch import search 
import urllib3
import sys

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


available_sites = ["w3schools", "stackoverflow"]

try:
	query = sys.argv[1]
except:
	print("Give search query as argument")
	sys.exit()

http = urllib3.PoolManager()
print()

for url in search(query, tld="co.in", num=10, stop=10, pause=2): 
	try:

		site = [x for x in available_sites if url.find(x)!=-1][0]

		if(site == "w3schools"):
			response = http.request('GET', url)
			soup = BeautifulSoup(response.data, features="lxml")
			result = soup.find("div", {"class": "w3-code"})
			result = result.get_text(separator="\n").strip()
			print(bcolors.OKCYAN + "w3schools: " + bcolors.FAIL + url + bcolors.ENDC) 
			print("-------------------------------------------")
			print(result)
			if(not result.endswith("\n")):
				print()
		elif(site == "stackoverflow"):
			response = http.request('GET', url)
			soup = BeautifulSoup(response.data, features="lxml")
			result = soup.find("div", {"class": "accepted-answer"})
			result = result.find("div", {"class": "s-prose"})
			result = result.find("pre").find(text=True)
			print(bcolors.OKCYAN + "stackoverflow: " + bcolors.FAIL + url + bcolors.ENDC) 
			print("-------------------------------------------")
			print(result)
			if(not result.endswith("\n")):
				print()

	except:
		pass
