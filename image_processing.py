from PIL import Image, ImageChops
import mss
import pytesseract
import win32gui
import win32ui
import ctypes

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

_scp = mss.mss()


class ImageProcessor:
    _DIMENSIONS_FULL = (1920, 1080)

    @staticmethod
    def grab_full_screen() -> Image:
        return ImageProcessor._grab_screen(ImageProcessor._DIMENSIONS_FULL)

    @staticmethod
    def _grab_screen(size) -> Image:
        hwnd = win32gui.FindWindow(None, 'VisualBoyAdvance')

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, size[0], size[1])

        save_dc.SelectObject(bitmap)

        ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)
        bitmap_info = bitmap.GetInfo()
        bitmap_bits = bitmap.GetBitmapBits(True)

        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

        image = Image.frombuffer(
            'RGB',
            (bitmap_info['bmWidth'], bitmap_info['bmHeight']),
            bitmap_bits, 'raw', 'BGRX', 0, 1)

        return image

    @staticmethod
    def are_same_image(image1, image2) -> bool:
        if image1 is None or image2 is None:
            return False

        if image1.size != image2.size:
            return False

        image = ImageChops.difference(image1, image2)
        return not image.getbbox()

    @staticmethod
    def is_black_image(image) -> bool:
        black_image = Image.open('images/black.png', 'r')
        black_image = black_image.resize(image.size)
        return ImageProcessor.are_same_image(image, black_image)

    @staticmethod
    def get_image_colors(image) -> list:
        return image.getcolors()

    @staticmethod
    def replace_color(image, from_color, to_color) -> None:
        data = image.getdata()
        new_data = []
        for color in data:
            if color != from_color:
                new_data.append(color)
            else:
                new_data.append(to_color)

        image.putdata(new_data)

    @staticmethod
    def make_tiles(image, size) -> list:
        max_x = int(image.size[0] / size[0])
        max_y = int(image.size[1] / size[1])

        tiles = []
        cur_x = 0
        for x in range(0, max_x):
            cur_y = 0
            for y in range(0, max_y):
                new_x = cur_x + size[0]
                new_y = cur_y + size[1]

                tile = image.crop((cur_x, cur_y, new_x, new_y))
                tiles.append(((cur_x, cur_y, new_x, new_y), tile))

                cur_y = new_y

            cur_x = cur_x + size[0]

        return tiles

    @staticmethod
    def _remove_char_from_image(image) -> None:
        remove_char_image = Image.open('images/remove_char.png', 'r')
        pos_x = int(image.size[0] / 2 - (remove_char_image.size[0] / 2))
        pos_y = int(image.size[1] / 2 - (remove_char_image.size[1] / 2)) + 25
        image.paste(remove_char_image, (pos_x, pos_y), remove_char_image)

    '''
    @staticmethod
    def map_is_inside(image) -> bool:
        cover = Image.new('RGB', size=(1810, 905), color=(255, 255, 255))
        image.paste(cover, (30, 30))

        for k, v in ImageProcessor.get_image_colors(image):
            if v == (0, 0, 0):
                return True

        return False
    '''
