#! /usr/bin/env python

# prepare-images.py
#
# Creates pngs from multipage pdfs and tiffs
# Requires 'pdfimages' and 'convert'

import Image, os, sys, argparse, re
from subprocess import call

imagesperfile = 22

def check_if_converted(bundle, imagelist, imagerange):
  basename = os.path.splitext(bundle)[0]
  expected_images = set([ basename + '-{num:03d}'.format(num=i) + '.jpg' for i in imagerange ])
  existing_images = set( i for i in imagelist if i.startswith(basename) )

  if existing_images == expected_images:
    return True
  elif existing_images == set([]):
    return False
  else:
    raise BaseException('Something is wrong with the world today: {}'.format(bundle))

def main():

  parser = argparse.ArgumentParser(description='''Convert scanned PDF files into appropriately rotated JPEGs, 
    which can be uploaded to Captricity for processing.
    Support for TIFF files not yet fully tested!''')
  
  parser.add_argument('-p', '--pattern', action="store",
                      dest="infile_pattern", default=None,
                      help="only extract JPEGs from pdfs whose file names matches this pattern")
  parser.add_argument('-i', '--indir', action="store",
                      dest="input_dir", default=".",
                      help="directory to search for input (pdf files; default: current directory)")
  parser.add_argument('-o', '--outdir', action="store",
                      dest="output_dir", default=".",
                      help="directory for saving resulting .jpg files (default: current directory)")

  args = parser.parse_args()

  listdir = os.listdir(os.path.expanduser(args.input_dir))
  listoutdir = os.listdir(os.path.expanduser(args.output_dir))

  pdfbundles = filter( lambda x: x.endswith('.pdf'), listdir )
  tifbundles = filter( lambda x: x.endswith( ('.tif', '.tiff') ), listdir )

  if args.infile_pattern != None:
    pdfbundles = filter( lambda x: bool(re.search(args.infile_pattern, x)), pdfbundles )
    tifbundles = filter( lambda x: bool(re.search(args.infile_pattern, x)), tifbundles )

  jpglist = filter( lambda x: x.endswith('.jpg'), listoutdir )
  
  if len(pdfbundles) == len(tifbundles) == 0 :
    print 'Nothing to be done, quitting.'
    return
  
  bundle_filter = lambda x: not check_if_converted( x, jpglist, xrange(imagesperfile)) 

  for bundle in filter( bundle_filter, tifbundles):
    print 'Converting {}'.format(bundle)
    im=Image.open(args.input_dir + '/' + bundle)
    try:
      while True:
        im.rotate(270)
        # NB: not sure if just changing the extension will let this save as a jpeg; double-check
        im.save( os.path.splitext(bundle)[0] + '-' + str(im.tell()) + '.jpg' )
        im.seek(im.tell()+1)
    except EOFError:
      pass

  for bundle in filter(bundle_filter, pdfbundles):
    print 'Converting {}'.format(bundle)
    basename = os.path.splitext(bundle)[0]

    retcode = call([ 'pdfimages', '-j', args.input_dir + '/' + bundle, args.output_dir + '/' + basename ])

    tempnames = filter( lambda x: x.startswith(basename) and x.endswith('.jpg'),  os.listdir(args.output_dir) )

    if len(tempnames) != imagesperfile:
        raise BaseException('Something is wrong with the world today: {}'.format(bundle))
    else:
        for name in tempnames:
            retcode = call([ 'convert', '-rotate', '90', args.output_dir+'/'+name,
                              args.output_dir+'/'+os.path.splitext(name)[0]+'.jpg' ])

  print 'Done.'
  return 0

main()

