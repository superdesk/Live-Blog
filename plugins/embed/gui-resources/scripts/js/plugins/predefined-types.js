'use strict';

define([
    'plugins',
    'dust',
    'lib/utils'
], function (plugins, dust, utils) {
    plugins['predefined-types'] = function (config) {
        utils.dispatcher.on('before-render.post-view', function (view) {
            if (view.model.get('item') !== 'posttype/normal') {
                return;
            }
            var Meta = view.model.get('Meta'),
                predefinedType;
            if (Meta['post-predefined-type']) {
                predefinedType = Meta['post-predefined-type'].text.toLowerCase();
                if (dust.cache['theme/item/predefined/' + predefinedType]) {
                    view.setTemplate('theme/item/predefined/' + predefinedType);
                }
            }
        });
    };
    return plugins['predefined-types'];
});
