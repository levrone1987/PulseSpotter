import torch
from torch.utils.data import Dataset


class TrendingTopicsDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # we need to convert ObjectId into strings
        topic_id = str(self.data.iloc[idx]['topic_id'])
        counts = torch.tensor(self.data.iloc[idx]['count'], dtype=torch.float32)
        embedding = torch.tensor(self.data.iloc[idx]['embedding'], dtype=torch.float32)
        label = torch.tensor(self.data.iloc[idx]['matches_trending'], dtype=torch.float32)
        return {"topic_id": topic_id, "counts": counts, "embedding": embedding, "label": label}
