#!/bin/env python

# prepare-images.py
#
# Creates pngs from multipage pdfs and tiffs
#
# BUG: supposes files located in working directory

import Image, os
from subprocess import call

pdfbundles = filter( lambda x: x.endswith('.pdf'), os.listdir('.') )
tifbundles = filter( lambda x: x.endswith( ('.tif', '.tiff') ), os.listdir('.') )

for bundle in tifbundles:
  im=Image.open(bundle)
  try:
    while True:
      im.rotate(270)
      im.save( bundle[:-3] + '-' + str(im.tell()) + '.png' )
      im.seek(im.tell()+1)
  except EOFError:
    pass

for bundle in pdfbundles:
  retcode = call([ 'convert', '-rotate', '90', bundle, bundle[:-3]+'.png' ])

