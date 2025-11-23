"""
RAG Pipeline Module
Handles knowledge chunking, embedding generation, and vector store management
for context blueprints and knowledge data.
"""

import json
import textwrap

import tiktoken
from dotenv import load_dotenv
from rich import print
from embeddingsUtiles import load_embedding_model
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

# Constants
NAMESPACE_KNOWLEDGE = "KnowledgeStore"
NAMESPACE_CONTEXT = "ContextLibrary"
CHUNK_SIZE = 100
OVERLAP = 20


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """
    Chunks text based on token count with overlap for RAG.

    Args:
        text: Input text to chunk
        chunk_size: Maximum tokens per chunk
        overlap: Number of overlapping tokens between chunks

    Returns:
        List of text chunks
    """
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunk_text = chunk_text.replace("\n", " ").strip()
        if chunk_text:
            chunks.append(chunk_text)

    return chunks


def create_context_blueprints():
    """Creates and returns context blueprint definitions."""
    return [
        {
            "id": "blueprint_suspense_narrative",
            "description": "A precise Semantic Blueprint designed to generate suspenseful and tense narratives, suitable for children's stories. Focuses on atmosphere, perceived threats, and emotional impact. Ideal for creative writing.",
            "blueprint": json.dumps({
                "scene_goal": "Increase tension and create suspense.",
                "style_guide": "Use short, sharp sentences. Focus on sensory details (sounds, shadows). Maintain a slightly eerie but age-appropriate tone.",
                "participants": [
                    {"role": "Agent", "description": "The protagonist experiencing the events."},
                    {"role": "Source_of_Threat", "description": "The underlying danger or mystery."}
                ],
                "instruction": "Rewrite the provided facts into a narrative adhering strictly to the scene_goal and style_guide."
            })
        },
        {
            "id": "blueprint_technical_explanation",
            "description": "A Semantic Blueprint designed for technical explanation or analysis. This blueprint focuses on clarity, objectivity, and structure. Ideal for breaking down complex processes, explaining mechanisms, or summarizing scientific findings.",
            "blueprint": json.dumps({
                "scene_goal": "Explain the mechanism or findings clearly and concisely.",
                "style_guide": "Maintain an objective and formal tone. Use precise terminology. Prioritize factual accuracy and clarity over narrative flair.",
                "structure": ["Definition", "Function/Operation", "Key Findings/Impact"],
                "instruction": "Organize the provided facts into the defined structure, adhering to the style_guide."
            })
        },
        {
            "id": "blueprint_casual_summary",
            "description": "A goal-oriented context for creating a casual, easy-to-read summary. Focuses on brevity and accessibility, explaining concepts simply.",
            "blueprint": json.dumps({
                "scene_goal": "Summarize information quickly and casually.",
                "style_guide": "Use informal language. Keep it brief and engaging. Imagine explaining it to a friend.",
                "instruction": "Summarize the provided facts using the casual style guide."
            })
        }
    ]


def prepare_context_vectors(context_blueprints):
    """
    Prepares context vectors from blueprint definitions.

    Args:
        context_blueprints: List of context blueprint dictionaries

    Returns:
        List of vector dictionaries with metadata
    """
    vectors_context = []
    for item in context_blueprints:
        vectors_context.append({
            "id": item["id"],
            "metadata": {
                "description": item["description"],
                "blueprint_json": item["blueprint"]
            }
        })
    return vectors_context


def create_context_vector_store(vectors_context, embedding_model):
    """
    Creates Chroma vector store for context blueprints.

    Args:
        vectors_context: List of context vectors
        embedding_model: Embedding model instance

    Returns:
        Chroma vector store instance
    """
    context_texts = [vc["metadata"]["description"] for vc in vectors_context]
    context_metadata = [
        {"id": vc["id"], "blueprint_json": vc["metadata"]["blueprint_json"]}
        for vc in vectors_context
    ]

    return Chroma.from_texts(
        texts=context_texts,
        embedding=embedding_model,
        metadatas=context_metadata,
        collection_name=NAMESPACE_CONTEXT
    )


def get_knowledge_data():
    """Returns raw knowledge data for processing."""
    return """
    Space exploration is the use of astronomy and space technology to explore outer space. The early era of space exploration was driven by a "Space Race" between the Soviet Union and the United States. The launch of the Soviet Union's Sputnik 1 in 1957, and the first Moon landing by the American Apollo 11 mission in 1969 are key landmarks.

    The Apollo program was the United States human spaceflight program carried out by NASA which succeeded in landing the first humans on the Moon. Apollo 11 was the first mission to land on the Moon, commanded by Neil Armstrong and lunar module pilot Buzz Aldrin, with Michael Collins as command module pilot. Armstrong's first step onto the lunar surface occurred on July 20, 1969, and was broadcast on live TV worldwide. The landing required Armstrong to take manual control of the Lunar Module Eagle due to navigational challenges and low fuel.

    Juno is a NASA space probe orbiting the planet Jupiter. It was launched on August 5, 2011, and entered a polar orbit of Jupiter on July 5, 2016. Juno's mission is to measure Jupiter's composition, gravitational field, magnetic field, and polar magnetosphere to understand how the planet formed. Juno is the second spacecraft to orbit Jupiter, after the Galileo orbiter. It is uniquely powered by large solar arrays instead of RTGs (Radioisotope Thermoelectric Generators), making it the farthest solar-powered mission.

    A Mars rover is a remote-controlled motor vehicle designed to travel on the surface of Mars. NASA JPL managed several successful rovers including: Sojourner, Spirit, Opportunity, Curiosity, and Perseverance. The search for evidence of habitability and organic carbon on Mars is now a primary NASA objective. Perseverance also carried the Ingenuity helicopter.
    """


def prepare_knowledge_vectors(knowledge_chunks):
    """
    Prepares knowledge vectors from text chunks.

    Args:
        knowledge_chunks: List of text chunks

    Returns:
        List of vector dictionaries with metadata
    """
    batch_vectors = []
    for chunk_id, chunk in enumerate(knowledge_chunks):
        batch_vectors.append({
            "id": chunk_id,
            "metadata": {"text": chunk}
        })
    return batch_vectors


def create_knowledge_vector_store(batch_vectors, embedding_model):
    """
    Creates Chroma vector store for knowledge chunks.

    Args:
        batch_vectors: List of knowledge vectors
        embedding_model: Embedding model instance

    Returns:
        Chroma vector store instance
    """
    knowledge_texts = [item['metadata']['text'] for item in batch_vectors]
    knowledge_metadata = [{'id': str(item['id'])} for item in batch_vectors]

    return Chroma.from_texts(
        texts=knowledge_texts,
        embedding=embedding_model,
        metadatas=knowledge_metadata,
        collection_name=NAMESPACE_KNOWLEDGE
    )


def display_vector_store_records(vector_store, namespace):
    """
    Fetches and displays all records from a vector store.

    Args:
        vector_store: Chroma vector store instance
        namespace: Name of the collection for display
    """
    all_records = vector_store.get(include=['embeddings', 'documents', 'metadatas'])

    print(f"\n=== Total Records in {namespace}: {len(all_records['ids'])} ===\n")

    for i, (doc_id, text, metadata, embedding) in enumerate(
            zip(all_records['ids'], all_records['documents'],
                all_records['metadatas'], all_records['embeddings'])):
        print(f"--- Record {i + 1} ---")
        print(f"ID: {doc_id}")
        print(f"Text: {text[:200]}...")
        print(f"Metadata: {metadata}")
        print(f"Embedding (first 10 dimensions): {embedding[:10]}")
        print(f"Embedding dimension: {len(embedding)}")
        print()

def create_mcp_message(sender, content, metadata=None):
    """Creates a standardized MCP message (Educational Version)."""
    return {
        "protocol_version": "1.1 (RAG-Enhanced)",
        "sender": sender,
        "content": content,
        "metadata": metadata or {}
    }


def display_mcp(message, title="MCP Message"):
    """Helper function to display MCP messages clearly during the trace."""
    print(f"\n--- {title} (Sender: {message['sender']}) ---")
    # Display content snippet or keys if content is complex
    if isinstance(message['content'], dict):
         print(f"Content Keys: {list(message['content'].keys())}")
    else:
        print(f"Content: {textwrap.shorten(str(message['content']), width=100)}")
    # Display metadata keys
    print(f"Metadata Keys: {list(message['metadata'].keys())}")
    print("-" * (len(title) + 25))

def query_chroma(query_text, NAMESPACE_CONTEXT, top_k):
    """Embeds the query text and searches the specified Pinecone namespace."""
    try:
        index = Chroma(collection_name=NAMESPACE_CONTEXT)

        query_embedding = get_embedding(query_text)
        response = index.query(
            vector=query_embedding,
            namespace=namespace,
            top_k=top_k,
            include_metadata=True
        )
        return response['matches']
    except Exception as e:
        print(f"Error querying Pinecone (Namespace: {namespace}): {e}")
        return []


def agent_context_librarian(mcp_message):
    """
    Retrieves the appropriate Semantic Blueprint from the Context Library.
    """
    print("\n[Librarian] Activated. Analyzing intent...")
    requested_intent = mcp_message['content']['intent_query']

    # Query Pinecone Context Namespace
    results = query_chroma(requested_intent, NAMESPACE_CONTEXT, top_k=1)

    if results:
        match = results[0]
        print(f"[Librarian] Found blueprint '{match['id']}' (Score: {match['score']:.2f})")
        # Retrieve the blueprint JSON string stored in metadata
        blueprint_json = match['metadata']['blueprint_json']
        content = {"blueprint": blueprint_json}
    else:
        print("[Librarian] No specific blueprint found. Returning default.")
        # Fallback default
        content = {"blueprint": json.dumps({"instruction": "Generate the content neutrally."})}

    return create_mcp_message("Librarian", content)

# === 4.2. Researcher Agent (Factual RAG) ===
def agent_researcher(mcp_message):
    """
    Retrieves and synthesizes factual information from the Knowledge Base.
    """
    print("\n[Researcher] Activated. Investigating topic...")
    topic = mcp_message['content']['topic_query']

    # Query Pinecone Knowledge Namespace
    results = query_chroma(topic, NAMESPACE_KNOWLEDGE, top_k=3)

    if not results:
        print("[Researcher] No relevant information found.")
        return create_mcp_message("Researcher", {"facts": "No data found."})

    # Synthesize the findings (Retrieve-and-Synthesize)
    print(f"[Researcher] Found {len(results)} relevant chunks. Synthesizing...")
    source_texts = [match['metadata']['text'] for match in results]

    system_prompt = """You are an expert research synthesis AI.
    Synthesize the provided source texts into a concise, bullet-pointed summary relevant to the user's topic. Focus strictly on the facts provided in the sources. Do not add outside information."""

    user_prompt = f"Topic: {topic}\n\nSources:\n" + "\n\n---\n\n".join(source_texts)

    findings = call_llm(system_prompt, user_prompt)

    return create_mcp_message("Researcher", {"facts": findings})

# === 4.3. Writer Agent (Generation) ===
def agent_writer(mcp_message):
    """
    Combines the factual research with the semantic blueprint to generate the final output.
    """
    print("\n[Writer] Activated. Applying blueprint to facts...")

    facts = mcp_message['content']['facts']
    # The blueprint is passed as a JSON string
    blueprint_json_string = mcp_message['content']['blueprint']

    # The Writer's System Prompt incorporates the dynamically retrieved blueprint
    system_prompt = f"""You are an expert content generation AI.
    Your task is to generate content based on the provided RESEARCH FINDINGS.
    Crucially, you MUST structure, style, and constrain your output according to the rules defined in the SEMANTIC BLUEPRINT provided below.

    --- SEMANTIC BLUEPRINT (JSON) ---
    {blueprint_json_string}
    --- END SEMANTIC BLUEPRINT ---

    Adhere strictly to the blueprint's instructions, style guides, and goals. The blueprint defines HOW you write; the research defines WHAT you write about.
    """

    user_prompt = f"""
    --- RESEARCH FINDINGS ---
    {facts}
    --- END RESEARCH FINDINGS ---

    Generate the content now.
    """

    # Generate the final content (slightly higher temperature for potential creativity)
    final_output = call_llm(system_prompt, user_prompt)

    return create_mcp_message("Writer", {"output": final_output})

def main():
    """Main execution function for the RAG pipeline."""
    # Load embedding model
    print("Loading embedding model...")
    embedding_model = load_embedding_model()
    print("✓ Loaded embedding model successfully.\n")

    # === CONTEXT BLUEPRINTS PROCESSING ===
    print("=== Processing Context Blueprints ===")
    context_blueprints = create_context_blueprints()
    print(f"✓ Prepared {len(context_blueprints)} context blueprints.")

    vectors_context = prepare_context_vectors(context_blueprints)
    context_vector_store = create_context_vector_store(vectors_context, embedding_model)
    print(f"✓ Added context embeddings to Chroma ({NAMESPACE_CONTEXT}).\n")

    # Display context records (uncomment to view)
    # display_vector_store_records(context_vector_store, NAMESPACE_CONTEXT)

    # === KNOWLEDGE DATA PROCESSING ===
    print("=== Processing Knowledge Data ===")
    knowledge_data = get_knowledge_data()
    knowledge_chunks = chunk_text(knowledge_data)
    print(f"✓ Created {len(knowledge_chunks)} knowledge chunks.")

    batch_vectors = prepare_knowledge_vectors(knowledge_chunks)
    print(f"✓ Generated embeddings for {len(batch_vectors)} chunks.")

    knowledge_vector_store = create_knowledge_vector_store(batch_vectors, embedding_model)
    print(f"✓ Added knowledge embeddings to Chroma ({NAMESPACE_KNOWLEDGE}).\n")

    # Display knowledge records (uncomment to view)
    # display_vector_store_records(knowledge_vector_store, NAMESPACE_KNOWLEDGE)

    print("=== RAG Pipeline Complete ===")
    return context_vector_store, knowledge_vector_store


if __name__ == '__main__':
    context_store, knowledge_store = main()
