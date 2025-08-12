import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer


def create_tokenizer(text):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts([text])
    return tokenizer


def generate_padded_sequences(tokenizer, lines):
    sequences = tokenizer.texts_to_sequences(lines)
    input_sequences = []
    for line in sequences:
        for i in range(1, len(line)):
            n_gram_sequence = line[: i + 1]
            input_sequences.append(n_gram_sequence)

    if not input_sequences:
        return np.array([]), 0

    max_sequence_len = max([len(x) for x in input_sequences])
    input_sequences = np.array(
        pad_sequences(input_sequences, maxlen=max_sequence_len, padding="pre")
    )
    return input_sequences, max_sequence_len


def predict_next_words(model, tokenizer, text, max_sequence_len, num_predictions=5):
    token_list = tokenizer.texts_to_sequences([text])[0]
    token_list = pad_sequences([token_list], maxlen=max_sequence_len - 1, padding="pre")

    predicted_probs = model.predict(token_list, verbose=0)[0]
    reverse_word_index = {index: word for word, index in tokenizer.word_index.items()}
    top_indices = np.argsort(predicted_probs)[-num_predictions:][::-1]
    predictions = [reverse_word_index.get(i, "") for i in top_indices]
    return predictions
