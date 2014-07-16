'use strict';

define(['underscore', 'jed'], function(_, Jed) {

    var defaults = {
        'locale_data': {
            'messages': {
                '': {
                    'domain': 'messages',
                    'lang': 'en',
                    'plural_forms': 'nplurals=2; plural=(n != 1);'
                }
            }
        },
        // The default domain if one is missing
        'domain': 'messages'
    };
    Jed.context_delimiter = ':';
    // Add a method to load the messages
    var gettext = new Jed(defaults);
    gettext.loadMessages = function (messages) {
        _.extend(this.options.locale_data.messages, messages);
    };
    return gettext;
});
