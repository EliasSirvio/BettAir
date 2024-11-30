import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from fcmeans import FCM
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.decomposition import PCA


# Initialize NLTK data
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('wordnet')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Load your data from CSV
df = pd.read_csv('my_fake_data.csv', quotechar='"', encoding='utf-8')

# Ensure the DataFrame has the required columns
df = df[['post_id', 'user_post']]

# Text Preprocessing
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

def preprocess_text(text):
    # Lowercase
    text = text.lower()
    # remove username
    text = re.sub(r'^\s*[^:]+:\s*', '', text)
    # Remove punctuation and numbers
    text = re.sub(r'[^a-z\s]', '', text)
    # Tokenize
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    # Rejoin words
    text = ' '.join(tokens)
    return text


df['processed_post'] = df['user_post'].apply(preprocess_text)

vectorizer = TfidfVectorizer(
    stop_words='english',
    ngram_range=(1, 3),
    max_features=2000,
    max_df=0.85,
    min_df=2
)
X = vectorizer.fit_transform(df['processed_post'])

print(df[['user_post', 'processed_post']].head())


n_topics = 5  # Adjust based on your data
lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda.fit(X)

df['topic'] = lda.transform(X).argmax(axis=1)

for i in range(n_topics):
    print(f"\n--- Topic {i} Sample Posts ---")
    sample_posts = df[df['topic'] == i]['user_post'].sample(5, random_state=42)
    for post in sample_posts:
        print(f"- {post}")

pca = PCA(n_components=2, random_state=42)
reduced_data = pca.fit_transform(lda.transform(X))

plt.figure(figsize=(10, 6))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=df['topic'], cmap='tab10', alpha=0.7)
plt.title("PCA Visualization of Topics")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.colorbar(label='Topic')
plt.show()

# Determine Optimal Number of Clusters
from sklearn.metrics import silhouette_score

range_n_clusters = list(range(2, 5))
silhouette_scores = []

for n_clusters in range_n_clusters:
    fcm = FCM(n_clusters=n_clusters, random_state=42)
    fcm.fit(X.toarray())
    labels = fcm.predict(X.toarray())
    score = silhouette_score(X, labels)
    silhouette_scores.append(score)
    print(f"Number of clusters: {n_clusters}, Silhouette Score: {score:.4f}")

# Plot Silhouette Scores
plt.figure(figsize=(10, 6))
plt.plot(range_n_clusters, silhouette_scores, marker='o')
plt.title('Silhouette Score for Various Numbers of Clusters')
plt.xlabel('Number of clusters')
plt.ylabel('Silhouette Score')
plt.xticks(range_n_clusters)
plt.grid(True)
plt.show()

# Select Optimal Number of Clusters
optimal_n_clusters = range_n_clusters[silhouette_scores.index(max(silhouette_scores))]
print(f"Optimal number of clusters: {optimal_n_clusters}")

# Apply Fuzzy C-Means Clustering with optimal number of clusters
fcm = FCM(n_clusters=optimal_n_clusters, random_state=42)
fcm.fit(X.toarray())

# Retrieve fuzzy membership degrees
fuzzy_labels = fcm.u

# Assign clusters based on highest membership degree
df["cluster"] = fcm.predict(X.toarray())

# Optionally, assign cluster labels (for now, use numeric labels)
df['cluster_label'] = df['cluster']

# Analyze Clusters
centroids = fcm.centers
feature_names = vectorizer.get_feature_names_out()

def get_top_terms(centroids, feature_names, top_n=10):
    top_terms = {}
    for idx, centroid in enumerate(centroids):
        top_indices = centroid.argsort()[-top_n:][::-1]
        top_terms[idx] = [feature_names[i] for i in top_indices]
    return top_terms

top_terms = get_top_terms(centroids, feature_names, top_n=10)

for cluster, terms in top_terms.items():
    print(f"Cluster {cluster}: {', '.join(terms)}")

# Display sample posts for each cluster
def get_sample_posts(df, cluster_label, sample_size=5):
    cluster_posts = df[df['cluster'] == cluster_label]['user_post']
    available_posts = len(cluster_posts)
    
    if available_posts == 0:
        return ["No posts available in this cluster."]
    elif available_posts < sample_size:
        print(f"Cluster {cluster_label} has only {available_posts} posts. Sampling all available posts.")
        return cluster_posts.tolist()
    else:
        return cluster_posts.sample(n=sample_size, random_state=42).tolist()

for cluster in range(optimal_n_clusters):
    print(f"\n--- Cluster {cluster} Sample Posts ---")
    sample_posts = get_sample_posts(df, cluster, sample_size=5)
    for post in sample_posts:
        print(f"- {post}")

# Perform Fuzzy Sentiment Analysis
def get_sentiment_scores(text):
    scores = sia.polarity_scores(text)
    return scores

df['sentiment_scores'] = df['user_post'].apply(get_sentiment_scores)

# Expand sentiment scores into separate columns
sentiment_df = pd.json_normalize(df['sentiment_scores'])
df = pd.concat([df, sentiment_df], axis=1)

# Assign fuzzy sentiment membership degrees
df['positive_membership'] = df['pos']
df['negative_membership'] = df['neg']
df['neutral_membership'] = df['neu']

# Normalize sentiment memberships
df['total_membership'] = df['positive_membership'] + df['negative_membership'] + df['neutral_membership']
df['positive_membership'] = df['positive_membership'] / df['total_membership']
df['negative_membership'] = df['negative_membership'] / df['total_membership']
df['neutral_membership'] = df['neutral_membership'] / df['total_membership']

# Drop the total_membership column as it's no longer needed
df.drop('total_membership', axis=1, inplace=True)

# Visualize Sentiment Distribution per Cluster
sentiment_columns = ['positive_membership', 'negative_membership', 'neutral_membership']
sentiment_per_cluster = df.groupby('cluster')[sentiment_columns].mean()

sentiment_per_cluster.plot(kind='bar', figsize=(12, 8))
plt.title('Average Sentiment Membership Degrees per Cluster')
plt.ylabel('Average Membership Degree')
plt.xticks(rotation=0)
plt.legend(title='Sentiment')
plt.show()

# Cluster Visualization with t-SNE
tsne = TSNE(n_components=2, random_state=42)
reduced_data = tsne.fit_transform(X.toarray())

plt.figure(figsize=(12, 8))
scatter = plt.scatter(
    reduced_data[:, 0],
    reduced_data[:, 1],
    c=df['cluster'],
    cmap='tab20',
    alpha=0.6
)
plt.title("Cluster Visualization")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.colorbar(label='Cluster')
plt.show()

# Save Results
df.to_csv("clustered_and_sentiment_forum_posts.csv", index=False)
