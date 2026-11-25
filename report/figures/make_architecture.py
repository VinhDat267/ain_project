"""Draw Figure 1 (system architecture) in black and white for the final report."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Times New Roman"
fig, ax = plt.subplots(figsize=(10, 7.4), dpi=200)
ax.set_xlim(-5, 101); ax.set_ylim(-4, 79); ax.axis("off")


def box(x, y, w, h, title, lines=(), dashed=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0", linewidth=1.2,
                                edgecolor="black", facecolor="white", linestyle="--" if dashed else "-"))
    ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top", fontsize=11.5, fontweight="bold")
    for i, line in enumerate(lines):
        ax.text(x + w / 2, y + h - 5.4 - i * 3.2, line, ha="center", va="top", fontsize=9.5)


def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1.1, color="black"))


def label(x, y, text, ha="center"):
    ax.text(x, y, text, ha=ha, va="center", fontsize=9, style="italic")


box(26, 66, 48, 12, "User interface", ["Streamlit app (starter/app.py) or React web app",
                                       "served by FastAPI (webapp/)"])
box(26, 50, 48, 10, "Public core API (starter/student_core.py)", ["retrieve(query, top_k), classify_intent(query)"])
box(0, 27, 36, 15, "Retriever (own NumPy code)", ["char_wb 3-5 n-grams, sublinear TF,", "smoothed IDF, L2 norm,",
                                                  "cosine ranking, explain()"])
box(40, 27, 20, 15, "Corpus", ["84 FAQs, 28 notices,", "7 intents", "(read-only JSON/CSV)"], dashed=True)
box(64, 27, 36, 15, "Intent classifier (scikit-learn)", ["word TF-IDF + Logistic", "Regression, C = 10,",
                                                         "231 training texts"])
box(26, 13.5, 48, 10, "Dual-gate abstention", ["answer only if top-1 cosine >= 0.15", "and max P(intent | q) >= 0.34"])
box(26, -3.5, 48, 12, "Result view", ["top-3 answer cards with source and score,", "or a refusal that names the failed gate"])
box(77, -3.5, 23, 21.5, "Evaluation", ["experiments/, scripts/", "call the same API:", "benchmark, dev split,",
                                   "CV, noise, scenarios"], dashed=True)

arrow(50, 65.6, 50, 60.4); label(53.5, 63, "query", ha="left")
arrow(36, 49.6, 20, 42.4); label(25.5, 47.2, "query")
arrow(64, 49.6, 80, 42.4); label(74.5, 47.2, "query")
arrow(39.6, 34.5, 36.4, 34.5); arrow(60.4, 34.5, 63.6, 34.5)
arrow(20, 26.6, 36, 23.9); label(21, 23.2, "ranked documents, cosine s", ha="right")
arrow(80, 26.6, 64, 23.9); label(79, 23.2, "intent c, confidence p", ha="left")
arrow(50, 13.1, 50, 8.9); label(53.5, 11.0, "top-3 list or empty list", ha="left")
ax.plot([25.6, -3, -3], [2.5, 2.5, 72], color="black", lw=1.1)
arrow(-3, 72, 25.6, 72); label(-1.8, 60, "shown to the student", ha="left")

out = Path(__file__).with_name("fig_architecture.png")
fig.savefig(out, bbox_inches="tight", facecolor="white")
