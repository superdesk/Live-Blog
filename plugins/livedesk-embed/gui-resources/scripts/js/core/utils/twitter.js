define(function(){ 
	var twitter = {
		link: {
			anchor: function(str) 
			{
			  return str.replace(/[äéöüßÄÖÜA-Za-z]+:\/\/[äéöüßÄÖÜA-Za-z0-9-_]+\.[äéöüßÄÖÜA-Za-z0-9-_:%&\?\/.=]+/g, function(m) 
			  {
				m = m.link(m);
				m = m.replace('href="','target="_blanka" href="');
				return m;
			  });
			},
			user: function(str) 
			{
			  return str.replace(/[@]+[äéöüßÄÖÜA-Za-z0-9-_]+/g, function(us) 
			  {
				var username = us.replace("@","");
				
				us = us.link("http://twitter.com/"+username);
				us = us.replace('href="','target="_blankb" onclick="loadProfile(\''+username+'\');return(false);"  href="');
				return us;
			  });
			},
			tag: function(str) 
			{
			  return str.replace(/[#]+[äéöüßÄÖÜA-Za-z0-9-_]+/g, function(t) 
			  {
				var tag = t.replace("#","%23");
				t = t.link("http://twitter.com/search?q="+tag);
				t = t.replace('href="','target="_blank" href="');
				return t;
			  });
			},
			all: function(str)
			{
				str = this.anchor(str);
				str = this.user(str);
				str = this.tag(str);
				return str;
			}
		}
	};
	return twitter;
});