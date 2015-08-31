define('providers', function(){
  window.fbAsyncInit = function() {
    window.FB.init({
      xfbml: true,
      version: 'v2.2'
    });
  };
	return {};
});