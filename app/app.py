"""
Streamlit chat UI for the Neo4j GraphRAG pipeline.

Run: streamlit run streamlit_app.py
"""
import os
import streamlit as st
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OllamaEmbeddings
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.llm import OllamaLLM
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.message_history import InMemoryMessageHistory

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
NEO4J_URI = os.environ["URI"]
NEO4J_AUTH = (os.environ["USERNAME"], os.environ["PASSWORD"])
EMBED_MODEL = "qwen3-embedding:0.6b"
LLM_MODEL = "gemma4:31b-cloud"
INDEX_NAME = "dataProductIndex"
DEFAULT_TOP_K = 8

st.set_page_config(page_title="GraphRAG Chat", page_icon="🕸️", layout="wide")

# ---------------------------------------------------------------------------
# Cached resources — created once per session, not on every rerun
# ---------------------------------------------------------------------------
@st.cache_resource
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)


@st.cache_resource
def get_embedder():
    return OllamaEmbeddings(model=EMBED_MODEL)


@st.cache_resource
def get_retriever():
    return VectorRetriever(
        get_driver(),
        index_name=INDEX_NAME,
        embedder=get_embedder(),
    )


@st.cache_resource
def get_rag():
    llm = OllamaLLM(model_name=LLM_MODEL)
    return GraphRAG(retriever=get_retriever(), llm=llm)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{role, content, context (optional)}]

if "top_k" not in st.session_state:
    st.session_state.top_k = DEFAULT_TOP_K

if "history" not in st.session_state:
    # persists conversation memory across turns within this browser session
    st.session_state.history = InMemoryMessageHistory()

# ---------------------------------------------------------------------------
# Sidebar — controls + connection status
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🕸️ GraphRAG Settings")

    try:
        get_driver().verify_connectivity()
        st.success("Connected to Neo4j")
    except Exception as e:
        st.error(f"Neo4j connection failed: {e}")

    st.session_state.top_k = st.slider(
        "Retrieved products (top_k)", min_value=1, max_value=30,
        value=st.session_state.top_k,
        help="How many DataProduct nodes to pull from vector search before answering.",
    )

    show_context = st.toggle("Show retrieved context", value=True)

    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------
st.title("Data Product Assistant")
st.caption("Ask about data products, domains, divisions, or status — grounded in your Neo4j graph.")

# render existing history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("context") and show_context:
            with st.expander(f"Retrieved context ({len(msg['context'])} items)"):
                for i, item in enumerate(msg["context"], 1):
                    st.markdown(f"**Match {i}**")
                    st.code(item, language=None)

# ---------------------------------------------------------------------------
# GraphRAG call — retrieval + prompt assembly + generation, all in one
# ---------------------------------------------------------------------------
def ask(question: str, top_k: int) -> tuple[str, list[str]]:
    response = get_rag().search(
        query_text=question,
        message_history=st.session_state.history,
        retriever_config={"top_k": top_k},
        return_context=True,   # ask GraphRAG to include what it retrieved
    )

    st.session_state.history.add_message({"role": "user", "content": question})
    st.session_state.history.add_message({"role": "assistant", "content": response.answer})

    context_items = [item.content for item in response.retriever_result.items] if response.retriever_result else []
    return response.answer, context_items


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
if question := st.chat_input("Ask about a data product, domain, or division..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving from graph and generating answer..."):
            full_answer, context_items = ask(question, st.session_state.top_k)

        st.markdown(full_answer)

        if show_context and context_items:
            with st.expander(f"Retrieved context ({len(context_items)} items)"):
                for i, item in enumerate(context_items, 1):
                    st.markdown(f"**Match {i}**")
                    st.code(item, language=None)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_answer,
        "context": context_items,
    })