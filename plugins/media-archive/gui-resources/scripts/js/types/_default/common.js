define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'models/meta-info'),
    config.guiJs('media-archive', 'models/languages'),
    'tmpl!media-archive>types/_default/menu', // list/grid item context menu
    'tmpl!media-archive>types/_default/view',
    'tmpl!media-archive>types/_default/edit',
    'tmpl!media-archive>types/_default/languages'
],
function($, superdesk, giz, MetaInfo, Languages)
{
    var 
    /*!
     * edit box for languages
     */
    LanguagesEditView = giz.View.extend
    ({
        tagName: 'span',
        init: function()
        {
            this.collection = new Languages();
            this.collection.on('read update', this.render, this);
            this.collection.xfilter('Id, Name').sync();
        },
        render: function(selected)
        {
            var data = {Languages: this.collection.feed()};
            // select if we have any value
            if(selected) data.selected = function(chk, ctx){ return ctx.current().Id == selected ? "selected='selected'" : ""; }
            this.el && $(this.el).tmpl('media-archive>types/_default/languages', data);
            return this;
        }
    }),
    /*!
     * the instance
     * we're using this to generate the same tpl for language editing
     */
    LangEditView = new LanguagesEditView,
    /*!
     * view item view
     */
    ViewDetails = giz.View.extend
    ({
        events:
        {
            '[data-dismiss="modal"]': { 'click' : 'hide' },
            '[data-action="edit"]': { 'click': 'edit' }
        },
        edit: function()
        {
            this.parentView.edit.call(this.parentView);
        },
        modalState: false,
        init: function()
        {
            this.getModel().on('full-refresh', this.render, this);
            var self = this;
            $(this.el).modal({show: false});
            $(this.el).on('hide', function(){ self.modalState = false; });
            $(this.el).on('show', function(){ self.modalState = true; });
        },
        /*!
         * adds possibillity to overwrite the model
         */
        getModel: function()
        {
            return this.model;
        },
        refresh: function()
        {
            /*!
             * @see media-archive/models/meta-data 
             */
            this.model.refresh();
            return this;
        },
        /*!
         * build data for template
         */
        feedTemplate: function()
        {
            var data = this.model.feed(true);
            // calculate human readable size
            data.SizeInBytes = parseInt(data.SizeInBytes);
            var sizes = [ _('n/a'), _('Bytes'), _('KB'), _('MB'), _('GB'), _('TB'), _('PB'), _('EB'), _('ZB'), _('YB')],
                i = +Math.floor(Math.log(data.SizeInBytes) / Math.log(1024));
            data.Size = (data.SizeInBytes / Math.pow(1024, i)).toFixed( i ? 2 : 0 ) + ' ' + sizes[ isNaN( data.SizeInBytes ) ? 0 : i+1 ];
            
            return {Item: data};
        },
        tmpl: 'media-archive>types/_default/view',
        render: function()
        {
            var self = this,
                data = this.feedTemplate();
            // get language box 
            data.Languages = LangEditView.render().el.clone().html();
            // get language box for each meta
            for(var i=0; i<data.Meta.length; i++)
                data.Meta[i].Languages = LangEditView.render(data.Meta.Language).el.clone().html();
            $(this.el).tmpl(this.tmpl, data);
            return this;
        },
        activate: function()
        {
            return $(this.el).modal('show');
        },
        hide: function()
        {
            $(this.el).modal('hide');
        }
    }),
    
    /*!
     * edit item view
     */
    Edit = ViewDetails.extend
    ({
        events:
        {
            '[data-dismiss="modal"]': { 'click' : 'hide' }
        },
        edit: $.noop,
        tmpl: 'media-archive>types/_default/edit',
        init: function()
        {
            this.getModel().on('full-refresh', this.render, this);
            var self = this;
        }
    }),
    
    /*!
     * list item
     */
    ItemView = giz.View.extend
    ({
        events: 
        {
            '[data-action="view"]': { 'click': 'viewDetails' },
            '[data-action="edit"]': { 'click': 'edit' },
            '[data-action="download"]': { 'click': 'download' },
            '[data-action="delete"]': { 'click': 'remove' }
        },
        
        // view modal
        
        viewClass: ViewDetails,
        viewDetailsView: false, // the instance
        getViewDetails: function()
        {
            return !this.viewDetailsView ? (this.viewDetailsView = new (this.viewClass)({ model: this.model, parentView: this})) : this.viewDetailsView;
        },
        /*!
         * show "view details" modal
         */
        viewDetails: function()
        {
            this.getViewDetails().refresh().activate();
        },
        
        // edit modal
        
        editClass: Edit,
        editView: false, // the instance
        getEdit: function()
        {
            return !this.editView ? (this.editView = new (this.editClass)({ model: this.model })) : this.editView;
        },
        /*!
         * show "edit" modal
         * doing a trick to reuse the view element if open for edit 
         */
        edit: function()
        {
            var e = this.getEdit(),
                v = this.viewDetailsView;
            (v && v.modalState) && e.setElement(v.el);
            e.refresh();
            (!v || !v.modalState) && e.activate(); 
        },
        
        download: function(){},
        
        remove: function()
        {
            this.model.remove().sync();
        },
        
        model: null,
        tagName: 'div',
        
        render: function()
        {
            var self = this,
                data = this.model.feed();
            data.Content = function(chk, ctx)
            {
                return data.Thumbnail && data.Thumbnail.href ? '<img src="'+data.Thumbnail.href+'" />' : '';
            };
            $(this.el).tmpl(this.tmpl, {Item: data}).prop('model', this.model).prop('view', this);
            
            return this;
        }
    });
    
    return {item: ItemView, view: ViewDetails, edit: Edit, languages: LangEditView};
});

