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

"""Utils for labeled vectors."""

import warnings

warnings.warn(
    "This module has been renamed and should now be imported as `pyxem.utils.vectors`",
    FutureWarning,
)
from pyxem.utils.vectors import (
    column_mean,
    vectors2image,
    points_to_polygon,
    convert_to_markers,
    points_to_poly_collection,
)
