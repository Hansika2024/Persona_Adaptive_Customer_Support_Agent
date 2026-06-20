import os
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# Load environment variables
load_dotenv()

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="support_kb")


# -----------------------------
# 1. Load documents
# -----------------------------
def load_documents(data_folder="data"):
    documents = []

    for file in os.listdir(data_folder):
        filepath = os.path.join(data_folder, file)

        # TXT and MD files
        if file.endswith(".txt") or file.endswith(".md"):
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
                documents.append({
                    "source": file,
                    "content": text
                })

        # PDF files
        elif file.endswith(".pdf"):
            reader = PdfReader(filepath)

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    documents.append({
                        "source": file,
                        "page": page_num + 1,
                        "content": text
                    })

    return documents


# -----------------------------
# 2. Split documents into chunks
# -----------------------------
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = []

    for doc in documents:
        split_texts = splitter.split_text(doc["content"])

        for idx, chunk in enumerate(split_texts):
            chunks.append({
                "id": f"{doc['source']}_{len(chunks)}",
                "text": chunk,
                "source": doc["source"]
            })

    return chunks


# -----------------------------
# 3. Store embeddings in ChromaDB
# -----------------------------
def store_embeddings(chunks):
    ids = []
    texts = []
    embeddings = []
    metadatas = []

    for chunk in chunks:
        embedding = embedding_model.encode(chunk["text"]).tolist()

        ids.append(chunk["id"])
        texts.append(chunk["text"])
        embeddings.append(embedding)
        metadatas.append({
            "source": chunk["source"]
        })

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("Embeddings stored successfully.")


# -----------------------------
# 4. Retrieve relevant chunks
# -----------------------------
def retrieve_chunks(query, top_k=3):
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []

    for i in range(len(results["documents"][0])):
        distance = results["distances"][0][i]

        retrieved.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": distance,
            "score": 1 - distance
        })

    return retrieved


# -----------------------------
# Main function for testing
# -----------------------------
if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")

    chunks = split_documents(docs)
    print(f"Created {len(chunks)} chunks")

    if collection.count() == 0:
        store_embeddings(chunks)
    else:
        print("Embeddings already exist in ChromaDB.")

    query = "How do I reset my password?"
    results = retrieve_chunks(query)

    print("\nTop Retrieved Results:")
    for idx, result in enumerate(results, 1):
        print(f"\nResult {idx}")
        print("Source:", result["source"])
        print("Score:", result["score"])
        print("Text:", result["text"][:300])