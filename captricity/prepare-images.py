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

  #
  # convert all of the tiffs
  #
  for bundle in filter( bundle_filter, tifbundles):
    print 'Converting {}'.format(bundle)
    basename = os.path.splitext(bundle)[0]

    # use imagemagick to convert tiffs to jpgs
    # NB: imagemagick complains about format issues with the tiffs, but this
    #     doesn't appear to have any effect on the result...
    retcode = call([ 'convert', 
                     args.input_dir + '/' + bundle, 
                     args.output_dir + '/' + basename + '-%03d.jpg' ])

    tempnames = filter( lambda x: x.startswith(basename) and x.endswith('.jpg'),  
                        os.listdir(args.output_dir) )

    # be sure that conversion produced the right number of jpgs, and
    # rotate each one so that it is right-side up
    # (so far, we haven't had to rotate the tiffs, so the part that actually rotates
    #  is commented out)
    if len(tempnames) != imagesperfile:
        raise BaseException('The file {} does not appear to have {} pages!'.format(bundle, imagesperfile))
    else:
        for name in tempnames:
            pass
            #retcode = call([ 'convert', '-rotate', '0', args.output_dir+'/'+name,
            #                  args.output_dir+'/'+os.path.splitext(name)[0]+'.jpg' ])

  #
  # convert all of the pdfs
  #
  for bundle in filter(bundle_filter, pdfbundles):

    print 'Converting {}'.format(bundle)
    basename = os.path.splitext(bundle)[0]

    # use pdfimages to get jpgs from the pdf files; this is much faster than
    # other methods we tried
    retcode = call([ 'pdfimages', '-j', args.input_dir + '/' + bundle, args.output_dir + '/' + basename ])

    tempnames = filter( lambda x: x.startswith(basename) and x.endswith('.jpg'),  
                        os.listdir(args.output_dir) )

    # be sure that conversion produced the right number of jpgs, and
    # rotate each one so that it is right-side up
    if len(tempnames) != imagesperfile:
        raise BaseException('The file {} does not appear to have {} pages!'.format(bundle, imagesperfile))
    else:
        for name in tempnames:
            retcode = call([ 'convert', '-rotate', '90', args.output_dir+'/'+name,
                              args.output_dir+'/'+os.path.splitext(name)[0]+'.jpg' ])

  print 'Done.'
  return 0

main()

