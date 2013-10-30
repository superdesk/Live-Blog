define
([
    'jquery', 'jquery/superdesk', 'gizmo/superdesk', 
    'gizmo/superdesk/action', 'utils/sha512',
    'gizmo/superdesk/models/auth-token',
    'gizmo/superdesk/models/auth-login',
    'jquery/tmpl', 'jquery/rest', 'bootstrap',
    'tmpl!auth', 'tmpl!auth-page' 
],
function($, superdesk, gizmo, Action, jsSHA, AuthToken, AuthLogin)
{
    var 
    /*!
     * performs login
     */
    AuthLoginApp = function(username, password, loginToken)
    {
        var shaUser = new jsSHA(username, "ASCII"),
            shaPassword = new jsSHA(password, "ASCII"),         
            shaStep1 = new jsSHA(shaPassword.getHash("SHA-512", "HEX"), "ASCII"),
            shaStep2 = new jsSHA(loginToken, "ASCII"),          
            authLogin = new $.rest('Security/Authentication/Login').xfilter('User.Name,User.Id,User.EMail'),
            
            HashedToken = shaStep1.getHMAC(username, "ASCII", "SHA-512", "HEX");            
            HashedToken = shaStep2.getHMAC(HashedToken, "ASCII", "SHA-512", "HEX");
            
        authLogin.resetData().insert
        ({
            UserName: username,
            Token: loginToken, 
            HashedToken: HashedToken
        })
        .done(function(data)
        {
            var user = data.User;
            
            // h4xx to set login href.. used in menu to get actions path
            localStorage.setItem('superdesk.login.selfHref', (data.User.href.indexOf('my/') === -1 ? data.User.href.replace('resources/','resources/my/') : data.User.href) );
            // /h4axx
            
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
    AuthTokenApp = 
    {
        get: function(username, password) 
        {
            // new token model
            var authToken = new AuthToken,
                self = this;
            authToken.set({ userName: username }).sync()
            .done(function(data)
            {
                // attempt login after we got token
                authLogin = new AuthLogin;
                authLogin.authenticate(username, password, data.Token)
                .done(function(data)
                {
                    var user = data.User;
                    localStorage.setItem('superdesk.login.selfHref', (data.User.href.indexOf('my/') === -1 ? data.User.href.replace('resources/','resources/my/') : data.User.href) );
                    
                    localStorage.setItem('superdesk.login.session', data.Session);
                    localStorage.setItem('superdesk.login.id', user.Id);
                    localStorage.setItem('superdesk.login.name', user.Name);
                    localStorage.setItem('superdesk.login.email', user.EMail);
                    
                    $.restAuth.prototype.requestOptions.headers.Authorization = localStorage.getItem('superdesk.login.session');
                    
                    $.extend(true, Action.actions.syncAdapter.options.headers, {'Authorization': localStorage.getItem('superdesk.login.session')});
                    
                    superdesk.login = {Id: localStorage.getItem('superdesk.login.id'), Name: localStorage.getItem('superdesk.login.name'), EMail: localStorage.getItem('superdesk.login.email')}
                    $(authLogin).trigger('success');
                })
                .fail(function(data)
                {
                    //if ( data.status == 400) {
                        $(self).triggerHandler('dashfailed', 'authToken');
                    //}
                });
                authLogin.on('failed', function()
                {
                    $(self).triggerHandler('failed', 'authToken');
                })
                .on('success', function()
                {
                    $(self).triggerHandler('success');
                });
            });
            return self;
        }
    },
    
    AuthApp = gizmo.View.extend
    ({
        events:
        {
            'form': { 'submit': 'login' },
            '.login-popup': { 'submit': 'login' }
        },
        /*!
         * login state
         */
        _loggedIn: false,
        /*!
         * set login if storage item exists
         */
        init: function()
        {
            if( localStorage.getItem('superdesk.login.session') )
            {
                this._loggedIn = true;
                // rev compat
                superdesk.login = {Id: localStorage.getItem('superdesk.login.id'), Name: localStorage.getItem('superdesk.login.name'), EMail: localStorage.getItem('superdesk.login.email')}
            }
            
            var self = this;
            $(document).on('submit', '.login-popup', function(evt){ self.login(evt, $('.login-popup')); });
            
            $(AuthTokenApp)
            .on('failed', function(evt, type)
            {
                password.val('');
                username.focus();
                // show error message
                alertmsg.removeClass('hide');
                self._loggedIn = false;
                // trigger login-failed event
                $(self).triggerHandler('login-failed');
            })
            .on('dashfailed', function(evt, type, el)
            {
                 self.alertmsg.removeClass('hide');
            })
            .on('success', function(evt)
            { 
                self.password.val('');
                self.loginerr.addClass('hide');
                // close auth dialog if any 
                $(self._dialog).dialog('close');
                self._loggedIn = true;
                // trigger login event
                $(self).triggerHandler('login');
            });
        },
        /*!
         * perform authentication
         */
        login: function(event, el)
        {
            var el = el || this.el,
                username = $(el).find('#username'), 
                password = $(el).find('#password'),
                alertmsg = $(el).find('.alert'),
                self = this;
            this.alertmsg = alertmsg;
            self._loggedIn = false;
            // make new authentication process
            AuthTokenApp.get(username.val(), password.val());
            event.preventDefault();

            this.password = password;
            this.loginerr = $(el).find('#login-failed-msg');
        },
        /*!
         * remove authentication
         */
        logout: function()
        {
            // delete local storage items
            localStorage.removeItem('superdesk.login.selfHref');
            localStorage.removeItem('superdesk.login.session');
            localStorage.removeItem('superdesk.login.id');
            localStorage.removeItem('superdesk.login.name');
            localStorage.removeItem('superdesk.login.email');
            
            // TODO these souldn't be here 
            delete $.restAuth.prototype.requestOptions.headers.Authorization;
            delete Action.actions.syncAdapter.options.headers.Authorization;
            delete superdesk.login;
            // ---
            
            // trigger logout handler
            $(this).triggerHandler('logout');
        },
        
        /*!
         * render the login page
         */
        render: function()
        {
            var self = this;
            if( self._loggedIn ) 
            {
                $(self).triggerHandler('login');
                return this;
            }
            // display authentication page
            $.tmpl('auth-page', {}, function(e, o){ self.el.html(o); });
            return this;
        },
        /*!
         * login popup element
         */
        _dialog: null,
        /*!
         * render and show login dialog
         */
        renderPopup: function(msg)
        {
            var self = this,
                data = this.loginExpired ? {'expired': true} : {}; // rest
            if( msg ) data.error = msg;

            // return if dialog showing
            if( $(this._dialog).is(':visible') ) return;
            // render template
            (!this._dialog || !this._dialog.length) && $.tmpl('auth', data, function(e, o)
            { 
                self._dialog = $(o);
                self._dialog.dialog
                ({ 
                    draggable: false,
                    resizable: false,
                    modal: true,
                    width: "40.1709%",
                    buttons: 
                    [
                         { text: "Login", click: function(){ $(this).find('form:eq(0)').trigger('submit'); }, class: "btn btn-primary"},
                         { text: "Close", click: function(){ $(this).dialog('close'); }, class: "btn"}
                    ]
                });
            });
            this._dialog.length && this._dialog.dialog('open');
        }
    });
    
    return new AuthApp;
});
