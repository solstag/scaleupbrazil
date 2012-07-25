#! /usr/bin/env python

# prepare-images.py
#
# Creates pngs from multipage pdfs and tiffs

import Image, os, sys
from subprocess import call

def check_if_converted(bundle, imagelist, imagerange):
  basename = bundle[:-4]
  expected_images = set([ basename + '-' + str(i) + '.png' for i in imagerange ])
  existing_images = set( i for i in imagelist if i.startswith(basename) )
  if existing_images == expected_images:
    return True
  elif existing_images == set([]):
    return False
  else:
    raise BaseException('Something is wrong with the world today: {}'.format(bundle))

def main():
  if len(sys.argv)>1:
    try:
      os.chdir(sys.argv[1])
    except OSErrori as e:
      print e
      return
  
  listdir = os.listdir('.')
  pdfbundles = filter( lambda x: x.endswith('.pdf'), listdir )
  tifbundles = filter( lambda x: x.endswith( ('.tif', '.tiff') ), listdir )
  pnglist = filter( lambda x: x.endswith('.png'), listdir )
  
  if len(pdfbundles) == len(tifbundles) == 0 :
    print 'Nothing to be done, quitting.'
    return
  
  bundle_filter = lambda x: not check_if_converted( x, pnglist, xrange(22) ) 

  for bundle in filter( bundle_filter, tifbundles):
    print 'Converting {}'.format(bundle)
    im=Image.open(bundle)
    try:
      while True:
        im.rotate(270)
        im.save( bundle[:-3] + '-' + str(im.tell()) + '.png' )
        im.seek(im.tell()+1)
    except EOFError:
      pass
  
  for bundle in filter( bundle_filter, pdfbundles):
    print 'Converting {}'.format(bundle)
    retcode = call([ 'convert', '-rotate', '90', '-density', '600', bundle, bundle[:-4]+'.png' ])

  print 'Done.'

main()

