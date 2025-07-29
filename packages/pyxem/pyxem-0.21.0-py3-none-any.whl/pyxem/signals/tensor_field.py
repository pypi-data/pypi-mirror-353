# -*- coding: utf-8 -*-
# Copyright 2016-2025 The pyXem developers
#
# This file is part of pyXem.
#
# pyXem is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyXem is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyXem.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from scipy.linalg import polar
import math

from hyperspy.signals import Signal2D
from hyperspy.utils import stack

from pyxem.signals import StrainMap
from hyperspy._signals.lazy import LazySignal


def _polar_decomposition(image, side):
    """Perform a polar decomposition of a second rank tensor.

    Parameters
    ----------
    image : numpy.ndarray
        Matrix on which to form polar decomposition.
    side : str
        'left' or 'right' the side on which to perform polar decomposition.

    Returns
    -------
    R, U :  numpy.ndarray
        Stretch and rotation matrices obtained by polar decomposition.

    """
    return np.array(polar(image, side=side))


def _get_rotation_angle(matrix):
    """Find the rotation angle associated with a given rotation matrix.

    Parameters
    ----------
    matrix : numpy.ndarray
        A rotation matrix.

    Returns
    -------
    angle :  numpy.ndarray
        Rotation angle associated with matrix.

    """
    return np.array(-math.asin(matrix[1, 0]))


class DisplacementGradientMap(Signal2D):
    """Signal class for Tensor Fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check that the signal dimensions are (3,3) for it to be a valid
        # TensorField

    def polar_decomposition(self):
        """Perform polar decomposition on the second rank tensors describing
        the TensorField. The polar decomposition is right handed and given by
        :math:`D = RU`

        Returns
        -------
        R : TensorField
            The orthogonal matrix describing the rotation field.
        U : TensorField
            The strain tensor field.

        """
        RU = self.map(
            _polar_decomposition, side="right", inplace=False, silence_warnings=True
        )
        return RU.isig[:, :, 0], RU.isig[:, :, 1]

    def get_strain_maps(self):
        """Obtain strain maps from the displacement gradient tensor at each
        navigation position in the small strain approximation.

        Returns
        -------
        strain_results : BaseSignal
            Signal of shape < 4 | , > , navigation order is e11,e22,e12,theta
        """
        if self._lazy:
            self.compute()
        R, U = self.polar_decomposition()

        e11 = np.reciprocal(U.isig[0, 0].T) - 1
        e12 = U.isig[0, 1].T
        # e21 = U.isig[1, 0].T # Same as e12
        e22 = np.reciprocal(U.isig[1, 1].T) - 1
        theta = R.map(_get_rotation_angle, inplace=False, silence_warnings=True)
        theta = theta.transpose(2)
        strain_results = stack([e11, e22, e12, theta])
        strain_map = StrainMap(strain_results)
        if len(strain_map.axes_manager.signal_axes) == 2:
            strain_map.axes_manager.signal_axes[0].name = (
                self.axes_manager.navigation_axes[0].name
            )
            strain_map.axes_manager.signal_axes[0].scale = (
                self.axes_manager.navigation_axes[0].scale
            )
            strain_map.axes_manager.signal_axes[0].units = (
                self.axes_manager.navigation_axes[0].units
            )
            strain_map.axes_manager.signal_axes[0].offset = (
                self.axes_manager.navigation_axes[0].offset
            )

            strain_map.axes_manager.signal_axes[1].name = (
                self.axes_manager.navigation_axes[1].name
            )
            strain_map.axes_manager.signal_axes[1].scale = (
                self.axes_manager.navigation_axes[1].scale
            )
            strain_map.axes_manager.signal_axes[1].units = (
                self.axes_manager.navigation_axes[1].units
            )
            strain_map.axes_manager.signal_axes[1].offset = (
                self.axes_manager.navigation_axes[1].offset
            )
        return strain_map


class LazyDisplacementGradientMap(LazySignal, DisplacementGradientMap):
    """Lazy signal class for Tensor Fields."""

    pass
