import argparse
import importlib
import math
import os
import textwrap
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont

# Local imports
from webhandler import image_from_code_selenium


@dataclass
class XY:
    x: int
    y: int

    def __call__(self):
        return self.x, self.y


@dataclass
class RGB:
    r: int
    g: int
    b: int

    def __call__(self):
        return self.r, self.g, self.b


IG_IM_SIZE = XY(1080, 1350)
BG_COL = RGB(29, 33, 41)
WHITE_COL = RGB(255, 255, 255)
GREY_COL = RGB(182, 182, 182)
DARK_GREY_COL = RGB(120, 120, 120)

TITLE_FONT_SIZE = 48
SUB_FONT_SIZE = 42
POST_TITLE_FONT_SIZE = 72
DESC_FONT_SIZE = 31
FOOTER_FONT_SIZE = 24

X_MARGIN = 120
CODE_WINDOW_MARGIN = 92  # Using carbon to generate code image, when rescaled to 1080px wide, margin is 92px.

TITLE_Y_POS = 60
FOOTER_OFFSET = XY(600, 1300)
ICON_POS = XY(810, TITLE_Y_POS)
SUB_Y_POS = TITLE_Y_POS + TITLE_FONT_SIZE

DESC_NR_CHARS_LINE = 45

CODE_IMG_MARGIN_RAW = 224  # Whitespace on each side of code window.
CODE_IMG_WANTED_WIDTH = 896  # A width that fits the instagram aspect.

FONT_PATH_REG = './fonts/FreeMono.ttf'
FONT_PATH_BOLD = './fonts/FreeMonoBold.ttf'
ICON_PATH = './icons/python_icon.png'

RAW_FOLDER = './raw_material'
OUTPUT_FOLDER = './posts'

TITLE = "Python"


class ImageComposer:
    """Composes an output image from source images and text."""

    def __init__(self, nr_img: int, target_folder: str, img_idx_to_gen: list):
        self.nr_img: int = nr_img
        self.offset: XY = XY(0, 0)  # Offset when drawing onto image.
        self.img_size: XY = XY(1080, 1350)
        self.target_folder: str = target_folder
        self.img_idx_to_gen = img_idx_to_gen

    def compose_images(self):
        """Compose the resulting output image and return it."""
        img: Image = self.init_image()

        for img_idx in range(self.nr_img):
            if not self.should_generate(img_idx):
                continue

            self.offset = XY(self.img_size.x * img_idx, 0)
            x_offset = self.offset.x + X_MARGIN

            # Create code view for first image.
            image_from_code_selenium(source_folder=self.target_folder, img_idx=img_idx)

            # Load text for first image.
            texts = self.load_texts(img_idx)

            # If first image, render title and subtitle.
            if img_idx == 0:
                # Title and subtitle.
                self.text_on_image(img, TITLE, TITLE_FONT_SIZE, (x_offset, TITLE_Y_POS), WHITE_COL())
                self.text_on_image(img, texts.subtitle, SUB_FONT_SIZE, (x_offset, SUB_Y_POS), GREY_COL())

                # Draw python icon.
                icon_img = Image.open(ICON_PATH)
                icon_img = self.resize_img(icon_img, TITLE_FONT_SIZE + SUB_FONT_SIZE)
                self.image_on_image(img, icon_img, ICON_POS())

            # Draw code image.
            code_img = Image.open(os.path.join(RAW_FOLDER, self.target_folder, f'code_{img_idx}.png'))
            code_img = self.resize_code_img(code_img)
            code_img_pos = self.calc_code_img_pos(code_img, img_idx)
            self.image_on_image(img, code_img, code_img_pos)

            # Draw dynamic content.
            y_min, y_max = self.calc_content_avail_space(img_idx, code_img.size)
            self.draw_dynamic_content(img, img_idx, texts, y_min, y_max)

            # Draw footer text.
            footer_pos = (FOOTER_OFFSET.x + x_offset, FOOTER_OFFSET.y)
            self.text_on_image(img, f'@software_bonanza', FOOTER_FONT_SIZE, footer_pos, DARK_GREY_COL())

        # Slice image into self.nr_img of IG friendly size.
        for img_idx in range(self.nr_img):
            if not self.should_generate(img_idx):
                continue
            out_path = os.path.join(OUTPUT_FOLDER, self.target_folder, f'post_{img_idx}.png')
            slice_boundary = (self.img_size.x * img_idx, 0,
                              self.img_size.x * (img_idx + 1), self.img_size.y)
            img_slice = img.crop(box=slice_boundary)
            self.save_img(img_slice, out_path)

    def calc_content_avail_space(self, img_idx: int, code_img_size: tuple):
        """Calculates available space for dynamic context, i.e. post title and description."""
        y_max = self.img_size.y - code_img_size[1] + CODE_WINDOW_MARGIN  # 92 is margin to code window.
        if img_idx == 0:
            y_min = TITLE_Y_POS + TITLE_FONT_SIZE + SUB_FONT_SIZE
        else:
            y_min = 0

        return y_min, y_max

    def calc_code_img_pos(self, code_img: Image, img_idx: int):
        # Width:
        x_pos = (self.img_size.x - code_img.width) // 2 + self.img_size.x * img_idx
        # Height:
        y_pos = self.img_size.y - code_img.height
        return x_pos, y_pos

    def should_generate(self, img_idx):
        if self.img_idx_to_gen and not img_idx in self.img_idx_to_gen:
            return False
        else:
            return True

    def draw_dynamic_content(self, img: Image, img_idx: int, texts, y_min: int, y_max: int):
        x_offset = X_MARGIN + img_idx * self.img_size.x
        # Calculate total size of title and description.
        desc_height = math.ceil(len(texts.post_description) / DESC_NR_CHARS_LINE) * DESC_FONT_SIZE
        if img_idx == 0:
            total_height = desc_height + POST_TITLE_FONT_SIZE
        else:
            total_height = desc_height
        # Split left over margin in 7 pieces, 3 above title, 1 between title and description and 3 below title.
        margin_segment = math.floor((y_max - y_min - total_height) / 7)

        # Draw post title
        post_title_pos = XY(x_offset, y_min + 2 * margin_segment)
        self.text_on_image(img, texts.post_title, POST_TITLE_FONT_SIZE, post_title_pos(), WHITE_COL())

        # Draw description.
        post_desc_pos = (x_offset, post_title_pos.y + POST_TITLE_FONT_SIZE + margin_segment)
        post_desc_wrapped = textwrap.fill(texts.post_description, DESC_NR_CHARS_LINE)
        self.text_on_image(img, post_desc_wrapped, DESC_FONT_SIZE, post_desc_pos, WHITE_COL())

    def init_image(self):
        """Creates the image object to draw on to."""
        return Image.new('RGB', (self.img_size.x * self.nr_img, self.img_size.y), BG_COL())

    def load_texts(self, img_idx: int):
        return importlib.import_module(f'raw_material.{self.target_folder}.texts_{img_idx}')

    def text_on_image(self, img: Image, text: str, font_size: int, text_pos: tuple, text_color: tuple, bold=False):
        """Writes text on to target image."""
        font_path = FONT_PATH_BOLD if bold else FONT_PATH_REG
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(img)
        draw.text(text_pos, text, fill=text_color, font=font, spacing=10)

    def image_on_image(self, img: Image, paste_img: Image, paste_img_pos: tuple):
        img.paste(paste_img, paste_img_pos, paste_img)

    def resize_code_img(self, code_img: Image):
        code_window_w = code_img.width - CODE_IMG_MARGIN_RAW * 2  # Width of code view part of image (exclude margins).
        scaling = CODE_IMG_WANTED_WIDTH / code_window_w  # Scaling factor to get a good size for 1080px wide window.
        new_size = (int(scaling * code_img.width), int(scaling * code_img.height))
        return code_img.resize(new_size)

    def resize_img(self, img: Image, width: int):
        scaling = width / img.width
        new_size = (int(scaling * img.width), int(scaling * img.height))
        return img.resize(new_size)

    def save_img(self, img, output_path):
        """Saves image to output file path."""
        os.makedirs(output_path.rsplit('/', 1)[0], exist_ok=True)
        img.save(output_path)


def main(args):
    img_composer = ImageComposer(nr_img=args.n, target_folder=args.t, img_idx_to_gen=args.s)
    img_composer.compose_images()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate image for instagram')
    parser.add_argument('-t', type=str, required=True,
                        help='Target folder name inside "raw_material" to load data from and name inside posts to \
                              generate output to.')
    parser.add_argument('-n', type=int, default=1,
                        help='Number of images to generate. Expects there to be an equal number of source text files.')
    parser.add_argument('-s', type=int, nargs='+',
                        help='List of which images to generate. Default is to generate all. Throws error if larger \
                              than the number of images (-n).')

    main(parser.parse_args())
