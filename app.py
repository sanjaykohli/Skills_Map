from flask import Flask, render_template, jsonify
import pandas as pd
import networkx as nx

app = Flask(__name__)

def load_network_data():
    # Load data from Excel
    df = pd.read_excel("skills.xlsx", engine="openpyxl")
    
    # Determine unique skills
    unique_skills = set(df["Skill1"]).union(set(df["Skill2"]))
    
    # Filter collaborations
    collaborations = df[df["Possible Collaboration"].str.lower() == "yes"][["Skill1", "Skill2"]].values.tolist()
    
    # Create network graph
    G = nx.Graph()
    G.add_nodes_from(unique_skills)
    G.add_edges_from(collaborations)
    
    # Calculate node positions using spring layout
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Prepare nodes data
    nodes_data = []
    for node in G.nodes():
        nodes_data.append({
            "id": node,
            "degree": G.degree[node],
            "x": float(pos[node][0]) * 1000,  # Scale coordinates
            "y": float(pos[node][1]) * 1000
        })
    
    # Prepare edges data
    edges_data = [{"source": source, "target": target} for source, target in G.edges()]
    
    return {"nodes": nodes_data, "edges": edges_data}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/network')
def get_network():
    return jsonify(load_network_data())

@app.route('/api/skills')
def get_skills():
    network_data = load_network_data()
    skills = [node["id"] for node in network_data["nodes"]]
    return jsonify(sorted(skills))

@app.route('/api/connections/<skill>')
def get_connections(skill):
    network_data = load_network_data()
    connections = []
    for edge in network_data["edges"]:
        if edge["source"] == skill:
            connections.append(edge["target"])
        elif edge["target"] == skill:
            connections.append(edge["source"])
    return jsonify(sorted(connections))

if __name__ == '__main__':
    app.run(debug=True)
