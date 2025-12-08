# Author: Bradley R. Kinnard
# shadowecology/oracle/trace.py
# Captures lattice evolution and renders animated tension GIF

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image
import io
from shadowecology.ecology.tension import node_tension


# tag color mapping for visualization
TAG_COLORS = {
    "curiosity": "#00D9FF",    # cyan
    "caution": "#FFB800",      # amber
    "humor": "#FF6B9D",        # pink
    "verbosity": "#C77DFF",    # purple
    "depth": "#0077B6",        # blue
    "risk": "#FF5400",         # orange-red
    "empathy": "#06FFA5",      # mint
    "identity": "#FFD60A",     # gold
    "untagged": "#777777",     # gray
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

    # render animated GIF showing tension evolution
    def save_gif(self, path: str):
        if not self.frames:
            return

        images = []

        for frame in self.frames:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.axis('off')

            nodes = frame["nodes"]
            edges = frame["edges"]
            step = frame["step"]

            # simple circular layout
            import math
            n = len(nodes)
            positions = {}
            for i, nid in enumerate(nodes.keys()):
                angle = 2 * math.pi * i / max(n, 1)
                positions[nid] = (0.7 * math.cos(angle), 0.7 * math.sin(angle))

            # draw edges first (underneath)
            for src, targets in edges.items():
                if src not in positions:
                    continue
                for tgt, strength in targets.items():
                    if tgt not in positions:
                        continue
                    x1, y1 = positions[src]
                    x2, y2 = positions[tgt]

                    # edge color and width based on strength
                    color = "red" if strength < 0 else "green"
                    width = abs(strength) * 2
                    alpha = min(abs(strength), 0.8)

                    ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, alpha=alpha, zorder=1)

            # draw nodes on top
            for nid, node in nodes.items():
                if nid not in positions:
                    continue
                x, y = positions[nid]

                # node size = tension
                from shadowecology.ecology.lattice import Lattice
                lat = Lattice.from_dict({"nodes": nodes, "edges": edges})
                tension = node_tension(node, lat, step)
                size = 100 + tension * 500

                # node color = primary tag
                primary_tag = node["tags"][0] if node["tags"] else "untagged"
                color = TAG_COLORS.get(primary_tag, "#777777")

                ax.scatter(x, y, s=size, c=color, alpha=0.7, edgecolors='white', linewidths=2, zorder=2)

                # label with truncated content
                label = node["content"][:20] + "..." if len(node["content"]) > 20 else node["content"]
                ax.text(x, y - 0.15, label, fontsize=8, ha='center', va='top')

            # title with step
            ax.set_title(f"Step {step}", fontsize=14, fontweight='bold')

            # legend for tags
            legend_patches = [mpatches.Patch(color=color, label=tag) for tag, color in TAG_COLORS.items()]
            ax.legend(handles=legend_patches[:8], loc='upper left', fontsize=8, framealpha=0.9)

            # render to image
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            images.append(Image.open(buf))
            plt.close(fig)

        # save as animated GIF
        images[0].save(
            path,
            save_all=True,
            append_images=images[1:],
            duration=500,  # 500ms per frame
            loop=0
        )
