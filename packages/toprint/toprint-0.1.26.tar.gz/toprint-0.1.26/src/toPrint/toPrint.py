

def toPrint(texts, tokenizer, max_len=512):
    """Converts a list of texts to a list of tokenized documents."""
    docs = []
    for text in texts:
        tokens = tokenizer.tokenize(text)
        if len(tokens) > max_len:
            tokens = tokens[:max_len]
        docs.append(tokens)
    return docs