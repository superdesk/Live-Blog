define([ 'jquery', 'gizmo/superdesk' ], function( $, Gizmo) {
	var ViewEvents = Gizmo.View.extend({
		/*!
		 * used to remove events from this view
		 */
		off: function(evt, handler)		
		{
			$(this).off(evt, handler);
			return this;
		},
		/*!
		 * used to place events on this view,
		 * scope of the call method is sent as obj argument
		 */
		on: function(evt, handler, obj)
		{
			if(obj === undefined) {
				$(this).off(evt, handler);
				$(this).on(evt, handler);
			}
			else {			
				$(this).on(evt, function(){
					handler.apply(obj, arguments);
				});
			}
			return this;
		},
		one: function(evt, handler, obj)
		{
			if(obj === undefined) {
				$(this).off(evt, handler);
				$(this).one(evt, handler);
			}
			else {			
				$(this).one(evt, function(){
					handler.apply(obj, arguments);
				});
			}
			return this;
		},
		
		/*!
		 * used to trigger view events
		 * this also calls the view method with the event name
		 */
		trigger: function(evt, data)
		{
			$(this).trigger(evt, data);
			return this;
		},
		/*!
		 * used to trigger handle of view events
		 * this doens't call any method see: trigger
		 */
		triggerHandler: function(evt, data)
		{
			$(this).triggerHandler(evt, data);
			return this;
		}
	});
	Gizmo.View = ViewEvents;
	return Gizmo;
});