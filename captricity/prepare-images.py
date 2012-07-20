#!/bin/env python

# prepare-images.py
#
# Creates pngs from multipage pdfs and tiffs
#
# BUG: supposes files located in working directory
#
# BUG: file names from tiff have fixed (=2) zfilled numbering

import Image

pdfbundles = filter( os.listdir('.'), lambda x: x.endswith('.pdf') )
tifbundles = filter( os.listdir('.'), lambda x: x.endswith('.tif') or x.endswith('.tiff') )

for bundle in tifbundles:
  im=Image.open(bundle)
  try:
    while True:
      im.rotate(270)
      im.save( bundle[:-3] + '-' + str(im.tell()).zfill(2) + '.png' )
      im.seek(im.tell()+1)
  except EOFError:
    pass

for bundle in pdfbundles:
  from subprocess import call
  retcode = call([ 'pdftoppm', '-png', bundle, bundle[:-3] ])

