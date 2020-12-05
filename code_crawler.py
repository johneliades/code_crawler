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

http = urllib3.PoolManager()

query = sys.argv[1]
print()

for url in search(query, tld="co.in", num=10, stop=10, pause=2): 
	try:
		if(url.find("w3schools")!=-1):
			response = http.request('GET', url)
			soup = BeautifulSoup(response.data, features="lxml")
			result = soup.find("div", {"class": "w3-code"})
			result = result.get_text(separator="\n").strip()
			print(bcolors.OKCYAN + "w3schools: " + bcolors.FAIL + url + bcolors.ENDC) 
			print("-------------------------------------------")
			print(result)
			if(not result.endswith("\n")):
				print()

		elif(url.find("stackoverflow")!=-1):
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
