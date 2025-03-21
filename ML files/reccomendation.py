import pandas as pd
import tensorflow as tf
import tensorflow_recommenders as tfrs
from sklearn.model_selection import train_test_split
import numpy as np

# Sample event dataset (user_event_data.csv - assumes columns: user_id, event_id, rating)
data = pd.read_csv('user_event_data.csv')

# Convert the user-event interaction into a format suitable for TensorFlow Recommenders
# Drop the rating column if you're working with implicit feedback (like views or clicks)
data = data[['user_id', 'event_id']]

# Split the data into train and test sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# Create a TensorFlow dataset from the train and test data
# The dataset needs to return a dictionary with the features (user_id, event_id)
train = tf.data.Dataset.from_tensor_slices({
    "user_id": train_data['user_id'].values,
    "event_id": train_data['event_id'].values
})

test = tf.data.Dataset.from_tensor_slices({
    "user_id": test_data['user_id'].values,
    "event_id": test_data['event_id'].values
})

# Batch the data (for performance reasons)
train = train.batch(4096)
test = test.batch(4096)

# Define the model architecture
# Use embeddings for users and events (learnable representations)

embedding_dimension = 32  # The size of the embedding vectors

# Define the user and event models
user_model = tf.keras.Sequential([
    tf.keras.layers.StringLookup(
        vocabulary=data['user_id'].unique(), mask_token=None, oov_token="[UNK]"),
    tf.keras.layers.Embedding(len(data['user_id'].unique()) + 1, embedding_dimension)
])

event_model = tf.keras.Sequential([
    tf.keras.layers.StringLookup(
        vocabulary=data['event_id'].unique(), mask_token=None, oov_token="[UNK]"),
    tf.keras.layers.Embedding(len(data['event_id'].unique()) + 1, embedding_dimension)
])

# Define the retrieval task model
class RecommenderModel(tfrs.Model):
    def __init__(self, user_model, event_model):
        super().__init__()
        self.user_model = user_model
        self.event_model = event_model

        self.task = tfrs.tasks.Retrieval(self.event_model)

    def compute_loss(self, features, training=False):
        # Ensure the features are being passed correctly as a dictionary
        user_embeddings = self.user_model(features["user_id"])
        event_embeddings = self.event_model(features["event_id"])

        # Get the candidate ids (event_ids)
        candidate_ids = features["event_id"]

        # The task computes the similarity between user embeddings and event embeddings.
        # We need to pass the embeddings and candidate_ids to the Retrieval task
        return self.task(query_embeddings=user_embeddings, candidate_embeddings=event_embeddings, candidate_ids=candidate_ids)

# Instantiate and compile the model
model = RecommenderModel(user_model, event_model)
model.compile(optimizer=tf.keras.optimizers.Adagrad(0.5))

# Train the model
model.fit(train, epochs=3)

# Function to recommend events for a given user
def recommend_events(user_id, model, top_n=10):
    # Get the embeddings for the user
    user_embedding = model.user_model(tf.constant([user_id]))

    # Get all event embeddings
    event_embeddings = model.event_model.embeddings

    # Compute the similarity between the user embedding and all event embeddings
    scores = np.dot(user_embedding, event_embeddings.T)

    # Get the top N event recommendations based on similarity
    recommended_event_indices = np.argsort(scores[0])[-top_n:][::-1]
    recommended_events = data['event_id'].unique()[recommended_event_indices]

    return recommended_events

# Example: Recommend top 10 events for a specific user (user_id = "user123")
recommended_events = recommend_events("user123", model, top_n=10)
print(f"Recommended Events for user123: {recommended_events}")
