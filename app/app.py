"""
Streamlit chat UI for the Neo4j GraphRAG pipeline.

Run: streamlit run streamlit_app.py
"""
import os
import sys
import streamlit as st
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils import (
    GraphDB,
    graphRAG,
    load_conf
)
from neo4j_graphrag.message_history import InMemoryMessageHistory

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CONF_PATH = Path(__file__).parent/ "config" / "dev.conf"
config = load_conf(CONF_PATH)
NEO4J_URI = os.environ["URI"]
NEO4J_AUTH = (os.environ["USERNAME"], os.environ["PASSWORD"])
EMBED_MODEL = config["EMBED_MODEL"]
LLM_MODEL = config["LLM_MODEL"]
INDEX_NAME = config["INDEX_NAME"]
DEFAULT_TOP_K = int(config["DEFAULT_TOP_K"])

st.set_page_config(page_title="GraphRAG Chat", page_icon="🕸️", layout="wide")

# ---------------------------------------------------------------------------
# Cached resources — created once per session, not on every rerun
# ---------------------------------------------------------------------------
@st.cache_resource
def get_driver():
    return GraphDB(
        URI = NEO4J_URI,
        AUTH = NEO4J_AUTH
    )

@st.cache_resource
def get_rag():
    return graphRAG(
        llm = LLM_MODEL,
        embedding_model = EMBED_MODEL,
        index_name = INDEX_NAME,
        driver = get_driver()
    )


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
        get_driver()
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