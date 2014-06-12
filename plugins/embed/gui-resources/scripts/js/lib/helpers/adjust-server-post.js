'use strict';

define(['underscore'], function(_) {
    return function(data) {
        var newAdvertisment = 'infomercial';
        if (data.Type.Key === 'advertisement') {
            data.Type.Key = newAdvertisment;
        }
        if (data.Author.Source.Name === 'advertisement') {
            data.Author.Source.Name = newAdvertisment;
        }
        if (data.Author.Source.Type.Key === 'smsblog') {
            data.Author.Source.IsModifiable = 'False';
            data.Author.Source.Name = 'sms';
        }
        if (data.Author.Source && data.Author.Source.Name === 'embed') {
            data.Author.Source.IsModifiable = 'False';
            data.Author.Source.Name = 'comments';
        }
        return data;
    };
});
