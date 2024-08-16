# From Qgis Model Baker's about:

> This project is open source under the terms of the GPLv2 or later and
the source code can be found on https://github.com/opengisch/QgisModelBaker. This plugin is developed by OPENGIS.ch in collaboration with SwissTierras
Colombia.

**Note**: Adaptation of the Qgis Model Baker plugin v1.7.0


## Personalización QMB

A continuación de lista las personalizaciones realizadas sobre el plugin QgisModelBaker para poderlo usar sin QGIS, utilizando únicamente PyQt5.

Este ajuste fue requerido debido a que el ambiente de conda generaba error en la ejecución.


### Actualización de importaciones

- from qgis.PyQt. --> from PyQt5.

### Se remueven clases de QGIS

No se utiliza la clase QgsNetworkAccessManager

- iliwrapper/ili2dbconfig.py (Se deshabilita el uso del proxy)
- utils/qt_utils.py (Se actualiza la función download_file)

### Se remueven clases no disponibles po CLI

Se remueve la clase QEventLoop
Error: QEventLoop: Cannot be used without QApplication

- iliwrapper/iliexporter.py (Se actualia la clase para no usar QEventLoop)