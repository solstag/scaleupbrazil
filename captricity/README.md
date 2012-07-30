scaleupbrazil/captricity
========================

This directory has scripts related to using Captricity to convert scanned survey forms into datasets for analysis.

The Captricity API token should be in a file in your home directory called:

~/.scaleupbrazil/captricity-token

The scripts will look for the scanned survey forms under the directory:

~/.scaleupbrazil/scanned-forms

Do not include scanned forms in the repository as it wouldn't be appropriate to release them to the public.

Software requirements
---------------------

For the prepare-images.py script, you need:

* the Python Image Library (PIL)

Assuming you have pip installed, you can install PIL with

$ sudo pip install PIL

http://www.pythonware.com/library/pil/handbook/image.htm

* 'convert' from the ImageMagick suite

http://imagemagick.org/

* 'pdfimages' from the Poppler PDF rendering library

http://poppler.freedesktop.org/

