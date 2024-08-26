import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, roc_auc_score
from torch.utils.data import DataLoader
from torchinfo import summary
from tqdm import tqdm

from pulsespotter.config import RESOURCES_DIR
from pulsespotter.training.utils.dataset import TrendingTopicsDataset
from pulsespotter.training.utils.model import Model
from pulsespotter.utils.logging_utils import get_logger


def train_test_split(df, test_pct: float = 0.2):
    num_train_samples = int(df.shape[0] * (1 - test_pct))
    num_test_samples = df.shape[0] - num_train_samples
    shuffled = df.sample(frac=1.0)
    train_df = shuffled.head(num_train_samples).reset_index(drop=True)
    test_df = shuffled.tail(num_test_samples).reset_index(drop=True)
    return train_df, test_df


def train_epoch(model, dataloader, criterion, optimizer):
    model.train()
    running_loss = 0.0

    for batch in dataloader:
        optimizer.zero_grad()
        logits = model(batch["counts"], batch["embedding"])
        labels = batch["label"]
        loss = criterion(logits.squeeze(), labels)
        running_loss += loss.item()
        loss.backward()
        optimizer.step()

    avg_loss = running_loss / len(dataloader)
    return avg_loss


def evaluate_model(model, dataloader, criterion, prefix: str = ""):
    model.eval()

    all_probs = []
    all_preds = []
    all_labels = []
    running_loss = 0.0

    with torch.no_grad():
        for batch in dataloader:
            logits = model(batch["counts"], batch["embedding"])
            probs = torch.sigmoid(logits).squeeze()
            preds = probs > 0.5
            labels = batch["label"]

            # Compute loss
            loss = criterion(logits.squeeze(), labels)
            running_loss += loss.item()

            # Collect all predictions and labels
            all_probs.extend(probs.cpu().numpy().tolist())
            all_preds.extend(preds.cpu().numpy().tolist())
            all_labels.extend(labels.cpu().numpy().tolist())

    probabilities = np.array(all_probs)
    predictions = np.array(all_preds)
    actuals = np.array(all_labels)

    response = {
        "loss": running_loss / len(dataloader),
        "precision": precision_score(predictions, actuals, zero_division=0.0),
        "recall": recall_score(predictions, actuals, zero_division=0.0),
        "f1": f1_score(predictions, actuals, zero_division=0.0),
        "accuracy": accuracy_score(predictions, actuals),
        "auc": roc_auc_score(actuals, probabilities)
    }
    if prefix:
        response = {f"{prefix}{key}": value for key, value in response.items()}
    return response


def save_model(model):
    model_output_path = RESOURCES_DIR.joinpath("best_model.pt")
    Path(model_output_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Content ingestion script.")
    parser.add_argument(
        "--dataset-filename", type=str, required=True,
        help="Filename of the dataset to use for training."
    )
    args = parser.parse_args()

    logger = get_logger(__name__)
    # logger.info("Environment vars:")
    # logger.info(f"{PROJECT_DIR=}")
    # logger.info(f"{MONGO_HOST=}")
    # logger.info(f"{MONGO_DATABASE=}")
    # logger.info(f"{QDRANT_HOST=}")
    # logger.info(f"{QDRANT_API_KEY=}")
    # logger.info(50 * "-")

    logger.info("Initialising script with following parameters:")
    logger.info(f"Dataset filename: {args.dataset_filename}")
    logger.info(50 * "-")

    # load dataset
    dataset_path = RESOURCES_DIR.joinpath(args.dataset_filename)
    logger.info(f"Loading dataset from {dataset_path} ...")
    dataset_df = pd.read_json(dataset_path)
    dataset_df["topic_end_date"] = dataset_df["date"].apply(max)
    logger.info(f"{dataset_df.shape=}")
    pos_labels_per_topic_end_date = dataset_df.groupby(by='topic_end_date')['matches_trending'].sum()
    logger.info(f"{pos_labels_per_topic_end_date=}")

    # remove dates with 0 positive labels
    valid_topic_end_dates = pos_labels_per_topic_end_date[pos_labels_per_topic_end_date > 0].index.tolist()
    dataset_df = dataset_df.loc[dataset_df["topic_end_date"].isin(valid_topic_end_dates)]
    dataset_df = dataset_df.reset_index(drop=True)

    # do train/test split
    # todo: should include train/val/test splits
    train_df, val_df = train_test_split(dataset_df, test_pct=0.2)
    print(f"{train_df.shape=}")
    print(f"{val_df.shape=}")
    assert len(set(train_df["topic_id"]).intersection(set(val_df["topic_id"]))) == 0
    logger.info(f"{train_df.shape=}")
    logger.info(f"{val_df.shape=}")

    # create dataset objects
    train_dataset = TrendingTopicsDataset(train_df)
    val_dataset = TrendingTopicsDataset(val_df)

    # model initialisation
    logger.info("Preparing the model ...")
    counts_hidden_size = 64
    embedding_dim = train_dataset[0]["embedding"].shape[-1]
    counts_dim = len(train_dataset[0]["counts"])
    model = Model(embedding_dim=embedding_dim, counts_dim=counts_dim, counts_hidden_size=counts_hidden_size)
    logger.info(summary(model))

    # training parameters
    train_batch_size = 16
    val_batch_size = 16
    num_epochs = 200
    learning_rate = 5e-5
    weight_decay = 1e-3
    log_every = 10

    # optimizer and loss function
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )

    # initialize a variable to track the best metric
    eval_metric = "val_f1"
    best_metric = float('-inf')
    best_epoch = 0

    # training loop
    logger.info("Running training ...")
    train_log = []
    pbar = tqdm(total=num_epochs, position=0, leave=True)
    for epoch in range(num_epochs):
        train_dataloader = DataLoader(train_dataset, batch_size=train_batch_size, shuffle=True)
        train_loss = train_epoch(model, train_dataloader, criterion, optimizer)

        train_dataloader = DataLoader(train_dataset, batch_size=val_batch_size)
        train_metrics = evaluate_model(model, train_dataloader, criterion, "train_")

        val_dataloader = DataLoader(val_dataset, batch_size=val_batch_size)
        val_metrics = evaluate_model(model, val_dataloader, criterion, "val_")
        train_log.append({"epoch": epoch, **train_metrics, **val_metrics})

        current_metric = val_metrics[eval_metric]
        if current_metric >= best_metric:
            best_metric = current_metric
            best_epoch = epoch
            save_model(model)

        # todo: improve logging
        if epoch % log_every == 0:
            logger.info(train_log[-1])
        pbar.update(1)

    pbar.close()
    logger.info("Training completed.")

    # save training log
    train_log = pd.DataFrame(train_log).set_index("epoch")
    log_output_filename = "train_log.csv"
    log_output_path = RESOURCES_DIR.joinpath(log_output_filename)
    logger.info(f"Saving training log into: {log_output_path.resolve()}.")
    train_log.to_csv(log_output_path)
