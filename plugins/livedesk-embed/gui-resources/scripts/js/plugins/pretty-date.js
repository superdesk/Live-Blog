define(['jquery', 'livedesk-embed/dispatcher' ], function($){
	function prettyDate(t){
		if(t === undefined)
			return;
		var now = new Date(),
			date = new Date(parseInt(t)),
			diff = ((now.getTime() - date.getTime()) / 1000),
			day_diff = Math.floor(diff / 86400),
			minutes_diff = Math.floor( diff / 60 ),
			hours_diff = Math.floor( diff / 3600 ),
			weeks_diff = Math.ceil( day_diff / 7 );
		if ( isNaN(day_diff) || day_diff < 0 )
			return;
		return day_diff == 0 && (
				diff < 5 && _("Just now")+'' ||
				diff < 60 && _("%(seconds)s seconds ago").format({ seconds: parseInt(diff)}) ||
				diff < 3600 && ngettext("One minute ago", "%(minutes)s minutes ago", minutes_diff ).format({ minutes: minutes_diff})||
				diff < 86400 && ngettext("One hour ago", "%(hours)s hours ago", hours_diff ).format({ hours: hours_diff}) )||
			day_diff < 7 && ngettext("Yesterday", "%(days)s days ago", day_diff ).format({ days: day_diff}) ||
			day_diff < 31 &&  _("%(weeks)s weeks ago").format({ weeks: weeks_diff}) ||
			day_diff > 31 && date.format('mm/dd/yyyy HH:MM');
	}
	var interval;
	$.dispatcher.on('after-render', function(){
			var self = this,
				render = function(){
					self.el.find('[data-date]').each(function(){
						$(this).text(prettyDate($(this).attr('data-date')));
					});
				}
			render();
			clearInterval(interval);
			interval = setInterval(render, 5000);
	});
});