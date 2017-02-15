# -*- coding: utf-8 -*-
"""
/***************************************************************************
 callejero
                                 A QGIS plugin
 Callejero basado en los ejes de calle de catastro
                             -------------------
        begin                : 2017-02-10
        copyright            : (C) 2017 by Santiago Soto López-Cepero
        email                : sasoloce@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load callejero class from file callejero.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .callejero import callejero
    return callejero(iface)
