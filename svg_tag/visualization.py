import textwrap, os
import pandas as pd
import random
import numpy as np
import matplotlib.ft2font as ft
import matplotlib.pyplot as plt
from PIL import ImageFont, Image, ImageDraw
from PIL.Image import Image as PilImage

def text_to_image(
    text: str,
    font_filepath: str,
    size: int,
    color: str,
    title: str):
    font = ImageFont.truetype(font=font_filepath, size=10)
    left, top, right, bottom = font.getbbox(text)
    width, height = right - left, bottom - top
    scale = 0.9*min(size[0]/width, size[1]/height)
    font = ImageFont.truetype(font=font_filepath, size=int(10*scale))
    image = Image.new(mode='RGB', size=size, color=color)
    draw = ImageDraw.Draw(im=image)
    draw.text(xy=tuple(ti/2 for ti in size), text=text, font=font, fill='black', anchor='mm')
    image._exif = text
    image.filename = title
    return image

def random_coordinates(width, height, existing_coordinates, image):
    """Generate random x, y coordinates within the given dimensions,
    making sure they do not overlap with any existing coordinates."""
    img_width, img_height = image.size
    x, y = random.randint(0, width-img_width), random.randint(0, height-img_height)
    while any(x <= x2+w and x+img_width >= x2 and y <= y2+h and y+img_height >= y2 for x2, y2, w, h in existing_coordinates):
        x, y = random.randint(0, width-img_width), random.randint(0, height-img_height)
    return (x, y, img_width, img_height)

def place_images(images, background_path):
    """Paste the given images onto the background, with or without overlap."""
    background = Image.new('RGB', (1920, 1080), (255, 255, 255))
    coordinates = []
    for image in images:
        x, y, w, h = random_coordinates(background.width, background.height, coordinates, image)
        coordinates.append((x, y, w, h))
        background.paste(image, (x, y))
    background.save(background_path)
    return background

def gen_table(data, font_title = [], text = [], width = 2**10):
    print('Total number of items :', data.shape[0])
    pad = 15
    cols = 4
    rows = int(np.ceil(data.shape[0] / cols))
    height = int(width / cols / 4 * rows)
    
    x = np.linspace(pad, int(width-width/cols+pad/2), cols)
    y = np.linspace(pad, int(height-height/rows+pad/2), rows)
    xv, yv = np.meshgrid(x, y)
    positions = np.array([xv.astype(int), yv.astype(int)]).reshape(2, -1).T
    
    background = Image.new(mode='RGB', size=(width, height), color='#F0FFFF')#ffaa00
    draw = ImageDraw.Draw(im=background)
    i=0

    font_dict = data.to_dict('records')
    for row in font_dict:
        if text == []:
            txt = row['Family']
        else:
            txt = text
        image = text_to_image(text=txt, font_filepath = os.path.join(row['Path'], row['Name']),
                          size=(int((width - pad) / cols - pad), int((height - pad)/rows - pad)), color='#FFFFFF')

        background.paste(image, tuple(positions[i]))
        if font_title != []:
            draw.text(tuple(positions[i]-pad), row['Name'], fill=(0, 0, 0), 
                      font=ImageFont.truetype(os.path.join(
                          font_list['Path'].loc[font_list['Name'] == font_title].values[0],font_title), int(pad)))
        i=i+1
    return background

def display_images(
    images: [PilImage], 
    columns=3, width=15, height=50, max_images=30, 
    label_wrap_length=50, label_font_size=20, title=''):

    if not images:
        print("No images to display.")
        return 

    if len(images) > max_images:
        print(f"Showing {max_images} images of {len(images)}:")
        images=images[0:max_images]

    plt.figure(figsize=(width, height), constrained_layout=True)
    plt.suptitle(title, y=0, fontsize = int(2 * label_font_size))
    
    for i, image in enumerate(images):

        plt.subplot(int(np.ceil(len(images) / columns)), columns, i + 1)
        plt.imshow(image)

        if hasattr(image, 'filename') | hasattr(image, '_exif'):
            if hasattr(image, 'filename'):
                title=image.filename
            else:
                title=image._exif
            if title.endswith("/"): title = title[0:-1]
            title=os.path.basename(title)
            title=textwrap.wrap(title, label_wrap_length)
            title="\n".join(title)
            plt.title(title, fontsize=label_font_size);
        
        ax = plt.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        
def make_space_above(axes, topmargin=1):
    """ increase figure size to make topmargin (in inches) space for 
        titles, without changing the axes sizes"""
    fig = axes.flatten()[0].figure
    s = fig.subplotpars
    w, h = fig.get_size_inches()

    figh = h - (1-s.top)*h  + topmargin
    fig.subplots_adjust(bottom=s.bottom*h/figh, top=1-topmargin/figh)
    fig.set_figheight(figh)

def main():
    root = './static/fonts'
    files = [os.path.join(path, name) for path, subdirs, files in os.walk(root) for name in files
             if name.lower().endswith(('.otf', '.ttf'))] #'.eot', '.woff', '.woff2'
    font_list = {'Name':[], 'Family':[], 'Style':[], 'PS Name':[], 'Path':[]};
    for f in files:
        font_list['Name'].append(os.path.basename(f))
        font_list['Family'].append(ft.FT2Font(f).family_name)
        font_list['Style'].append(ft.FT2Font(f).style_name)
        font_list['PS Name'].append(ft.FT2Font(f).postscript_name)
        font_list['Path'].append(os.path.dirname(f))
    font_list = pd.DataFrame(font_list)
    font_list.head()
    
    print(font_list.dtypes)
    Styles = pd.unique(font_list['Style'])
    print(Styles)
    
    for Style in Styles:
        print(Style)
        gen_preview(data=font_list.loc[font_list['Style'] == Style])
        gen_table(data=font_list.loc[font_list['Style'] == Style], font_title = [], text = [], width = 2**10)
    
            # Classic fonts
    fonts_c = ['Roboto', 
                'Open Sans', 
                'Montserrat', 
                'Lato', 
                'Poppins', 
                'Source Code Pro', 
                'Raleway', 
                'Noto Sans', 
                'Inter', 
                'Roboto Slab', 
                'Merriweather', 
                'Playfair Display']
    
    # Nice fonts
    fonts_g = ['Arial', 
                'Oswald', 
                'Boogaloo', 
                'Kanit', 
                'Anton', 
                'Audiowide', 
                'Righteous', 
                'Notable', 
                'Architects Daughter', 
                'Michroma', 
                'Holtwood One Sc', 
                'Permanent Marker', 
                'Century Gothic', 
                'Julius Sans One']
    
    # Script fonts
    fonts_s = ['Shadows Into Light', 
                'Great Vibes', 
                'Dancing Script', 
                'Gloria Hallelujah', 
                'Nanum pen script', 
                'Reenie Beanie', 
                'Gochi Hand', 
                'Allison', 
                'Corinthia', 
                'Qwitcher Grypen', 
                'Birthstone bounce', 
                'Windsong']
    fonts_a = fonts_c + fonts_g + fonts_s
    
    tab = {'Classics': fonts_c,
           'Nice': fonts_g,
           'Scripts': fonts_s,
           'All': fonts_a}
    
    # table = gen_table(font_list[font_list['Family'].isin(fonts_c)].loc[font_list['Style'] == 'Regular'], width = 2**12)
    # table.save('fonts_c.png')
    
    # table = gen_table(font_list[font_list['Family'].isin(fonts_g)].loc[font_list['Style'] == 'Regular'], width = 2**12)
    # table.save('fonts_g.png')
    
    # table = gen_table(font_list[font_list['Family'].isin(fonts_s)].loc[font_list['Style'] == 'Regular'], width = 2**12)
    # table.save('fonts_s.png')
    
    # for Style in Styles:
    #     print(Style)
    #     gen_preview(data=font_list.loc[font_list['Style'] == Style])
    
    for font in tab:
        # If table
        # selec = font_list[font_list['Family'].isin(font)].loc[font_list['Style'] == 'Regular']
        # images = [text_to_image(text = ft.FT2Font('./static/fonts/' + f).family_name, font_filepath = './static/fonts/' + f, size=(2**10, 2**8), color='#F0FFFF') for f in selec.Name]
        
        # If dictionary:
        selec = font_list[font_list['Family'].isin(tab.get(font))].loc[font_list['Style'] == 'Regular']
        # images = [text_to_image(text = ft.FT2Font('./static/fonts/' + f).family_name, font_filepath = './static/fonts/' + f, size=(2**10, 2**8), color='#F0FFFF') for f in selec.Name]
        images = [text_to_image(text = 'Example', font_filepath = './static/fonts/' + f, 
                                size=(2**10, 2**8), color='#F0FFFF', title = ft.FT2Font('./static/fonts/' + f).family_name) for f in selec.Name]
        n = len(images)
        max_images = n
        font_size = 20
        D = 5
        cols = 3
        rows = int(np.ceil(n / cols))
        width = D * cols
        height = int(2 * (rows + .5))
        print(cols, rows, width, height)
        display_images(images, columns=cols, width=width, height=height,
               max_images=n, label_wrap_length=50, label_font_size=font_size, title=font)        
        
        plt.savefig('./outputs/fonts_' + font + '.png', dpi='figure', format='png', bbox_inches = 'tight', pad_inches = 0.5)
    

if __name__ == "__main__":
    main()