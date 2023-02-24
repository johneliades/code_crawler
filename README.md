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
Or by clicking on the green "Clone or download" button on top and then 
decompressing the zip.

Then download the pretrained model download .bin file from this 
[google-drive-link](https://drive.google.com/file/d/1VxrJ8zUZuNA-ojTA-z1FQuvPseqYQOJE/view?usp=share_link) 
and paste it in code_crawler/code_classifier/CodeBERT-github-code-snippet-tiny directory.

## Run

Install the missing libraries:

```
pip install -r requirements.txt
```

and then you can run:

```
python code_crawler.py "any possible programming question"
```

or:

```
python code_crawler.py any possible programming question
```

## How it works

After google searching your question and taking the first 7(by default) sites 
into account, the script visits the site if it belongs in the aforementioned 
sites. It then takes the accepted answer's code block, and uses the specified 
lexer provided in the search keywords. If not specified then it identifies the 
appropriate lexer using the model's best prediction and then highlights the 
code, giving you the answer in an organised way.

## Code Classifier

It's based on [CodeBERTA](https://huggingface.co/huggingface/CodeBERTa-language-id) 
and finetuned using [Github-code-snippets-sample](https://www.kaggle.com/datasets/simiotic/github-code-snippets-development-sample?datasetId=1198320), a smaller dataset made for 
prototyping purposes, in order to be able to classify 20 popular programming and 
scripting languages. Although the predictions most of the time are correct, for some 
languages the confidence score is low. We think that the problem might be resolved by 
using the bigger version [Github-code-snippets](https://www.kaggle.com/datasets/simiotic/github-code-snippets). 

inference dependencies : 
```
pip install huggingface
```
train dependencies : 
```
pip install -r code_classifier/requirements.txt
```
The code classifier can be also used independently by downloading the pretrained model 
(pytorch_model.bin) file from this [google-drive-link](https://drive.google.com/file/d/1VxrJ8zUZuNA-ojTA-z1FQuvPseqYQOJE/view?usp=share_link) and pasting it in the same directory 
as the "config.json" found in code_classifier/CodeBERT-github-code-snippet-tiny. Then using 
the inference.py as a base example on how to run the model.

## Authors

**Eliades John** - *Developer* - [Github](https://github.com/johneliades)

**Milas Kostas** - *Developer* - [Github](https://github.com/kmilas)
