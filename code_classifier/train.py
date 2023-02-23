import numpy as np
from sklearn.metrics import f1_score,accuracy_score
from tqdm import tqdm, trange
import logging
import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from  transformers import RobertaForSequenceClassification
from accelerate import Accelerator
from dataset import train_test_tokenizer

def evaluate(model,test_loader):
    eval_loss = 0.0
    nb_eval_steps = 0
    preds = np.empty((0), dtype=np.int64)
    out_label_ids = np.empty((0), dtype=np.int64)
    logging.basicConfig(filename = './test.log',level=logging.INFO)

    model.eval()

    for step, (input_ids, attention_masks, labels) in enumerate(tqdm(test_loader, desc="Test")):
        input_ids = torch.squeeze(input_ids, 1)
        with torch.no_grad():
            outputs = model(input_ids=input_ids.to(device), attention_mask=attention_masks.to(device), labels=labels.to(device))
            loss = outputs[0]
            logits = outputs[1]
            eval_loss += loss.mean().item()
            nb_eval_steps += 1
        preds = np.append(preds, logits.argmax(dim=1).detach().cpu().numpy(), axis=0)
        out_label_ids = np.append(out_label_ids, labels.detach().cpu().numpy(), axis=0)
        eval_loss = eval_loss / nb_eval_steps
        acc = accuracy_score(preds, out_label_ids)
        f1 = f1_score(y_true=out_label_ids, y_pred=preds, average="macro")
    print("=== Eval: loss ===", eval_loss)
    print("=== Eval: acc. ===", acc)
    print("=== Eval: f1 ===", f1)
    logging.info(f'eval, loss: {eval_loss} acc: {acc} f1: {f1}')


def train(labels,device,dataloader):
    tb_writer = SummaryWriter()
    model = RobertaForSequenceClassification.from_pretrained("huggingface/CodeBERTa-small-v1", num_labels=labels).to(device)
    optimizer = torch.optim.AdamW(model.parameters())
    for param in model.roberta.parameters():
        param.requires_grad = False
    
    print(f"num params:", model.num_parameters())
    print(f"num trainable params:", model.num_parameters(only_trainable=True))

    accelerator = Accelerator(mixed_precision='fp16')
    model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)
    train_iterator = trange(0, 5, desc="Epoch")

    for _ in train_iterator:
        epoch_iterator = tqdm(dataloader, desc="Iteration")
        for step, (input_ids, attention_masks, labels) in enumerate(epoch_iterator,start=1):
            model.train()
            optimizer.zero_grad()
            input_ids = torch.squeeze(input_ids, 1)
            
            outputs = model(input_ids=input_ids.to(device), attention_mask=attention_masks.to(device), labels=labels.to(device))
            loss = outputs[0]
            
            accelerator.backward(loss)
            optimizer.step()
            optimizer.zero_grad()

            tb_writer.add_scalar('Loss/train: ',loss.item())
    tb_writer.close()
    return model
    
if __name__ == '__main__':
    train_loader, test_loader, tokenizer = train_test_tokenizer(pkl_file='./code_snippet/snippets-dev.pkl',test_size=0.2)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tb_writer = SummaryWriter()

    model = train(labels=20, device=device, dataloader=train_loader)
    tb_writer.close()
    #model = RobertaForSequenceClassification.from_pretrained("./CodeBERT-github-code-snippet-tiny").to(device)

    evaluate(model,test_loader)
    model.save_pretrained("./CodeBERT-github-code-snippet-tiny")
