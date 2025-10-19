import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer 
from PyPDF2 import PdfReader

# Load environment variables from .env file
load_dotenv()

# Check if OpenAI library is available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    # Print warning if library is missing
    print("Warning: OpenAI library not installed. Run 'pip install openai' for LLM response.")
    OPENAI_AVAILABLE = False

# Determine the base directory and setup file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define PDF File Paths (All 3 categories included)
PDF_PATHS = {
    "doc1": os.path.join(BASE_DIR, '..', 'pdfs', 'pdf1.pdf'),
    "doc2": os.path.join(BASE_DIR, '..', 'pdfs', 'pdf2.pdf'),
    "doc3": os.path.join(BASE_DIR, '..', 'pdfs', 'pdf3.pdf')
}

# -------------------------------
# 1️⃣ ChromaDB Setup
# -------------------------------
# Use an in-memory ChromaDB instance
client = chromadb.Client()
collection_name = "rag_demo_collection"

# Delete and recreate the collection for fresh start
try:
    client.delete_collection(collection_name)
    # print(f"Collection '{collection_name}' deleted.")
except Exception:
    pass

# -------------------------------
# 2️⃣ Embedding Model (DÜZELTME BAŞLANGICI)
# -------------------------------
# Sentence-transformer yükleniyor (hızlı ve verimli bir model)
# Model adını kullanarak ChromaDB için bir gömme fonksiyonu oluşturuyoruz
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Collection'ı oluştururken embedding_function'ı parametre olarak veriyoruz
collection = client.create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}, # Kosinüs mesafesi (distance) kullanılıyor: 0.0 en iyi eşleşme
    embedding_function=embedding_function 
)

# -------------------------------
# 3️⃣ PDF Reading + Chunk Creation
# -------------------------------
def read_pdf_chunks(file_path, category, chunk_size=300):
    """Reads PDF file, extracts text, and creates chunks."""
    if not os.path.exists(file_path):
        # print(f"ERROR: PDF file not found: {file_path}")
        return []

    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            # Extract text and normalize spaces
            page_text = page.extract_text()
            if page_text:
                text += ' '.join(page_text.split()).strip() + " "
        
        # Simple chunking by character size
        chunks = []
        doc_id_prefix = os.path.basename(file_path).split('.')[0]
        
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i+chunk_size].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "category": category,
                        "source_file": os.path.basename(file_path),
                        "chunk_id": f"{doc_id_prefix}_{i//chunk_size}"
                    }
                })
        return chunks
    except Exception as e:
        # print(f"PDF reading error ({file_path}): {e}")
        return []


# -------------------------------
# 4️⃣ Load PDF Files
# -------------------------------
pdf_files = PDF_PATHS # Uses all 3 categories

all_chunks = []
pdf_found_count = 0
for category, path in pdf_files.items():
    chunks = read_pdf_chunks(path, category)
    if chunks:
        pdf_found_count += 1
        # print(f"   > Read {len(chunks)} chunks from '{category}' category.")
    all_chunks.extend(chunks)

# -------------------------------
# 5️⃣ Add to ChromaDB
# -------------------------------
if all_chunks:
    texts = [c["text"] for c in all_chunks]
    metadatas = [c["metadata"] for c in all_chunks]
    ids = [c["metadata"]["chunk_id"] for c in all_chunks]

    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ {pdf_found_count} PDFs loaded, {len(all_chunks)} total chunks added to ChromaDB!")
else:
    print("❌ No chunks found. Please ensure 'pdfs/pdf1.pdf', 'pdfs/pdf2.pdf', and 'pdfs/pdf3.pdf' exist.")


# -------------------------------
# 6️⃣ Vector DB Search Function
# -------------------------------
def search_vector_db(query, top_k=1):
    """Searches the vector database for the given query and returns the closest document."""
    # Check if the collection has any data
    if collection.count() == 0:
        return None

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    # Return None if results are empty
    if not results['documents'] or not results['documents'][0]:
        return None
    
    best_doc = {
        'id': results['ids'][0][0],
        'text': results['documents'][0][0],
        # Lower score (distance) means better match.
        'score': results['distances'][0][0], 
        'metadata': results['metadatas'][0][0]
    }
    
    return best_doc

# -------------------------------
# 7️⃣ OpenAI Response Function
# -------------------------------
def answer_with_openai(prompt):
    """Generates a response using the OpenAI API."""
    if not OPENAI_AVAILABLE:
        return "❌ OpenAI library is not installed."
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "❌ OPENAI_API_KEY environment variable not found. Please check your .env file."
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. ABSOLUTELY use the provided CONTEXT information to answer the questions. If the answer is not in the context, state: 'Üzgünüm, bu bilgi bağlamda bulunamadı.' You are knowledgeable about Sports, Culture, and Economy."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400, # Increased token count for longer answers
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API error: {str(e)}"

# -------------------------------
# 8️⃣ RAG Prompt Creation
# -------------------------------
def create_rag_prompt(query, context):
    """Creates a prompt for the LLM that includes context information."""
    prompt = f"""Aşağıdaki BAĞLAM bilgisini kullanarak, SORU'yu yanıtla.

BAĞLAM: {context['text']}

SORU: {query}

YANIT:"""
    return prompt

# -------------------------------
# 9️⃣ RAG Pipeline
# -------------------------------
def rag_pipeline(query, use_openai=False):
    """The main RAG pipeline."""
    context = search_vector_db(query)
    
    if not context:
        return {
            "query": query,
            "context": None,
            "prompt": None,
            "response": "❌ Database is empty. Please ensure your PDF files are read and added to ChromaDB."
        }

    # Cosine Distance check
    DISSIMILARITY_THRESHOLD = 0.5 
    
    if context['score'] > DISSIMILARITY_THRESHOLD:
        return {
            "query": query,
            "context": context,
            "prompt": None,
            # Updated list of categories
            "response": f"Üzgünüm, ben sadece Spor, Kültür ve Ekonomi konuları üzerinden bilgi verebilirim. Sorgunuz mevcut belgelerle (Skor: {context['score']:.3f}) eşleşmiyor."
        }
    
    prompt = create_rag_prompt(query, context)
    
    if use_openai:
        response = answer_with_openai(prompt)
    else:
        # Return a demo response if LLM is off
        response = f"""🤖 DEMO YANITI (LLM KAPALI)

Bu, bulduğum en alakalı bağlamdır. Eğer LLM açık olsaydı, aşağıdaki bağlamı kullanarak yanıt oluşturacaktı:

**En Alakalı Belge:** {context['id']} ({context['metadata']['category']})
**Mesafe Skoru (Daha Düşük Daha İyi):** {context['score']:.3f}
**İçerik:** ---
{context['text'][:500]}...
---
"""
    return {
        "query": query,
        "context": context,
        "prompt": prompt,
        "response": response
    }

# -------------------------------
# 10️⃣ Demo Test
# -------------------------------
if __name__ == "__main__":
    test_queries = [
        "Futbolun stratejik dizilişleri nelerdir?",
        "Türk kahve ritüelleri hakkında bilgi ver",
        "Enflasyonu kontrol etme yöntemleri nelerdir?",
        "Kuru fasulye tarifi ver"
    ]
    
    api_key = os.getenv('OPENAI_API_KEY')
    use_real_llm = api_key is not None and OPENAI_AVAILABLE
    
    if use_real_llm:
        print("✅ OpenAI API Key Found. Generating response with real LLM.")
    else:
        print("⚠️ OpenAI API Key Not Found or Library Missing. Using demo response.")

    for q in test_queries:
        print(f"\n" + "="*50)
        print(f"🔍 Query: {q}")
        result = rag_pipeline(q, use_openai=use_real_llm)
        print("\n" + result['response'])
        print("="*50)