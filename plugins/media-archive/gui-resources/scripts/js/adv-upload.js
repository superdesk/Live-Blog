define
([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('media-archive', 'upload'),
    config.guiJs('media-archive', 'list'),
    config.guiJs('media-archive', 'models/meta-data-info'),
    config.guiJs('media-archive', 'models/meta-data'),
    'tmpl!media-archive>adv-upload/main',
    'tmpl!media-archive>adv-upload/archive-list',
    'tmpl!media-archive>adv-upload/archive-list-item',
    'tmpl!media-archive>adv-upload/archive-filter'
], 
function($, gizmo, UploadCom, MA, MetaDataInfo, MetaData)
{
    var 
    FilterView = gizmo.View.extend
    ({
        tagName: 'span',
        events: { '[name="search"]': { 'keypress': 'key2Search' } },
        init: function(){ this.render(); },
        render: function()
        {
            var self = this; 
            $(this.el).tmpl('media-archive>adv-upload/archive-filter');
        },
        placeInView: function(el)
        {
            el.append(this.el);
        },
        getSearch: function()
        {   
            return [{'all.inc': $('[name="search"]', this.el).val() }];
        },
        key2Search: function(evt)
        {
            switch(evt.keyCode)
            {
                case 27: $('[name="search"]', this.el).val('');
                case 13: 
                    $(this).triggerHandler('trigger-search'); 
                    evt.preventDefault();
                break;
            }
        }
    }),
    // use custom item template
    ItemView = MA.ItemView.extend
    ({ 
        tmpl: 'media-archive>adv-upload/archive-list-item',
        events: 
        {
            '.add-button': { 'click': 'selectSelf' }
        },
        tagName: 'li',
        selectSelf: function(evt)
        {
            if( $(evt.currentTarget).hasClass("grid-selected") == true ) 
            {
                $(evt.currentTarget).removeClass("grid-selected");
                $(evt.currentTarget).find("i").attr("class","icon-plus icon-white");
            }
            else 
            {
                $(evt.currentTarget).addClass("grid-selected");
                $(evt.currentTarget).find("i").attr("class","icon-minus icon-white");
            }
            $(this).triggerHandler('selected', [this.model]);
        }
    }),
    // use custom template and the above declared item view
    // new method to get generic item view
    ListView = MA.ListView.extend
    ({ 
        tmpl: 'media-archive>adv-upload/archive-list',
        /*!
         * 
         */
        getItemView: function(model)
        {
            var self = this,
                iview = new ItemView({ model: model, parent: this });
            $(iview).on('selected', function(){ self.registerItem.apply(self, arguments); });
            iview.render();
            return iview.el;
        },
        /*!
         * 
         */
        getFilterView: function()
        {
            return new FilterView;
        },
        /*!
         * 
         */
        renderCallback: function()
        {
            this.filterView.placeInView($('[data-placeholder="media-archive-filter"]', this._parent.el));
        },
        /*!
         * 
         */
        registerItem: function(evt, model)
        {
            $(this).triggerHandler('register-item', [model.getMetaData()]);
        }
    }),
    
    /*!
     * main upload view
     */
    UploadView = gizmo.View.extend
    ({
        events: 
        {
            "[data-action='browse']": { 'change': 'upload' },
            "[data-action='cancel-upload']": { 'click': 'cancelUpload' },
            "[data-proxy='browse']": { 'click': 'proxyBrowse' },
            "[data-action='complete']": { 'click': 'complete' },
            ".modal-pane-menu li a": { 'click': 'switchTabs' }
        },
        switchTabs: function(evt)
        {
            var sc_id = $(evt.currentTarget).attr("screen-id");
            $(".uploadimage-screen", this.el).addClass('hide');
            $('.uploadimage-screen[screen-id="' + sc_id  +'"]', this.el).removeClass('hide');
            $(".modal-pane-menu li", this.el).removeClass("activelink");
            $(evt.currentTarget).parent().addClass("activelink");
        },
        /*!
         * handler for what to display during the upload
         */
        uploadingDisplay: function()
        { 
            
        },
        /*!
         * handler on upload complete
         */
        uploadComplete: function(event)
        {
            var content = false;
            // either get it from the responseXML or responseText
            try
            { 
                var xml = $(event.target.responseXML.firstChild),
                    content = xml.find('Thumbnail');
                    id = $('>Id', xml).get(0).text();
            }
            catch(e){ 
                var txt = $(event.target.responseText),
                    content = txt.find('thumbnail'),
                    id = txt.find('Id:eq(0)').text();
            }
            if(!content) return;
            var img = new Image,
                self = this; 
            img.src = content.attr('href');
            img.onload = function()
            {
                $('form', self.el).addClass('hide');
                $('[data-placeholder="preview-area"]', self.el).removeClass('hide');
                $('[data-placeholder="preview"]', self.el).html(img); 
            };
            img.onerror = function(){  };
            
            var meta = new MetaData(MetaData.prototype.url.get()+'/'+id);
            meta.sync().done(function()
            { 
                self.lastUpload = meta.get('Id');
                self.registerItem(null, meta);
            });
        },
        cancelUpload: function()
        {
            $('form', self.el).removeClass('hide');
            $('[data-placeholder="preview-area"]', self.el).addClass('hide');
            $('[data-placeholder="preview"]', self.el).html('');
            delete this.returnImageList[this.lastUpload];
        },
        /*!
         * triggers file input
         */
        proxyBrowse: function()
        {
            $('[data-action="browse"]', this.el).trigger('click');
        },
        
        returnImageList: {},
        registerItem: function(evt, model)
        {
            var id = model.get('Id'), itm = this.returnImageList[id];
            if( itm ) delete this.returnImageList[id];
            else this.returnImageList[id] = model;
        },
        getRegisteredItems: function()
        {
            return this.returnImageList;
        },
        
        /*!
         * performs upload
         */
        upload: function()
        {
            var self = this,
                xhr = UploadCom.upload( $('[data-action="browse"]', self.el)[0].files[0], 
                        'upload_file', 
                        $("form", self.el).attr('action'), 
                        self.uploadingDisplay );
            xhr.onload = function(){ self.uploadComplete.apply(self, arguments); };
        },
        complete: function()
        {
            $(this).triggerHandler('complete');
        },
        /*!
         * init -> renders
         */
        init: function()
        {
            var self = this;
            this.listView = new ListView,
            $(this.listView).on('register-item', function(){ self.registerItem.apply(self, arguments); });
            this.listView._parent = this;
            this.render();
        },
        /*!
         * activates
         */
        activate: function()
        {
            this.returnImageList = {};
            this.listView.activate();
        },
        /*!
         * renders stuff
         */
        render: function()
        {
            var self = this;
            $(self.el).tmpl('media-archive>adv-upload/main', {UploadAction: self.getUploadEndpoint()}, function()
            {
                self.listView.renderPlaceholder = $('[data-placeholder="media-archive"]', self.el);
                self.listView.itemsPlaceholder = '[data-placeholder="media-archive-items"]';
            });
        },
        getUploadEndpoint: function()
        {
            return $.superdesk.apiUrl+'/resources/my/HR/User/'+localStorage.getItem('superdesk.login.id')+'/MetaData/Upload?thumbSize=large&X-Filter=*&Authorization='+ localStorage.getItem('superdesk.login.session');
        }
    });
    
    return UploadView;
});