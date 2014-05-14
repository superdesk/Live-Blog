'use strict';

define({

    urls: {
        // Pinterest URL, params: permanent link, img src, blog title
        pin:         '//pinterest.com/pin/create/button/?url=%s' +
                            '&media=%s' +
                            '&description=%s',

        // Twitter URL, params: message, blog title, permanent link
        twt:     '//twitter.com/home?status=' + '%s %s: %s',

        // LinkedIn URL, params: permanent link, blog title, summary
        lin:    '//www.linkedin.com/shareArticle?mini=true&url=%s&title=%s&summary=%s',

        // Google URL, params: permanent link
        ggl:      '//plus.google.com/share?url=%s&t=',

        // Email URL, params: subject, permanent link
        email:       'mailto:?to=&subject=%s&body=%s',

        // Facebook URL, params: blog title, summary, permanent link, image param
        fb:          '//www.facebook.com/sharer.php?s=100&p[title]=%s' +
                            '&p[summary]=%s' +
                            '&p[url]=%s%s',

        // Facebook URL image component, to be added at the end of fbURL
        // params: index, img src
        fbImageComp: '&p[images][%s]=%s'
    },

    shareWindowSize: {
        pin:   {h: 400, w: 700},
        twt:   {h: 400, w: 570},
        lin:   {h: 400, w: 570},
        ggl:   {h: 400, w: 570},
        email: {h: 1024, w: 768},
        fb:    {h: 400, w: 570}
    }
});
