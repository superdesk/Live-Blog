 define([
    'jquery', 
    'gizmo/superdesk',  
    config.guiJs('livedesk', 'views/blogtype/add/posts'), 
    config.guiJs('livedesk', 'models/blogtype'),
    config.guiJs('livedesk', 'models/post'),
    'tmpl!livedesk>blogtype/add',
], function( $, Gizmo, PostsView ) {
   
   return Gizmo.View.extend({
        _currentStep: 0,
        _bgimage: false,
        _post_settings: {},
        events: {
            '#save-add-blogtype': { 'click': 'save' },
            'a[name="save-post"]': { 'click': 'savePost' },
            'a[name="save-post-close"]': { 'click': 'savePostClose' },
            'a[name="addnewpost"]': { 'click': 'addPost' },
            'a[name="wizard-back"]': { 'click': 'previousStep' },
            'a[name="wizard-next"]': { 'click': 'nextStep' },
            'select[name="post-fontfamily"]': { 'change': 'selectFontFamily'},
            'select[name="post-fontsize"]': { 'change': 'selectFontSize'},
            'a[name="post-bold"]': { 'click': 'selectBold' },
            'a[name="post-italic"]': { 'click': 'selectItalic' },
            'a[name="post-underline"]': { 'click': 'selectUnderline' },
            'a[name="post-align"]': { 'click': 'selectAlign' },
            'button[name="picked-color"]': { 'click': 'bootstrapFix'},
            '#colorpicker1 ul li span': { 'click': 'selectColorPicker1'},
            '#colorpicker2 ul li span': { 'click': 'selectColorPicker2'},
            'input[name="post-addbgimage"]': { 'click': 'showBgImages'},
            '.wizard-picture-selection ul li': { 'click': 'selectBgImage'},
            '[name="wizard-start"]': { 'click': 'wizardStart' }
        },
        restBlog: function() {
            this.el.find('[name="blogtypename"]').val('');
        },
        init: function(){
            var self = this;
            if( !self.model ) {
                self.model = Gizmo.Auth(new Gizmo.Register.BlogType({ Post: []}));
            }
            self.render();
        },

        render: function(evt, data){
            var self = this;
            self.el.tmpl('livedesk>blogtype/add', self.model.feed(), function(){
                self.postPosts = new PostsView({
                    el: self.el.find('.blogtype-content'),
                    collection: self.model.get('Post'),
                    _parent: self
                });
            });
            self._currentStep = 0;
        },
        refresh: function(evt, data) {
            var self = this;
            self.el.find('[name="blogtypename"]').val('');
            //self.switchModal(evt, 0);
        },
        save: function(evt) {
            var self = this;
            var postspost = self.model.data['Post'];
            delete self.model.data['Post'];
            self.model
                .syncParse({ Name: self.el.find('[name="blogtypename"]').val()})
                .done(function(){
                    self.model.data['Post'] = postspost;
                    self.model.get('Post').savePending(self.model.href+'/Post');
                })
                .fail(function(){
                    evt.preventDefault();
                });
            self.model.data['Post'] = postspost;
        },
        resetMeta: function() {
            var self = this,
                el;
            if(self.currentPost.get('Content')) {
                var el1 = $(self.currentPost.get('Content')).addClass('wizard-preview');
                var el2 = $(self.currentPost.get('Content')).addClass('wizard-preview');
                self.el.find('.wizard-preview').eq(0).replaceWith(el1);
                self.el.find('.wizard-preview').eq(1).replaceWith(el2);
            } else {
                self.el.find('.wizard-preview').attr('style','');
            }
            self.el.find('[name="post-name"]').val(self.currentPost.get('Name'));
            self.el.find('[name="post-predefined"]').val(self._post_settings.predefinedContent);
            self.el.find('[name="post-fontfamily"]').val(self._post_settings['font-family']);
            self.el.find('[name="post-fontsize"]').val(self._post_settings['font-size']);
            self.el.find('[name="post-bold"]').toggleClass('active', self._post_settings['font-bold']);
            self.el.find('[name="post-italic"]').toggleClass('active', self._post_settings['font-italic']);
            self.el.find('[name="post-underline"]').toggleClass('active', self._post_settings['font-underline']);
            self.el.find('[name="post-align"]').removeClass('active');
            self.el.find('[align="'+ self._post_settings['font-align']+'"]').addClass('active');
            self.el.find('#colorpicker1 span[name="picked-color"]').attr('class',"wizard-color "+self._post_settings['color']);
            self.el.find('#colorpicker2 span[name="picked-color"]').attr('class',"wizard-color "+self._post_settings['background-color']);
            if(self._post_settings["background-image-id"] != 0) {
                self.el.find('[name="post-addbgimage"]').attr('checked','checked');
            } else {
                self.el.find('[name="post-addbgimage"]').removeAttr( 'checked' );
            }

        },
        resetPostSettings: function() {
            this._post_settings = {
                'name': '',
                'type' : '',
                'predefinedContent' : '',
                'font-family': 1,
                'font-size': 13,
                'font-bold': false,
                'font-italic': false,
                'font-underline': false,
                'font-align': 'left',
                'color': 'black',
                'color-code': '',
                'background-color': 'white',
                'background-color-code': '',
                'background-image': '',
                'background-image-id': 0
            };            
        },
        addPost: function(evt) {
            var self = this;
            self.currentPost = Gizmo.Auth(new Gizmo.Register.Post({}));
            self.resetPostSettings();
            self.resetMeta();
            self.switchModal(evt, 1);
        },
        editPost: function(evt, model) {
            var self = this;
            self.currentPost = model;
            if(model.get('Meta')) {
                self._post_settings = JSON.parse(model.get('Meta'));
            } else {
                self.resetPostSettings();
            }
            self.resetMeta();
            self.switchModal(evt, 1);
        }, 
        savePost: function(evt) {
            var self = this;
            //console.log(JSON.stringify($.extend({},self._post_settings)));
            if(self.currentPost._new) {
                self.currentPost.set({
                    Type: 'normal',
                    Meta: JSON.stringify($.extend({},self._post_settings)),
                    Content: self.el.find('.wizard-preview').clone().removeClass('wizard-preview').wrap('<p>').parent().html(),
                    Name: self._post_settings.name,
                    Creator: localStorage.getItem('superdesk.login.id')
                });    
            } else {
                self.currentPost.set({
                        Meta: JSON.stringify($.extend({},self._post_settings)),
                        Content: self.el.find('.wizard-preview').clone().removeClass('wizard-preview').wrap('<p>').parent().html(),
                        Name: self._post_settings.name
                    });
            }
            self.model.get('Post').addPending(self.currentPost);
            this.switchModal(evt, 0);
        },
        savePostClose: function(evt) {
            this.addPost(evt);
            this.save(evt);
        },
        showBgImages: function(evt) {
            var self = this,
                el = $(evt.target);
            if (el.prop("checked")==true)  {
              self._bgimage = true;
              self.el.find('.wizard-picture-selection').show();      
            }
            else {
              self._bgimage = false;
              self.el.find('.wizard-picture-selection').hide();
            } 
            self.checkBGimage();
        },
        /*!
         * Set or add the image selected to the post
         */
        selectBgImage: function(evt) {
            var self = this,
                el = $(evt.target);
            self.el.find('.wizard-picture-selection ul li').removeClass("picked");
            el.parents('li').addClass("picked");
            self.checkBGimage();            
        },
        /*!
         * Check and add the image selected to the post
         */
        checkBGimage: function() {
            var self = this;
            if (self._bgimage && self.el.find('.wizard-picture-selection ul li.picked').size()>0) {
                var imageurl = "url(" + self.el.find('.wizard-picture-selection ul li.picked img').attr("src") + ")";
                self._post_settings['background-image-id'] = parseInt(self.el.find('.wizard-picture-selection ul li.picked img').attr("imageID"));
                self._post_settings['background-image'] = self.el.find('.wizard-picture-selection ul li.picked img').attr("src");
                self.el.find('.wizard-preview').css({
                    'padding-left' : '50px',
                    'background-image' : imageurl,
                    'background-repeat' : 'no-repeat',
                    'background-position' : '5px 5px'
                });
            } else 
            {
                self.el.find('.wizard-preview').css({'background-image' : 'none',
                    'padding-left' : '5px'});
                self._post_settings['background-image-id'] = 0;
            }
        },
        /*!
         * bootstrap button bug fixed for both color pickers
         */
        bootstrapFix: function(evt) {
            return false;
        },
        selectColorPicker1: function(evt) {
            var self = this,
                el = $(evt.target);
            self.el.find('#colorpicker1 span[name="picked-color"]').attr("class",el.attr("class"));
            self.el.find('.wizard-preview').css("color",el.css("background-color"));
            self._post_settings['color-code'] = el.css("background-color");
            self._post_settings['color'] = el.attr("class").replace("wizard-color ","");
        },
        selectColorPicker2: function(evt) {
            var self = this,
                el = $(evt.target);
            self.el.find('#colorpicker2 span[name="picked-color"]').attr("class",el.attr("class"));
            self.el.find('.wizard-preview').css("background-color",el.css("background-color"));
            self._post_settings['background-color-code'] = el.css("background-color");
            self._post_settings['background-color'] = el.attr("class").replace("wizard-color ","");
        },
        selectItalic: function(evt){
            var self = this,
                el = $(evt.target);
            if(el.get(0).tagName.toUpperCase() !== 'A')
                el = el.parents('a');
            if (el.hasClass("active")) {
                self.el.find('.wizard-preview').css("font-style","normal");
                self._post_settings['font-italic'] = false;
            }
            else {
                self.el.find('.wizard-preview').css("font-style","italic");
                self._post_settings['font-italic'] = true;
            }            
        },
        selectUnderline: function(evt){
            var self = this,
                el = $(evt.target);
            if(el.get(0).tagName.toUpperCase() !== 'A')
                el = el.parents('a');
            if (el.hasClass("active")) {
                self.el.find('.wizard-preview').css("text-decoration","none");
                self._post_settings['font-underline'] = false;
            }
            else {
                self.el.find('.wizard-preview').css("text-decoration","underline");
                self._post_settings['font-underline'] = true;
            }            
        },
        selectAlign:  function(evt){
            var self = this,
                el = $(evt.target);
            if(el.get(0).tagName.toUpperCase() !== 'A')
                el = el.parents('a');
            if (el.hasClass("active")) {
                self.el.find('.wizard-preview').css("text-align","none");
                self._post_settings['font-align'] = 'none';
            }
            else {
                self.el.find('.wizard-preview').css("text-align",el.attr("align"));
                self._post_settings['font-align'] =el.attr("align");
            }            
        },
        selectBold: function(evt) {
            var self = this,
                el = $(evt.target);
            if(el.get(0).tagName.toUpperCase() !== 'A')
                el = el.parents('a');
            if (el.hasClass("active")) {
                self.el.find('.wizard-preview').css("font-weight","normal");
                self._post_settings['font-bold'] =false ;
            } 
            else {
                self.el.find('.wizard-preview').css("font-weight","bold");
                self._post_settings['font-bold'] = true;
            }
        },
        selectFontFamily: function(evt) {
            var self = this;
            switch($(evt.target).val()) {
                case '1' : self.el.find('.wizard-preview').css("font-family","Arial, Helvetica, sans-serif"); break;
                case '2' : self.el.find('.wizard-preview').css("font-family","Times New Roman, Times, serif"); break;
                case '3' : self.el.find('.wizard-preview').css("font-family","Courier New, Courier, monospace"); break;
                case '4' : self.el.find('.wizard-preview').css("font-family","Verdana, Arial, Helvetica, sans-serif"); break;
            }
            self._post_settings['font-family'] = $(evt.target).val();            
        },
        selectFontSize: function(evt) {
            var self = this,
                size = $(evt.target).val();
            var l_height = parseInt($(evt.target).val()) + 5;
            self.el.find('.wizard-preview').css({'font-size' : size+'px', 'line-height' : l_height+'px'});
            self._post_settings['font-size'] = size;            
        },
        previousStep: function(evt) {
            var self = this,
                previous_step = parseInt($(evt.target).parents().eq(1).attr("screenid"))-1;
            self.switchModal(evt, previous_step);
        },
        nextStep: function(evt) {
            var self = this,
                next_step  = parseInt($(evt.target).parents().eq(1).attr("screenid"))+1;
            if(self._currentStep === 0) {
                var current_screen = self.el.find('div.modalscreen[screenid="'+self._currentStep+'"]');
                name = current_screen.find('input[name="post-name"]').val();
                if($.trim(name) === '' ) {
                    return false;
                } 
            }
            self.switchModal(evt, next_step );
        },
        wizardStart: function(evt) {
            var self = this;
            self.switchModal(evt, 0);
            self._currentStep = 0;            
        },
        switchModal: function(evt, id){
            var self = this;
            //getting and saving data from current screen
            var current_screen = self.el.find('div.modalscreen[screenid="'+self._currentStep+'"]');
            switch(self._currentStep) {
              case 1: 
                self._post_settings['name']=current_screen.find('input[name="post-name"]').val();  
                break;
              case 2: 
                self._post_settings['predefinedContent']=current_screen.find('[name="post-predefined"]').val();
                self.el.find('.wizard-preview').html(current_screen.find('[name="post-predefined"]').val());
                break;
            }
            current_screen.css("display","none");

            if (self._currentStep != 0) {
              for(var i=1; i<5;i++) {
                var step_element  = self.el.find('div.modalscreen[screenid="'+i+'"] .wizard ul li').eq(self._currentStep-1);
                step_element.attr("class","back-step"); 
                step_element.click(function(){
                  var step = parseInt($(this).html());
                  self.switchModal(evt, step);
                }); 
              }
            }
            self.el.find('div.modalscreen[screenid="'+id+'"]').css("display","block");
            if (id != 0) {
              self.el.find('div.modalscreen[screenid="'+id+'"] .wizard ul li').eq(id-1).attr("class","current-step");
            }
            self._currentStep = id;

        }
    });
});