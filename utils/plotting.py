import matplotlib.pyplot as plt
import numpy as np

def plot_sfd_bmd(x, V, M, V_compare=None, M_compare=None):
    fig, ax = plt.subplots(2, 1, figsize=(8, 8), constrained_layout=True)
    ax[0].plot(x, V, linestyle="--", label="Custom (SFD)")
    if V_compare is not None:
        ax[0].plot(x, V_compare, linestyle="-", label="Example (SFD)")
    ax[0].axhline(0, color="black", linewidth=0.6)
    ax[0].set_ylabel("Shear Force (kN)")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(x, M, linestyle="--", color="tab:red", label="Custom (BMD)")
    if M_compare is not None:
        ax[1].plot(x, M_compare, linestyle="-", color="tab:orange", label="Example (BMD)")
    ax[1].axhline(0, color="black", linewidth=0.6)
    ax[1].set_ylabel("Bending Moment (kNm)")
    ax[1].set_xlabel("Position along beam (m)")
    ax[1].grid(True)
    ax[1].legend()

    plt.show()
    return fig

def draw_beam_schematic(length, loads, support):
    fig, ax = plt.subplots(figsize=(10, 2.5))
    ax.set_xlim(-0.1*length, 1.1*length)
    ax.set_ylim(-1, 1)
    ax.axis("off")

    # Beam line
    ax.plot([0, length], [0, 0], color="black", linewidth=4)

    # Supports
    if support == "simply_supported":
        ax.plot([0], [0], marker=(3, 0, 0), markersize=20, color="black")
        ax.plot([length], [0], marker=(3, 0, 180), markersize=20, color="black")
    elif support == "cantilever":
        # fixed at left
        ax.add_patch(plt.Rectangle((-0.02*length, -0.2), 0.02*length, 0.4, color="black"))

    # Loads
    for ld in loads:
        if ld["type"] == "point":
            a = ld["a"]
            P = ld["P"]
            ax.annotate("", xy=(a, 0.6), xytext=(a, 0.05), arrowprops=dict(arrowstyle="->", color="red", lw=2))
            ax.text(a, 0.65, f"{P} kN", ha="center", color="red")
        elif ld["type"] == "udl":
            s = ld["start"]
            e = ld["end"]
            w = ld["w"]
            xs = np.linspace(s, e, 10)
            for xi in xs:
                ax.annotate("", xy=(xi, 0.45), xytext=(xi, 0.05), arrowprops=dict(arrowstyle="->", color="blue", lw=1))
            ax.text((s+e)/2, 0.5, f"{w} kN/m", ha="center", color="blue")

    ax.set_title("Beam Schematic")
    plt.close(fig)
    return fig
