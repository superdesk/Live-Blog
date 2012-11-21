define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'models/meta-info'),
    'tmpl!media-archive>types/_default/menu', // list/grid item context menu
    'tmpl!media-archive>types/_default/view',
    'tmpl!media-archive>types/_default/edit'
],
function($, superdesk, giz, MetaInfo)
{
    var 
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
            this.model.on('full-refresh', this.render, this);
            var self = this;
            $(this.el).modal({show: false});
            $(this.el).on('hide', function(){ self.modalState = false; });
            $(this.el).on('show', function(){ self.modalState = true; });
        },
        refresh: function()
        {
            /*!
             * @see media-archive/models/meta-data 
             */
            this.model.refresh();
            return this;
        },
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
            $(this.el).tmpl(this.tmpl, this.feedTemplate());
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
        tmpl: 'media-archive>types/_default/edit',
        events:
        {
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
            return !this.editView ? (this.editView = new (this.editClass)({ model: this.model})) : this.editView;
        },
        /*!
         * show "edit" modal
         * doing a trick to reuse the view element for edit if open
         */
        edit: function()
        {
            var e = this.getEdit(),
                v = this.getViewDetails();
            v.modalState && e.setElement(v.el);
            e.refresh();
            !v.modalState && e.activate(); 
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
                return data.Thumbnail && data.Thumbnail.href ? '<img src="'+data.Thumbnail.href+'" />' : ''
            }
            $(this.el).tmpl(this.tmpl, {Item: data}).prop('model', this.model).prop('view', this);
            
            return this;
        }
    });
    
    return {item: ItemView, view: ViewDetails, edit: Edit};
});

