# code_crawler

A simple code crawler to avoid visiting stackoverflow, w3schools, tutorialspoint, 
geeksforgeeks, pyp, askubuntu and mathworks ever again. On the rare ocasion its 
necessary just click the available link.
					
![Image of crawler](https://github.com/johneliades/code_crawler/blob/main/preview.png)

## Clone

Clone the repository locally by entering the following command:
```
git clone https://github.com/johneliades/code_crawler.git
```
Or by clicking on the green "Clone or download" button on top and then decompressing the zip.

## Run

After installing the missing libraries and getting a free and fast API key from the link in the Credits below,
for the optional syntax highlighting to work, you can run:

```
python3 code_crawler.py "any possible programming question"
```

## How it works

After google searching your question and taking the first 10(by default) sites into account, 
the script visits the site if it belongs in the aforementioned sites. It then takes the 
accepted answer's code block, and sends it to the ProgrammingLanguageIdentification API. 
The most probable language is returned and the appropriate lexer is used for the syntax 
highlighting, giving you the answer in an organised way.

## Credits

Credits to https://algorithmia.com/algorithms/PetiteProgrammer/ProgrammingLanguageIdentification
for providing the useful programming language identification API. Algorithmia gives 5k free tokens
per month and the tool uses some for each search. One day I will build my own fully free and 
offline neural network for this for faster results.

## Author

**Eliades John** - *Developer* - [Github](https://github.com/johneliades)
