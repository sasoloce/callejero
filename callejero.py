# -*- coding: utf-8 -*-
"""
/***************************************************************************
 callejero
                                 A QGIS plugin
 Callejero basado en los ejes de calle de catastro. Es necesarios descargarse
 la cartografia de catastro de la sede electronica en formato Shapefile e incluir
 en el proyecto las capas EJES y Carvia, que son las que utiliza el componente.
 No cambiar el nombre de las capas pues en ese caso no las encontraria.
                              -------------------
        begin                : 2017-02-10
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Santiago Soto López-Cepero
        email                : sasoloce@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
#from PyQt4.QtGui import QAction, QIcon, QMessageBox
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import QgsMessageBar
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from callejero_dialog import callejeroDialog
import os.path


class callejero:
    """QGIS Plugin Implementation."""



    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'callejero_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = callejeroDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&callejero')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'callejero')
        self.toolbar.setObjectName(u'callejero')

        # Iniciamos lo que queremos hacer con los botones
        self.dlg.nom_calle.clear()
        self.dlg.buscar_btn.clicked.connect(self.buscar_calle)
        self.dlg.limpiar_btn.clicked.connect(self.limpiar_lista)
        self.dlg.ir_a_btn.clicked.connect(self.ir_a)

        # Inicamos la lista de resultados. Las interfaces son generadas con QT Designer
        self.lista = self.dlg.tableView
        # Modificamos el comportamiento para que solo se puedan seleccionar columnas
        self.lista.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Modificamos la seleccion a modo una sola fila
        self.lista.setSelectionMode(QAbstractItemView.SingleSelection)
        # Actuamos en la seleccion de una fila
        self.lista.clicked.connect(self.fila_seleccionada)
        # Ocultamos la columna de indices
        self.lista.verticalHeader().hide()
        self.model = QStandardItemModel(self.lista)
        self.model.setColumnCount(2)
        headerNames = []
        # Añadimos la cabeceras de la tabla
        headerNames.append("Codigo")
        headerNames.append("Nombre Calle")
        self.model.setHorizontalHeaderLabels(headerNames)

        # Aplicamos el modelo
        self.lista.setModel(self.model)
        self.lista.setColumnWidth(0, 80)
        self.lista.setColumnWidth(1, 270)
        #self.lista.resizeColumnsToContents()


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('callejero', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/callejero/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Callejero Catastro'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&callejero'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def buscar_calle(self):
        self.limpiar_lista()
        cadena = self.dlg.nom_calle.text()
        if cadena == "":
            self.iface.messageBar().pushMessage("Buscar Calle", 'Cadena de busqueda vacia', QgsMessageBar.INFO, 5)
        else:
            layerList = QgsMapLayerRegistry.instance().mapLayersByName("Carvia")
            if layerList:

                layer = layerList[0]
                print layer.featureCount()
                print cadena
                # formamos la cadena de busqueda con caracteres comodines que en QGIS (python) es el %
                cadena_busqueda = "'%" + cadena.upper() + "%'"
                print cadena_busqueda
                st = '"DENOMINA" LIKE ' + cadena_busqueda
                print(st)
                # Obtenemos el conjunto de registros resultado de la busqueda
                it = layer.getFeatures(QgsFeatureRequest().setFilterExpression(st))
                #try:
                #    row = it.next()
                #    print(row)
                #except StopIteration:
                #    print("No rows")
                #except:
                #    print("something else went wrong")
                #lista = self.dlg.lista_resultados
                #model = QStandardItemModel(lista)

                idx1 = layer.fieldNameIndex('DENOMINA')
                idx2 = layer.fieldNameIndex('VIA')
                for feature in it:
                    # retrieve every feature
                    # Create an item witha caption

                    #item = QStandardItem(feature.attributes()[idx])
                    itemvia = QStandardItem(str(feature.attributes()[idx2]))
                    itemnom = QStandardItem(feature.attributes()[idx1])
                    # Add a checkbox to it
                    #item.setCheckable(True)

                    # Add the item to the model
                    self.model.appendRow([itemvia,itemnom])
                    print "VIA: %s " % feature.attributes()[idx2]
                    print "DENOMINA: %s " % feature.attributes()[idx1]

                #lista.setModel(model)
            else:
                self.iface.messageBar().pushMessage("Buscar Calle", 'No existe la capa con nombre Carvia',
                                                    QgsMessageBar.INFO, 5)

                # QMessageBox.information(self.iface.mainWindow(), "Prueba", 'Mensaje de Prueba ')

    def limpiar_lista(self):
        for i in reversed(range(self.model.rowCount())):
            self.model.removeRow(i)
        self.dlg.ir_a_btn.setEnabled(False)

    def ir_a(self):

        # Obtenemos la fila (row) seleccionada
        fila = self.lista.selectionModel().currentIndex().row()
        # Obtenemos la primera columna con el codigo de la fila seleccionada
        codigo = self.model.item(fila, 0).index().data()
        # Tambien obtenemos el nombre de la calle
        nom_calle = self.model.item(fila, 1).index().data()

        # Obtenemos la capa EJES de calle
        layerList = QgsMapLayerRegistry.instance().mapLayersByName("EJES")
        if layerList:

            # Obtenemos la capa actual
            capa_actual =  self.iface.activeLayer()

            # Obtenemos la capa de los ejes de calle
            layer = layerList[0]

            # Establecemos esta capa como la activa
            self.iface.setActiveLayer(layer)
            #print layer.featureCount()

            # Establecemos la cadena de busqueda
            st = '"VIA" = ' + codigo
            #print "Cadena de busqueda: " + st
            # Obtenemos el conjunto de registros resultado de la busqueda
            it = layer.getFeatures(QgsFeatureRequest().setFilterExpression(st))

            # for feature in it:
            #     geom = feature.geometry()
            #     print(geom)

            # Obtenemos el conjunto de registros resultado de la busqueda
            its = layer.getFeatures(QgsFeatureRequest().setFilterExpression(st))

            # Vamos a la calle mediante la seleccion y hacemos zoom
            ids = [i.id() for i in its]
            # Comprobamos que hayamos encontrado valores en la capa de ejes de calle (tramos de calle). Los nombres de calles sin geometria no apareceran
            if ids:
                layer.setSelectedFeatures(ids)
                self.iface.mapCanvas().zoomToSelected()
            else:
                QMessageBox.information(self.dlg, "Calle sin Geometria", 'La calle ' + nom_calle + ' no tiene geometria')

            # Reestablecemos la capa anterior al goto
            self.iface.setActiveLayer(capa_actual)

        else:
            self.iface.messageBar().pushMessage("Buscar Calle", 'No existe la capa con nombre EJES',
                                                QgsMessageBar.INFO, 5)


    def fila_seleccionada(self,index_item):
        row = index_item.row()
        # Activamos el boton de ir a
        self.dlg.ir_a_btn.setEnabled(True)
        #print self.lista.model()
        #Obtenemos el valor de la primera columna con el codigo que queremos
        #codigo = self.lista.model().takeItem(row, 0)
        #print self.lista.model().takeItem(row,0)
        #item = self.lista.model().data(index, Qt.DisplayRole).toPyObject()
        #print ("index : " + item)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
