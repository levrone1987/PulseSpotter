import torch
import torch.nn as nn
import torch.nn.functional as F


class Model(nn.Module):
    def __init__(self, embedding_dim, counts_dim, counts_hidden_size):
        super(Model, self).__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=counts_hidden_size, batch_first=True)
        self.fc_counts = nn.Linear(counts_hidden_size, counts_hidden_size)
        self.fc_topic = nn.Linear(embedding_dim, embedding_dim)
        self.fc_combined = nn.Linear(embedding_dim + counts_hidden_size, 1)

    def forward(self, counts, topic_emb):
        # Reshape counts for LSTM
        counts = counts.unsqueeze(-1)  # Shape: [batch_size, counts_dim, 1]

        # Process counts with LSTM
        lstm_out, _ = self.lstm(counts)

        # Use the output from the last step
        counts_emb = lstm_out[:, -1, :]

        # Transform counts_emb to match embedding dimensions
        counts_emb = F.relu(self.fc_counts(counts_emb))

        # Transform topic embeddings
        topic_emb_processed = F.relu(self.fc_topic(topic_emb))

        # Combine the embeddings
        combined_emb = torch.cat((counts_emb, topic_emb_processed), dim=1)

        # Classification
        output = self.fc_combined(combined_emb)
        return output
