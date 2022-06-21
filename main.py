import datetime
import importlib
import math
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

IG_IM_SIZE = (1080, 1350)

BG_COL = (29, 33, 41)
WHITE_COL = (255, 255, 255)
GREY_COL = (182, 182, 182)
DARK_GREY_COL = (120, 120, 120)

TITLE_FONT_SIZE = 62
SUB_FONT_SIZE = 49
POST_FONT_SIZE = 79
DESC_FONT_SIZE = 31
FOOTER_FONT_SIZE = 24

X_MARGIN = 120
CODE_WINDOW_MARGIN = 92  # Using carbon to generate code image, when rescaled to 1080px wide, margin is 92px.

TITLE_POS = (X_MARGIN, 60)
FOOTER_POS = (720, IG_IM_SIZE[1] - 50)
SUBTITLE_POS = (X_MARGIN, TITLE_POS[1] + TITLE_FONT_SIZE)
ICON_POS = (810, TITLE_POS[1])
SUBTITLE_BOTTOM = SUBTITLE_POS[1] + SUB_FONT_SIZE
POST_TITLE_POS = (X_MARGIN, SUBTITLE_POS[1] + SUB_FONT_SIZE + 79)
DESC_POS = (X_MARGIN, POST_TITLE_POS[1] + POST_FONT_SIZE + 50)

N_CHARS_PER_LINE = 45

OUTFILE = 'test.png'
FONT_PATH_REG = './fonts/FreeMono.ttf'
FONT_PATH_BOLD = './fonts/FreeMonoBold.ttf'
ICON_PATH_PNG = './icons/python_icon.png'

RAW_FOLDER = './raw_material'
OUTPUT_FOLDER = './finished_posts'

CODE_IMG_MARGIN_RAW = 224  # Whitespace on each side of code window.
CODE_IMG_WANTED_WIDTH = 896  # A width that fits the instagram aspect.


def create_bg():
    img = Image.new('RGB', IG_IM_SIZE, BG_COL)
    return img


def draw_text(img, text, font_size, pos, color, bold=False):
    font_path = FONT_PATH_BOLD if bold else FONT_PATH_REG
    mono_font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(img)
    draw.text(pos, text, fill=color, font=mono_font, spacing=10)


def draw_image_from_path(img, pos, img_path, width=None):
    new_img = Image.open(img_path)
    if width is not None:
        scaling = width / new_img.width
        new_size = (int(scaling * new_img.width), int(scaling * new_img.height))
        new_img = new_img.resize(new_size)
    img.paste(new_img, pos, new_img)


def resize_code_img(code_img_path):
    code_img = Image.open(code_img_path)  # Img of code segment.
    code_img_w = code_img.size[0]  # Width of code segment image.
    code_window_w = code_img_w - CODE_IMG_MARGIN_RAW * 2  # Width of code window part of image.
    scaling = CODE_IMG_WANTED_WIDTH / code_window_w  # Scaling factor to get a good size for 1080px wide window.
    new_size = tuple(int(scaling * dim) for dim in code_img.size)

    return code_img.resize(new_size)


def calculate_code_img_pos(code_img: Image):
    # Width:
    x_pos = (IG_IM_SIZE[0] - code_img.size[0]) // 2
    # Height:
    y_pos = IG_IM_SIZE[1] - code_img.size[1]
    return x_pos, y_pos

def draw_dynamic_content(img, code_img_size, texts):
    # Calculate total size of title and description.
    desc_height = math.ceil(len(texts.post_description) / N_CHARS_PER_LINE) * DESC_FONT_SIZE
    total_height = desc_height + POST_FONT_SIZE

    y_min = TITLE_POS[1] + TITLE_FONT_SIZE + SUB_FONT_SIZE
    y_max = IG_IM_SIZE[1] - code_img_size[1] + CODE_WINDOW_MARGIN  # 92 is margin to code window.

    # Split left over margin in 7 pieces, 3 above title, 1 between title and description and 3 below title.
    margin_segment = math.floor((y_max - y_min - total_height) / 7)

    # Draw post title
    draw_text(img, texts.post_title, POST_FONT_SIZE, (X_MARGIN, y_min + 3 * margin_segment), WHITE_COL)

    # Draw description.
    desc = textwrap.fill(texts.post_description, N_CHARS_PER_LINE)
    draw_text(img, desc, DESC_FONT_SIZE, (X_MARGIN, y_min + POST_FONT_SIZE + 4 * margin_segment), WHITE_COL)

def get_today_str():
    today = datetime.datetime.today()
    return f'{today:%Y%m%d}'

def compose_image():
    texts = importlib.import_module(f'raw_material.{get_today_str()}.texts')

    # Create background.
    img = create_bg()

    # Draw title.
    draw_text(img, "Python", TITLE_FONT_SIZE, TITLE_POS, WHITE_COL)

    # Draw subtitle.
    draw_text(img, texts.subtitle, SUB_FONT_SIZE, SUBTITLE_POS, GREY_COL)

    # Draw icon.
    draw_image_from_path(img, ICON_POS, ICON_PATH_PNG, width=TITLE_FONT_SIZE + SUB_FONT_SIZE)

    # Draw code image.
    code_img = resize_code_img(f'raw_material/{get_today_str()}/carbon.png')
    code_img_pos = calculate_code_img_pos(code_img)

    img.paste(code_img, code_img_pos, code_img)

    # Draw post specific title and text such that we always fit between code image and subtitle.
    draw_dynamic_content(img, code_img.size, texts)

    # Draw footer text.
    draw_text(img, f'@software_bonanza', FOOTER_FONT_SIZE, FOOTER_POS, DARK_GREY_COL)

    return img

def generate_out_path():
    today = datetime.datetime.today()
    today_str = f'{today:%Y%m%d}'
    return os.path.join(OUTPUT_FOLDER, today_str, f'post.png')

def main():
    # Create image path
    out_path = generate_out_path()
    os.makedirs(out_path.rsplit('/', 1)[0], exist_ok=True)  # Make all dirs except leaf.

    # Compose image
    img = compose_image()

    # Save image to file
    img.save(out_path)


if __name__ == '__main__':
    main()
