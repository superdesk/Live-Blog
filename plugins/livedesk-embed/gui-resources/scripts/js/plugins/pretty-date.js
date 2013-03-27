define(['jquery', 'livedesk-embed/dispatcher' ], function($){
	function prettyDate(t){
		if(t === undefined)
			return;
		var n = (new Date()).toISOString(),
			date = new Date(t.substr(0,4),parseInt(t.substr(5,2))-1,parseInt(t.substr(8,2)),t.substr(11,2),t.substr(14,2),t.substr(17,2),t.substr(20,3)),
			now = new Date(n.substr(0,4),parseInt(n.substr(5,2))-1,parseInt(n.substr(8,2)),n.substr(11,2),n.substr(14,2),n.substr(17,2),n.substr(20,3)),
			diff = ((now.getTime() - date.getTime()) / 1000),
			day_diff = Math.floor(diff / 86400);		
		console.log(t,',',n);
		if ( isNaN(day_diff) || day_diff < 0 )
			return;
		minutes_diff = Math.floor( diff / 60 ); 
		hours_diff = Math.floor( diff / 3600 );
		weeks_diff = Math.ceil( day_diff / 7 );
		return day_diff == 0 && (
				diff < 5 && _("Just now") ||
				diff < 60 && _("{seconds} seconds ago").format({ seconds: parseInt(diff)}) ||
				diff < 3600 && ngettext("One minute ago", "%(minutes)s minutes ago", minutes_diff ).format({ minutes: minutes_diff})||
				diff < 86400 && ngettext("One hour ago", "%(hours)s hours ago", hours_diff ).format({ hours: hours_diff}) )||
			day_diff < 7 && ngettext("Yesterday", "{days} days ago", day_diff ).format({ days: day_diff}) ||
			day_diff < 31 &&  _("{weeks} weeks ago").format({ weeks: weeks_diff}) ||
			day_diff > 31 && date.format('dddd, mmmm d, yyyy');
	}
	$.dispatcher.on('after-render', function(){
			console.log(this.el);
			this.el.find('[data-date]').each(function(){
				$(this).html(prettyDate($(this).attr('data-date')));
			});
	});
});