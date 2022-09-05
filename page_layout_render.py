import numpy as np
from cv2 import aruco
import matplotlib.pyplot as plt
from hexagons import HexagonsGrid
from pdfrw import PageMerge, PdfReader, PdfWriter
from fpdf import FPDF, HTMLMixin
import qrcode

# global documents param
h = 297  # height in mm
w = 210  # width in mm
pf = 100  # pixel factor (how many pixels in one mm)
pd = 5  # padding in mm
header_size = 55  # height fo the header in mm
corner_aruco_size = 8  # size of the corner aruco markers in mm


def create_hex_grid(grid_size=5, orientation='pointy', ax=None):
    if ax is None:
        ax = plt.gca()

    hex_grid = HexagonsGrid(orientation=orientation, size=grid_size * pf,
                            start_pos=((pd + 10) * pf, (header_size + pd + 15) * pf),
                            corners=(((pd + 10) * pf, (header_size + pd + 15) * pf),
                                     ((w - pd - 10) * pf, (h - pd - 15) * pf)))
    q = np.array(hex_grid.get_polygons(loop=True))
    ax.plot(q[:, :, 0].T, q[:, :, 1].T, color='gainsboro', zorder=1)
    return hex_grid


def plot_aruco(i, x, y, size, ax=None):
    """

    Parameters
    ----------
    ax
    i
    x
    y
    size: Float
        Size in mm

    Returns
    -------

    """
    if ax is None:
        ax = plt.gca()
    aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
    aruco_img = aruco.drawMarker(aruco_dict, i, size * pf)
    ax.imshow(aruco_img, extent=(x * pf, (x + size) * pf, (y + size) * pf, y * pf),
              cmap='Greys_r', zorder=5, interpolation='none')


def draw_random_markers(hex_grid, ax=None):
    if ax is None:
        ax = plt.gca()

    q = np.array(hex_grid.get_polygons(loop=True))
    qc = np.array(hex_grid.get_centers())

    n_participants = 8
    participant_aruco_size = 5
    ids = q.shape[0]
    rng = np.random.RandomState(seed=42)
    selected = rng.choice(np.arange(ids), n_participants, replace=False)
    for i in range(n_participants):
        plot_aruco(i + 10, (qc[selected[i], 0] / pf - participant_aruco_size / 2),
                   (qc[selected[i], 1] / pf - participant_aruco_size / 2),
                   size=participant_aruco_size)
        ax.fill(q[selected[i], :, 0].T, q[selected[i], :, 1].T, color='gainsboro', zorder=0)


def draw_markers(hex_grid, players, ax=None):
    if ax is None:
        ax = plt.gca()

    participant_aruco_size = 5

    for p in players:
        hex = hex_grid[p['coords'][0], p['coords'][1]]
        center = hex.get_center()
        vertices = np.array(hex.get_polygon(loop=True))
        plot_aruco(10, (center[0] / pf - participant_aruco_size / 2),
                   (center[1] / pf - participant_aruco_size / 2),
                   size=participant_aruco_size)
        ax.fill(vertices[:, 0], vertices[:, 1], color='gainsboro', zorder=0)


def draw_corner_aruco(ax):
    # add aruco to corners
    plot_aruco(0, pd, header_size + pd, corner_aruco_size, ax=ax)
    plot_aruco(1, w - pd - corner_aruco_size, header_size + pd, corner_aruco_size, ax=ax)
    plot_aruco(2, pd, h - pd - corner_aruco_size, corner_aruco_size, ax=ax)
    plot_aruco(3, w - pd - corner_aruco_size, h - pd - corner_aruco_size, corner_aruco_size, ax=ax)


def sanitise_figure(fig):
    ax = fig.gca()
    # pull plots on the A4 size page
    ax.set_position([0, 0, 1, 1])
    ax.set_xlim(0, w * pf)
    ax.set_ylim(0, h * pf)
    ax.invert_yaxis()
    ax.axis('off')
    ax.set_axis_off()

    fig.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0, wspace=0)
    ax.margins(0, 0)
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())


class PDF(FPDF, HTMLMixin):
    pass


def get_fpdf_page():
    fpdf = PDF()
    fpdf.add_page()
    fpdf.add_font("Futura PT", fname=r'./fonts/FuturaPTBook.ttf')
    fpdf.add_font("Futura PT", style='I', fname=r'./fonts/FuturaPTBookOblique.ttf')
    fpdf.add_font("Futura PT", style='B', fname=r'./fonts/FuturaPTHeavy.ttf')
    return fpdf


def add_text(fpdf):
    # text part
    title = "The Coffee Game"
    text_left = "Welcome to The Coffee Game. The rules are simple - you " \
                "drink your coffee, you put a cross next to the field " \
                "associated with your name. The only two requirements are:\n" \
                "1. Keep your field of crosses **connected**; \n" \
                "2. Never get closer than **one tile** to " \
                "the fields of other participants. Enjoy!"

    fpdf.set_font("Futura PT")
    # title
    fpdf.set_font("helvetica", size=32)
    width = fpdf.get_string_width(title) + 6
    fpdf.set_x((210 - width) / 2)
    fpdf.set_line_width(1)
    fpdf.cell(
        width,
        9,
        title,
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    fpdf.ln(6)
    fpdf.set_font("Futura PT", size=12)
    # Printing text in a 6cm width column:
    fpdf.multi_cell(120, 5, text_left, markdown=True)
    fpdf.ln()


def draw_qr(fpdf, qr_string):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=4,
    )

    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    fpdf.image(img.get_image(), x=120 + 40, y=23,
               w=35, h=35)


def renger_field(config, output_name):
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = fig.gca()

    hex_grid = create_hex_grid(grid_size=config['grid_size'], orientation=config['orientation'], ax=ax)
    draw_markers(hex_grid, players=config['players'], ax=ax)
    draw_corner_aruco(ax)
    sanitise_figure(fig)
    fig.savefig(output_name, bbox_inches='tight', pad_inches=0.0)
    plt.close()


def create_text_and_merge(qr_string, output_name):
    fpdf = get_fpdf_page()
    add_text(fpdf)
    draw_qr(fpdf, qr_string)

    pdf_with_text = PdfReader(fdata=bytes(fpdf.output())).pages[0]

    pdf_field = PdfReader(output_name)
    pdf_merged = PdfWriter()
    pdf_merged.addpage(pdf_field.pages[0])

    PageMerge(pdf_merged.pagearray[0]).add(pdf_with_text, prepend=False).render()
    pdf_merged.write(output_name)


def render_page(config, qr_string, output_name='documents/game_field.pdf'):
    renger_field(config, output_name)
    create_text_and_merge(qr_string, output_name)


if __name__ == '__main__':
    s = 'https://test.org?dshfkjdshfkdsjhgkjsdngshgjdshgflsgfkjshgdksjnghgoijgkhflgsgkdshgsad' \
        'jgkshlgkdjs;kgfslhgacm;sjgkfjgmcajgc;lgjmlkdsjg;lmsdhkfd'

    config = {'type': 'pointy',
              'hex_size': 5,
              'players': [{'name': 'Player1', 'coords': [-2, 12]},
                          {'name': 'Player2', 'coords': [-8, 17]},
                          {'name': 'Player3', 'coords': [0, 9]},
                          {'name': 'Player4', 'coords': [18, 2]},
                          {'name': 'Player5', 'coords': [-11, 27]},
                          {'name': 'Player6', 'coords': [3, 24]},
                          {'name': 'Player7', 'coords': [9, 9]}]}
    render_page(config, s)
