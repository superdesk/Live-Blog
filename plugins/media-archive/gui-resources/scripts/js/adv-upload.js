define
([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('media-archive', 'list'),
    config.guiJs('media-archive', 'models/meta-data-info'),
    config.guiJs('media-archive', 'models/meta-data'),
    'tmpl!media-archive>adv-upload/main',
    'tmpl!media-archive>adv-upload/archive-list',
    'tmpl!media-archive>adv-upload/archive-list-item',
    'tmpl!media-archive>adv-upload/archive-filter'
], 
function($, gizmo, MA, MetaDataInfo, MetaData)
{
    'use strict';

    /*!
     * upload one file to server
     * @param {object} file The object to append to FormData (form.files[i])
     * @param {string} filename The key of the file in post data
     * @param {string} path Server path to upload to
     * @param {function} startCb Callback for upload start, falls back to format if string and !format 
     */
    function upload(file, filename, path, startCb)
    {
        var delay = new $.Deferred();
        var fd = new FormData();
        var format = typeof startCb == 'string' && !format ? startCb : (format ? format : 'json');
        fd.append(filename || 'upload_file', file);
        var xhr = new XMLHttpRequest();
        // replace or add format we want as response in url // path = path.search(/(((\..+)?\?))/) != -1 ? path.replace(/(((\..+)?\?))/,'.xml?') : path+'.xml';
        xhr.open('POST', (path+' ').replace(/(((\.[\w\d-]+)?\?)|(\s$))/,'.'+format+'$1'), true);
        xhr.setRequestHeader('X-Filter', 'Content');
        startCb && startCb.apply(this);
        xhr.send(fd);

        xhr.onload = function(event) {
            var data = $.parseJSON(event.target.responseText);
            delay.resolve(data);
        };

        return delay.promise();
    }

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
            if( $(evt.currentTarget.parentNode).hasClass("grid-selected") == true ) 
            {
                $(evt.currentTarget.parentNode).removeClass("grid-selected");
                $(evt.currentTarget).find("i").attr("class","icon-plus icon-white");
            }
            else 
            {
                $(evt.currentTarget.parentNode).addClass("grid-selected");
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
            var meta = model.getMetaData(),
                self = this;
            meta.sync({data: {thumbSize: this.thumbSize}}).done(function(){ $(self).triggerHandler('register-item', [meta]); });
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
        uploadComplete: function(data)
        {
            var content = data.Thumbnail;
            var id = data.Id;

            var img = new Image,
                self = this; 
            img.src = content.href;

            img.onload = function()
            {
                $('form', self.el).addClass('hide');
                $('[data-placeholder="preview-area"]', self.el).removeClass('hide');
                $('[data-placeholder="preview"]', self.el).html(img); 
            };

            img.onerror = function(){  };
            
            var meta = new MetaData(MetaData.prototype.url.get()+'/'+id);
            meta.sync({data: {thumbSize: 'large'}}).done(function()
            { 
                self.lastUpload = meta.get('Id');
                self.registerItem(null, meta);
            });
        },
        cancelUpload: function()
        {
            $('form', this.el).removeClass('hide');
            $('[data-placeholder="preview-area"]', this.el).addClass('hide');
            $('[data-placeholder="preview"]', this.el).html('');
            this.removeImageById(this.lastUpload);
        },
        /*!
         * triggers file input
         */
        proxyBrowse: function()
        {
            $('[data-action="browse"]', this.el).trigger('click');
        },

        findImageById: function(id) {
            for (var i = 0; i < this.returnImageList.length; i++) {
                if (this.returnImageList[i].data.Id === id) {
                    return i;
                }
            }
        },

        removeImageByPos: function(pos) {
            this.returnImageList.splice(pos, 0);
        },

        removeImageById: function(id) {
            var pos = this.findImageById(id);
            if (pos !== undefined) {
                this.removeImageByPos(pos);
            }
        },
        
        returnImageList: [],
        registerItem: function(evt, model)
        {
            var pos = this.findImageById(model.data.Id);
            if (pos !== undefined) {
                this.removeImageByPos(pos);
            } else {
                this.returnImageList.push(model);
            }
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
            var self = this;
            upload(
                $('[data-action="browse"]', self.el)[0].files[0],
                'upload_file',
                this.getUploadEndpoint(),
                self.uploadingDisplay
            ).then(function(data) {
                $('[data-action="browse"]').val('');
                self.uploadComplete(data);
            });
        },
        complete: function()
        {
            this.delay.resolve(this.returnImageList);
        },
        /*!
         * init -> renders
         * @param {Object} options Options for add image popup.
         *
         *   Available options:
         *
         *   - showArchive - {Boolean} - Show archive for selecting existing image.
         */
        init: function(options)
        {
            var self = this;
                this.listView = new ListView({thumbSize: this.thumbSize});
            $(this.listView).on('register-item', function(){ self.registerItem.apply(self, arguments); });
            this.listView._parent = this;
            this.render($.extend({showArchive: true}, options));
        },
        /*!
         * activates
         */
        activate: function()
        {
            this.delay = $.Deferred();
            this.cancelUpload();
            this.returnImageList = [];
            this.listView.activate();
            $(this.el).addClass('modal hide fade responsive-popup').modal();
            return this.delay.promise();
        },
        /*!
         * renders stuff
         */
        render: function(options)
        {
            var self = this;
            $(self.el).tmpl('media-archive>adv-upload/main', options, function()
            {
                self.listView.renderPlaceholder = $('[data-placeholder="media-archive"]', self.el);
                self.listView.itemsPlaceholder = '[data-placeholder="media-archive-items"]';
            });
        },
        getUploadEndpoint: function()
        {
            return $.superdesk.apiUrl+'/resources/my/HR/User/'+localStorage.getItem('superdesk.login.id')+'/MetaData/Upload?thumbSize='+(this.thumbSize||'large')+'&X-Filter=*&Authorization='+ localStorage.getItem('superdesk.login.session');
        }
    });
    
    return UploadView;
});