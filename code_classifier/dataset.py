import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split
from utils import load_pkl, sql_to_pkl

class CodeClassificationDataset(Dataset):
    def __init__(self, df, text_col, label_col, tokenizer):
        self.df = df
        self.text_col = text_col
        self.label_col = label_col
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        code = self.df.iloc[idx][self.text_col]
        label = self.df.iloc[idx][self.label_col]

        # tokens = preprocess_code(code, label)
        # code = "".join(tokens)

        inputs = self.tokenizer.encode_plus(code,
                                            add_special_tokens=True,
                                            return_tensors='pt',
                                            max_length=512,
                                            padding='max_length',
                                            truncation = True)
        token_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']

        return token_ids, attention_mask, label

def train_test_tokenizer(pkl_file, test_size):
    #sql_to_pkl('./code_snippet/snippets-dev.db')
    df = load_pkl(pkl_file)
    df_train, df_test = train_test_split(df, test_size=test_size, random_state=42)
    tokenizer = AutoTokenizer.from_pretrained("huggingface/CodeBERTa-small-v1")

    train_dataset = CodeClassificationDataset(df_train, "snippet", "language", tokenizer)
    test_dataset = CodeClassificationDataset(df_test, "snippet", "language", tokenizer)

    # Define the DataLoaders for the train and test datasets
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, pin_memory=False)

    return train_loader, test_loader, tokenizer