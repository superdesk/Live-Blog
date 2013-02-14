.. -*- mode: rst -*-
.. This text is in reStucturedText format, so it may look a bit odd.
.. See http://docutils.sourceforge.net/rst.html for details.

=========================
Installing GraphicsMagick
=========================

.. contents::
  :local:

Executive Summary
-----------------

GraphicsMagick provides a comprehensive collection of utilities,
programming interfaces, and GUIs, to support file format conversion,
image processing, and 2D vector rendering.

GraphicsMagick is originally based on ImageMagick from ImageMagick Studio
(which was originally written by John Cristy at Dupont). The goal of
GraphicsMagick is to provide the highest quality product possible while
encouraging open and active participation from all interested developers.
The GraphicsMagick usage license is designed to allow it to be used for
any application, including proprietary or GPLed applications. Please see
the file `Copyright.txt <Copyright.html>`_ for the GraphicsMagick licence.

Availability
------------

The master ftp site for GraphicsMagick distributions is
ftp://ftp.graphicsmagick.org/pub/GraphicsMagick/. Bandwidth on this
site is very limited, so it is recommended to download from SourceForge
at http://sourceforge.net/projects/graphicsmagick/files/ if
possible.

GraphicsMagick is a continual work in progress. The very latest code
is available via the Mercurial distributed source control management
tool (http://mercurial.selenic.com/). GraphicsMagick may be retrieved
via the following command:

  hg clone http://graphicsmagick.hg.sourceforge.net/hgweb/graphicsmagick/graphicsmagick/ GM

Mercurial provides a complete stand-alone repository which contains
the full history of the GraphicsMagick project.  You may use the
cloned repository for your own purposes related to GraphicsMagick
(e.g. manage local GraphicsMagick changes), and can easily pull
GraphicsMagick updates from the main repository whenever you like.

Documentation
-------------

  Open the file index.html in a web browser, or refer to the gm(1) manual
  page. Also read the GraphicsMagick frequently asked questions in the
  file `www/FAQ.html <FAQ.html>`_.

Installation
------------

  GraphicsMagick may be compiled from source code for virtually any
  modern Unix system (including Linux and MacOS X) and Microsoft Windows.
  Installation instructions may be found in the following files (or their
  HTML equivalents):

  * Unix / MacOS-X / Cygwin / MinGW:

    `INSTALL-unix.txt <INSTALL-unix.html>`_

  * Microsoft Windows (Via "setup" style installer or from source code):

    `INSTALL-windows.txt <INSTALL-windows.html>`_

Add-On Libraries & Programs
---------------------------

To further enhance the capabilities of GraphicsMagick, you may want to
get these programs or libraries. Note that these packages are already
integrated into the GraphicsMagick Mercurial repository for use when
building under Microsoft Windows:

* GraphicsMagick requires the BZLIB library from

    http://www.bzip.org/

  to read and write BZip compressed MIFF images.

* GraphicsMagick requires 'ralcgm' from

    http://www.agocg.ac.uk/train/cgm/ralcgm.htm

  to read the Computer Graphics Metafile (CGM) image format. You also
  need Ghostscript and Ghostscript Fonts (see below).

* GraphicsMagick requires 'dcraw' from

    http://www.cybercom.net/~dcoffin/dcraw/

  to read raw images from digital cameras.  Dcraw is invoked
  automatically when used to read files using a common RAW file format
  extension.

* GraphicsMagick requires 'fig2dev' provided in the transfig package
  from

    http://www.xfig.org/

  to read the Fig image format. Ghostscript and Ghostscript Fonts (see
  below) are also required.

* GraphicsMagick requires the FreeType software, version 2.0 or above,
  available as

    http://www.freetype.org/

  to annotate with TrueType and Postscript Type 1 fonts.

* GraphicsMagick requires Ghostscript software (version 9.04
  recommended) available from

    http://pages.cs.wisc.edu/~ghost/

      or

    http://sourceforge.net/projects/ghostscript/

  to read the Postscript or the Portable Document Format (PDF).

  Ghostscript Fonts are available from

    https://sourceforge.net/projects/gs-fonts/

  Ghostscript is available for use under both free (GPL) and
  commercial licenses.  We are not lawyers so we can not provide
  advice as to when the commercial license from Artifex is required.
  Please make sure that you are aware of Ghostscript licencing and
  usage terms if you plan to use it in some sort of commercial
  situation.

  Ghostscript (release 7.0 and later) may optionally install a library
  (libgs) under Linux. If this library is installed, GraphicsMagick may
  be configured to use it. We do **NOT** recommend using this library
  under Unix type systems. The Ghostscript library does not support
  concurrency since only one instance of the interpreter is available.
  Unix systems will obtain better performance from executing Ghostscript as
  an external process since then multiple interpreters may execute at
  once on multiple CPU cores.

  If the Ghostscript library is used, then please be aware that
  Ghostscript provides its own modified version of libjpeg and
  libJasper while GraphicsMagick will be using these libraries as
  provided with the system. If Ghostscript is not using the same
  libraries, then identically named symbols may be used from the wrong
  code, causing confusion or a program crash. If conflicts cause JPEG
  to fail (JPEG returns an error regarding expected structure sizes),
  it may be necessary to use Ghostscript's copy of libjpeg for
  GraphicsMagick, and all delegate libraries which depend on libjpeg,
  or convince Ghostscript to build against an unmodified installed
  JPEG library (and lose compatibility with some Postscript files).

* GraphicsMagick requires hp2xx available from

     http://www.gnu.org/software/hp2xx/hp2xx.html

  to read the HP-GL image format. Note that HPGL is a plotter file
  format. HP printers usually accept PCL format rather than HPGL
  format.  Ghostscript (see above) is also required.

* GraphicsMagick requires the lcms library (1.11 or later, including
  2.X) available from

     http://www.littlecms.com/

  to perform ICC CMS color management.

* GraphicsMagick requires gnuplot available from

     http://gnuplot.sourceforge.net/

  to read GNUPLOT plot files (with extension gplt).  Ghostscript (see
  above) is also required.

* GraphicsMagick requires Graphviz available from

     http://www.graphviz.org/

  to read Graphvis 'dot' digraph files (with extension dot).
  Ghostscript (see above) is also required.

* GraphicsMagick requires html2ps available from

     http://user.it.uu.se/~jan/html2ps.html

  to rasterize HTML files.  Ghostscript (see above) is also required.

* GraphicsMagick requires the JBIG-Kit software available via
  HTTP from

     http://www.cl.cam.ac.uk/~mgk25/jbigkit/

  to read the JBIG image format.

* GraphicsMagick requires the Independent JPEG Group's software
  available from

     http://www.ijg.org/

  to read the JPEG v1 image format.

  Apply this JPEG patch to Independent JPEG Group's (6b release!)
  source distribution if you want to read lossless jpeg-encoded DICOM
  (medical) images:

     ftp://ftp.graphicsmagick.org/pub/GraphicsMagick/delegates/ljpeg-6b.tar.gz

  Use of lossless JPEG is not encouraged. Unless you have a requirement
  to read lossless jpeg-encoded DICOM images, please disregard the patch.

* GraphicsMagick requires the JasPer Project's JasPer library version
  1.701.0 (or later) available via http from

     http://www.ece.uvic.ca/~mdadams/jasper/

  to read and write the JPEG-2000 format. Please note that JasPer 1.900.1
  may have a problem when used with GraphicsMagick's modules build. To
  solve this problem, edit the file src/libjasper/base/jas_init.c and
  comment out the line which invokes atexit().

* On Unix-type systems, Windows/MinGW, and Windows/Cygwin,
  GraphicsMagick requires libltdl from libtool in order to support
  building GraphicsMagick with dynamically loadable modules.  A copy
  of libltdl is bundled with GraphicsMagick and may be optionally
  configured to be installed with GraphicsMagick (via
  --enable-ltdl-install option), but it is recommended to install it
  separately via a binary package or by building and installing the
  libtool source package.  Libtool is available via anonymous FTP from

     ftp://ftp.gnu.org/pub/gnu/libtool/

* GraphicsMagick requires the MPEG utilities from the MPEG Software
  Simulation Group, which are available via anonymous FTP as

     ftp://ftp.GraphicsMagick.org/pub/GraphicsMagick/delegates/mpeg2vidcodec_v12.tar.gz

  to read or write the MPEG image format.

* GraphicsMagick requires the LIBPNG library, version 1.0 or above, from

     http://www.libpng.org/pub/png/pngcode.html

  to read or write the PNG, MNG, or JNG image formats.  LIBPNG depends
  upon the ZLIB library (see below).

* GraphicsMagick requires ra_ppm from Greg Ward's Radiance software
  available from

     http://radsite.lbl.gov/radiance/HOME.html

  to read the Radiance image format.

* GraphicsMagick requires rawtorle from the Utah Raster Toolkit
  available via anonymous FTP as

     ftp://ftp.graphicsmagick.org/pub/GraphicsMagick/delegates/urt-3.1b.tar.Z

  to write the RLE image format.

* GraphicsMagick requires scanimage from

     http://www.sane-project.org/
							 
  to import an image from a scanner device.

* GraphicsMagick requires Sam Leffler's TIFF software available via
  anonymous FTP at

     ftp://ftp.remotesensing.org/libtiff/

  or via HTTP at

     http://www.remotesensing.org/libtiff/

  to read the TIFF image format. It in turn optionally requires the
  JPEG and ZLIB libraries.  Libtiff 3.8.2 or later is recommended.

* GraphicsMagick may optionally use the TRIO library from

     http://sourceforge.net/projects/ctrio/

  to substitute for the vsnprintf function when the operating system
  does not provide one. Older operating systems (e.g. Solaris 2.5)
  may not provide a vsnprintf function. If vsnprintf (or the TRIO
  replacement) is not used, then vsprintf is used instead, which
  decreases the security of GraphicsMagick due to possible buffer
  overrun exploits.

* GraphicsMagick may optionally use the umem memory allocation library
  which is included in Sun's Solaris operating system or available from

     https://labs.omniti.com/trac/portableumem

  to provide enhanced versions of the standard memory allocation
  facilities. Use of umem may improve performance for multi-threaded
  programs and provides access to debugging features that detect memory
  leaks, buffer overruns, multiple frees, use of uninitialized data, use
  of freed data, and many other common programming errors.

* GraphicsMagick requires libwmf 0.2.5 (or later) from

     http://sourceforge.net/projects/wvware/

  to render files in the Windows Meta File (WMF) metafile format
  (16-bit WMF files only, not 32-bit "EMF"). This is the format
  commonly used for Windows clipart (available on CD at your local
  computer or technical book store). WMF support requires the FreeType
  2 library in order to render TrueType and Postscript fonts.

  While GraphicsMagick uses the libwmflite (parser) component of the
  libwmf package which does not depend on any special libraries, the
  libwmf package as a whole depends on FreeType 2 and either the
  xmlsoft libxml, or expat libraries. Since GraphicsMagick already uses
  libxml (for reading SVG and to retrieve files via HTTP or FTP), it is
  recommended that the options '--without-expat --with-xml' be supplied
  to libwmf's configure script.

  GraphicsMagick's WMF renderer provides some of the finest WMF
  rendering available due its use of antialiased drawing algorithms.
  You may select a background color or texture image to render on. For
  example, "-background '#ffffffff'" renders on a transparent
  background while "-texture plasma:fractal" renders on a fractal image.

   A free set of Microsoft Windows fonts may be retrieved from
   http://sourceforge.net/projects/corefonts/. Note that the license
   for these fonts requires that they be distributed in the original
   .exe form, but the Linux folks have found ways to deal with that on
   non-Windows systems.

* GraphicsMagick requires an X server for the 'display', 'animate', and
  'import' functions to work properly. Unix systems usually provide an X
  server as part of their standard installation. For MacOS-X, X11 is a
  system install time option.

  A free X server for Microsoft Windows is included as part of
  Cygwin and may be selected from the Cygwin installer. Cygwin is
  available from

     http://www.cygwin.com/

  There is a nearly free X server available for Windows and Macintosh at

     http://www.microimages.com/downloads/mix/

* GraphicsMagick requires libxml2 available from

     http://xmlsoft.org/

  to read the SVG image format and to retrieve files from over a
  network via FTP and HTTP.

* GraphicsMagick requires the liblzma library from XZ Utils available from

     http://www.tukaani.org/xz/

  to support TIFF with LZMA compression and future LZMA-compression
  features (yet to be developed).  The utilities from this package are
  also necessary in order to decompress GraphicsMagick packages
  distributed with ".xz" or ".lzma" extensions.

* GraphicsMagick requires the ZLIB library from

     http://www.zlib.net/

  to read or write the PNG or Zip compressed MIFF images.


--------------------------------------------------------------------------

.. |copy|   unicode:: U+000A9 .. COPYRIGHT SIGN

Copyright |copy| GraphicsMagick Group 2002 - 2012
