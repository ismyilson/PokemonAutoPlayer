import pytest
from PIL import Image
import mss

from image_processing import ImageProcessor


class TestImageProcessor(object):
    def test_image_processor_grab_full_screen(self, mocker):
        # Setup
        expected_mode = 'RGB'
        expected_dimensions = (1920, 1080)

        # Exec
        image = ImageProcessor.grab_full_screen()

        # Validate
        assert isinstance(image, Image.Image)
        assert expected_mode == image.mode
        assert expected_dimensions == image.size

    def test_image_processor_are_same_image_should_return_true_when_same(self):
        # Setup
        image = Image.new('RGB', size=(100, 100), color=(100, 100, 100))
        other_image = Image.new('RGB', size=(100, 100), color=(100, 100, 100))

        # Exec
        ret = ImageProcessor.are_same_image(image, other_image)

        # Validate
        assert ret is True

    @pytest.mark.parametrize('image, other_image', [
        [
            Image.new('RGB', size=(100, 100), color=(100, 100, 100)),
            Image.new('RGB', size=(50, 50), color=(100, 100, 100))
        ],
        [
            Image.new('RGB', size=(100, 100), color=(100, 100, 100)),
            Image.new('RGB', size=(100, 100), color=(50, 100, 100))
        ]
    ])
    def test_image_processor_are_same_image_should_return_false_when_different(self, image, other_image):
        # Setup

        # Exec
        ret = ImageProcessor.are_same_image(image, other_image)

        # Validate
        assert ret is False

    def test_image_processor_is_black_image_should_return_true(self, mocker):
        # Setup
        mocker.patch('PIL.Image.open', return_value=Image.new('RGB', size=(300, 300), color=(0, 0, 0)))

        image = Image.new('RGB', size=(100, 100), color=(0, 0, 0))

        # Exec
        ret = ImageProcessor.is_black_image(image)

        # Validate
        assert ret is True

    def test_image_processor_is_black_image_should_return_false(self, mocker):
        # Setup
        mock_image_open = mocker.patch('PIL.Image.open', return_value=Image.new('RGB', size=(300, 300), color=(0, 0, 0)))

        image = Image.new('RGB', size=(100, 100), color=(100, 100, 100))

        # Exec
        ret = ImageProcessor.is_black_image(image)

        # Validate
        assert ret is False

    def test_image_processor_get_image_colors(self):
        # Setup
        expected_return = [(10000, (100, 100, 100))]
        image = Image.new('RGB', size=(100, 100), color=(100, 100, 100))

        # Exec
        colors = ImageProcessor.get_image_colors(image)

        # Validate
        assert expected_return == colors

    def test_image_processor_remove_char_from_image(self, mocker):
        # Setup
        expected_return = [(240000, (100, 100, 100)), (10000, (0, 0, 0))]
        mock_image_open = mocker.patch('PIL.Image.open', return_value=Image.new('RGBA', size=(100, 100), color=(0, 0, 0, 255)))

        image = Image.new('RGB', size=(500, 500), color=(100, 100, 100))

        # Exec
        ImageProcessor._remove_char_from_image(image)

        # Validate
        assert expected_return == ImageProcessor.get_image_colors(image)

    def test_image_processor_replace_color(self):
        # Setup
        expected_colors = [(10000, (100, 100, 100))]

        image = Image.new('RGB', size=(100, 100), color=(0, 0, 0))

        # Exec
        ImageProcessor.replace_color(image, (0, 0, 0), (100, 100, 100))
        colors = ImageProcessor.get_image_colors(image)

        # Validate
        assert expected_colors == colors

    def test_image_processor_make_tiles(self):
        # Setup
        image = Image.new('RGB', size=(300, 300), color=(0, 0, 0))

        # Exec
        tiles = ImageProcessor.make_tiles(image, (100, 100))

        # Validate
        assert len(tiles) == 9
