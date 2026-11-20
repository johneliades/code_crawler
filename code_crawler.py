#!/usr/bin/python3

from bs4 import BeautifulSoup
from ddgs import DDGS
from pygments import lexers, highlight
from pygments.formatters import TerminalFormatter
import urllib3
import urllib.parse
import json
import re
import sys
import os
import shutil
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
			"and put it in code_classifier\\CodeBERT-github-code-snippet-tiny")
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
				"futurestud", "unity", "realpython"]

stackexchange_sites = ["stackoverflow", "askubuntu", "stackexchange"]

def stackexchange_code(url):
	# Stack Exchange pages now sit behind a Cloudflare bot check, so read the
	# answers through the official API instead (no key needed, ~300 req/day/IP).
	parsed = urllib.parse.urlparse(url)
	question_id = re.search(r"/(?:questions|q)/(\d+)", parsed.path).group(1)
	response = http.request("GET",
		f"https://api.stackexchange.com/2.3/questions/{question_id}/answers",
		fields={"site": parsed.hostname.removeprefix("www."), "filter": "withbody",
			"sort": "votes", "order": "desc", "pagesize": "30"})
	data = json.loads(response.data)
	if "error_message" in data:
		raise RuntimeError(data["error_message"])

	# Accepted answer first, then the rest by votes; take the first with code.
	answers = sorted(data["items"], key=lambda a: not a["is_accepted"])
	for answer in answers:
		pre = BeautifulSoup(answer["body"], features="html.parser").find("pre")
		if pre is not None:
			return pre.get_text()
	raise LookupError("no code block in any answer")

if(len(sys.argv)==1):
	print(f"\ne.g: python {os.path.basename(__file__)} append lists in python")
	sys.exit()
else:
	query = sys.argv[1]
	if("\"" not in query and "'" not in query):
		query = ' '.join(sys.argv[1:])

	chosen_lexer, predict = choose_lexer(query)
	if(predict):
		import_thread = threading.Thread(target=import_transformers, daemon=True)
		import_thread.start()

columns, _ = shutil.get_terminal_size()

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

# Google now requires JavaScript for search, so the old `googlesearch`
# scraper gets no results. ddgs can still query several engines; any single
# one fails now and then, so try them in order until one answers.
results = []
for backend in ["google", "bing", "yahoo", "mullvad_google", "auto"]:
	try:
		results = DDGS(timeout=10).text(query, max_results=num_search_results, backend=backend)
	except Exception:
		continue
	if results:
		break
else:
	print(bcolors.RED + "Search failed: no search engine returned results" + bcolors.ENDC)
	sys.exit(1)

for url in (r["href"] for r in results):
	
	site = [x for x in available_sites if url.find(x)!=-1]
	if(len(site)!=0):
		site = site[0]
	else:
		print(bcolors.RED + "Site not crawled: " + bcolors.CYAN + url + bcolors.ENDC + "\n")
		continue

	try:
		if site in stackexchange_sites:
			cur_code_block = stackexchange_code(url)
		else:
			response = http.request('GET', url)
			soup = BeautifulSoup(response.data, features="html.parser")

		if site == "w3schools":
			w3_code = soup.find("div", {"class": "w3-code"})
			cur_code_block = w3_code.get_text(separator="\n").strip()
		elif site == "tutorialspoint":
			tutorial_content = soup.find("div", {"class": "tutorial-content"})
			cur_code_block = tutorial_content.find("pre").get_text()	
		elif site == "geeksforgeeks":
			# highlighted code blocks first, then plain snippets (e.g. shell commands)
			pre = soup.select_one("div.highlight > pre") or soup.select_one("div.html-chunk > pre")
			if pre is not None:
				cur_code_block = pre.get_text()
			else:  # older GFG layout
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
		elif site == "realpython":
			pre = soup.select_one("div.codeblock__contents pre, div.codeblock pre")
			cur_code_block = pre.get_text()

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

	if(predict):
		print("\n" + bcolors.CYAN + "Prediction: " + bcolors.ENDC, end="")
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
