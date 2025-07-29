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


from pyxem.signals.diffraction1d import Diffraction1D


class DiffractionVariance1D(Diffraction1D):
    """Signal class for one-dimensional diffraction variance.

    Parameters
    ----------
    *args
        See :class:`hyperspy.api.signals.Signal1D`.
    **kwargs
        See :class:`hyperspy.api.signals.Signal1D`
    """

    _signal_type = "diffraction_variance"

    pass
