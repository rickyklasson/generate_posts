import textwrap

from PIL import Image, ImageDraw, ImageFont

IG_IM_SIZE = (1080, 1350)

BG_COL = (29, 33, 41)
WHITE_COL = (255, 255, 255)
GREY_COL = (182, 182, 182)

TITLE_FONT_SIZE = 62
SUB_FONT_SIZE = 49
POST_FONT_SIZE = 79
DESC_FONT_SIZE = 31

TITLE_POS = (120, 80)
SUBTITLE_POS = (TITLE_POS[0], TITLE_POS[1] + TITLE_FONT_SIZE)
ICON_POS = (810, TITLE_POS[1])
SUBTITLE_BOTTOM = SUBTITLE_POS[1] + SUB_FONT_SIZE
POST_TITLE_POS = (SUBTITLE_POS[0], SUBTITLE_POS[1] + SUB_FONT_SIZE + 105)
DESC_POS = (POST_TITLE_POS[0], POST_TITLE_POS[1] + POST_FONT_SIZE + 50)

N_CHARS_PER_LINE = 45

OUTFILE = 'test.png'
FONT_PATH_REG = './fonts/FreeMono.ttf'
FONT_PATH_BOLD = './fonts/FreeMonoBold.ttf'
ICON_PATH_PNG = './icons/python_icon.png'

CODE_IMG_MARGIN_RAW = 224  # Whitespace on each side of code window.


def create_bg():
    img = Image.new('RGB', IG_IM_SIZE, BG_COL)
    return img


def draw_text(img, text, font_size, pos, color, bold=False):
    font_path = FONT_PATH_BOLD if bold else FONT_PATH_REG
    mono_font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(img)
    draw.text(pos, text, fill=color, font=mono_font)


def draw_image_from_path(img, pos, img_path, width=None):
    new_img = Image.open(img_path)
    if width is not None:
        scaling = width / new_img.width
        new_size = (int(scaling * new_img.width), int(scaling * new_img.height))
        new_img = new_img.resize(new_size)
    img.paste(new_img, pos, new_img)


def resize_code_img(code_img_path):
    CODE_SEC_WANTED_W = 896  # A width that fits the instagram aspect.

    code_img = Image.open(code_img_path)  # Img of code segment.
    code_img_w = code_img.size[0]  # Width of code segment image.
    code_window_w = code_img_w - CODE_IMG_MARGIN_RAW * 2  # Width of code window part of image.
    scaling = CODE_SEC_WANTED_W / code_window_w  # Scaling factor to get a good size for 1080px wide window.
    new_size = tuple(int(scaling * dim) for dim in code_img.size)

    return code_img.resize(new_size)


def calculate_code_img_pos(code_img: Image):
    # Width:
    x_pos = (IG_IM_SIZE[0] - code_img.size[0]) // 2
    # Height:
    y_pos = IG_IM_SIZE[1] - code_img.size[1]
    return x_pos, y_pos


def main():
    # Create background.
    img = create_bg()

    # Draw title.
    draw_text(img, "Python", TITLE_FONT_SIZE, TITLE_POS, WHITE_COL)

    # Draw subtitle.
    draw_text(img, f"Beginner tip #1", SUB_FONT_SIZE, SUBTITLE_POS, GREY_COL)

    # Draw icon.
    draw_image_from_path(img, ICON_POS, ICON_PATH_PNG, width=TITLE_FONT_SIZE + SUB_FONT_SIZE)

    # Draw code image.
    code_img = resize_code_img('./carbon.png')
    code_img_pos = calculate_code_img_pos(code_img)

    img.paste(code_img, code_img_pos, code_img)

    # Draw post title
    draw_text(img, "Comprehensions", POST_FONT_SIZE, POST_TITLE_POS, WHITE_COL, bold=True)

    # Draw description.
    desc = "Similar to list comprehension, Python also supports dictionary comprehension."
    desc = textwrap.fill(desc, N_CHARS_PER_LINE)
    draw_text(img, desc, DESC_FONT_SIZE, DESC_POS, WHITE_COL)

    # Draw footer text.

    # Save output image.
    img.save(OUTFILE)


if __name__ == '__main__':
    main()
