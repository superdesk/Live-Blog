
		   ImageMagick Delegate Library Licenses
		   =====================================

ImageMagick may be built using a number of optional 3rd party libraries
that we call "delegate" libraries. Binary distributions built by, or
distributed by, ImageMagick Studio may include programs, libraries, or
modules, based on one or more of these 3rd party libraries.  Whenever
possible, dependence on a 3rd party library is isolated to a module so
that when ImageMagick is built using modules, this dependence may be
removed by simply deleting the module.

While ImageMagick Studio makes every effort to comply with the
requirements imposed by 3rd party libraries, the license requirements
for these libraries may not be compatible with the end-user's
requirements. In some cases the binary distribution of ImageMagick may
be brought into compliance with user requirements by simply removing a
loadable module, while in other cases, the user may need to build a
custom ImageMagick from scratch. ImageMagick Studio bears no
responsiblity for ensuring that the user properly complies with license
requirements.

In order to comply with some of the distribution licenses, and to assist
the user with evaluating compatibility the licenses for each 3rd party
library are included in this directory as seperate files.

Magick++
  Magick++ is the C++ library interface to the ImageMagick API.  Its
  license may be found in the file "Magick++.txt".

Bzlib
  Bzlib is a block-sorting file compressor (from the bzip2 package) used
  to support the optional bzip2 compression mode of the MIFF file
  format. Its license may be found in the file "bzlib.txt".

Cygwin API library
  This library is used to support building ImageMagick under the Cygwin
  Unix emulation environment for Microsoft Windows.  The license for this
  library may be found in the file "cygwin.txt".

Digital Imaging Group Flashpix OpenSource Toolkit
  This toolkit is used to support the FlashPIX file format.  The license for
  the toolkit may be found in the file "fpx.txt".

FreeType
  This library is used to support rendering TrueType and Postscript
  Type 1 fonts.  The license for this library may be found in the file
  "ttf.txt".

Ghostscript Library
  This library ("libgs") is used in some environments to support reading
  the Postscript, Encapsulated Postscript, and Portable Document Format (PDF).
  Its license may be found in the file "libgs.txt".

HDF5
  This library is used to support the HDF5 file format. Its license may
  be found in the file "hdf5.txt".

JBIG
  This library is used to support the JBIG file format. Its license may
  be found in the file "jbig.txt".

Hp2xx
  This stand-alone program is used to support rendering HP-GL plotter
  files.  Its license may be found in the file "hp2xx.txt".

JasPer
  This library is used to support the JPEG2 file format. Its license may
  be found in the file "jp2.txt".

Independent JPEG Group JPEG
  This library is used to support the JPEG file format. Its license may
  be found in the file "jpeg.txt".

LittleCMS
  This library is used to support CMS color profiles.  Its license may
  be found in the file "lcms.txt".

XML parser for Gnome
  This library is used to support parsing XML files (SVG & MSL) as well
  as to retrieve files via "ftp://" and "http://" URLs. Its license may
  be found in the file "libxml.txt".

GNU ISO C++ Library
  This library ("libstdc++") is used when compiling with gcc 3.0 or
  later to support the standard C++ classes used by Magick++. The terms
  of its license may be found in the files "libstdc++.txt" and
  "libstdc++2.txt".

GNU libltdl
  This library is used to support dynamically loadable modules on
  Unix-like systems. Its license may be found in the file "ltdl.txt".

  Note that while libltdl uses the GNU Lesser General Public License
  there is a special exception for programs which are built using
  GNU libtool.  See ltdl-except.txt for details.

libpng
  This library is used to support the PNG file format. Its license may
  be found in the file "png.txt".

libtiff
  This library is used to support the TIFF file format. Its license may
  be found in the file "tiff.txt".

libwmf
  This library is used to support reading the WMF file format. Its
  license may be found in the file "wmf.txt".

zlib
  This library is used to support the zlib and deflate compression
  algorithms. Its license may be found in the file "zlib.txt".

mpeg2dec
  This utility is used to decode MPEG v1 and MPEG v2 seqences. Its
  license (which includes a warning regarding applicable patents)
  may be found in the file "mpeg2dec.txt".

mpeg2enc
  This utility is used to encode MPEG v1 and MPEG v2 seqences. Its
  license (which includes a warning regarding applicable patents)
  may be found in the file "mpeg2enc.txt".
