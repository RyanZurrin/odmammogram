import time
import logging
from types import SimpleNamespace
from .normalizations import Normalize
import mahotas as mh
import numpy as np
from typing import Union, List

logger = logging.getLogger(__name__)


class Features:
    @staticmethod
    def histogram(
        pixels: Union[
            List[Union[SimpleNamespace, np.ndarray]], SimpleNamespace, np.ndarray
        ],
        norm_type: str = None,
        timing: bool = False,
        **kwargs
    ) -> np.ndarray:
        """
        Create histogram of data

        Parameters
        ----------
        pixels : list or np.ndarray
            List of images or single image
        norm_type : str, optional
            Type of normalization. The default is None.
        timing : bool, optional
            Whether to time the function. The default is False.

        Returns
        -------
        np.ndarray
            List of histograms
        """
        t0 = time.time()
        histograms = []
        # if pixels is a list of images get list of histograms for each image
        if isinstance(pixels, list):
            for i in range(len(pixels)):
                # if pixels is a list of SimpleNamespace use the pixels attribute
                if isinstance(pixels[i], SimpleNamespace):
                    tmp_pixels = pixels[i].pixels.copy()
                else:  # else assume pixels is a list of np.ndarray
                    tmp_pixels = pixels[i].copy()
                # if normalization is specified normalize pixels before histogram
                if norm_type is not None:
                    tmp_pixels = Normalize.get_norm(
                        tmp_pixels, norm_type=norm_type, timing=timing, **kwargs
                    )[0]
                # append histogram to list
                histograms.append(mh.fullhistogram(tmp_pixels.astype(np.uint8)))
        # if pixels is a single image get histogram
        else:
            tmp_pixels = pixels.copy()
            if norm_type is not None:
                tmp_pixels = Normalize.get_norm(
                    tmp_pixels, norm_type=norm_type, timing=timing, **kwargs
                )[0]
            histograms = mh.fullhistogram(tmp_pixels.astype(np.uint8))

        if timing:
            logger.info("Histogram: %s", time.time() - t0)
        return np.array(histograms)

    @staticmethod
    def get_features(
        data: Union[SimpleNamespace, np.ndarray],
        feature_type: str = "hist",
        norm_type: str = None,
        timing: bool = False,
        **kwargs
    ) -> np.ndarray:
        """
        Get features of data

        Parameters
        ----------
        data : SimpleNamespace, np.ndarray
            Array of pixels
        feature_type : str, optional
            Type of feature to extract. The default is "histogram".
        norm_type : str, optional
            Type of normalization. The default is None.
        timing: bool, optional
            Whether to time the function. The default is False.

        Returns
        -------
        np.ndarray
        """
        print("get_features")
        t0 = time.time()
        if feature_type in ["hist", "histogram"]:
            features = Features.histogram(
                data, norm_type=norm_type, timing=timing, **kwargs
            )
        else:
            raise ValueError("Feature type not supported")
        if timing:
            logger.info("Get features: %s", time.time() - t0)
        return features