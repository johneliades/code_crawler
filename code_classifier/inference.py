# pip install transformers

from transformers import TextClassificationPipeline, RobertaForSequenceClassification, RobertaTokenizer
from time import time

def code_classifier(code_snippet, tokenizer, model):
    start = time()
    pipeline = TextClassificationPipeline(
        model = model,
        tokenizer = tokenizer
    )
    
    print(pipeline(code_snippet), "exec_time: ", time()-start)

if __name__ == '__main__':
    code = ["""
#include "jcr.h"

#include <stdlib.h>
#include <string.h>
#include <limits.h>

char *fgetl(FILE *fp)
{
    if(feof(fp)) return 0;
    size_t size = 512;
    char *line = malloc(size*sizeof(char));
    if(!fgets(line, size, fp)){
        free(line);
        return 0;
    }

    size_t curr = strlen(line);

    while((line[curr-1] != '\n') && !feof(fp)){
        if(curr == size-1){
            size *= 2;
            line = realloc(line, size*sizeof(char));
            if(!line) {
                printf("%ld\n", size);
                malloc_error();
            }
        }
        size_t readsize = size-curr;
        if(readsize > INT_MAX) readsize = INT_MAX-1;
        fgets(&line[curr], readsize, fp);
        curr = strlen(line);
    }
    if(line[curr-1] == '\n') line[curr-1] = '\0';

    return line;
}
    ""","""
    def f(x):
        return x+2""","""package main
import (
    "fmt"
    "os"
)

func main() {
    fmt.Println("Hello World")

    // Exit successfully
    os.Exit(0)

    // Never runs
    fmt.Println("Something else...")
} 
        """
    ]
    code_tokenizer = RobertaTokenizer.from_pretrained("huggingface/CodeBERTa-language-id")
    model = RobertaForSequenceClassification.from_pretrained("./CodeBERT-github-code-snippet-tiny")

    code_classifier(code, code_tokenizer, model)