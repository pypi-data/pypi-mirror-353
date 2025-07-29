# This file is part of CFELPyUtils.
#
# CFELPyUtils is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# CFELPyUtils is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with CFELPyUtils.
# If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2021 Deutsches Elektronen-Synchrotron DESY,
# a research centre of the Helmholtz Association.
"""
Peakfinder8 algorithm for detection of Bragg peaks in detector frame data.
"""

import sys
from collections import namedtuple
from typing import Union

import h5py  # type: ignore
import numpy  # type: ignore

from .lib import peakfinder_8

PeakList = namedtuple("PeakList", ["num_peaks", "fs", "ss", "intensity"])
"""
Information about Bragg peaks found in a detector data frame (list of peaks).

Arguments:

    num_peaks(int): number of peaks that were detected in the data frame.

    fs (List[float]): a list of fractional fs indexes locating the detected peaks
        in the detector data frame.

    ss (List[float]): a list of fractional ss indexes locating the detected peaks
        in the detector data frame.

    intensity (List[float]): a list of integrated intensities for the detected
        peaks.
"""


class Peakfinder8PeakDetection:
    """
    See documentation of the '__init__' function.
    """

    def __init__(
        self,
        max_num_peaks: int,
        asic_nx: int,
        asic_ny: int,
        nasics_x: int,
        nasics_y: int,
        adc_threshold: float,
        minimum_snr: float,
        min_pixel_count: int,
        max_pixel_count: int,
        local_bg_radius: int,
        min_res: int,
        max_res: int,
        bad_pixel_map_filename: Union[str, None],
        bad_pixel_map_hdf5_path: Union[str, None],
        radius_pixel_map: numpy.ndarray,
    ) -> None:
        """
        Peakfinder8 algorithm for peak detection.

        This class stores the parameters needed by the 'peakfinder8' algorithm, and
        detect peaks in a detector data frame upon request. The 'peakfinder8' algorithm
        is described in the following publication:

        A. Barty, R. A. Kirian, F. R. N. C. Maia, M. Hantke, C. H. Yoon, T. A. White,
        and H. N. Chapman, "Cheetah: software for high-throughput reduction and
        analysis of serial femtosecond X-ray diffraction data", J Appl  Crystallogr,
        vol. 47, pp. 1118-1131 (2014).

        Arguments:

            max_num_peaks (int): the maximum number of peaks that will be retrieved
                from each data frame. Additional peaks will be ignored.

            asic_nx (int): the fs size in pixels of each detector's ASIC in the data
                frame.

            asic_ny (int): the ss size in pixels of each detector's ASIC in the data
                frame.

            nasics_x (int): the number of ASICs along the fs axis of the data frame.

            nasics_y (int): the number of ASICs along the ss axis of the data frame.

            adc_threshold (float): the minimum ADC threshold for peak detection.

            minimum_snr (float): the minimum signal-to-noise ratio for peak detection.

            min_pixel_count (int): the minimum size of a peak in pixels.

            max_pixel_count (int): the maximum size of a peak in pixels.

            local_bg_radius (int): the radius for the estimation of the
                local background in pixels.

            min_res (int): the minimum resolution for a peak in pixels.

            max_res (int): the maximum resolution for a peak in pixels.

            bad_pixel_map_filename (Union[str, None): the absolute or relative path to
                an HDF5 file containing a bad pixel map. The map should mark areas of
                the data frame that must be excluded from the peak search. If this and
                the 'bad_pixel_map_hdf5_path' arguments are not None, the map is loaded
                and will be used by the algorithm. Otherwise no area is excluded from
                the search. Defaults to None.

                * The map must be a numpy array of the same shape as the data frame on
                  which the algorithm will be applied.

                * Each pixel in the map must have a value of either 0, meaning that
                  the corresponding pixel in the data frame must be ignored, or 1,
                  meaning that the corresponding pixel must be included in the search.

                * The map is only used to exclude areas from the peak search: the data
                  is not modified in any way.

            bad_pixel_map_hdf5_path (str): the internal HDF5 path to the data block
                where the bad pixel map is stored.

                * If the 'bad_pixel_map_filename' argument is not None, this argument
                  must also be provided, and cannot be None. Otherwise it is ignored.

            radius_pixel_map (numpy.ndarray): a numpy array with radius information.

                * The array must have the same shape as the data frame on which the
                  algorithm will be applied.

                * Each element of the array must store the distance in pixels from
                  the center of the detector of the corresponding pixel in the data
                  frame.
        """
        self._max_num_peaks = max_num_peaks  # type: int
        self._asic_nx = asic_nx  # type: int
        self._asic_ny = asic_ny  # type: int
        self._nasics_x = nasics_x  # type: int
        self._nasics_y = nasics_y  # type: int
        self._adc_thresh = adc_threshold  # type: float
        self._minimum_snr = minimum_snr  # type: float
        self._min_pixel_count = min_pixel_count  # type: int
        self._max_pixel_count = max_pixel_count  # type: int
        self._local_bg_radius = local_bg_radius  # type: int
        self._radius_pixel_map = radius_pixel_map  # type: numpy.ndarray
        self._min_res = min_res  # type: int
        self._max_res = max_res  # type: int
        self._mask_initialized = False  # type: bool

        if bad_pixel_map_filename is not None:
            try:
                with h5py.File(bad_pixel_map_filename, "r") as hdf5_file_handle:
                    self._mask = hdf5_file_handle[bad_pixel_map_hdf5_path][
                        :
                    ]  # type: Union[numpy.ndarray, None]
            except (IOError, OSError, KeyError) as exc:
                exc_type, exc_value = sys.exc_info()[:2]
                raise RuntimeError(
                    "The following error occurred while reading the {0} field"
                    "from the {1} bad pixel map HDF5 file:"
                    "{2}: {3}".format(
                        bad_pixel_map_filename,
                        bad_pixel_map_hdf5_path,
                        exc_type.__name__,  # type: ignore
                        exc_value,
                    )
                ) from exc
        else:
            self._mask = None

    def find_peaks(self, data: numpy.ndarray) -> PeakList:
        """
        Finds peaks in a detector data frame.

        This function not only retrieves information about the position of the peaks in
        the data frame but also about their integrated intensity.

        Arguments:

            data (numpy.ndarray): the detector data frame on which the peak finding
                must be performed.

        Returns:

            PeakList: a namedtuple with information about the Bragg peaks
            detected in a data frame. The object has the following attributes:

            - An attribute named "num_peaks" whose value is the number of peaks that were
              detected in the data frame.

            - An attribute named 'fs' whose value is a list of fractional fs indexes locating
              the detected peaks in the data frame.

            - An attribute named 'ss' whose value is a list of fractional ss indexes locating
              the detected peaks in the data frame.

            - An attribute named 'intensity' whose value is a list of integrated intensities
              for the detected peaks.
        """
        if not self._mask_initialized:
            if self._mask is None:
                self._mask = numpy.ones_like(data, dtype=numpy.int8)
            else:
                self._mask = self._mask.astype(numpy.int8)

            res_mask = numpy.ones(shape=self._mask.shape, dtype=numpy.int8)
            res_mask[numpy.where(self._radius_pixel_map < self._min_res)] = 0
            res_mask[numpy.where(self._radius_pixel_map > self._max_res)] = 0
            self._mask *= res_mask

        peak_list = peakfinder_8(
            self._max_num_peaks,
            data.astype(numpy.float32),
            self._mask,
            self._radius_pixel_map,
            self._asic_nx,
            self._asic_ny,
            self._nasics_x,
            self._nasics_y,
            self._adc_thresh,
            self._minimum_snr,
            self._min_pixel_count,
            self._max_pixel_count,
            self._local_bg_radius,
        )

        return PeakList(
            num_peaks=len(peak_list[0]),
            fs=peak_list[0],
            ss=peak_list[1],
            intensity=peak_list[2],
        )
