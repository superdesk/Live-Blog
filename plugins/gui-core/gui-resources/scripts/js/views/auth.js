define
([
    'jquery', 'jquery/superdesk', 'gizmo/superdesk', 'utils/sha512', 'jquery/tmpl', 'jquery/rest', 'bootstrap',  
    'tmpl!auth',
], 
function($, superdesk, Gizmo, jsSHA)
{
    var AuthLogin = function(username, password, logintoken)
    {
		var 
			shaUser = new jsSHA(username, "ASCII"),
			shaPassword = new jsSHA(password, "ASCII"),			
			shaStep1 = new jsSHA(shaPassword.getHash("SHA-512", "HEX"), "ASCII"),
			shaStep2 = new jsSHA(logintoken, "ASCII"),			
			authLogin = new $.rest('Superdesk/Authentication/Login').xfilter('User.Name,User.Id,User.EMail');
			
			HashedToken = shaStep1.getHMAC(username, "ASCII", "SHA-512", "HEX");			
			HashedToken = shaStep2.getHMAC(HashedToken, "ASCII", "SHA-512", "HEX");
			authLogin.resetData().insert
			({
				UserName: username,
			    Token: logintoken, 
			    HashedToken: HashedToken
			})
			.done(function(data)
			{
				var user = data.User;
			    localStorage.setItem('superdesk.login.session', data.Session);
			    localStorage.setItem('superdesk.login.id', user.Id);
			    localStorage.setItem('superdesk.login.name', user.Name);
			    localStorage.setItem('superdesk.login.email', user.EMail);
			    $.restAuth.prototype.requestOptions.headers.Authorization = localStorage.getItem('superdesk.login.session');
			    superdesk.login = {Id: localStorage.getItem('superdesk.login.id'), Name: localStorage.getItem('superdesk.login.name'), EMail: localStorage.getItem('superdesk.login.email')}
			    $(authLogin).trigger('success');
		});
		return $(authLogin);
	},
	AuthToken = function(username, password) 
	{
	    /*var Authentication = Gizmo.Model.extend({url: new Gizmo.Url}),
	        auth = new Authentication('Authentication');
	    
	    auth.set({ userName: username }).sync();*/
	    
		var authToken = new $.rest('Superdesk/Authentication');
		authToken.resetData().insert({ userName: username })
		.done(function(data)
		{
		    authLogin = AuthLogin(username, password, data.Token);
			authLogin.on('failed', function()
			{
			    $(authToken).trigger('failed', 'authToken');
			})
			.on('success', function()
			{
			    $(authToken).trigger('success');
			});
		});
		return $(authToken);
	},
	AuthApp = 
    {
        success: $.noop,
		showed: false,
        require: function()
        {
			if(AuthApp.showed) return;
            var self = this,
                data = this.loginExpired ? {'expired': true} : {}; // rest
			AuthApp.showed = true;	
            $.tmpl('auth', data, function(e, o)
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
                        ],
                        close: function(){ $(this).remove(); AuthApp.showed = false; }
                    }),
                    form = dialog.find('form');
                
                form.off('submit.superdesk')
                .on('submit.superdesk', function(event)
                {
                    var username = $(this).find('#username'), 
                        password = $(this).find('#password'),
                        alertmsg = $(this).find('.alert');
                    
					AuthToken(username.val(), password.val())
    					.on('failed', function(evt, type)
    					{ 
    					    password.val('');
    					    username.focus();
    					    alertmsg.removeClass('hide');
    					})
    					.on('success', function(evt)
    					{ 
    					    AuthApp.success && AuthApp.success(); 
    					    $(dialog).dialog('close'); 
    					    AuthApp.showed = false; 
    					    $(AuthApp).trigger('authenticated');
    					});
                    event.preventDefault();
					
                });
                
            });
        }
    };
	
    return AuthApp;
});