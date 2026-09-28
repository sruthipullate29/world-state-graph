import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from extractor import extract_graph_from_news
from graph_db import Neo4jConnector

st.set_page_config(page_title="Geopolitical Knowledge Graph", layout="wide")
st.title("🌐 Live Geopolitical Knowledge Graph")

# Neo4j connection configs
NEO4J_URI = st.secrets["neo4j+s://61d24e46.databases.neo4j.io"]
NEO4J_USER = st.secrets["61d24e46"]
NEO4J_PASSWORD = st.secrets["qRPi0x5-Cl-HfoVBjcNTj57-jJvt6stNCFeadKODloc"]

db = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# Ingestion Sidebar
with st.sidebar:
    st.header("Ingest News Report")
    news_input = st.text_area("Paste breaking news text:", height=200)
    if st.button("Extract & Ingest"):
        if news_input.strip():
            with st.spinner("Extracting entities & relations..."):
                extracted = extract_graph_from_news(news_input)
                db.ingest_graph_data(extracted)
                st.success(f"Ingested {len(extracted.entities)} entities and {len(extracted.relationships)} relations!")
        else:
            st.warning("Please enter text first.")

# Graph Query & Visualization
st.subheader("Network Map")
records = db.fetch_subgraph(limit=150)

if not records:
    st.info("The graph database is currently empty. Ingest news articles using the sidebar to populate nodes.")
else:
    net = Network(height="650px", width="100%", bgcolor="#111827", font_color="white", directed=True)
    
    color_map = {
        "Country": "#3B82F6",       # Blue
        "Leader": "#10B981",        # Green
        "Organization": "#F59E0B",  # Amber
        "MilitaryBloc": "#EF4444",  # Red
        "Treaty": "#8B5CF6"         # Purple
    }

    for row in records:
        src, src_type = row["source"], row["source_type"]
        tgt, tgt_type = row["target"], row["target_type"]
        rel, summary = row["relation"], row.get("summary", "")

        net.add_node(src, label=src, color=color_map.get(src_type, "#9CA3AF"), title=f"Type: {src_type}")
        net.add_node(tgt, label=tgt, color=color_map.get(tgt_type, "#9CA3AF"), title=f"Type: {tgt_type}")
        net.add_edge(src, tgt, label=rel, title=summary)

    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": { "gravitationalConstant": -50, "centralGravity": 0.01, "springLength": 100 },
        "solver": "forceAtlas2Based"
      }
    }
    """)

    html_file = "graph.html"
    net.save_graph(html_file)
    with open(html_file, "r", encoding="utf-8") as f:
        components.html(f.read(), height=670)