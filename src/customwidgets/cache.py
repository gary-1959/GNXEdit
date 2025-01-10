#
# Image cache
#
# Copyright 2024 gary-1959
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PySide6.QtGui import QImage

IMAGE_CACHE = {}
IMAGE_CACHING = True   # for development
# get or add image to cache
def cache_image(key, path):
    if IMAGE_CACHING:
        if key not in IMAGE_CACHE.keys():
            img = QImage(path)
            IMAGE_CACHE[key] = img

        return(IMAGE_CACHE[key])
    else:
        return QImage(path)