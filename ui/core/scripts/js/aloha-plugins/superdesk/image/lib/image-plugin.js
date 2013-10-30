define
([
    'aloha/plugin',
    'ui/scopes',
    'ui/ui',
    'ui/button',
    'i18n!aloha/nls/i18n'
], 
function(Plugin, Scopes, Ui, Button, i18n)
{ 
    return Plugin.create('image', 
    {
        init: function()
        {
            Scopes.createScope('name', 'Aloha.empty');

            this._insertImageButton = Ui.adopt("insertImage", Button, 
            {
                tooltip: i18n.t('button.addimg.tooltip'),
                icon: 'aloha-button aloha-image-insert',
                scope: 'Aloha.continuoustext',
                click: this.handleInsert
            });
        },
        handleInsert: $.noop
    });
});