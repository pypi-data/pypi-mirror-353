varboxes
===================

A varbox is an object to store permanently objects between python session. It uses json module, so it restricts the type of variable to store accordingely.


Installation
============

.. code-block:: bash

    pip install varboxes

Usage
=====


.. code-block:: python

    from varboxes import VarBox
    vb = VarBox('MyApp')
    # you can create any variable as attribute of the varbox:
    vb.a = 1
    # now, you could quit this session, restart the computer, and recreate a varbox (with the same app name):
    vb2 = VarBox('MyApp')
    print(vb2.a)
    >>>  1
    # and the attribute has been remembered!!


Features
========

* to use permanent variable between session, use attribute of a varbox
* the attribute will be saved on the disk and retrieved later


License
=======

The project is licensed under GNU GENERAL PUBLIC LICENSE v3.0
