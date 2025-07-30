#from rich.pretty import pprint as PP
import turbocore
import trimesh
import numpy as np
import matplotlib.pyplot
from trimesh.path.entities import Line, Arc, Bezier
import matplotlib.image as mpimg
import qrcode


def main():
    turbocore.cli_this(__name__, 'cli_')


def cli_xy(STLFILE, LAYOUT, Z, TITLE, SUBTITLE, PDF):
    filename = STLFILE
    mesh = trimesh.Trimesh()
    if STLFILE != "":
        mesh = trimesh.load(filename)
    plane_origin = [0,0,float(Z)]
    plane_normal = [0,0,1]
    
    width = 210
    height = 297
    width_inch = width / 25.4
    height_inch = height / 25.4

    fig, ax = matplotlib.pyplot.subplots(figsize=(width_inch, height_inch))
    ax = fig.add_axes([0, 0, 1, 1])

    section = mesh.section(plane_origin=plane_origin,plane_normal=plane_normal)

    if section is not None:
        slice_2d, to_3d = section.to_planar()

        min_xy, max_xy = slice_2d.bounds
        # print(slice_2d.bounds)
        # print(min_xy)
        center_slice = (min_xy + max_xy) / 2
        center_page = np.array([width/2, height/2])
        shift = center_page - center_slice

        if LAYOUT == "auto":
            slice_2d.apply_translation(shift)
        else:
            layout_cols_s = LAYOUT.split(",")
            l_mode = layout_cols_s[0]

            if l_mode == "o":
                # o,10,10 # origin x=10, y=10
                dx = float(layout_cols_s[1])
                dy = float(layout_cols_s[2])
                shift = np.array([dx,dy])
                slice_2d.apply_translation(shift)

            if l_mode == "bb":
                # bb,20,30 # bounding box x=20, y=30
                dx = float(layout_cols_s[1])
                dy = float(layout_cols_s[2])
                shift = min_xy * (-1) + np.array([dx, dy])
                slice_2d.apply_translation(shift)

        discretized = slice_2d.discrete
        for segment in discretized:
            xs, ys = segment[:, 0], segment[:, 1]
            ax.plot(xs,ys,color="black", linewidth=0.8)
    
    major_ticks = np.arange(0, max(width, height), 10)
    minor_ticks = np.arange(0, max(width, height), 1)

    ax.set_xticks(major_ticks)
    ax.set_yticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_yticks(minor_ticks, minor=True)

    grid_alpha = 0.6
    alpha_x = 0.6;
    alpha_y = 0.6;

    ax.grid(which='minor', color='lightgrey', linewidth=0.3, alpha=grid_alpha)
    ax.grid(which='major', color='grey', linewidth=0.7, alpha=grid_alpha)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.invert_yaxis()  # damit oben = 0 ist, wie auf Papier üblich
    ax.set_aspect('equal')
    ax.tick_params(labelbottom=False, labelleft=False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    if TITLE != "":
        ax.text(15, 280-5, TITLE, fontweight="bold", fontfamily='monospace', fontsize=9, color="black",bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0.3"))
    if SUBTITLE != "":
        ax.text(15, 285-5, SUBTITLE, fontfamily='monospace', fontsize=9, color="black",bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0.3"))


    for x_ in range(1, 21):
        hori_down = 4
        ax.text(10*x_ + 0.8, 3+hori_down, "%d" % (x_*10), fontfamily='monospace', fontsize=5, color="black", alpha=alpha_x)
        if x_ > 0 and x_ < 20:
            ax.text(10*x_ + 0.8, 287-5+hori_down, "%d" % (x_*10), fontfamily='monospace', fontsize=5, color="black", alpha=alpha_x)
            ax.text(10*x_ + 0.8, 180+2+hori_down, "%d" % (x_*10), fontfamily='monospace', fontsize=5, color="black", alpha=alpha_x)
            ax.text(10*x_ + 0.8, 80+2+hori_down, "%d" % (x_*10), fontfamily='monospace', fontsize=5, color="black", alpha=alpha_x)

    for y_ in range(1, 30):
        ax.text(5+1, 10*y_ + 2, "%d" % (y_*10), fontfamily='monospace', fontsize=5, color="black", alpha=alpha_y, fontweight="bold")
        ax.text(210-4-5, 10*y_ + 2, "%d" % (y_*10), fontfamily='monospace', fontsize=5, color="black", alpha=alpha_y, fontweight="bold")

    #img = mpimg.imread("dein_bild.png")
    # Bild platzieren: extent = (x_min, x_max, y_min, y_max)
    #ax.imshow(img, extent=(x0, x1, y0, y1))

    # qr = qrcode.make("Test Daten")
    # qr_np = np.array(qr)
    # x0, x1 = 10, 50
    # y0, y1 = 250, 290  # Beachte deine invertierte Y-Achse!
    # ax.imshow(qr_np, extent=(x0, x1, y0, y1), cmap='gray', zorder=100)

    matplotlib.pyplot.savefig(PDF, format="pdf", pad_inches=0)
    matplotlib.pyplot.close()
