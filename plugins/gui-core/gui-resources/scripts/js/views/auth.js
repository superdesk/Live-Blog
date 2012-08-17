define
([
    'jquery', 'jquery/superdesk', 'dust/core', 'utils/sha512', 'jquery/tmpl', 'jquery/rest', 'bootstrap',  
    'tmpl!auth',
], 
function($, superdesk, dust, jsSHA)
{
    var AuthLogin = function(username, password, logintoken){
		var shaObj = new jsSHA(logintoken, "ASCII"),shaPassword = new jsSHA(password, "ASCII"),
			authLogin = new $.rest('Authentication');
			authLogin.resetData().insert({ 
			UserName: username, 
			LoginToken: logintoken, 
			HashedLoginToken: shaObj.getHMAC(username+shaPassword.getHash("SHA-512", "HEX"), "ASCII", "SHA-512", "HEX")
		}).done(function(user){
			localStorage.setItem('superdesk.login.session', user.Session);
			localStorage.setItem('superdesk.login.id', user.Id);
			localStorage.setItem('superdesk.login.name', user.UserName);
			localStorage.setItem('superdesk.login.email', user.EMail);			
			$(authLogin).trigger('success');
		});
		return $(authLogin);
	},
	AuthToken = function(username, password) {
		var authToken = new $.rest('Authentication');
		authToken.resetData().select({ userName: username }).done(
			function(data){
				authLogin = AuthLogin(username, password, data.Token);
				authLogin.on('failed', function(){
					$(authToken).trigger('failed', 'authToken');
				}).on('success', function(){
					$(authToken).trigger('success');
				});
			}
		);
		return $(authToken);
	},
	AuthApp = 
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
            var self = this; // rest
			AuthApp.showed = true;			
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
                    var username = $(this).find('#username'), password=$(this).find('#password');
					AuthToken(username.val(), password.val()).on('failed',function(evt, type){						
						username.val('');
						password.val('')
					}).on('success', function(){
                        AuthApp.success && AuthApp.success.apply();
						$(dialog).dialog('close');
						self.showed = false;
					});
                    event.preventDefault();
					
                });
            });
        }
    };
    return AuthApp;
});