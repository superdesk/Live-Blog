require.config({
    paths: { "twitterWidgets": "//platform.twitter.com/widgets" },
    shim: {
      'twitterWidgets':  { 'exports': 'twttr' }
    }
});

define([
	'jquery',
	'plugins',
	'dust',
	'jquery-path/waypoints',
	'dispatcher'
], function($, plugins, dust, waypoints){
	return plugins["twitter-widgets"] = function(config){

    $.dispatcher.on('rendered-after.post-view', function(){
      if(this.shortItem != '/item/source/twitter')
        return;
      if(!this._parent._twitterPosts)
        this._parent._twitterPosts = [];
      this._parent._twitterPosts.push(this);
    });

    $.dispatcher.on('added-pending.posts-view', function(){
      addWaypoints(this);
    });

    $.dispatcher.on('add-all.posts-view', function(){
      addWaypoints(this);
    });

    var addWaypoints = function(self){
      if(!self._twitterPosts){ return; }

      require(['twitterWidgets'], function(twttr){
        twttr.ready(function(){
          $.each(self._twitterPosts, function(index, post){
            post.el.waypoint(function(){
              twttr.widgets.createTweet(
                post.templateData.Meta.id_str,
                post.el.find('.post-content-full').get(0),
                function(){
                  post.el.find('.post-core-content').remove();
                },
                { cards: 'all' }
              );
            },
            {
              triggerOnce: true,
              offset: '120%',
              context: self.el
            });
          });
          self._twitterPosts = [];
        });
      }, function(err){
        // twitterWidgets dependency failed to load, probably blocked by user with adblock
        return;
      });
    }
	}
});
