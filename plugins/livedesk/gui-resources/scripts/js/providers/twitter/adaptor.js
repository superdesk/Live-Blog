define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'codebird',
    'jquery/rest',
    'jquery/tmpl',
    'tmpl!livedesk>providers/generic-error'
], function(providers, $, PrepublishView, Codebird) {
    
    $.extend(providers.twitter, {
        adaptor: {
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id, Source.Key')
                    .request({data: { 'qs.name': 'twitter'}})
                    .done(function(collabs) {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                            try{
                                self.key = JSON.parse(collabs[0].Source.Key);
                            } catch(e){
                                self.key = { 'ConsumerKey': '', 'ConsumerSecret': '' };
                            }
                            var cb = new Codebird;
                            cb.setConsumerKey(self.key.ConsumerKey, self.key.ConsumerSecret);
                            cb.__call(
                                'oauth2_token',
                                {},
                                function (reply) {
                                    if(reply.httpstatus === 200) {
                                        var bearer_token = reply.access_token;
                                        cb.setBearerToken(bearer_token);
                                        self._parent.render();
                                    } else {
                                        //self._parent.render();
                                        $.tmpl('livedesk>providers/generic-error', {message: reply.errors[0].message}, function(e,o) {
                                            $(providers.twitter.el).append(o);
                                        });
                                    }
                                });
                            providers.twitter.cb = cb;
                    });
            },
            universal: function(obj) {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta['$idx'];
                delete meta['$len'];                
                return new PrepublishView({
                    sourceTemplate: 'sources/twitter',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: obj.text,
                        Type: 'normal',
                        Author: this.author,
                        Meta: meta
                    }
                });
            }
        }
    });
    return providers;
});


