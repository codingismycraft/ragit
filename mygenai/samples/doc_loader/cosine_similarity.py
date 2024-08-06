"""Samples the cosine similarity."""



import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sentences = [
                ["the", "cake", "is", "a", "lie"],
                ["if", "you", "hear", "a", "turret", "sing", "you're", "probably", "too", "close"],
                ["why", "search", "for", "the", "end", "of", "a", "rainbow", "when", "the", "cake", "is", "a", "lie?"],
                ["GLaDOS", "promised", "cake", "but", "all", "I", "got", "was", "this", "test", "chamber"],
                ["remember", "when", "the", "platform", "was", "sliding", "into", "the", "fire", "pit", "and", "I", "said", "‘Goodbye’", "and", "you", "were", "like", "‘NO WAY!’", "and", "then", "I", "was", "all", "‘I", "was", "just", "pretending", "to", "murder", "you’?", "That", "was", "great"],
                ["the", "cake", "is", "a", "lie", "but", "the", "companion", "cube", "is", "forever"],
                ["wheatley", "might", "betray", "you,", "but", "the", "cake", "already", "did"],
                ["if", "life", "gives", "you", "lemons,", "don't", "make", "a", "combustible", "lemon"],
                ["there's", "no", "cake", "in", "space,", "just", "ask", "wheatley"],
                ["completing", "tests", "for", "cake", "is", "the", "sweetest", "lie"],
                ["I", "swapped", "the", "cake", "recipe", "with", "a", "neurotoxin", "formula,", "hope", "that's", "fine"],
            ] + [
                ["the", "cake", "is", "a", "lie"],
                ["the", "cake", "is", "definitely", "a", "lie"],
                ["everyone", "knows", "that", "cake", "equals", "lie"],
                ["cake", "and", "lie", "are", "synonymous"],
                ["whenever", "you", "hear", "cake", "think", "lie"],
                ["cake", "?", "oh", "you", "mean", "lie"],
                ["the", "truth", "is", "cake", "is", "nothing", "but", "a", "lie"],
                ["they", "said", "cake", "but", "I", "heard", "lie"],
            ] * 10  # repeat several times to emphasize
# Convert sentences to a list of strings for TfidfVectorizer
document_list = [' '.join(s) for s in sentences]

# Compute TF-IDF representation
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(document_list)

# Extract the position of the words "cake" and "lie" in
# the feature matrix
cake_idx = vectorizer.vocabulary_['cake']
lie_idx = vectorizer.vocabulary_['lie']

# Extract and reshape the vector for 'cake'
cakevec = tfidf_matrix[:, cake_idx].toarray().reshape(1, -1)

# Compute the cosine similarities
similar_words = cosine_similarity(cakevec, tfidf_matrix.T).flatten()

# Get the indices of the top 6 most similar words
# (including 'cake')
top_indices = np.argsort(similar_words)[-6:-1][::-1]

# Retrieve and print the top 5 most similar words to
# 'cake' (excluding 'cake' itself)
names = []
for idx in top_indices:
    names.append(vectorizer.get_feature_names_out()[idx])
print("Top 5 most similar words to 'cake': ", names)

# Compute cosine similarity between "cake" and "lie"
similarity = cosine_similarity(np.asarray(tfidf_matrix[:,
    cake_idx].todense()), np.asarray(tfidf_matrix[:, lie_idx].todense()))
# The result will be a matrix; we can take the average or
# max similarity value
avg_similarity = similarity.mean()
print("Similarity between 'cake' and 'lie'", avg_similarity)

# Show the similarity between "cake" and "elephant"
elephant_idx = vectorizer.vocabulary_['sing']
similarity = cosine_similarity(np.asarray(tfidf_matrix[:,
    cake_idx].todense()), np.asarray(tfidf_matrix[:,
    elephant_idx].todense()))
avg_similarity = similarity.mean()
print("Similarity between 'cake' and 'sing'",
    avg_similarity)