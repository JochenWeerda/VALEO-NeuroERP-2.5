��#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS v1.3 Streamlit Dashboard
Dieses Script erstellt ein Streamlit-Dashboard zur Visualisierung des GENXAIS-Zyklus.
"""

import streamlit as st
import json
import os
import time
import datetime
from pathlib import Path
import pandas as pd
import altair as alt
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Konfiguration
st.set_page_config(
    page_title="GENXAIS v1.3 Dashboard",
    page_icon=">���",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Pfade
DATA_DIR = Path("data/dashboard")
PHASE_DATA_PATH = DATA_DIR / "phase_data.json"
PIPELINE_DATA_PATH = DATA_DIR / "pipeline_data.json"
ARTIFACT_DATA_PATH = DATA_DIR / "artifact_data.json"
GRAPHITI_DATA_PATH = DATA_DIR / "graphiti_data.json"

# Hilfsfunktionen
def load_json_data(path):
    """L�dt JSON-Daten aus einer Datei"""
    try:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return None
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten aus {path}: {e}")
        return None

def format_timestamp(timestamp):
    """Formatiert einen Zeitstempel"""
    if timestamp:
        try:
            dt = datetime.datetime.fromisoformat(timestamp)
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        except:
            return timestamp
    return "Keine Daten"

def create_progress_chart(data, title):
    """Erstellt ein Fortschrittsdiagramm"""
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('progress:Q', scale=alt.Scale(domain=[0, 100]), title='Fortschritt (%)'),
        y=alt.Y('phase:N', title='Phase', sort=None),
        color=alt.Color('status:N', 
                      scale=alt.Scale(
                          domain=['Aktiv', 'Abgeschlossen', 'Ausstehend', 'Fehler'],
                          range=['#1E88E5', '#4CAF50', '#9E9E9E', '#F44336']
                      ),
                      title='Status'),
        tooltip=['phase:N', 'progress:Q', 'status:N']
    ).properties(
        title=title,
        width=600,
        height=300
    )
    return chart

def create_pipeline_chart(data):
    """Erstellt ein Pipeline-Fortschrittsdiagramm"""
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('progress:Q', scale=alt.Scale(domain=[0, 100]), title='Fortschritt (%)'),
        y=alt.Y('pipeline:N', title='Pipeline', sort=None),
        color=alt.Color('status:N', 
                      scale=alt.Scale(
                          domain=['Initialisierung', 'Aktiv', 'Abgeschlossen', 'Fehler'],
                          range=['#FFC107', '#1E88E5', '#4CAF50', '#F44336']
                      ),
                      title='Status'),
        tooltip=['pipeline:N', 'progress:Q', 'status:N', 'runtime:N']
    ).properties(
        title='Pipeline-Status',
        width=600,
        height=300
    )
    return chart

def create_graphiti_graph(graphiti_data):
    """Erstellt einen Graphiti-Graphen mit NetworkX"""
    if not graphiti_data:
        return None
    
    G = nx.DiGraph()
    
    # Knoten hinzuf�gen
    for node in graphiti_data.get("nodes", []):
        G.add_node(node["id"], 
                  label=node["label"], 
                  type=node["type"],
                  status=node["status"])
    
    # Kanten hinzuf�gen
    for edge in graphiti_data.get("edges", []):
        G.add_edge(edge["source"], edge["target"], label=edge["label"])
    
    # Farben basierend auf Status
    status_colors = {
        "completed": "#4CAF50",  # Gr�n
        "active": "#1E88E5",     # Blau
        "pending": "#9E9E9E",    # Grau
        "error": "#F44336"       # Rot
    }
    
    # Farben basierend auf Knotentyp
    type_shapes = {
        "entry": "o",      # Kreis
        "phase": "s",      # Quadrat
        "exit": "^",       # Dreieck
        "decision": "d"    # Raute
    }
    
    # Positionen berechnen
    pos = nx.spring_layout(G, seed=42)
    
    # Figur erstellen
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Knoten zeichnen
    for node, attrs in G.nodes(data=True):
        node_color = status_colors.get(attrs.get("status", "pending"), "#9E9E9E")
        node_shape = type_shapes.get(attrs.get("type", "phase"), "o")
        nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=node_color, 
                              node_shape=node_shape, node_size=700, ax=ax)
    
    # Kanten zeichnen
    nx.draw_networkx_edges(G, pos, edge_color='black', width=1.0, 
                          arrowstyle='->', arrowsize=15, ax=ax)
    
    # Knotenbeschriftungen
    labels = {node: data.get("label", node) for node, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold', ax=ax)
    
    # Kantenbeschriftungen
    edge_labels = {(u, v): d.get("label", "") for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
    
    # Layout anpassen
    plt.axis('off')
    plt.tight_layout()
    
    return fig

# Dashboard-Layout
def main():
    """Hauptfunktion f�r das Dashboard"""
    # Titel
    st.title(">��� GENXAIS v1.3 Dashboard")
    st.markdown("Echtzeit-Monitoring des GENXAIS v1.3 Zyklus mit Multi-Pipeline-Betrieb und Graphiti-Integration")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Seite ausw�hlen", ["�bersicht", "Phasen", "Pipelines", "Graphiti", "Artefakte"])
    
    # Auto-Refresh
    auto_refresh = st.sidebar.checkbox("Auto-Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh-Intervall (Sekunden)", 5, 60, 10)
    
    # Daten laden
    phase_data = load_json_data(PHASE_DATA_PATH)
    pipeline_data = load_json_data(PIPELINE_DATA_PATH)
    artifact_data = load_json_data(ARTIFACT_DATA_PATH)
    graphiti_data = load_json_data(GRAPHITI_DATA_PATH)
    
    # Pr�fen, ob Daten vorhanden sind
    if not all([phase_data, pipeline_data, artifact_data, graphiti_data]):
        st.warning("Einige Daten konnten nicht geladen werden. Bitte starten Sie den GENXAIS-Zyklus.")
        if st.button("Dashboard neu laden"):
            st.rerun()
        return
    
    # �bersichtsseite
    if page == "�bersicht":
        # Status-Karten
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_phase = phase_data.get("current_phase", "Keine Phase aktiv")
            st.info(f"Aktuelle Phase: **{current_phase}**")
        
        with col2:
            active_pipelines = sum(1 for status in pipeline_data.get("status", {}).values() 
                                if status.get("status") == "Aktiv")
            total_pipelines = len(pipeline_data.get("pipelines", []))
            st.info(f"Aktive Pipelines: **{active_pipelines}/{total_pipelines}**")
        
        with col3:
            completed_artifacts = sum(1 for status in artifact_data.get("status", {}).values() 
                                   if status.get("status") == "Abgeschlossen")
            total_artifacts = len(artifact_data.get("artifacts", []))
            st.info(f"Abgeschlossene Artefakte: **{completed_artifacts}/{total_artifacts}**")
        
        # Fortschrittsdiagramme
        col1, col2 = st.columns(2)
        
        with col1:
            # Phasen-Fortschritt
            phase_progress_data = []
            for phase, status in phase_data.get("status", {}).items():
                phase_progress_data.append({
                    "phase": phase,
                    "progress": status.get("progress", 0),
                    "status": status.get("status", "Ausstehend")
                })
            
            phase_progress_df = pd.DataFrame(phase_progress_data)
            if not phase_progress_df.empty:
                st.altair_chart(create_progress_chart(phase_progress_df, "Phasen-Fortschritt"), use_container_width=True)
        
        with col2:
            # Pipeline-Fortschritt
            pipeline_progress_data = []
            for pipeline, status in pipeline_data.get("status", {}).items():
                pipeline_progress_data.append({
                    "pipeline": pipeline,
                    "progress": status.get("progress", 0),
                    "status": status.get("status", "Initialisierung"),
                    "runtime": status.get("runtime", "0h 0m")
                })
            
            pipeline_progress_df = pd.DataFrame(pipeline_progress_data)
            if not pipeline_progress_df.empty:
                st.altair_chart(create_pipeline_chart(pipeline_progress_df), use_container_width=True)
        
        # Graphiti-Graph (vereinfacht)
        st.subheader("Graphiti Knowledge Graph")
        graphiti_fig = create_graphiti_graph(graphiti_data)
        if graphiti_fig:
            st.pyplot(graphiti_fig)
        
        # Letzte Aktualisierung
        st.markdown("---")
        last_updated = format_timestamp(phase_data.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: {last_updated}")
    
    # Phasen-Seite
    elif page == "Phasen":
        st.header("GENXAIS v1.3 Phasen")
        
        # Phasen-Fortschritt
        phase_progress_data = []
        for phase, status in phase_data.get("status", {}).items():
            phase_progress_data.append({
                "phase": phase,
                "progress": status.get("progress", 0),
                "status": status.get("status", "Ausstehend")
            })
        
        phase_progress_df = pd.DataFrame(phase_progress_data)
        if not phase_progress_df.empty:
            st.altair_chart(create_progress_chart(phase_progress_df, "Phasen-Fortschritt"), use_container_width=True)
        
        # Phasen-Details
        st.subheader("Phasen-Details")
        for phase, status in phase_data.get("status", {}).items():
            with st.expander(f"{phase} ({status.get('status', 'Ausstehend')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Fortschritt", f"{status.get('progress', 0)}%")
                with col2:
                    st.metric("Status", status.get('status', 'Ausstehend'))
                
                # Fortschrittsbalken
                st.progress(status.get('progress', 0) / 100)
        
        # Letzte Aktualisierung
        st.markdown("---")
        last_updated = format_timestamp(phase_data.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: {last_updated}")
    
    # Pipelines-Seite
    elif page == "Pipelines":
        st.header("GENXAIS v1.3 Pipelines")
        
        # Pipeline-Fortschritt
        pipeline_progress_data = []
        for pipeline, status in pipeline_data.get("status", {}).items():
            pipeline_progress_data.append({
                "pipeline": pipeline,
                "progress": status.get("progress", 0),
                "status": status.get("status", "Initialisierung"),
                "runtime": status.get("runtime", "0h 0m")
            })
        
        pipeline_progress_df = pd.DataFrame(pipeline_progress_data)
        if not pipeline_progress_df.empty:
            st.altair_chart(create_pipeline_chart(pipeline_progress_df), use_container_width=True)
        
        # Pipeline-Details
        st.subheader("Pipeline-Details")
        for pipeline, status in pipeline_data.get("status", {}).items():
            with st.expander(f"{pipeline} ({status.get('status', 'Initialisierung')})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fortschritt", f"{status.get('progress', 0)}%")
                with col2:
                    st.metric("Status", status.get('status', 'Initialisierung'))
                with col3:
                    st.metric("Laufzeit", status.get('runtime', '0h 0m'))
                
                # Fortschrittsbalken
                st.progress(status.get('progress', 0) / 100)
        
        # Letzte Aktualisierung
        st.markdown("---")
        last_updated = format_timestamp(pipeline_data.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: {last_updated}")
    
    # Graphiti-Seite
    elif page == "Graphiti":
        st.header("GENXAIS v1.3 Graphiti Knowledge Graph")
        
        # Graphiti-Konfiguration anzeigen
        st.subheader("Graphiti-Konfiguration")
        config = graphiti_data.get("config", {})
        col1, col2 = st.columns(2)
        with col1:
            st.write("Aktiviert:", config.get("activate", False))
            st.write("Fallback-Pfade aktiviert:", config.get("enable_fallback_paths", False))
        with col2:
            st.write("Memory mit Graph verkn�pft:", config.get("link_memory_to_graph", False))
            st.write("Entscheidungen visualisieren:", config.get("visualize_decisions", False))
        
        # Graphiti-Graph
        st.subheader("Knowledge Graph Visualisierung")
        graphiti_fig = create_graphiti_graph(graphiti_data)
        if graphiti_fig:
            st.pyplot(graphiti_fig)
        else:
            st.warning("Keine Graphiti-Daten verf�gbar.")
        
        # Knoten- und Kantendetails
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Knoten")
            nodes_df = pd.DataFrame(graphiti_data.get("nodes", []))
            if not nodes_df.empty:
                st.dataframe(nodes_df, use_container_width=True)
        
        with col2:
            st.subheader("Kanten")
            edges_df = pd.DataFrame(graphiti_data.get("edges", []))
            if not edges_df.empty:
                st.dataframe(edges_df, use_container_width=True)
        
        # Letzte Aktualisierung
        st.markdown("---")
        last_updated = format_timestamp(graphiti_data.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: {last_updated}")
    
    # Artefakte-Seite
    elif page == "Artefakte":
        st.header("GENXAIS v1.3 Artefakte")
        
        # Artefakt-Status
        artifact_status_data = []
        for artifact, status in artifact_data.get("status", {}).items():
            artifact_status_data.append({
                "artifact": artifact,
                "status": status.get("status", "Ausstehend"),
                "last_updated": format_timestamp(status.get("last_updated", None))
            })
        
        artifact_status_df = pd.DataFrame(artifact_status_data)
        if not artifact_status_df.empty:
            st.dataframe(artifact_status_df, use_container_width=True)
        
        # Artefakt-Details
        st.subheader("Artefakt-Details")
        for artifact, status in artifact_data.get("status", {}).items():
            with st.expander(f"{artifact} ({status.get('status', 'Ausstehend')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Status", status.get('status', 'Ausstehend'))
                with col2:
                    st.metric("Letzte Aktualisierung", format_timestamp(status.get('last_updated', None)))
        
        # Letzte Aktualisierung
        st.markdown("---")
        last_updated = format_timestamp(artifact_data.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: {last_updated}")
    
    # Auto-Refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
