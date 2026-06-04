import matplotlib.pyplot as plt
import networkx as nx

# -------------------------------------------------------------------------
# GLOBAL TYPOGRAPHY & SVG CONFIGURATION
# -------------------------------------------------------------------------
plt.rcParams.update({
    'font.family': 'monospace',
    'font.monospace': ['JetBrains Mono', 'DejaVu Sans Mono', 'Consolas', 'monospace'],
    'svg.fonttype': 'none'  # Forces Matplotlib to export text as clean strings for browsers
})


def generate_topology_plots():
    # Initialize system parameters
    N = 25
    players = list(range(1, N + 1))
    owner = 0

    # Create figure with side-by-side subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='white')

    # -------------------------------------------------------------------------
    # PANEL 1: The Decentralized Gaussian Regime (Messy Spiderweb / Complete Graph)
    # -------------------------------------------------------------------------
    G_decentralized = nx.complete_graph(N)

    # Use spring layout to create a dense, tangled, chaotic web appearance
    pos_dec = nx.spring_layout(G_decentralized, seed=42, k=0.5)

    # Draw edges with high transparency and thin weights to look like a web
    nx.draw_networkx_edges(G_decentralized, pos_dec, ax=ax1,
                           edge_color='#4a4a4a', width=0.5, alpha=0.15)

    # Draw nodes as uniform, sharp black dots
    nx.draw_networkx_nodes(G_decentralized, pos_dec, ax=ax1,
                           node_color='#111111', node_size=40)

    ax1.set_title("Decentralized Mesh Regime: O(N^2) Interaction Channels",
                  fontsize=11, fontweight='bold', pad=15, color='#111111')
    ax1.axis('off')

    # -------------------------------------------------------------------------
    # PANEL 2: The Centralized Pareto Regime (Star Graph via Shell Layout)
    # -------------------------------------------------------------------------
    G_centralized = nx.Graph()

    # Construct star topology: Connect every player node directly to the owner hub (0)
    for player in players:
        G_centralized.add_edge(owner, player)

    # Isolate peripherals and define concentric shells
    peripheral_nodes = [n for n in G_centralized.nodes if n != owner]
    pos_cent = nx.shell_layout(G_centralized, nlist=[[owner], peripheral_nodes])

    # Draw peripheral edges as sharp, clean, directional spokes
    nx.draw_networkx_edges(G_centralized, pos_cent, ax=ax2,
                           edge_color='#222222', width=1.0, alpha=0.7)

    # Draw peripheral player nodes
    nx.draw_networkx_nodes(G_centralized, pos_cent, ax=ax2, nodelist=peripheral_nodes,
                           node_color='#666666', node_size=40)

    # Draw the Central Hub (Bar Owner) as a structurally distinct, dominant node
    nx.draw_networkx_nodes(G_centralized, pos_cent, ax=ax2, nodelist=[owner],
                           node_color='#111111', node_size=140, node_shape='s')

    ax2.set_title("Centralized Star Regime: O(N) Interaction Channels",
                  fontsize=11, fontweight='bold', pad=15, color='#111111')
    ax2.axis('off')

    # -------------------------------------------------------------------------
    # RENDER AND EXPORT
    # -------------------------------------------------------------------------
    plt.tight_layout()
    plt.savefig("network_phase_transition.svg", format="svg", transparent=True)
    plt.show()


if __name__ == "__main__":
    generate_topology_plots()