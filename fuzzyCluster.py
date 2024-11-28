import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from fcmeans import FCM
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from faker import Faker
import random
from wordcloud import WordCloud
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline


# Initialize Faker and download NLTK data
fake = Faker()
nltk.download('vader_lexicon')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Define a more diverse set of topics with enhanced detail
topics = {
    "Parks and Recreation": "The city is expanding its parks and recreational areas to provide more green spaces and facilities for community activities.",
    "Traffic and Pollution": "Efforts to manage traffic congestion and reduce pollution levels are critical for improving urban living conditions.",
    "Public Transport and Safety": "Enhancing public transportation systems and ensuring safety measures are vital for a well-functioning city.",
    "Cycling Infrastructure": "Developing comprehensive cycling infrastructure supports eco-friendly transportation and healthier lifestyles.",
    "Green Energy and Sustainability": "Investing in green energy projects and sustainable practices is essential for long-term environmental health.",
    "Housing and Development": "Addressing housing affordability and promoting sustainable development are key to meeting the needs of a growing population.",
    "Education and Schools": "Improving educational facilities and resources ensures that residents have access to quality education.",
    "Public Safety and Security": "Enhancing public safety measures and emergency response systems protects residents and maintains order.",
    "Economic Development": "Fostering economic growth through supporting local businesses and attracting new investments boosts the city's prosperity.",
    "Healthcare Facilities": "Expanding healthcare infrastructure and services ensures that all residents have access to necessary medical care.",
    "Cultural Heritage and Events": "Preserving cultural heritage sites and promoting diverse cultural events enrich the community's social fabric.",
    "Accessibility and Inclusivity": "Making public spaces and services accessible to all, including individuals with disabilities, promotes an inclusive community.",
    "Waste Management and Recycling": "Implementing effective waste management and recycling programs reduces environmental impact and promotes sustainability.",
    "Water Management and Infrastructure": "Ensuring efficient water supply and managing stormwater infrastructure are crucial for urban resilience.",
    "Technology and Smart City Initiatives": "Integrating technology into city management through smart initiatives enhances efficiency and quality of life.",
}

# Define additional fake text templates for each category with more diversity
fake_text_templates = {
    "Parks and Recreation": [
        "The new community center offers a variety of classes and activities for all age groups.",
        "Urban gardens are being developed to promote local agriculture and green living.",
        "Playground equipment has been updated to include more inclusive and safe options.",
        "Regular maintenance ensures that parks remain clean and welcoming for everyone.",
        "Local sports leagues are thriving thanks to improved recreational facilities.",
        # Nuanced Templates
        "I appreciate the new playground equipment, but why aren't there more shaded areas for families?",
        "Urban gardens sound great, but the maintenance fees are skyrocketing. Is it worth it?",
        "The community center's classes are useful, but they're always fully booked. More sessions are needed.",
        "It's wonderful that parks are clean, but the lack of lighting at night makes them feel unsafe.",
        "While local sports leagues are thriving, the registration costs are too high for some residents."
    ],
    "Traffic and Pollution": [
        "Emission levels have increased despite new regulations.",
        "Residents are frustrated with the lack of progress on traffic congestion.",
        "Air quality has deteriorated due to increased industrial activities.",
        "Noise pollution is a constant issue in downtown areas.",
        "Efforts to reduce pollution have been insufficient.",
        # Nuanced Templates
        "Emission controls are tighter, but traffic still feels unbearable during rush hour.",
        "I understand the need for traffic projects, but the construction is causing more delays.",
        "Industrial activities are booming, but at what cost to our air quality?",
        "Noise pollution has gotten worse, yet the city hasn't taken effective measures to address it.",
        "Efforts to reduce pollution are commendable, but they lack the necessary funding to make a real impact."
    ],
    "Public Transport and Safety": [
        "New subway lines are being planned to connect underserved neighborhoods.",
        "Safety protocols on buses and trains have been enhanced to protect passengers.",
        "Real-time tracking apps for public transport are improving commuter experiences.",
        "Affordable fare options are being introduced to make public transport more accessible.",
        "Regular maintenance of public transport vehicles ensures reliability and safety.",
        # Nuanced Templates
        "The new subway lines are a good idea, but construction noise is disrupting our daily lives.",
        "Enhanced safety protocols are welcome, but some areas still feel unsafe during late hours.",
        "Real-time tracking is useful, but the app frequently crashes, causing frustration.",
        "Affordable fares are great, but they might lead to overcrowded buses and trains.",
        "Maintenance schedules are thorough, but the delays caused by repairs are inconvenient."
    ],
    "Cycling Infrastructure": [
        "Protected bike lanes are being constructed to ensure cyclist safety.",
        "Bike-sharing stations are expanding to cover more areas of the city.",
        "Community bike repair workshops are promoting DIY maintenance skills.",
        "Cycling events are encouraging more residents to take up biking as a mode of transport.",
        "Integration of cycling paths with public transport hubs is enhancing connectivity.",
        # Nuanced Templates
        "Protected bike lanes are a step forward, but their placement sometimes blocks pedestrian walkways.",
        "Bike-sharing is convenient, but the bikes are often in poor condition and not properly maintained.",
        "Repair workshops are helpful, but they only operate on weekends, limiting accessibility.",
        "Cycling events are fun, but they tend to exclude those who are less experienced riders.",
        "Integrating cycling paths with transport hubs is ideal, but there's still a lack of signage guiding cyclists."
    ],
    "Green Energy and Sustainability": [
        "Community solar projects are allowing residents to invest in renewable energy.",
        "Green roofs are being mandated for new buildings to improve insulation and reduce runoff.",
        "Energy-efficient street lighting is being installed across the city.",
        "Recycling programs are expanding to include electronic waste and hazardous materials.",
        "Sustainability certifications are being promoted for local businesses.",
        # Nuanced Templates
        "Community solar projects are innovative, but the initial investment costs are too high for many families.",
        "Green roof mandates are great for sustainability, but they increase construction costs significantly.",
        "Energy-efficient lighting reduces energy bills, yet some areas still experience frequent outages.",
        "Expanding recycling is necessary, but the lack of proper disposal facilities makes it challenging.",
        "Sustainability certifications are beneficial, but the application process is too cumbersome for small businesses."
    ],
    "Housing and Development": [
        "Affordable housing initiatives are addressing the needs of low-income families.",
        "Mixed-use developments are creating vibrant neighborhoods with diverse amenities.",
        "Historic buildings are being preserved while integrating modern architectural elements.",
        "Smart home technologies are being incorporated into new housing projects.",
        "Rental assistance programs are supporting residents in securing stable housing.",
        # Nuanced Templates
        "Affordable housing is essential, but the locations are often too far from essential services.",
        "Mixed-use developments bring diversity, but they sometimes lead to increased traffic and congestion.",
        "Preserving historic buildings is important, yet the integration of modern elements can disrupt the area's character.",
        "Smart home technologies are convenient, but they raise concerns about privacy and data security.",
        "Rental assistance helps many, but the application process is lengthy and complicated."
    ],
    "Education and Schools": [
        "New STEM programs are being introduced to enhance science and technology education.",
        "School facilities are being upgraded with modern classrooms and laboratories.",
        "After-school programs are providing additional learning opportunities for students.",
        "Partnerships with local businesses are offering internships and practical experiences for students.",
        "Inclusive education policies are ensuring that all students receive equitable learning opportunities.",
        # Nuanced Templates
        "STEM programs are exciting, but they overshadow the importance of arts and humanities education.",
        "Upgraded facilities are impressive, yet some schools still lack basic resources and support.",
        "After-school programs are beneficial, but they're not accessible to all students due to transportation issues.",
        "Business partnerships offer great opportunities, but they can sometimes influence the curriculum in biased ways.",
        "Inclusive policies are necessary, but proper training for educators is lacking to implement them effectively."
    ],
    "Public Safety and Security": [
        "Neighborhood watch programs are increasing community involvement in safety.",
        "Emergency response times are being reduced through improved coordination.",
        "Surveillance systems are being upgraded to enhance public security.",
        "Disaster preparedness drills are educating residents on how to respond to emergencies.",
        "Mental health resources are being integrated into public safety strategies.",
        # Nuanced Templates
        "Neighborhood watch programs foster community spirit, but they sometimes lead to increased tensions with law enforcement.",
        "Reduced emergency response times are crucial, yet some areas still experience delays due to traffic.",
        "Upgraded surveillance improves security, but it raises concerns about privacy invasion.",
        "Disaster drills are informative, but they're often too infrequent to ensure preparedness.",
        "Integrating mental health into safety strategies is commendable, but the resources allocated are insufficient to meet demand."
    ],
    "Economic Development": [
        "Incentives for startups are fostering innovation and job creation.",
        "Local marketplaces are being revitalized to support small businesses.",
        "Tourism campaigns are highlighting the city's unique attractions to attract visitors.",
        "Workforce training programs are equipping residents with skills needed for emerging industries.",
        "Public-private partnerships are driving large-scale economic projects.",
        # Nuanced Templates
        "Startup incentives boost innovation, but they can sometimes lead to market saturation and competition issues.",
        "Revitalizing marketplaces is positive, yet some long-standing businesses struggle to adapt to new changes.",
        "Tourism campaigns attract visitors, but they also contribute to overcrowding in popular areas.",
        "Workforce training is essential, but the programs often lack up-to-date curricula to match industry needs.",
        "Public-private partnerships fund large projects, but they can lead to prioritizing profit over community benefits."
    ],
    "Healthcare Facilities": [
        "New clinics are being established to provide accessible healthcare in all neighborhoods.",
        "Telemedicine services are expanding to offer remote consultations for residents.",
        "Mental health facilities are receiving increased funding and support.",
        "Health education programs are promoting preventive care and wellness initiatives.",
        "Specialized medical services are being introduced to address diverse health needs.",
        # Nuanced Templates
        "New clinics improve access, but some are understaffed, leading to longer wait times.",
        "Telemedicine is convenient, yet it lacks the personal touch of in-person consultations.",
        "Increased funding for mental health is necessary, but stigma still prevents many from seeking help.",
        "Preventive care programs are valuable, but their reach is limited in underserved communities.",
        "Specialized services address diverse needs, but they often come with higher costs that are unaffordable for some residents."
    ],
    "Cultural Heritage and Events": [
        "Restoration projects are preserving historical landmarks for future generations.",
        "Annual festivals are celebrating the city's diverse cultural heritage.",
        "Art installations in public spaces are enhancing the city's aesthetic appeal.",
        "Cultural exchange programs are fostering international relationships and understanding.",
        "Local museums are expanding their exhibits to include contemporary art and history.",
        # Nuanced Templates
        "Restoration preserves history, but it can limit modern development and expansion opportunities.",
        "Annual festivals are enjoyable, yet they sometimes disrupt local businesses and traffic.",
        "Public art installations beautify the city, but they can be controversial regarding artistic choices.",
        "Cultural exchanges are enriching, but they require significant funding and coordination to be effective.",
        "Expanding museum exhibits is great, but maintaining and updating them poses financial challenges."
    ],
    "Accessibility and Inclusivity": [
        "Public buildings are being retrofitted with ramps and elevators for better accessibility.",
        "Inclusive playgrounds are being designed to accommodate children with disabilities.",
        "Language translation services are being offered in public institutions to support non-native speakers.",
        "Community centers are hosting events that cater to diverse cultural groups.",
        "Accessible public transportation options are being developed to support all residents.",
        # Nuanced Templates
        "Retrofitting buildings improves accessibility, but it's often costly and time-consuming.",
        "Inclusive playgrounds are necessary, yet they require regular maintenance to remain functional for all children.",
        "Translation services help non-native speakers, but they aren't available in all public institutions.",
        "Diverse community events are welcoming, but they sometimes lack representation from all cultural groups.",
        "Accessible transportation is essential, but the routes still don't cover all areas adequately."
    ],
    "Waste Management and Recycling": [
        "Composting programs are being introduced to reduce organic waste.",
        "Recycling bins are being strategically placed in high-traffic areas for convenience.",
        "Public education campaigns are raising awareness about proper waste sorting.",
        "Waste-to-energy facilities are being explored as a sustainable disposal method.",
        "Bulk waste collection days are scheduled to manage large items effectively.",
        # Nuanced Templates
        "Composting reduces waste, but many residents lack the knowledge to participate correctly.",
        "Strategically placed recycling bins are helpful, yet they are sometimes neglected and contaminated with non-recyclables.",
        "Education campaigns are informative, but they need to be more engaging to change long-term behaviors.",
        "Waste-to-energy is sustainable, but it raises concerns about emissions and environmental impact.",
        "Bulk waste days are convenient, but the limited scheduling makes it difficult for some families to participate."
    ],
    "Water Management and Infrastructure": [
        "Rainwater harvesting systems are being implemented in residential areas.",
        "Upgrades to the water supply network are ensuring clean and reliable access for all.",
        "Flood prevention measures are being enhanced to protect vulnerable neighborhoods.",
        "Smart water meters are being installed to monitor and optimize usage.",
        "Public awareness campaigns are educating residents on water conservation techniques.",
        # Nuanced Templates
        "Rainwater harvesting is eco-friendly, but installation costs are prohibitive for some homeowners.",
        "Water supply upgrades improve reliability, yet construction can lead to temporary shortages and disruptions.",
        "Flood prevention is crucial, but the allocated budget doesn't cover all high-risk areas adequately.",
        "Smart meters help optimize usage, but privacy concerns arise regarding data collection and monitoring.",
        "Conservation campaigns are necessary, but they need to provide practical tips that residents can easily implement."
    ],
    "Technology and Smart City Initiatives": [
        "Smart lighting systems are reducing energy consumption and enhancing security.",
        "IoT devices are being used to monitor and manage city infrastructure in real-time.",
        "High-speed internet access is being expanded to bridge the digital divide.",
        "Data analytics are improving urban planning and resource allocation.",
        "Autonomous public transport options are being piloted to increase efficiency.",
        # Nuanced Templates
        "Smart lighting cuts energy costs, but the initial installation is expensive and disruptive.",
        "IoT devices enhance infrastructure management, yet they increase the city's vulnerability to cyberattacks.",
        "Expanding high-speed internet is essential, but some rural areas still remain underserved.",
        "Data analytics aid urban planning, but concerns about data privacy and surveillance are growing.",
        "Autonomous transport is efficient, but it raises questions about job losses in the driving sector."
    ],
}

"""""
posts = []
for _ in range(1000):
    topic = random.choice(list(topics.keys()))
    template = random.choice(fake_text_templates[topic])
    post = f"{topic} {template}"
    posts.append(post)

data = {
    "post_id": list(range(1, 1001)),
    "user_post": posts,
}
"""
# Load your data from CSV
# Load your data from CSV
df = pd.read_csv('my_fake_data.csv')

# Ensure the DataFrame has the required columns
# Adjust column names if necessary
df = df[['post_id', 'user_post']]



# Convert to DataFrame
#df = pd.DataFrame(data)

# Text Preprocessing and Feature Extraction using TF-IDF with bi-grams
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_features=500
)
X = vectorizer.fit_transform(df["user_post"])

# Apply Fuzzy C-Means Clustering
n_clusters = 15
fcm = FCM(n_clusters=n_clusters, random_state=42)
fcm.fit(X.toarray())

# Retrieve fuzzy membership degrees
fuzzy_labels = fcm.u

# Assign clusters based on highest membership degree
df["cluster"] = fcm.predict(X.toarray())

# Add membership degrees to DataFrame
membership_df = pd.DataFrame(fuzzy_labels, columns=[f'cluster_{i+1}_membership' for i in range(n_clusters)])
df = pd.concat([df, membership_df], axis=1)

cluster_labels = {
    0: "Parks and Recreation",
    1: "Traffic and Pollution",
    2: "Public Transport and Safety",
    3: "Cycling Infrastructure",
    4: "Green Energy and Sustainability",
    5: "Housing and Development",
    6: "Education and Schools",
    7: "Public Safety and Security",
    8: "Economic Development",
    9: "Healthcare Facilities",
    10: "Cultural Heritage and Events",
    11: "Accessibility and Inclusivity",
    12: "Waste Management and Recycling",
    13: "Water Management and Infrastructure",
    14: "Technology and Smart City Initiatives",
}

# Map cluster numbers to labels
df['cluster_label'] = df['cluster'].map(lambda x: cluster_labels.get(x, "Unknown"))

# Text Preprocessing and Feature Extraction
vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=500)
X = vectorizer.fit_transform(df["user_post"])

# Retrieve fuzzy membership degrees
fuzzy_labels = fcm.u

# Assign clusters based on highest membership degree
df["cluster"] = fcm.predict(X.toarray())

# Add membership degrees to DataFrame
membership_df = pd.DataFrame(fuzzy_labels, columns=[f'cluster_{i}_membership' for i in range(n_clusters)])
df = pd.concat([df, membership_df], axis=1)


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

# Function to generate word cloud
def generate_wordcloud(terms, cluster_label):
    text = ' '.join(terms)
    wordcloud = WordCloud(width=400, height=200, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Cluster {cluster_label + 1} Word Cloud')
    plt.show()

## Generate word clouds
##for cluster, terms in top_terms.items():
  ##  generate_wordcloud(terms, cluster)

# Display the number of posts in each cluster
cluster_counts = df['cluster'].value_counts().sort_index()
for cluster_num, count in cluster_counts.items():
    print(f"Cluster {cluster_num + 1}: {count} posts")

# Function to get sample posts with handling for small clusters
def get_sample_posts(df, cluster_label, sample_size=5):
    cluster_posts = df[df['cluster'] == cluster_label]['user_post']
    available_posts = len(cluster_posts)
    
    if available_posts == 0:
        return ["No posts available in this cluster."]
    elif available_posts < sample_size:
        print(f"Cluster {cluster_label + 1} has only {available_posts} posts. Sampling all available posts.")
        return cluster_posts.tolist()
    else:
        return cluster_posts.sample(n=sample_size, random_state=42).tolist()

# Display sample posts for each cluster
for cluster in range(n_clusters):
    print(f"\n--- Cluster {cluster}: {cluster_labels[cluster]} Sample Posts ---")
    sample_posts = get_sample_posts(df, cluster, sample_size=5)
    for post in sample_posts:
        print(f"- {post}")

# Perform Fuzzy Sentiment Analysis
# Function to get sentiment scores
def get_sentiment_scores(text):
    scores = sia.polarity_scores(text)
    return scores  # Returns a dictionary with 'neg', 'neu', 'pos', and 'compound'

# Apply sentiment analysis to each post
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

# Display the DataFrame with sentiment scores
print(df[['post_id', 'user_post', 'cluster_label', 'pos', 'neg', 'neu', 'compound', 'positive_membership', 'negative_membership', 'neutral_membership']].head())

# Visualize Overall Sentiment Distribution
sentiment_columns = ['positive_membership', 'negative_membership', 'neutral_membership']
df[sentiment_columns].mean().plot(kind='bar', color=['green', 'red', 'gray'])
plt.title('Average Sentiment Membership Degrees')
plt.ylabel('Average Membership Degree')
plt.xticks(ticks=range(len(sentiment_columns)), labels=['Positive', 'Negative', 'Neutral'], rotation=0)
plt.show()

# Calculate average sentiment scores per cluster
sentiment_per_cluster = df.groupby('cluster_label')[sentiment_columns].mean()

# Plot sentiment distribution per cluster
sentiment_per_cluster.plot(kind='bar', figsize=(12, 8))
plt.title('Average Sentiment Membership Degrees per Cluster')
plt.ylabel('Average Membership Degree')
plt.xticks(rotation=45)
plt.legend(title='Sentiment')
plt.show()

tsne = TSNE(n_components=2, random_state=42)
reduced_data = tsne.fit_transform(X.toarray())

plt.figure(figsize=(12, 8))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=df['cluster'], cmap='tab20', alpha=0.6)
plt.title("Cluster Visualization")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.colorbar(label='Cluster')
plt.show()

# Example: Print sentiment summary
print("\nSentiment Summary per Cluster:")
print(sentiment_per_cluster)
""""
sentiment_pipeline = pipeline("sentiment-analysis")

def get_sentiment_scores(text):
    result = sentiment_pipeline(text)[0]
    if result['label'] == 'POSITIVE':
        return {'neg': 0.0, 'neu': 0.0, 'pos': result['score'], 'compound': result['score']}
    else:
        return {'neg': result['score'], 'neu': 0.0, 'pos': 0.0, 'compound': -result['score']}

df['sentiment_scores'] = df['user_post'].apply(get_sentiment_scores)
"""
# Optional: Save the clustered and sentiment-analyzed data to a CSV for further analysis
df.to_csv("clustered_and_sentiment_forum_posts.csv", index=False)
