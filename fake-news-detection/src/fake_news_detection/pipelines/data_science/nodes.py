import logging
from typing import Tuple, List, Dict
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from tqdm import tqdm

logger = logging.getLogger(__name__)

class FakeNewsDataset(Dataset):
    def __init__(self, encodings: Dict[str, List[int]], labels: List[int]):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def split_data(data: pd.DataFrame, parameters: dict) -> tuple:
    """Splits data into features and targets training and test sets.

    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters/data_science.yml.
    Returns:
        Split data.
    """
    logger.info("Splitting dataset...")
    X = data[parameters["features"]]
    y = data["is_fake"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=parameters["test_size"], random_state=parameters["random_state"]
    )
    return X_train.to_list(), X_test.to_list(), y_train.to_list(), y_test.to_list()

def tokenize_data(
    train_texts: List[str], val_texts: List[str], model_name: str = 'bert-base-uncased', max_length: int = 512
) -> Tuple[Dict, Dict, BertTokenizer]:
    logger.info("Tokenizing texts...")
    tokenizer = BertTokenizer.from_pretrained(model_name)
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=max_length)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=max_length)
    return train_encodings, val_encodings, tokenizer


def create_datasets(train_encodings, val_encodings, train_labels, val_labels) -> Tuple[Dataset, Dataset]:
    logger.info("Creating datasets...")
    return FakeNewsDataset(train_encodings, train_labels), FakeNewsDataset(val_encodings, val_labels)


def train_and_evaluate(
    train_dataset: Dataset,
    val_dataset: Dataset,
    parameters: dict
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    logger.info("Loading model and starting training...")
    model = BertForSequenceClassification.from_pretrained(
        parameters["model_name"], num_labels=parameters["num_labels"]
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    train_loader = DataLoader(train_dataset, batch_size=parameters["batch_size"], shuffle=True)
    optimizer = AdamW(model.parameters(), lr=parameters["lr"])

    for epoch in range(parameters["epochs"]):
        model.train()
        total_loss = 0
        logger.info(f"Epoch {epoch+1}/{parameters['epochs']} starting...")
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1} Training"):
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            total_loss += loss.item()
        logger.info(f"Epoch {epoch+1} Loss: {total_loss:.4f}")

    logger.info("Training complete. Starting evaluation...")
    model.eval()
    val_loader = DataLoader(val_dataset, batch_size=parameters["batch_size"])

    all_preds, all_labels, all_probs = [], [], []
    for batch in tqdm(val_loader, desc="Evaluating"):
        batch = {k: v.to(device) for k, v in batch.items()}
        with torch.no_grad():
            outputs = model(**batch)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
            preds = torch.argmax(logits, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(batch['labels'].cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    predictions_df = pd.DataFrame({
        "label": all_labels,
        "prediction": all_preds,
        "prob_0": [p[0] for p in all_probs],
        "prob_1": [p[1] for p in all_probs]
    })

    report_dict = classification_report(all_labels, all_preds, output_dict=True)
    report_df = pd.DataFrame(report_dict).transpose().reset_index().rename(columns={"index": "class"})

    return predictions_df, report_df
