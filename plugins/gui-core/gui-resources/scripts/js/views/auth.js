define
([
    'jquery', 'jquery/superdesk', 'dust/core', 'jquery/tmpl', 'jquery/rest', 'bootstrap',  
    'tmpl!auth',
], 
function($, superdesk, dust)
{
    var AuthApp = 
    {
        success: $.noop,
        require: function()
        {
            var self = this; // rest
            $.tmpl('auth', null, function(e, o)
            { 
                var dialog = $(o).eq(0).dialog
                ({ 
                    draggable: false,
                    resizable: false,
                    modal: true,
                    width: "40.1709%",
                    buttons: 
                    [
                         { text: "Login", click: function(){ $(form).trigger('submit'); }, class: "btn btn-primary"},
                         { text: "Close", click: function(){ $(this).dialog('close'); }, class: "btn"}
                    ]
                }),
                    form = dialog.find('form');
                form.off('submit.superdesk')
                .on('submit.superdesk', function(event)
                {
                    var username = $(this).find('#username').val(),
                        form = this;
                    new $.rest('Superdesk/User').xfilter('Name,Id').done(function(users)
                    {
                        var found = false;
                        for(var i=0; i<users.length; i++)
                        {
                            if(users[i].Name == username) 
                            { 
                                found = users[i].Id;
                                $.restAuth.prototype.requestOptions.headers.Authorization = users[i].Id;
                                superdesk.login = users[i];
                                if($(form).find('#remember:checked').length)
                                {
                                    localStorage.setItem('superdesk.login.id', users[i].Id);
                                    localStorage.setItem('superdesk.login.name', users[i].Name);
                                }
                                AuthApp.success && AuthApp.success.apply();
                                dialog.dialog('close');
                                break;
                            }
                        };
                        !found && dialog.find('#login-failed').removeClass('hide');
                    });
                    event.preventDefault();
                });
            });
        }
    };
    return AuthApp;
});