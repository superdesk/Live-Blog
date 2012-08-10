define
([
    'jquery', 'jquery/superdesk', 'dust/core', 'utils/sha512', 'jquery/tmpl', 'jquery/rest', 'bootstrap',  
    'tmpl!auth',
], 
function($, superdesk, dust, jsSHA)
{
    var AuthDetails = function(username){
		var authDetails = new $.rest('Superdesk/User');
		authDetails.resetData().xfilter('Name,Id,EMail').select({ name: username }).done(function(users){
			var user = users.UserList[0];
			localStorage.setItem('superdesk.login.id', user.Id);
			localStorage.setItem('superdesk.login.name', user.Name);
			localStorage.setItem('superdesk.login.email', user.EMail);
		});
		return $(authDetails);
	},
	AuthLogin = function(username, password, token){
		var shaObj = new jsSHA(token, "ASCII"),
			authLogin = new $.rest('Authentication');
		authLogin.resetData().select({ 
			userName: username, 
			loginToken: token, 
			hashedLoginToken: shaObj.getHMAC(username+password, "ASCII", "SHA-512", "HEX")
		}).done(function(data){
			localStorage.setItem('superdesk.login.token', data);
			authDetails = AuthDetails(username);
			$(authDetails).on('failed', function(){
				$(authLogin).trigger('failed', 'authDetails');
			});
			
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
				});
			}
		);
		return $(authToken);
	},
	AuthApp = 
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
                form.off('submit.superdesk')//
                .on('submit.superdesk', function(event)
                {
                    var username = $(this).find('#username').val(), password=$(this).find('#password').val();
					AuthToken(username, password).on('failed',function(evt, type){						
						console.log(type);
					});
                    event.preventDefault();
					
                });
            });
        }
    };
    return AuthApp;
});