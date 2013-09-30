 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/languages'),
    config.guiJs('livedesk', 'views/blogtypes'),
    config.guiJs('livedesk', 'views/configure/themes'),
    config.guiJs('livedesk', 'views/configure/api-keys'),
    'gizmo/superdesk/action',
    config.guiJs('livedesk', 'models/blog'),
    config.guiJs('media-archive', 'upload'),
    config.guiJs('media-archive', 'adv-upload'),
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!core>layouts/footer-dinamic',
    'tmpl!livedesk>configure',
    'tmpl!livedesk>configure/languages',
    'tmpl!livedesk>providers/edit/imagelink',
], function( $, Gizmo, LanguagesView, BlogTypesView, ThemesView, ApiKeysView, Action, BlogModel, uploadCom, UploadView ) {
   return Gizmo.View.extend({
        events: {
            '[data-action="save"]': { 'click': 'save' },
            '[data-action="save-close"]': { 'click': 'saveClose' },
            '[data-action="cancel"]': { 'click': 'close' },
            '[name="Language"]': { change: 'changeLanguage' },
            '[name="FrontendServer"]': { focusout: 'changeFrontendServer', keydown: 'keydownFrontendServer' },
			'[name="OutputLink"]': { click: 'selectInput', focusIn: 'selectInput' },
            '[name="ProviderLink"]': { click: 'selectInput', focusIn: 'selectInput' },
            "[data-toggle='modal-image']": { 'click': 'openUploadScreen' }
        },
        init: function() {
        },
        handleImageUpload: function(imgData) {
            var self = this;
            if (imgData.length) {
                var myData = imgData[0].data;
                self.el.find('[name="MediaImage"]').val(myData.Content.href);
                $.tmpl('livedesk>providers/edit/imagelink' , {fullimg: myData.Content.href, thumbimg:myData.Thumbnail.href}, function(e,o) {
                    self.el.find('#MediaImageThumb').html(o);
                });
            }
        },
        openUploadScreen: function() {
            var self = this;
            var uploadView = new UploadView({thumbSize: 'medium'});
            uploadView.activate().then(function(data) {
                self.handleImageUpload(data);
            });
        },
        selectInput: function(evt) {
			$(evt.target).select();
		},
        save: function(evt){
            var self = this,
                EmbedConfig = {
                    'theme': self.el.find('[name="Theme"]').val(),
                    'FrontendServer': self.el.find('[name="FrontendServer"]').val(),
                    'MediaImage': self.el.find('[name="MediaImage"]').val(),
                    'MediaUrl': self.el.find('[name="MediaUrl"]').val(),
                    'UserComments': self.el.find('[name="UserComments"]').is(':checked')
                },
                data = {
                    Language: self.el.find('[name="Language"]').val(),
                    Type: self.el.find('[name="blogtypeselection"]:checked').val(),
                    EmbedConfig: JSON.stringify(EmbedConfig)
                };
            self.apiKeysView.save();
			self.model.off('update');
            return self.model.set(data).sync();
        },
        saveClose: function(evt) {
            var self = this;
            self.save().done(function() {
                self.close();
            });
        },
        close: function() {
            Backbone.history.navigate('live-blog/' + this.model.get('Id'), true);
        },
        refresh: function() {
            var self = this;
            self.model = Gizmo.Auth(new Gizmo.Register.Blog(self.theBlog));
            self.model
                .one('read update', self.render, self)
                .sync();
        },
        changeFrontendServer: function(evt){
            this.themesView.change(evt);
        },
        keydownFrontendServer: function(e){
            var code = (e.keyCode ? e.keyCode : e.which);
             if(code == 13) {
                e.preventDefault();
                this.themesView.change(e);
            } 
        },
        changeLanguage: function(evt) {
           this.themesView.change(evt); 
        },

        render: function() {
            var embedConfig = this.model.get('EmbedConfig');
            if((embedConfig !== undefined) && $.isString(embedConfig)) {
                this.model.data['EmbedConfig'] = JSON.parse(this.model.get('EmbedConfig'));
            } else if(embedConfig === undefined){
                this.model.data['EmbedConfig'] = {};
            }
            var self = this,
                themesData,
                data = $.extend({}, self.model.feed(), {
                    BlogHref: self.theBlog,
                    BlogId: self.model.get('Id'),
                    ui: {
                        content: 'is-content=1',
                        side: 'is-side=1',
                        submenu: 'is-submenu',
                        submenuActive2: 'active'
                    }
                });
            embedConfig = this.model.get('EmbedConfig');
            if(!embedConfig.FrontendServer || embedConfig.FrontendServer == ''){
                embedConfig.FrontendServer = config.api_url;
            }
            if(this.model.href.indexOf(config.api_url) !== -1 ) {
                data["OutputLink"] = this.model.href.replace(config.api_url, embedConfig.FrontendServer);
            }
            else {
                data["OutputLink"] = embedConfig.FrontendServer + this.model.href;
            }
            data["ProviderLink"] = data["OutputLink"].split('/').slice(0,-1).join('/');
            $.superdesk.applyLayout('livedesk>configure', data, function() {
            //$.tmpl('livedesk>configure', self.model.feed(), function(e, o){
                //self.el.html(o);
                self.languagesView = new LanguagesView({
                    tmpl: 'livedesk>configure/languages',
                    el: self.el.find('.languages'),
                    _parent: self,
                    tmplData: { selected: self.model.get('Language').get('Id')}
                });
                self.blogtypesView = new BlogTypesView({
                    el: self.el.find('.blogtypes'),
                    _parent: self,
                    theBlog: self.theBlog,
                    tmplData: { selected: self.model.get('Type').get('Id') }
                });
                self.apiKeysView = new ApiKeysView({
                    el: self.el.find('.api-keys'),
                    _parent: self,
                    theBlog: self.theBlog
                });
                themesData = {
                    el: self.el.find('.themes'),
                    _parent: self,
                    theBlog: self.theBlog
                };
                if(self.model.get('EmbedConfig')) {
                    //embedConfig = self.model.get('EmbedConfig');
                    themesData.tmplData = { selected: embedConfig.theme };
                } 
                self.themesView = new ThemesView(themesData);
                // TODO: move this in emebed view or in theme view
                self.el.find('#emebed-script').focus(function() { $(this).select(); } );

                /* sf-toggle*/
                self.el.find('.sf-toggle').each(function(i,val){
                    var additional_class="";
                    if ($(val).attr("checked")=="checked")  additional_class += " sf-checked ";
                    if ($(val).hasClass("on-off")) additional_class +=" on-off-toggle ";
                    if ($(val).hasClass("sf-disable")) additional_class += " sf-disable ";
                    $(val).wrap('<div style="float:none" class="sf-toggle-custom ' + additional_class + '"><div class="sf-toggle-custom-inner"></div></div>');
                    $(val).hide();

                    $(val).parent().parent().on("click", function(e){
                        e.preventDefault();
                        if (!$(e.target).hasClass("sf-disable")) {
                            $(e.target).toggleClass('sf-checked');
                            var own_box = $(e.target).find(".sf-toggle");        
                            own_box.prop('checked', $(e.target).hasClass('sf-checked'));
                            own_box.change();
                        }
                    });
                });

            });
        }
    });
});
