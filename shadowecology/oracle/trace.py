# Author: Bradley R. Kinnard
# shadowecology/oracle/trace.py
# Captures lattice evolution and renders animated tension GIF

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patheffects import withStroke
from PIL import Image
import io
import math
import numpy as np
from shadowecology.ecology.tension import node_tension


# hand-tuned neon colors that pop on deep-space black
TAG_COLORS = {
    "curiosity": "#00FFFF",    # electric cyan
    "caution": "#FFA500",      # vivid orange
    "humor": "#FF1493",        # hot pink
    "verbosity": "#9D4EDD",    # vivid purple
    "depth": "#0096FF",        # electric blue
    "risk": "#FF4500",         # neon orange-red
    "empathy": "#00FF7F",      # spring green
    "identity": "#FFD700",     # pure gold
    "untagged": "#808080",     # neutral gray
}


class Trace:
    # captures evolution of lattice over time
    def __init__(self):
        self.frames = []

    # snapshot current state
    def append(self, lattice, step: int, tension_dict: dict[str, float]):
        frame = {
            "step": step,
            "nodes": dict(lattice.nodes),
            "edges": dict(lattice.edges),
            "tension": dict(tension_dict),
        }
        self.frames.append(frame)

    # render deep-space neon GIF with explosive tension visualization
    def save_gif(self, path: str):
        if not self.frames:
            return

        images = []

        for frame in self.frames:
            # deep-space black background
            fig, ax = plt.subplots(figsize=(12, 10), facecolor='#000000')
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-1.2, 1.2)
            ax.axis('off')
            ax.set_facecolor('#000000')

            nodes = frame["nodes"]
            edges = frame["edges"]
            step = frame["step"]

            # spring-force circular layout with better spacing
            n = len(nodes)
            positions = {}
            radius = 0.85
            for i, nid in enumerate(nodes.keys()):
                angle = 2 * math.pi * i / max(n, 1)
                # add slight jitter for visual interest
                r = radius + 0.05 * np.sin(angle * 3)
                positions[nid] = (r * np.cos(angle), r * np.sin(angle))

            # draw thicker, brighter contradiction edges
            for src, targets in edges.items():
                if src not in positions:
                    continue
                for tgt, strength in targets.items():
                    if tgt not in positions:
                        continue
                    x1, y1 = positions[src]
                    x2, y2 = positions[tgt]

                    # neon edge glow - thicker and brighter
                    if strength < 0:
                        color = "#FF0040"  # hot red for contradiction
                        width = 4.0
                        alpha = 0.9
                    else:
                        color = "#00FF88"  # bright green for agreement
                        width = 3.0
                        alpha = 0.7

                    ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, alpha=alpha, zorder=1)

            # draw nodes with neon glow rings
            from shadowecology.ecology.lattice import Lattice
            lat = Lattice.from_dict({"nodes": nodes, "edges": edges})

            for nid, node in nodes.items():
                if nid not in positions:
                    continue
                x, y = positions[nid]

                # calculate tension
                tension = node_tension(node, lat, step)

                # node size scales with tension
                base_size = 200
                size = base_size + tension * 800

                # primary tag determines color
                primary_tag = node["tags"][0] if node["tags"] else "untagged"
                color = TAG_COLORS.get(primary_tag, "#808080")

                # neon glow ring around high-tension nodes
                if tension > 0.5:
                    glow_size = size * 1.8
                    ax.scatter(x, y, s=glow_size, c=color, alpha=0.15, zorder=2, edgecolors='none')
                    ax.scatter(x, y, s=size * 1.4, c=color, alpha=0.3, zorder=2, edgecolors='none')

                # main node with bright edge
                ax.scatter(x, y, s=size, c=color, alpha=0.85, edgecolors='white', linewidths=3, zorder=3)

                # crisp white labels with black stroke for readability
                label = node["content"][:18] + "..." if len(node["content"]) > 18 else node["content"]
                text = ax.text(x, y - 0.18, label, fontsize=9, ha='center', va='top',
                              color='white', weight='bold', zorder=4)
                text.set_path_effects([withStroke(linewidth=3, foreground='black')])

            # title per frame with neon glow
            title = ax.text(0, 1.05, f"Cognitive Tension – Step {step}",
                           fontsize=18, ha='center', va='bottom',
                           color='#00FFFF', weight='bold')
            title.set_path_effects([withStroke(linewidth=4, foreground='#000000')])

            # compact legend with neon colors
            legend_items = [(tag, color) for tag, color in list(TAG_COLORS.items())[:8]]
            legend_patches = [mpatches.Patch(facecolor=color, edgecolor='white', label=tag)
                            for tag, color in legend_items]
            legend = ax.legend(handles=legend_patches, loc='upper left',
                             fontsize=9, frameon=True, facecolor='#000000',
                             edgecolor='white', framealpha=0.8)
            for text in legend.get_texts():
                text.set_color('white')

            # render to image with aggressive optimization
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=80,
                       facecolor='#000000', edgecolor='none')
            buf.seek(0)
            # convert to P mode (palette) for smaller file size
            img = Image.open(buf).convert('RGB')
            img = img.quantize(colors=64)  # reduce to 64 colors
            images.append(img)
            plt.close(fig)

        # save with heavy optimization for ~30% size reduction
        images[0].save(
            path,
            save_all=True,
            append_images=images[1:],
            duration=600,  # 600ms per frame for better viewing
            loop=0,
            optimize=True,
            disposal=2  # clear frame for better compression
        )
