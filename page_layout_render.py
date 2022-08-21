import numpy as np
from cv2 import aruco
import matplotlib.pyplot as plt
from hexagons import HexagonsGrid
from matplotlib import font_manager
from pdfrw import PageMerge, PdfReader, PdfWriter
from fpdf import FPDF, HTMLMixin
import qrcode


class PDF(FPDF, HTMLMixin):
    pass


# font_dirs = ['./fonts/']
# font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

# for font_file in font_files:
#    font_manager.fontManager.addfont(font_file)

# set font
# plt.rcParams['font.family'] = 'Futura PT'

# global documents param
h = 297  # height in mm
w = 210  # width in mm
pf = 100  # pixel factor (how many pixels in one mm)
pd = 5  # padding in mm
header_size = 55  # height fo the header in mm
corner_aruco_size = 8  # size of the corner aruco markers in mm


def plot_aruco(i, x, y, size):
    """

    Parameters
    ----------
    i
    x
    y
    size: Float
        Size in mm

    Returns
    -------

    """
    aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
    aruco_img = aruco.drawMarker(aruco_dict, i, size * pf)
    plt.imshow(aruco_img, extent=(x * pf, (x + size) * pf, (y + size) * pf, y * pf),
               cmap='Greys_r', zorder=5, interpolation='none')


fig = plt.figure(figsize=(8.27, 11.69))

# plot hexagonal grid
hg = HexagonsGrid(orientation='pointy', size=5 * pf,
                  start_pos=((pd + 10) * pf, (header_size + pd + 15) * pf),
                  corners=(((pd + 10) * pf, (header_size + pd + 15) * pf),
                           ((w - pd - 10) * pf, (h - pd - 15) * pf)))
q = np.array(hg.get_polygons(loop=True))
qc = np.array(hg.get_centers())

plt.plot(q[:, :, 0].T, q[:, :, 1].T, color='gainsboro', zorder=1)

# add random locations for participants
n_participants = 8
participant_aruco_size = 5
ids = q.shape[0]
rng = np.random.RandomState(seed=42)
selected = rng.choice(np.arange(ids), n_participants, replace=False)
for i in range(n_participants):
    plot_aruco(i + 10, (qc[selected[i], 0] / pf - participant_aruco_size / 2),
               (qc[selected[i], 1] / pf - participant_aruco_size / 2),
               size=participant_aruco_size)
    plt.fill(q[selected[i], :, 0].T, q[selected[i], :, 1].T, color='gainsboro', zorder=0)

# temporary plot border lines
# plt.axhline(pd * pf)
# plt.axhline((-pd + h) * pf)
# plt.axvline(pd * pf)
# plt.axvline((-pd + w) * pf)

# plt.axhline((header_size + pd) * pf, color='black')

# add aruco to corners
aruco_coords = np.array([
    [[pd], [header_size + pd]],
    [[w - pd - corner_aruco_size], [header_size + pd]],
    [[pd], [h - pd - corner_aruco_size]],
    [[w - pd - corner_aruco_size], [h - pd - corner_aruco_size]]
])
plot_aruco(0, pd, header_size + pd, corner_aruco_size)
plot_aruco(1, w - pd - corner_aruco_size, header_size + pd, corner_aruco_size)
plot_aruco(2, pd, h - pd - corner_aruco_size, corner_aruco_size)
plot_aruco(3, w - pd - corner_aruco_size, h - pd - corner_aruco_size, corner_aruco_size)
print(aruco_coords)
# pull plots on the A4 size page
plt.gca().set_position([0, 0, 1, 1])
plt.xlim(0, w * pf)
plt.ylim(0, h * pf)
plt.gca().invert_yaxis()
plt.gca().axis('off')
plt.gca().set_axis_off()

plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                    hspace=0, wspace=0)
plt.margins(0, 0)
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())

fig.savefig("documents/test.pdf", bbox_inches='tight', pad_inches=0.0)
plt.close()

# text part
title = "The Coffee Game"
text_left = "Welcome to The Coffee Game. The rules are simple - you " \
            "drink your coffee, you put a cross next to the field " \
            "associated with your name. The only two requirements are: " \
            "1. Keep your field of crosses **connected**; " \
            "2. Never get closer than **one tile** to " \
            "the fields of other participants. Enjoy!"
plt.text(w * pf / 2, (pd + 1) * pf, title, fontsize=32,
         horizontalalignment='center',
         verticalalignment='top')
plt.text((pd + 10) * pf / 2, (pd + 20) * pf, text_left, horizontalalignment='left',
         verticalalignment='top', fontsize=14, wrap=True)


def new_content():
    fpdf = PDF()
    fpdf.add_page()
    fpdf.add_font("Futura PT", fname=r'./fonts/FuturaPTBook.ttf')
    fpdf.add_font("Futura PT", style='I', fname=r'./fonts/FuturaPTBookOblique.ttf')
    fpdf.add_font("Futura PT", style='B', fname=r'./fonts/FuturaPTHeavy.ttf')
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

    img = qrcode.make("www.cancerclonemaps.org")
    fpdf.image(img.get_image(), x=120 + 40, y=23,
               w=25, h=25)

    reader = PdfReader(fdata=bytes(fpdf.output()))
    return reader.pages[0]


# merge text pdf with the game field pdf
pdf_field = PdfReader("documents/test.pdf")
pdf_merged = PdfWriter()
pdf_merged.addpage(pdf_field.pages[0])

PageMerge(pdf_merged.pagearray[0]).add(new_content(), prepend=False).render()
pdf_merged.write("documents/test.pdf")
