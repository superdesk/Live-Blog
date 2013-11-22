define(['gizmo/superdesk', 'utils/sha512'], 
function(Gizmo, jsSHA)
{
    return Gizmo.Model.extend
    ({ 
        //url: new Gizmo.Url('Security/Authentication/Login'),
        url: new Gizmo.Url('Security/Login'),
        authenticate: function(username, password, loginToken)
        {
            // build data for login
            var shaUser = new jsSHA(username, "ASCII"),
                shaPassword = new jsSHA(password, "ASCII"),         
                shaStep1 = new jsSHA(shaPassword.getHash("SHA-512", "HEX"), "ASCII"),
                shaStep2 = new jsSHA(loginToken, "ASCII"),      
                HashedToken = shaStep1.getHMAC(username, "ASCII", "SHA-512", "HEX");            
                HashedToken = shaStep2.getHMAC(HashedToken, "ASCII", "SHA-512", "HEX");
                
            return this.set({ UserName: username, Token: loginToken, HashedToken: HashedToken })
                .xfilter('User.Name, User.Id, User.EMail')
                .sync();
        }
    });
});