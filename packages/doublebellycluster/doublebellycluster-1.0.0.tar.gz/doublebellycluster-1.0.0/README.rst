Doublebellycluster
******************

Doublebellycluster - это Библиотека кластеризации на анализе плотности


Установка
*********


.. code:: bash

    pip install doublebellycluster

или

.. code:: bash

    python setup.py install

Примеры
*******

.. code:: python

    import doublebellycluster

    # Главный класс
    DD = doublebellycluster.Doubleclustering()
    # запустить кластеризацию на данных xy
    # данные должны быть непрерывными

    di = DD.hip_high(di,eps= 3)



История изменений
*****************

* **Release 1.3.2 (2023-03-20)**

  * Пока работает только на непрерывных данных

* **Release 1.3.1 (2025-02-28)**

  * Если гео данные - то их нужно подготавливать :code:`import pyproj` 
  * Исправлено :code:`AttributeError` при вызове :code:`ResourceLinkObject.public_listdir()`


