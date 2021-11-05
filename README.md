# code_crawler

A simple code crawler to avoid visiting stackoverflow, w3schools, tutorialspoint, 
geeksforgeeks, pyp, askubuntu and mathworks ever again. On the rare ocasion its 
necessary just click the available link.

![](https://github.com/johneliades/code_crawler/blob/main/preview.gif) 

## Clone

Clone the repository locally by entering the following command:
```
git clone https://github.com/johneliades/code_crawler.git
```
Or by clicking on the green "Clone or download" button on top and then 
decompressing the zip.

## Run

Install the missing libraries:

```
pip install -r requirements.txt
```

and then you can run:

```
python code_crawler.py "any possible programming question"
```

## How it works

After google searching your question and taking the first 10(by default) sites 
into account, the script visits the site if it belongs in the aforementioned 
sites. It then takes the accepted answer's code block, and uses Guesslang to 
find the most probable language and then the appropriate lexer is used for the 
syntax highlighting, giving you the answer in an organised way.

## Author

**Eliades John** - *Developer* - [Github](https://github.com/johneliades)
