'use strict';
define(['dust/core'], function(dust) {
    dust.themed = function(name) {
        // Check fist if name contains a theme base reference.
        if (name.substr(0, 10) === 'themeBase/') {
            // if so remove it.
            name = name.substr(10);
            // For a given template file name return the template name registered by dust.
            // Return the current theme template if registered, otherwise return the default
            // base theme template.
            // (ex: for 'container' return 'theme/container' or 'themeBase/container')
            return dust.cache['theme/' + name] ? ('theme/' + name) : ('themeBase/' + name);
        }
        return name;
    };
});
