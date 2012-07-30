#! /usr/bin/env python

# prepare-images.py
#
# Creates pngs from multipage pdfs and tiffs
# Requires 'pdfimages' and 'convert'

import Image, os, sys
from subprocess import call

imagesperfile = 22

def check_if_converted(bundle, imagelist, imagerange):
  basename = os.path.splitext(bundle)[0]
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
  
  bundle_filter = lambda x: not check_if_converted( x, pnglist, xrange(imagesperfile) ) 

  for bundle in filter( bundle_filter, tifbundles):
    print 'Converting {}'.format(bundle)
    im=Image.open(bundle)
    try:
      while True:
        im.rotate(270)
        im.save( os.path.splitext(bundle)[0] + '-' + str(im.tell()) + '.png' )
        im.seek(im.tell()+1)
    except EOFError:
      pass
  
  for bundle in filter( bundle_filter, pdfbundles):
    print 'Converting {}'.format(bundle)
    basename = os.path.splitext(bundle)[0]
    retcode = call([ 'pdfimages', '-j', bundle, basename ])
    tempnames = filter( lambda x: x.startswith(basename) and x.endswith('.jpg'),  os.listdir('.') ) 
    if len(tempnames) != imagesperfile:
        raise BaseException('Something is wrong with the world today: {}'.format(bundle))
    else:
        for name in tempnames:
            retcode = call([ 'convert', '-rotate', '90', name, os.path.splitext(name)[0]+'.png' ])
            os.remove(name)

  print 'Done.'

main()

