import numpy as np
from tensorflow.keras.layers import LSTM, Dense, Dropout, Embedding
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical

from utils import create_tokenizer, generate_padded_sequences


def create_lstm_model(vocab_size, max_sequence_len):
    model = Sequential(
        [
            Embedding(vocab_size, 128),
            LSTM(128, return_sequences=True),
            LSTM(128),
            Dropout(0.2),
            Dense(128, activation="relu"),
            Dense(vocab_size, activation="softmax"),
        ]
    )
    model.compile(
        loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
    )
    return model


async def train_model_on_text(text):
    tokenizer = create_tokenizer(text)
    input_sequences, max_sequence_len = generate_padded_sequences(
        tokenizer, text.lower().split("\n")
    )

    vocab_size = len(tokenizer.word_index) + 1

    predictors, label = input_sequences[:, :-1], input_sequences[:, -1]
    label = to_categorical(label, num_classes=vocab_size)

    model = create_lstm_model(vocab_size, max_sequence_len)

    history = model.fit(predictors, label, epochs=100, verbose=0)

    return model, tokenizer, max_sequence_len, history
