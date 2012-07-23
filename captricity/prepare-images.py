#! /usr/bin/env python

# prepare-images.py
#
# Creates pngs from multipage pdfs and tiffs

import Image, os, sys
from subprocess import call

def main():
  if len(sys.argv)>1:
    try:
      os.chdir(sys.argv[1])
    except OSErrori as e:
      print e
      return
  
  pdfbundles = filter( lambda x: x.endswith('.pdf'), os.listdir('.') )
  tifbundles = filter( lambda x: x.endswith( ('.tif', '.tiff') ), os.listdir('.') )
  
  if len(pdfbundles) == len(tifbundles) == 0 :
    print 'Nothing to be done, quitting.'
  
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

main()

