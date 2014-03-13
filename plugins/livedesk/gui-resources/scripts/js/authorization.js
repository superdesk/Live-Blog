define( function(){
	var authObject = {
		'Authorization': localStorage.getItem('superdesk.login.session')
	}
	return authObject;
});