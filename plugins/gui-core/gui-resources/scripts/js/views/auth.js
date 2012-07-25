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
		return authDetails;
	},
	AuthLogin = function(username, password, token){
		var shaObj = new jsSHA(token, "ASCII"),
			authLogin = new $.rest('Superdesk/Authentication');
		authLogin.resetData().select({ 
			userName: username, 
			loginToken: token, 
			hashedLoginToken: shaObj.getHMAC(username+password, "ASCII", "SHA-512", "HEX")
		}).done(function(data){
			localStorage.setItem('superdesk.login.token', data);
			AuthDetails(username);
		});
		return authLogin;
	},
	AuthToken = function(username, password) {
		var authToken = new $.rest('Superdesk/Authentication');
		authToken.resetData().select({ userName: username }).done(
			function(data){
				AuthLogin(username, password, data.token);
			}
		).always(function(){
			
		});
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
                    var username = $(this).find('#username').val(), password=$(this).find('#password').val(),
					AuthToken(username, password).on('fail',function(){
						console.log('fail');
					});
                    event.preventDefault();
					
                });
            });
        }
    };
    return AuthApp;
});