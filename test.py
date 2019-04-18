import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.cbook import get_sample_data
import os

os.chdir('/Users/peterpfleiderer/Projects/Persistence')



def imscatter(x, y, image, ax=None, zoom=1):
    if ax is None:
        ax = plt.gca()
    try:
        image = plt.imread(image)
    except TypeError:
        # Likely already an array...
        pass
    im = OffsetImage(image, zoom=zoom)
    x, y = np.atleast_1d(x, y)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    ax.update_datalim(np.column_stack([x, y]))
    ax.autoscale()
    return artists

icon_dict = {'storm_track':get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/weather.png')}

x = np.linspace(0, 10, 20)
y = np.cos(x)

fig, ax = plt.subplots()
imscatter(x, y, icon_dict['storm_track'], zoom=0.05, ax=ax)
ax.plot(x, y)
# image = plt.imread(image_path)
# plt.imshow(image)
plt.savefig('plots/test.png',dpi=300)
