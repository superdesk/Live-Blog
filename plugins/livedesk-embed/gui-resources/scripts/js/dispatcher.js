define(['jquery'], function($){
	var dispatcher = function () {};
	dispatcher.prototype = {
		on: function(evt, handler) {
			$(this).on(evt, function(evt, self){
				handler.call(self);
			});
		},
		triggerHandler: function(evt,self) {
			$(this).triggerHandler(evt,[self]);
		}
	};
	$.dispatcher = new dispatcher;
});