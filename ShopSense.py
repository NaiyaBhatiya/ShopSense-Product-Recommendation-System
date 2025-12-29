import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


df = pd.read_csv("styles_updated.csv")


df['combined'] = (
        df['productDisplayName'].fillna('') + ' ' +
        df['subCategory'].fillna('') + ' ' +
        df['articleType'].fillna('') + ' ' +
        df['baseColour'].fillna('') + ' ' +
        df['gender'].fillna('')
)


tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined'])


def recommend_products(user_input, top_n=10, min_similarity=0.2):
    user_input = user_input.lower().strip()
    input_vec = tfidf.transform([user_input])

    similarity_scores = cosine_similarity(input_vec, tfidf_matrix)[0]
    df['similarity'] = similarity_scores

    filtered_df = df[
        (df['similarity'] >= min_similarity) &
        (df['rating'] >= 3.5)
        ].sort_values(by='similarity', ascending=False)

    if filtered_df.empty:
        return pd.DataFrame()

    results = filtered_df.head(top_n).copy()
    results['image_path'] = results['id'].astype(str).apply(lambda x: f"images/{x}.jpg")
    return results
