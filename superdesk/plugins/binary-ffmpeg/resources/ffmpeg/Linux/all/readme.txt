
    ______ ______                                  __            _  __     __
   / ____// ____/____ ___   ____   ___   ____ _   / /_   __  __ (_)/ /____/ /
  / /_   / /_   / __ `__ \ / __ \ / _ \ / __ `/  / __ \ / / / // // // __  / 
 / __/  / __/  / / / / / // /_/ //  __// /_/ /  / /_/ // /_/ // // // /_/ /  
/_/    /_/    /_/ /_/ /_// .___/ \___/ \__, /  /_.___/ \__,_//_//_/ \__,_/   
                        /_/           /____/                                 


                build: ffmpeg-linux64-20120906.tar.bz2
              version: N-44202-gfb2e7ac

 
                  gcc: 4.7.1
                 yasm: 1.2.0

               libvpx: v1.1.0-223-gc6fd0a5
              libxavs: 0.1.x
              libx264: 0.128.2216 198a7ea configuration: --bit-depth=8 --chroma-format=all
             libspeex: 1.2~rc1-6
            libvorbis: 1.3.2-1.3
            libtheora: 1.1.1+dfsg.1-3.1
           libmp3lame: 3.99.5+repack1-3 
          libfreetype: 2.4.9-1
         libvo-aacenc: 0.1.2-1
       libvo-amrwbenc: 0.1.2-1
    libopencore-amrnb: 0.1.3-2
    libopencore-amrwb: 0.1.3-2

Note: ffmpeg now uses libx264's internal presets with the -preset flag. Look at the "libx264 AVOptions:"
      section of `ffmpeg -h | less` for a complete list of libx264 options.


      This build should be stable but if you do run into problems *DO NOT* file a bug report against           
      it! You should first check out the source from git://source.ffmpeg.org/ffmpeg.git, build it and           
      see if the problem persists. If so, then and only then should you file a bug report using the
      version you compiled.

      The source code for FFmpeg and all libs can be downloaded here.
      http://dl.dropbox.com/u/24633983/static-sources.7z

      Donate a few bucks via paypal if you've found this build helpful. 
      Donation link: http://goo.gl/1Ol8N

      Questions? Comments?
      email: john.vansickle@gmail.com
        irc: irc://irc.freenode.net #ffmpeg #libav nickname: relaxed
  build url: http://sites.google.com/site/linuxencoding/builds
