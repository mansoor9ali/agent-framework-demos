import json
import uuid

import tiktoken
from dotenv import load_dotenv
from rich import print
from embeddingsUtiles import load_embedding_model
from langchain_community.vectorstores import Chroma
load_dotenv()



def chunk_text(text, chunk_size=100, overlap=20):
    # Initialize tokenizer for robust, token-aware chunking
    tokenizer = tiktoken.get_encoding("cl100k_base")

    """Chunks text based on token count with overlap (Best practice for RAG)."""
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens)
        # Basic cleanup
        chunk_text = chunk_text.replace("\n", " ").strip()
        if chunk_text:
            chunks.append(chunk_text)
    return chunks


if __name__ == '__main__':

    NAMESPACE_KNOWLEDGE = "KnowledgeStore"
    NAMESPACE_CONTEXT = "ContextLibrary"
    #============================================
    context_blueprints = [
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
    print(f"\nPrepared {len(context_blueprints)} context blueprints.")

    #============================================
    # SECTION 1.4: The Embedding Model
    # ============================================
    embedding_model = load_embedding_model()
    print("Loaded embedding model successfully.")

    vectors_context = []
    for item in context_blueprints:
        text = item["description"]
        # # Prefer batch input for consistency; handle single-string return as well
        # try:
        #     emb_result = embedding_model.embed_documents([text])
        #     embeddings = emb_result[0] if isinstance(emb_result, (list, tuple)) else emb_result
        # except Exception:
        #     # Fallback if the model expects a single string
        #     embeddings = embedding_model.embed_documents(text)

        vectors_context.append({
            "id": item["id"],
           # "values": embeddings,
            "metadata": {
                "description": text,
                "blueprint_json": item["blueprint"]
            }
        })

    context_texts = [vc["metadata"]["description"] for vc in vectors_context]
    context_metadata = [{"id": vc["id"], "blueprint_json": vc["metadata"]["blueprint_json"]} for vc in vectors_context]

    context_vector_store = Chroma.from_texts(
        texts=context_texts,
        embedding=embedding_model,
        metadatas=context_metadata,
        collection_name=NAMESPACE_CONTEXT
    )

    print("Added context_texts embeddings to Chroma context_vector_store.")
    # Fetch all records from context_vector_store
    # all_context_records = context_vector_store.get(include=['embeddings', 'documents', 'metadatas'])
    #
    # # Display the records
    # print(f"\n=== Total Records in {NAMESPACE_CONTEXT}: {len(all_context_records['ids'])} ===\n")
    #
    # for i, (doc_id, text, metadata, embedding) in enumerate(
    #         zip(all_context_records['ids'], all_context_records['documents'],
    #             all_context_records['metadatas'], all_context_records['embeddings'])):
    #     print(f"--- Context Record {i + 1} ---")
    #     print(f"ID: {doc_id}")
    #     print(f"Description: {text[:200]}...")  # First 200 characters
    #     print(f"Metadata: {metadata}")
    #     print(f"Embedding (first 10 dimensions): {embedding[:10]}")
    #     print(f"Embedding dimension: {len(embedding)}")
    #     print()




    knowledge_data_raw = """
    Space exploration is the use of astronomy and space technology to explore outer space. The early era of space exploration was driven by a "Space Race" between the Soviet Union and the United States. The launch of the Soviet Union's Sputnik 1 in 1957, and the first Moon landing by the American Apollo 11 mission in 1969 are key landmarks.
    
    The Apollo program was the United States human spaceflight program carried out by NASA which succeeded in landing the first humans on the Moon. Apollo 11 was the first mission to land on the Moon, commanded by Neil Armstrong and lunar module pilot Buzz Aldrin, with Michael Collins as command module pilot. Armstrong's first step onto the lunar surface occurred on July 20, 1969, and was broadcast on live TV worldwide. The landing required Armstrong to take manual control of the Lunar Module Eagle due to navigational challenges and low fuel.
    
    Juno is a NASA space probe orbiting the planet Jupiter. It was launched on August 5, 2011, and entered a polar orbit of Jupiter on July 5, 2016. Juno's mission is to measure Jupiter's composition, gravitational field, magnetic field, and polar magnetosphere to understand how the planet formed. Juno is the second spacecraft to orbit Jupiter, after the Galileo orbiter. It is uniquely powered by large solar arrays instead of RTGs (Radioisotope Thermoelectric Generators), making it the farthest solar-powered mission.
    
    A Mars rover is a remote-controlled motor vehicle designed to travel on the surface of Mars. NASA JPL managed several successful rovers including: Sojourner, Spirit, Opportunity, Curiosity, and Perseverance. The search for evidence of habitability and organic carbon on Mars is now a primary NASA objective. Perseverance also carried the Ingenuity helicopter.
    """

    # Chunk the knowledge data
    knowledge_chunks = chunk_text(knowledge_data_raw)
    print(f"Created {len(knowledge_chunks)} knowledge chunks.")
    # for i, chunk in enumerate(knowledge_chunks):
    #     print(f"--------------------------------- chunk # {i + 1} -------------------------------------")
    #     print(chunk[:1000])  # Print first 1000 characters of each chunk
    #     print(f"-----------------------------------------------------------------------------------\n")


    # Generate embeddings for each chunk
    batch_vectors = []
    for chunk_id, chunk in enumerate(knowledge_chunks):
        # embeddings = embedding_model.embed_documents([chunk])
        batch_vectors.append({
            "id": chunk_id,
            #"values": embeddings,
            "metadata": {
                "text": knowledge_chunks[chunk_id]
            }
        })


    print(f"Generated embeddings for {len(batch_vectors)} chunks.")
    # for i, chunk_emb in enumerate(chunk_embeddings):
    #     print(f"--------------------------------- chunk embedding # {i + 1} -------------------------------------")
    #     print(f"ID: {chunk_emb['id']}")
    #     print(f"Metadata Text: {chunk_emb['metadata']['text'][:200]}")  # Print first 200 characters of text
    #     print(f"Embedding Values (first 5): {chunk_emb['values'][0][:5]}")  # Print first 5 values of embedding
    #     print(f"-----------------------------------------------------------------------------------\n")
    #Chroma.aadd_documents(chunk_embeddings, embedding_model, collection_name="knowledge_chunks").

    # Extract texts and metadata from batch_vectors
    knowledge_texts = [item['metadata']['text'] for item in batch_vectors]
    knowledge_metadata = [{'id': str(item['id'])} for item in batch_vectors]

    # Create Chroma vector store for knowledge chunks
    knowledge_vector_store = Chroma.from_texts(
        texts=knowledge_texts,
        embedding=embedding_model,
        metadatas=knowledge_metadata,
        collection_name=NAMESPACE_KNOWLEDGE
    )

    print("Added knowledge_texts embeddings to Chroma knowledge_vector_store.")

    # # Fetch all records from knowledge_vector_store
    # all_records = knowledge_vector_store.get(include=['embeddings', 'documents', 'metadatas'])
    #
    # # Display the records
    # print(f"\n=== Total Records in {NAMESPACE_KNOWLEDGE}: {len(all_records['ids'])} ===\n")
    #
    # for i, (doc_id, text, metadata, embedding) in enumerate(
    #         zip(all_records['ids'], all_records['documents'], all_records['metadatas'], all_records['embeddings'])):
    #     print(f"--- Record {i + 1} ---")
    #     print(f"ID: {doc_id}")
    #     print(f"Text: {text[:200]}...")  # First 200 characters
    #     print(f"Metadata: {metadata}")
    #     print(f"Embedding (first 10 dimensions): {embedding[:10]}")
    #     print(f"Embedding dimension: {len(embedding)}")
    #     print()


