import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
print("Loading sentence-transformer model...")
# Chota aur tez model
model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = [
    # Topic 1: AI & Technology (14 sentences)
    "Artificial intelligence is transforming industries.",
    "Machine learning algorithms find patterns in data.",
    "Neural networks are inspired by the human brain.",
    "Deep learning models require powerful GPUs to train.",
    "Python is the preferred language for data science.",
    "Large language models can generate human-like text.",
    "Self-driving cars use computer vision to navigate.",
    "Robotics combines software with hardware engineering.",
    "Natural language processing helps computers understand speech.",
    "Generative AI can write code and create beautiful art.",
    "Data privacy is a major concern in cloud computing.",
    "Supervised learning uses labeled datasets for training.",
    "Reinforcement learning is based on rewards and penalties.",
    "Quantum computing could solve complex mathematical problems.",

    # Topic 2: Cooking & Food (13 sentences)
    "Baking sourdough bread requires patience and a starter.",
    "Italian pasta is best cooked al dente.",
    "Fresh herbs like basil and oregano elevate any dish.",
    "A sharp chef knife makes prep work much safer.",
    "Slow cooking meat makes it incredibly tender.",
    "Spices should be toasted to release their essential oils.",
    "Olive oil is a staple of the healthy Mediterranean diet.",
    "Fermenting vegetables at home creates natural probiotics.",
    "Grilling steaks over charcoal adds a smoky flavor.",
    "Baking cookies fills the kitchen with a sweet aroma.",
    "A perfect omelet is cooked over low heat with butter.",
    "Making sushi requires high-quality vinegared rice.",
    "Homemade tomato sauce tastes much better than canned ones.",

    # Topic 3: Sports & Fitness (13 sentences)
    "Running daily builds cardiovascular endurance.",
    "Strength training helps maintain healthy muscle mass.",
    "The football world cup attracts billions of viewers.",
    "Yoga improves flexibility and mental focus.",
    "Swimming is a great low-impact full-body workout.",
    "Proper hydration is key during long marathons.",
    "The basketball team won the championship game.",
    "Tennis players need excellent hand-eye coordination.",
    "Cycling is a great way to explore the outdoors.",
    "High-intensity interval training burns calories quickly.",
    "Athletes use recovery days to prevent muscle injuries.",
    "Cricket matches require strategy and physical stamina.",
    "Gymnastics demands incredible balance and core strength."
]

print(f"Generating embeddings for {len(sentences)} sentences...")
embeddings = model.encode(sentences, convert_to_numpy=True)

inspection_data = {
    "sentences": sentences,
    "embeddings": embeddings.tolist() 
}

os.makedirs("inspection", exist_ok=True)
with open("inspection/embeddings_data.json", "w") as f:
    json.dump(inspection_data, f, indent=4)
print("Saved embeddings to 'inspection/embeddings_data.json' for inspection!")

def cosine_similarity(v1, v2):
    """Calculates the cosine similarity between two vectors."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def tiny_semantic_search(query, top_k=3):
    """Searches the 40 sentences and returns top K matches with scores."""
    query_embedding = model.encode(query, convert_to_numpy=True)
    
    results = []
    for idx, doc_emb in enumerate(embeddings):
        score = cosine_similarity(query_embedding, doc_emb)
        results.append((sentences[idx], score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
if __name__ == "__main__":
    print("\n" + "="*50)
    print("RUNNING DAY 8 TEST CASES")
    print("="*50)

    # Target in data: "Running daily builds cardiovascular endurance."
    test_query_1 = "jogging every morning improves heart health" 
    
    print(f"\nQuery 1: '{test_query_1}'")
    print("----------------------------------------")
    matches = tiny_semantic_search(test_query_1, top_k=3)
    for rank, (text, score) in enumerate(matches, 1):
        print(f"Rank {rank}: [Score: {score:.4f}] -> {text}")  
    # Target in data: "A sharp chef knife makes prep work much safer."
    test_query_2 = "cooking tools that are dangerous when dull"
    
    print(f"\nQuery 2: '{test_query_2}'")
    print("----------------------------------------")
    matches_2 = tiny_semantic_search(test_query_2, top_k=3)
    for rank, (text, score) in enumerate(matches_2, 1):
        print(f"Rank {rank}: [Score: {score:.4f}] -> {text}")


    print("\n" + "="*50)
    print("DEMONSTRATING A FAILURE CASE")
    print("="*50)
    failure_query = "I need a starter for my sourdough bread"
    print(f"Query: '{failure_query}'")
    print("Expected Match: 'Baking sourdough bread requires patience and a starter.'")
    print("----------------------------------------")
    
    failure_matches = tiny_semantic_search(failure_query, top_k=3)
    for rank, (text, score) in enumerate(failure_matches, 1):
        print(f"Rank {rank}: [Score: {score:.4f}] -> {text}")
        
    print("\n*Why this is a failure/struggle case:*")
    print("Though it retrieved the correct sourdough sentence at Rank 1, if we queried ")
    print("'how to get a starter for my car', the model might still suggest baking ")
    print("because 'starter' is highly linked to sourdough in this small dataset, ")
    print("showing how polysemy (words with multiple meanings) can confuse models without enough context.")
    if HAS_VISUALIZATION:
        print("\n" + "="*50)
        print("VISUALIZING EMBEDDINGS (2D PCA)")
        print("="*50)
        print("Generating PCA plot...")
        pca = PCA(n_components=2)
        embeddings_2d = pca.fit_transform(embeddings)
        
        plt.figure(figsize=(10, 8))
        plt.scatter(embeddings_2d[:14, 0], embeddings_2d[:14, 1], color='blue', label='AI & Tech', s=100)
        plt.scatter(embeddings_2d[14:27, 0], embeddings_2d[14:27, 1], color='green', label='Cooking & Food', s=100)
        plt.scatter(embeddings_2d[27:, 0], embeddings_2d[27:, 1], color='red', label='Sports & Fitness', s=100)
        
        plt.title("2D Projection of Day 8 Sentence Embeddings")
        plt.xlabel("PCA Component 1")
        plt.ylabel("PCA Component 2")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plot_path = "inspection/embeddings_visualization.png"
        plt.savefig(plot_path)
        print(f"Visualization saved to '{plot_path}'! Open it to see how different topics cluster together.")
    else:
        print("\nInstall 'matplotlib' and 'scikit-learn' to visualize embeddings in 2D.")