from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    split_data,
    tokenize_data,
    create_datasets,
    train_and_evaluate,
)

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=split_data,
            inputs=["news_data", "params:model_options"],
            outputs=["train_texts", "val_texts", "train_labels", "val_labels"],
            name="split_data_node",
        ),
        node(
            func=tokenize_data,
            inputs=["train_texts", "val_texts"],
            outputs=["train_encodings", "val_encodings", "tokenizer"],
            name="tokenize_data_node",
        ),
        node(
            func=create_datasets,
            inputs=["train_encodings", "val_encodings", "train_labels", "val_labels"],
            outputs=["train_dataset", "val_dataset"],
            name="create_datasets_node",
        ),
        node(
            func=train_and_evaluate,
            inputs=["train_dataset", "val_dataset", "params:model_options"],
            outputs=["predictions", "evaluation_report"],
            name="train_and_evaluate_node",
        ),
    