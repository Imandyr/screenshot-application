"""
Classes and functions for screenshot creation.
"""


# global imports
from typing import Tuple, Any, Union
from abc import ABC, abstractmethod
import screeninfo
import os
import mss
from PIL import Image
import imageio
import numpy as np
from datetime import datetime
import re


# local imports
from ..errors.errors import InvalidFilePathError, InvalidFileFormat, CroppingError


class Screenshot(ABC):
    """
    Base protocol for screenshot classes.

    attributes:
        save_dir: Path to directory where screenshots images will be saved.
        file_format: Format of file in what screenshots image will be saved.

    properties:
        image: property with screenshot image object.

    methods:
        take_screenshot: Method for taking new screenshot image.
        edit_screenshot: Method for screenshot image modification.
        save_screenshot: Method for writing screenshot image into file.

    """
    save_dir: str
    file_format: str

    def __init__(self, *args, **kwargs):
        """Placeholder for __init__ method."""
        self._image = None
        self._image_file_path = None

    @property
    def image(self) -> Any:
        """Screenshot image."""
        return self._image

    @image.setter
    def image(self, img: Any) -> None:
        """Set screenshot image."""
        self._image = img

    @property
    def image_file_path(self) -> Union[str, None]:
        """File path to last written image."""
        return self._image_file_path

    @abstractmethod
    def __repr__(self, *args, **kwargs):
        """Placeholder for __repr__ method."""

    @abstractmethod
    def take_screenshot(self, *args, **kwargs):
        """Placeholder for take_screenshot method."""

    @abstractmethod
    def edit_screenshot(self, *args, **kwargs):
        """Placeholder for edit_screenshot method."""

    @abstractmethod
    def save_screenshot(self, *args, **kwargs):
        """Placeholder for save_screenshot method."""


class MonitorScreenshot(Screenshot):
    """
    Class with base monitor screenshot creation functional.

    """
    def __init__(self, save_dir: str, file_format: str, *args, **kwargs) -> None:
        """
        Class with base monitor screenshot creation functional.

        :param save_dir: Path to directory where screenshots images will be saved.
        :param file_format: Format (without '.') of file in what screenshots image will be saved.
        """
        super().__init__(*args, **kwargs)

        self.save_dir = save_dir
        self.file_format = file_format

    def __repr__(self, *args, **kwargs) -> str:
        """
        Representation of current object state.

        :return: string with object state
        """

        return f"{str(self.__class__.__name__)}(save_dir='{self.save_dir}', file_format='{self.file_format}')"

    def take_screenshot(self, *args, **kwargs) -> None:
        """
        Method for taking new screenshot of monitor and write it to image attribute as numpy ndarray.

        :return: None
        """

        # take current monitor resolution
        monitor = screeninfo.get_monitors()[0]
        # use it to create a screenshot bounds
        monitor = {"top": 0, "left": 0, "width": monitor.width, "height": monitor.height}

        # take a screenshot
        with mss.mss() as sct:
            image = sct.grab(monitor)
            # convert to rgb
            image = Image.frombuffer(data=image.rgb, size=(image.size.width, image.size.height), mode="RGB")

        # convert to numpy array and write it as class attribute
        self._image = np.asarray(image, dtype="float32")

    def edit_screenshot(self, *args, **kwargs):
        """Nothing here for now."""

    def save_screenshot(self, *args, **kwargs) -> None:
        """
        Method for writing screenshot image into file.

        :return: screenshot image saved to a file.
        """

        # create blank file path
        file_path = ""

        # try to write screenshot image in file
        try:
            # rename file if another file already have this name
            conflict, count, c_str = True, 1, ""
            while conflict:

                # create path and name for new image file
                file_path = f"{self.save_dir}/{re.sub('[:. ]', '-', str(datetime.now()))}{c_str}.{self.file_format}"

                # write image to file if its name is no exist already
                if not os.path.exists(file_path):
                    conflict = False
                    imageio.imwrite(uri=file_path, im=np.asarray(self.image).astype("uint8"))

                # add prefix with number to file name if file with this name is already exist
                else:
                    count += 1
                    c_str = "_" + str(count)

            # save this file path
            self._image_file_path = file_path

        # if error occurred with file format
        except ValueError:
            raise InvalidFileFormat(f"File format '{self.file_format}' is invalid.")

        # if error occurred with file path
        except FileNotFoundError:
            raise InvalidFilePathError(f"File path '{file_path}' is invalid.")


class CroppedMonitorScreenshot(MonitorScreenshot):
    """
    Screenshot creation class for taking a some part of monitor image.

    """

    def edit_screenshot(self, box: Tuple[int, int, int, int], *args, **kwargs) -> None:
        """
        Crop screenshot image by pixel coordinates from box tuple.

        :param box: Tuple with pixel coordinates by what screenshot image will be cropped.
        :return: None
        """

        try:
            # load image from array to PIL
            image = Image.fromarray(np.uint8(self.image))
            # crop image by coordinates in box
            image = image.crop(box=box)
            # convert to numpy array and rewrite attribute
            self._image = np.asarray(image, dtype="float32")

        # if error occurred with image cropping
        except ValueError:
            raise CroppingError(f"Cropping coordinates '{box}' is invalid for this image.")






