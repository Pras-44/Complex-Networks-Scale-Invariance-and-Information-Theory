import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def run_scaling_simulation():
    """
    Simulates an agent-based monetary network modeling the phase transition 
    from linear arithmetic random walks to geometric multiplicative feedback loops.
    """
    # =====================================================================
    # 1. THE GEOMETRIC SCALING SIMULATION
    # =====================================================================
    num_agents = 2000
    initial_wealth = 100.0

    wealth = np.full(num_agents, initial_wealth)
    num_samples = 25
    sample_indices = np.random.choice(num_agents, size=num_samples, replace=False)

    epochs = [0, 500, 1500, 3000, 6000]
    distribution_history = {}
    player_tracks = {i: [] for i in sample_indices}
    bar_owner_track = []

    # Record baseline at Round 0
    distribution_history[0] = (wealth.copy(), 0.0)
    for idx in sample_indices:
        player_tracks[idx].append(wealth[idx])
    bar_owner_track.append(0.0)

    # --- PHASE 1: Linear Arithmetic Scale (Rounds 1 to 500) ---
    flat_bet = 1.50
    flat_fee = 0.10

    for r in range(1, 501):
        shuffled = np.random.permutation(num_agents)
        g1, g2 = shuffled[:num_agents // 2], shuffled[num_agents // 2:]
        flips = np.random.choice([-1, 1], size=num_agents // 2)

        # Vectorized array transformations
        wealth[g1] = np.maximum(0.1, wealth[g1] + flips * (flat_bet - flat_fee))
        wealth[g2] = np.maximum(0.1, wealth[g2] - flips * (flat_bet + flat_fee))

        for idx in sample_indices:
            player_tracks[idx].append(wealth[idx])

        current_flat_revenue = r * (num_agents // 2) * (flat_fee * 2.0)
        bar_owner_track.append(current_flat_revenue)

        if r in epochs:
            distribution_history[r] = (wealth.copy(), current_flat_revenue)

    # --- PHASE 2: Proportional Geometric Scale (Rounds 501 to 6000) ---
    bet_fraction = 0.05
    tax_rate = 0.01
    current_owner_wealth = bar_owner_track[-1]

    for r in range(501, 6001):
        shuffled = np.random.permutation(num_agents)
        g1, g2 = shuffled[:num_agents // 2], shuffled[num_agents // 2:]
        flips = np.random.choice([-1, 1], size=num_agents // 2)

        for i in range(num_agents // 2):
            idx1, idx2 = g1[i], g2[i]
            max_bet = min(wealth[idx1], wealth[idx2]) * bet_fraction
            if max_bet <= 0.01: continue

            tax = max_bet * tax_rate
            net_bet = max_bet - tax
            current_owner_wealth += (tax * 2.0)

            if flips[i] == 1:
                wealth[idx1] += net_bet
                wealth[idx2] -= max_bet
            else:
                wealth[idx1] -= max_bet
                wealth[idx2] += net_bet

        for idx in sample_indices:
            player_tracks[idx].append(wealth[idx])
        bar_owner_track.append(current_owner_wealth)

        if r in epochs:
            distribution_history[r] = (wealth.copy(), current_owner_wealth)

    # =====================================================================
    # 2. CONSTRUCTING THE THREE-PANEL COCKPIT
    # =====================================================================
    fig = make_subplots(
        rows=1, cols=3,
        horizontal_spacing=0.12,
        subplot_titles=(
            "25 Player Wealth",
            "Owner's Revenue",
            "Prob Density(Log-Log)"
        )
    )

    time_axis = np.array(range(6001))
    grayscale_shades = [f"rgb({int(g)},{int(g)},{int(g)})" for g in np.linspace(70, 200, num_samples)]

    def get_binned_data(data_matrix, owner_w):
        total_system = np.append(data_matrix, owner_w)
        log_bins = np.logspace(-1, 6, 35)
        counts, edges = np.histogram(total_system, bins=log_bins)
        centers = (edges[:-1] + edges[1:]) / 2
        valid = counts > 0
        return centers[valid], counts[valid]

    # --- INITIALIZATION LAYERS (Round 0) ---
    for i, idx in enumerate(sample_indices):
        fig.add_trace(
            go.Scatter(
                x=[0], y=[player_tracks[idx][0]], mode='lines',
                opacity=0.5, line=dict(width=1.3, color=grayscale_shades[i])
            ),
            row=1, col=1
        )

    fig.add_trace(
        go.Scatter(
            x=[0], y=[0.0], mode='lines',
            line=dict(width=3.5, color='#ffffff')
        ),
        row=1, col=2
    )

    init_w, init_owner = distribution_history[0]
    init_centers, init_counts = get_binned_data(init_w, init_owner)
    fig.add_trace(
        go.Scatter(
            x=init_centers, y=init_counts, mode='markers+lines',
            marker=dict(size=5, color='#ffffff'), line=dict(width=1.5, color='#aaaaaa')
        ),
        row=1, col=3
    )

    # =====================================================================
    # 3. INTERACTIVE TIMELINE SCRUB MECHANICAL MATRIX
    # =====================================================================
    slider_steps = []
    for epoch in epochs:
        current_time_slice = list(time_axis[:epoch + 1])

        sliced_x_lists = [current_time_slice] * num_samples
        sliced_y_lists = [player_tracks[idx][:epoch + 1] for idx in sample_indices]

        sliced_x_lists.append(current_time_slice)
        sliced_y_lists.append(bar_owner_track[:epoch + 1])

        w_matrix, o_wealth = distribution_history[epoch]
        centers, counts = get_binned_data(w_matrix, o_wealth)
        sliced_x_lists.append(centers)
        sliced_y_lists.append(counts)

        x_max_view = max(100, epoch)

        step = {
            "method": "update",
            "label": f"Round {epoch}",
            "args": [
                {
                    "x": sliced_x_lists,
                    "y": sliced_y_lists
                },
                {
                    "title": f"Scaling Laws Dashboard: State Synchronization at Round {epoch}",
                    "xaxis.range": [0, x_max_view],
                    "yaxis.autorange": True,
                    "xaxis2.range": [0, x_max_view],
                    "yaxis2.autorange": True
                }
            ]
        }
        slider_steps.append(step)

    # =====================================================================
    # 4. MONOCHROME INTERFACE CONFIGURATION & EXPORT
    # =====================================================================
    fig.update_layout(
        sliders=[{
            "active": 0,
            "currentvalue": {"prefix": "Simulation Step: ", "font": {"size": 13, "color": "#ffffff"}},
            "pad": {"t": 40},
            "steps": slider_steps
        }],
        template="plotly_dark",
        font=dict(family="JetBrains Mono, monospace", size=11),
        height=360,
        autosize=True,
        showlegend=False,
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        margin=dict(l=45, r=45, b=10, t=50),
    )

    axis_style = dict(gridcolor='#222222', zerolinecolor='#444444')
    full_log_style = {
        **axis_style,
        "type": "log",
        "minorloglabels": "complete",
        "exponentformat": "none"
    }

    fig.update_xaxes(title_text="Time (Rounds)", **axis_style, row=1, col=1)
    fig.update_yaxes(title_text="Player Wealth ($)", **axis_style, row=1, col=1)

    fig.update_xaxes(title_text="Time (Rounds)", **axis_style, row=1, col=2)
    fig.update_yaxes(title_text="Owner Capital ($)", **axis_style, row=1, col=2)

    fig.update_xaxes(title_text="Wealth Class ($ Log)", range=[-0.5, 5.5], **full_log_style, row=1, col=3)
    fig.update_yaxes(title_text="Density Profile (Log)", range=[0, 3.5], **full_log_style, row=1, col=3)

    fig.write_html(
        "scaling_laws_cockpit.html",
        full_html=False,
        include_plotlyjs='cdn',
        config={"displayModeBar": False}
    )

    fig.show(renderer="browser", config={"displayModeBar": False})


if __name__ == "__main__":
    make_subplots() # Clear registry state
    run_scaling_simulation()