#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import networkx as nx


PALETTE = {
    "panel_border": "#B0BEC5",
    "title": "#2C3E50",
    "arrow_fill": "#90CAF9",
    "arrow_edge": "#1565C0",
    "node": "#3F51B5",
    "edge": "#2E7D32",
    "time": "#F57F17",
    "fusion": "#00838F",
    "highlight": "#FFB300",
    "neighbor": "#4FC3F7",
    "context": "#A5D6A7",
}

PANEL_SPECS = {
    "context": {"box": [0.02, 0.05, 0.18, 0.85], "title": "(a) Context / Sampling", "bg": "#E1F5FE"},
    "embedding": {"box": [0.22, 0.05, 0.26, 0.85], "title": "(b) Feature Access / Embedding", "bg": "#F3E5F5"},
    "block": {"box": [0.50, 0.05, 0.30, 0.85], "title": "(c) Core Encoder / Message Block", "bg": "#FFF8E1"},
    "output": {"box": [0.82, 0.05, 0.16, 0.85], "title": "(d) Fusion / Readout", "bg": "#E8F5E9"},
}


def configure_axis(ax: plt.Axes) -> None:
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def inset_box(panel_box: list[float], rel_left: float, rel_bottom: float, rel_width: float, rel_height: float) -> list[float]:
    left, bottom, width, height = panel_box
    return [
        left + width * rel_left,
        bottom + height * rel_bottom,
        width * rel_width,
        height * rel_height,
    ]


def draw_section_bg(ax: plt.Axes, title: str, color: str) -> None:
    rect = patches.FancyBboxPatch(
        (0.02, 0.02),
        0.96,
        0.96,
        boxstyle="round,pad=0.01",
        facecolor=color,
        edgecolor=PALETTE["panel_border"],
        linewidth=2,
        alpha=0.32,
        zorder=0,
    )
    ax.add_patch(rect)
    ax.text(
        0.5,
        0.97,
        title,
        ha="center",
        va="top",
        fontsize=22,
        fontweight="bold",
        color="#1C2833",
        zorder=10,
    )


def draw_flow_arrow(fig: plt.Figure, x_start: float, x_end: float, y: float) -> None:
    arrow = patches.FancyArrowPatch(
        (x_start, y),
        (x_end, y),
        transform=fig.transFigure,
        arrowstyle="fancy,head_width=12,head_length=15,tail_width=8",
        facecolor=PALETTE["arrow_fill"],
        edgecolor=PALETTE["arrow_edge"],
        alpha=0.42,
        zorder=1,
    )
    fig.add_artist(arrow)


def draw_tensor(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    color: str,
    label: str,
    depth: float = 0.03,
    font_size: int = 14,
    text_color: str = "white",
) -> None:
    rect = patches.Rectangle(
        (x, y),
        width,
        height,
        facecolor=color,
        edgecolor="black",
        linewidth=1.5,
        zorder=2,
    )
    ax.add_patch(rect)
    if depth > 0:
        top = patches.Polygon(
            [[x, y + height], [x + depth, y + height + depth], [x + width + depth, y + height + depth], [x + width, y + height]],
            facecolor=color,
            edgecolor="black",
            linewidth=1.5,
            alpha=0.9,
            zorder=1,
        )
        side = patches.Polygon(
            [[x + width, y], [x + width + depth, y + depth], [x + width + depth, y + height + depth], [x + width, y + height]],
            facecolor=color,
            edgecolor="black",
            linewidth=1.5,
            alpha=0.6,
            zorder=1,
        )
        ax.add_patch(top)
        ax.add_patch(side)
    ax.text(
        x + width / 2,
        y + height / 2,
        label,
        ha="center",
        va="center",
        fontsize=font_size,
        fontweight="bold",
        color=text_color,
        zorder=3,
    )


def add_context_panel(fig: plt.Figure, ax: plt.Axes, panel_box: list[float]) -> None:
    inset_global = fig.add_axes(inset_box(panel_box, 0.06, 0.62, 0.78, 0.24))
    inset_global.set_title(r"Context Graph $\mathcal{G}$", fontsize=17, fontweight="bold", pad=0)
    inset_global.axis("off")

    graph = nx.barabasi_albert_graph(30, 2, seed=15)
    positions = nx.spring_layout(graph, seed=15, k=0.5)
    colors = [
        PALETTE["highlight"] if node == 0 else PALETTE["neighbor"] if node in list(graph.neighbors(0)) else PALETTE["context"]
        for node in range(30)
    ]
    sizes = [800 if node == 0 else 250 for node in range(30)]
    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=inset_global,
        node_color=colors,
        edgecolors="#333333",
        node_size=sizes,
        linewidths=1.5,
    )
    nx.draw_networkx_edges(graph, positions, ax=inset_global, edge_color="#BDBDBD", alpha=0.6, width=1.5)

    ax.text(0.5, 0.59, r"Target Query / Seed Set", ha="center", fontsize=16, fontweight="bold")
    ax.text(
        0.5,
        0.53,
        "Temporal or structural filter",
        ha="center",
        fontsize=15,
        color="#C62828",
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="#FFCDD2", edgecolor="#B71C1C", pad=0.3),
    )
    ax.text(
        0.5,
        0.46,
        "Multi-hop fanout / neighbor budget",
        ha="center",
        fontsize=14,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#7F8C8D"),
    )
    ax.annotate("", xy=(0.5, 0.38), xytext=(0.5, 0.44), arrowprops=dict(facecolor="black", shrink=0.05, width=2, headwidth=8))

    inset_ego = fig.add_axes(inset_box(panel_box, 0.06, 0.06, 0.82, 0.31))
    inset_ego.axis("off")
    ego = nx.Graph()
    ego.add_node(0, layer=0)
    for node in range(1, 5):
        ego.add_node(node, layer=1)
        ego.add_edge(0, node)
    for node in range(5, 15):
        ego.add_node(node, layer=2)
    ego.add_edges_from([(1, 5), (1, 6), (2, 7), (2, 8), (3, 9), (3, 10), (4, 11), (4, 12), (4, 13), (4, 14)])
    ego_pos = nx.multipartite_layout(ego, subset_key="layer", align="horizontal")
    ego_pos = {node: (coords[1], -coords[0]) for node, coords in ego_pos.items()}
    ego_colors = [PALETTE["highlight"] if node == 0 else PALETTE["neighbor"] if node < 5 else PALETTE["context"] for node in range(15)]
    ego_sizes = [900 if node == 0 else 500 for node in range(15)]
    nx.draw_networkx_nodes(
        ego,
        ego_pos,
        ax=inset_ego,
        node_color=ego_colors,
        edgecolors="#333333",
        node_size=ego_sizes,
        linewidths=1.5,
    )
    nx.draw_networkx_edges(ego, ego_pos, ax=inset_ego, edge_color="#E53935", arrows=True, arrowsize=15, width=2.5)
    nx.draw_networkx_labels(ego, ego_pos, labels={0: r"$v_t$"}, font_size=12, font_weight="bold", ax=inset_ego)
    ax.text(0.5, 0.05, r"Ego-graph / sampled subgraph", ha="center", fontsize=18, fontweight="bold", color="#283593")


def add_embedding_panel(fig: plt.Figure, ax: plt.Axes, panel_box: list[float]) -> None:
    draw_tensor(ax, 0.10, 0.81, 0.80, 0.08, "#ECEFF1", "Feature Store / Memory Bank", depth=0.0, font_size=15, text_color="black")
    ax.annotate("", xy=(0.5, 0.79), xytext=(0.5, 0.81), arrowprops=dict(arrowstyle="-|>", lw=2))

    ax.text(0.5, 0.75, "Node / token projection", ha="center", fontweight="bold", fontsize=16)
    draw_tensor(ax, 0.05, 0.58, 0.25, 0.11, PALETTE["node"], "Raw input\n$X \\in \\mathbb{R}^{d}$", depth=0.03, font_size=13)
    ax.annotate("", xy=(0.60, 0.635), xytext=(0.34, 0.635), arrowprops=dict(arrowstyle="-|>", lw=2))
    ax.text(0.47, 0.66, "Linear + GELU", ha="center", va="bottom", fontsize=14, color="#311B92", fontweight="bold", zorder=5)
    draw_tensor(ax, 0.63, 0.58, 0.28, 0.11, "#1A237E", "Embedded state\n$H^{(0)} \\in \\mathbb{R}^{D}$", depth=0.04, font_size=13)

    inset_left = fig.add_axes(inset_box(panel_box, 0.08, 0.48, 0.18, 0.10))
    inset_left.axis("off")
    nx.draw(nx.path_graph(2), node_color=[PALETTE["highlight"], PALETTE["neighbor"]], node_size=200, ax=inset_left)

    inset_right = fig.add_axes(inset_box(panel_box, 0.73, 0.48, 0.18, 0.10))
    inset_right.axis("off")
    nx.draw(nx.path_graph(2), node_color=["#1A237E", "#1A237E"], node_size=250, ax=inset_right)

    ax.text(0.5, 0.48, "Edge semantics and temporal context", ha="center", fontweight="bold", fontsize=16)
    draw_tensor(ax, 0.05, 0.35, 0.25, 0.07, PALETTE["edge"], "Relation / edge type", depth=0.02, font_size=13)
    ax.annotate("", xy=(0.60, 0.385), xytext=(0.34, 0.385), arrowprops=dict(arrowstyle="-|>", lw=2))
    ax.text(0.47, 0.40, "Embedding", ha="center", va="bottom", fontsize=14, fontweight="bold", color="#1B5E20", zorder=5)
    draw_tensor(ax, 0.63, 0.35, 0.25, 0.07, "#1B5E20", r"$r_e \in \mathbb{R}^{D_r}$", depth=0.02, font_size=14)

    draw_tensor(ax, 0.05, 0.22, 0.25, 0.07, PALETTE["time"], r"$\Delta t$ / positional code", depth=0.02, font_size=13, text_color="black")
    ax.annotate("", xy=(0.60, 0.255), xytext=(0.34, 0.255), arrowprops=dict(arrowstyle="-|>", lw=2))
    ax.text(0.47, 0.27, "Time MLP", ha="center", va="bottom", fontsize=14, fontweight="bold", color="#E65100", zorder=5)
    draw_tensor(ax, 0.63, 0.22, 0.25, 0.07, "#E65100", r"$t_e \in \mathbb{R}^{D_t}$", depth=0.02, font_size=14)

    ax.annotate("", xy=(0.76, 0.16), xytext=(0.76, 0.22), arrowprops=dict(arrowstyle="-|>", lw=2))
    ax.annotate("", xy=(0.76, 0.33), xytext=(0.76, 0.35), arrowprops=dict(arrowstyle="-|>", lw=2))
    draw_tensor(ax, 0.45, 0.05, 0.50, 0.10, PALETTE["fusion"], r"$E_{emb} = [r_e \Vert t_e]$", depth=0.04)
    ax.text(
        0.76,
        0.20,
        "Concat",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color="#C62828",
        bbox=dict(boxstyle="circle", facecolor="white", edgecolor="red", pad=0.1),
        zorder=4,
    )

    inset_edge = fig.add_axes(inset_box(panel_box, 0.10, 0.06, 0.30, 0.10))
    inset_edge.axis("off")
    edge_graph = nx.DiGraph()
    edge_graph.add_edge(0, 1)
    nx.draw(edge_graph, node_color="#CCCCCC", edge_color=PALETTE["fusion"], width=5, arrows=True, arrowsize=20, ax=inset_edge)


def add_block_panel(fig: plt.Figure, ax: plt.Axes, panel_box: list[float]) -> None:
    ax.text(0.5, 0.90, r"Layer inputs: $H^{(l)}$ and edge/context features", ha="center", fontsize=20, fontweight="bold", color="#D35400")
    ax.annotate("", xy=(0.5, 0.83), xytext=(0.5, 0.89), arrowprops=dict(facecolor="#D35400", shrink=0.05, width=3, headwidth=10))

    core = patches.Rectangle((0.05, 0.05), 0.80, 0.77, facecolor="#FFFFFF", edgecolor="#F39C12", linewidth=2, linestyle="--", zorder=0, alpha=0.9)
    ax.add_patch(core)
    ax.text(0.08, 0.80, "Layer $l$", fontsize=16, fontweight="bold", color="#B9770E")

    inset_mp = fig.add_axes(inset_box(panel_box, 0.10, 0.75, 0.30, 0.10))
    inset_mp.axis("off")
    graph = nx.DiGraph()
    graph.add_edge(1, 0)
    graph.add_edge(2, 0)
    nx.draw(
        graph,
        pos={0: (0, 0), 1: (-1, 1), 2: (1, 1)},
        node_color=[PALETTE["highlight"], PALETTE["neighbor"], PALETTE["context"]],
        edge_color="#D81B60",
        width=3,
        arrows=True,
        ax=inset_mp,
    )

    draw_tensor(ax, 0.35, 0.74, 0.30, 0.06, "#795548", r"$\tilde{h} = \mathrm{LayerNorm}(H^{(l)})$", font_size=15)
    ax.annotate("", xy=(0.25, 0.63), xytext=(0.5, 0.74), arrowprops=dict(arrowstyle="-|>", lw=2, connectionstyle="angle,angleA=180,angleB=90,rad=10"))
    ax.annotate("", xy=(0.75, 0.63), xytext=(0.5, 0.74), arrowprops=dict(arrowstyle="-|>", lw=2, connectionstyle="angle,angleA=0,angleB=90,rad=10"))

    draw_tensor(ax, 0.08, 0.52, 0.34, 0.11, "#C2185B", "Message MLP\n$m_{uv} = \\mathrm{MLP}(h_u \\Vert h_v \\Vert e)$", depth=0.0, font_size=14)
    draw_tensor(ax, 0.52, 0.52, 0.34, 0.11, "#8E24AA", "Gate / attention\n$g_{uv} = \\sigma(\\mathrm{MLP}(\\cdots))$", depth=0.0, font_size=14)

    ax.annotate("", xy=(0.46, 0.45), xytext=(0.25, 0.52), arrowprops=dict(arrowstyle="-|>", lw=2))
    ax.annotate("", xy=(0.54, 0.45), xytext=(0.75, 0.52), arrowprops=dict(arrowstyle="-|>", lw=2))
    gate_circle = patches.Circle((0.5, 0.43), 0.03, facecolor="white", edgecolor="#E65100", lw=2, zorder=5)
    ax.add_patch(gate_circle)
    ax.text(0.5, 0.43, r"$\odot$", ha="center", va="center", fontsize=24, zorder=6, color="#E65100", fontweight="bold")
    ax.text(
        0.58,
        0.43,
        r"$e_{repr} = m_{uv} \odot g_{uv}$",
        ha="left",
        va="center",
        fontsize=16,
        color="#C2185B",
        fontweight="bold",
        bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="none", alpha=0.85),
        zorder=3,
    )

    ax.annotate("", xy=(0.5, 0.34), xytext=(0.5, 0.40), arrowprops=dict(arrowstyle="-|>", lw=2))
    draw_tensor(ax, 0.15, 0.24, 0.60, 0.10, "#00ACC1", r"Aggregation: $a_v = \mathrm{Mean/Sum}(\{e_{repr}\})$", depth=0.0, font_size=16)
    ax.annotate("", xy=(0.5, 0.16), xytext=(0.5, 0.24), arrowprops=dict(arrowstyle="-|>", lw=2))
    draw_tensor(ax, 0.20, 0.08, 0.50, 0.08, "#FB8C00", r"Self update / FFN: $\Delta H = W_1 h_v + W_2 a_v$", depth=0.0, font_size=15)

    ax.plot([0.95, 0.95], [0.85, 0.12], color="#D32F2F", ls="--", lw=3, zorder=6)
    ax.plot([0.5, 0.95], [0.85, 0.85], color="#D32F2F", ls="--", lw=3, zorder=6)
    ax.annotate("", xy=(0.79, 0.12), xytext=(0.95, 0.12), arrowprops=dict(arrowstyle="-|>", lw=3, ls="--", color="#D32F2F"))
    add_circle = patches.Circle((0.80, 0.12), 0.04, facecolor="white", edgecolor="#D32F2F", lw=2, zorder=7)
    ax.add_patch(add_circle)
    ax.text(0.80, 0.12, "+", ha="center", va="center", fontsize=26, zorder=8, color="#D32F2F", fontweight="bold")
    ax.text(0.80, 0.03, r"$H_{inter} \rightarrow$ FFN $\rightarrow H^{(l+1)}$", ha="center", fontsize=16, fontweight="bold", color="#2E7D32")


def add_output_panel(fig: plt.Figure, ax: plt.Axes, panel_box: list[float]) -> None:
    ax.text(0.5, 0.90, "Terminal features", ha="center", fontweight="bold", fontsize=18)
    draw_tensor(ax, 0.10, 0.74, 0.80, 0.10, "#546E7A", "Jumping knowledge / layer fusion\n$H_{final} = \\sum_{l=1}^{L} H^{(l)}$", font_size=15, depth=0.02)
    ax.annotate("", xy=(0.5, 0.65), xytext=(0.5, 0.74), arrowprops=dict(arrowstyle="-|>", lw=2))

    draw_tensor(ax, 0.10, 0.55, 0.80, 0.10, "#00897B", "Subgraph pooling\n(Mean / Max / attention)", font_size=15, depth=0.02)
    ax.annotate("", xy=(0.5, 0.45), xytext=(0.5, 0.55), arrowprops=dict(arrowstyle="-|>", lw=2))

    draw_tensor(ax, 0.10, 0.35, 0.80, 0.10, "#26A69A", "Structural or global statistics", font_size=15, depth=0.02)

    fusion = patches.Polygon([[0.10, 0.28], [0.90, 0.28], [0.65, 0.20], [0.35, 0.20]], facecolor="#FFF59D", edgecolor="#FBC02D", zorder=2, lw=2)
    ax.add_patch(fusion)
    ax.text(0.5, 0.24, "Global fusion", ha="center", fontsize=15, fontweight="bold", zorder=3, color="#F57F17")

    ax.annotate("", xy=(0.5, 0.12), xytext=(0.5, 0.20), arrowprops=dict(arrowstyle="-|>", lw=2))
    draw_tensor(ax, 0.20, 0.04, 0.60, 0.08, "#D81B60", "Prediction head / classifier", depth=0.03, font_size=16)

    inset_out = fig.add_axes(inset_box(panel_box, 0.05, 0.00, 0.55, 0.10))
    inset_out.axis("off")
    out_graph = nx.star_graph(4)
    out_colors = ["#C62828" if node == 0 else "#90CAF9" for node in range(5)]
    nx.draw(out_graph, node_color=out_colors, edge_color="#B71C1C", node_size=100, width=2, ax=inset_out)
    ax.text(0.5, 0.03, r"Score $\hat{y}$ or logits", ha="left", va="center", fontsize=18, fontweight="bold", color="#B71C1C")


def build_figure(title: str) -> plt.Figure:
    fig = plt.figure(figsize=(30, 16), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    fig.suptitle(title, fontsize=32, fontweight="bold", y=0.96, fontfamily="sans-serif", color=PALETTE["title"])

    axes: dict[str, plt.Axes] = {}
    for key, spec in PANEL_SPECS.items():
        axis = fig.add_axes(spec["box"])
        configure_axis(axis)
        draw_section_bg(axis, spec["title"], spec["bg"])
        axes[key] = axis

    draw_flow_arrow(fig, 0.20, 0.22, 0.5)
    draw_flow_arrow(fig, 0.48, 0.50, 0.5)
    draw_flow_arrow(fig, 0.80, 0.82, 0.5)

    add_context_panel(fig, axes["context"], PANEL_SPECS["context"]["box"])
    add_embedding_panel(fig, axes["embedding"], PANEL_SPECS["embedding"]["box"])
    add_block_panel(fig, axes["block"], PANEL_SPECS["block"]["box"])
    add_output_panel(fig, axes["output"], PANEL_SPECS["output"]["box"])
    return fig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the v7-style native Python neural model figure template.")
    parser.add_argument("--title", default="Native Python Neural Figure Template (V7 Layout)")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/figures/v7-template"))
    parser.add_argument("--stem", default="neural_model_v7_template")
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    fig = build_figure(args.title)
    png_path = args.output_dir / f"{args.stem}.png"
    pdf_path = args.output_dir / f"{args.stem}.pdf"
    fig.savefig(png_path, dpi=args.dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    print(png_path)
    print(pdf_path)


if __name__ == "__main__":
    main()
