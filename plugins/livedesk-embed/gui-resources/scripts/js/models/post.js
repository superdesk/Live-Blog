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

    /**
     * Is the post mostly text or media?
     * Use by the live-dashboard-blog to determine if the post
     * should be shown in the fullSize or the text slider
     */
    isTextLike: function(){
      type = this.get('Type').Key;
      if(this.isExternalSource()){
        var autor = this.get('AuthorName');
        var meta = this.get('Meta');
        switch (autor) {
          case 'google':
            if (meta.contains('GnewsSearch')|| meta.contains('GwebSearch')){
              return true;
            }
            break;
          case 'twitter':
            if (!meta.contains('media_url_https')){
              return true;
            }
            break;
          case 'facebook':
          case 'sms':
            return true;
            break;
        }
      } else {
        var type = this.get('Type').Key
        if (type === 'normal' || type === 'quote' ||
            type === 'link' || type === 'wrapup'){
          return true;
        }
      }
      return false;
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
