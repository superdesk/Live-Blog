define(['gizmo/superdesk', 'models/user', 'utils/extend'], function(Gizmo) {
	return Gizmo.Model.extend({
		defaults:
		{
			Creator: Gizmo.Register.User
		},
		services: {
			'flickr': true,
			'google': true,
			'twitter': true,
			'facebook': true,
			'youtube': true
		},
    externalSources: {
      'flickr': true,
      'google': true,
      'twitter': true,
      'facebook': true,
      'youtube': true,
      'instagram': true,
      'soundcloud': true,
      'sms': true
    },
		/**
		* Get css class based on type
		*
		* @return {string}
		*/
		getClass: function() {
			switch (this.get('Type').Key) {
				case 'wrapup':
					return 'wrapup';
					break;

				case 'quote':
					return 'quotation';
					break;

				case 'advertisement':
					return 'advertisement';
					break;

				default:
					if (this.isService()) {
						return 'service';
					}

					return 'tw';
			}
		},
		/**
		* Test if post is from service
		*
		* @return {bool}
		*/
		isService: function() {
			return this.get('AuthorName') in this.services;
		},

		/**
		* Test if post is quote
		*
		* @return {bool}
		*/
		isQuote: function() {
			return this.getClass() == 'quotation';
		},

    isExternalSource: function(){
      return this.get('AuthorName') in this.externalSources;
    },

		twitter: {
			link: {
				anchor: function(str)
				{
					return str.replace(/[A-Za-z]+:\/\/[A-Za-z0-9-_]+\.[A-Za-z0-9-_:%&\?\/.=]+/g, function(m) 
					{
						m = m.link(m);
						m = m.replace('href="','target="_blank" href="');
						return m;
					});
				},
				user: function(str)
				{
					return str.replace(/[@]+[A-Za-z0-9-_]+/g, function(us) 
					{
						var username = us.replace("@","");

						us = us.link("http://twitter.com/"+username);
						us = us.replace('href="','target="_blank" onclick="loadProfile(\''+username+'\');return(false);"  href="');
						return us;
					});
				},
				tag: function(str)
				{
					return str.replace(/[#]+[A-Za-z0-9-_]+/g, function(t) 
					{
						var tag = t.replace(" #"," %23");
						t = t.link("http://summize.com/search?q="+tag);
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
		}
	}, { register: 'Post' });
});
