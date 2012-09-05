scaleupbrazil/captricity
========================

This directory has scripts related to using Captricity to convert scanned survey forms into datasets for analysis.

The Captricity API token should be in a file in your home directory called:

~/.scaleupbrazil/captricity-token

The scripts will look for the scanned survey forms under the directory:

~/.scaleupbrazil/scanned-forms

Do not include scanned forms in the repository as it wouldn't be appropriate to release them to the public.

Also, the upload scans tools will save the survey forms in the directory

~/.scaleupbrazil/scanned-forms/raw-scans/YYYYMMDD

where YYYYMMDD is the day's date

The JSON document which describes different possible paths through the survey (due, for example, to skip patterns), should be in

~/.scaleupbrazil/template-ids.json

The root directory for scanned survey forms, and where intermediate .jpg images will be created, is (probably a symlink)

~/.scaleupbrazil/scanned-forms

Datasets that get downloaded will be stored in the directory 

~/.scaleupbrazil/downloaded-data

Information about the database to use should be in 

[TODO -- WORKING ON THIS]

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

* 'pymongo' for interacting with MongoDB

$ sudo pip install pymongo

* 'bcrypt' for handling passwords

$ sudo pip install py-bcrypt





