define(['jquery', 'livedesk-embed/dispatcher' ], function($){
	function prettyDate(t){
		/*!
		 * If no date is provided then return nothing
		 */
		if(t === undefined)
			return;
		/*!
		 * Compute diffecences for seconds sec_diff
		 * for minutes, days and so on for later use
		 */
		var now = new Date(),
			date = new Date(parseInt(t)),
			sec_diff = ((now.getTime() - date.getTime()) / 1000),
			day_diff = Math.floor(sec_diff / 86400),
			minutes_diff = Math.floor( sec_diff / 60 ),
			hours_diff = Math.floor( sec_diff / 3600 ),
			weeks_diff = Math.ceil( day_diff / 7 );
		/*!
		 * If somethign gone wrong return nothing
		 */
		if ( isNaN(day_diff) || day_diff < 0 )
			return;
		/*!
		 * return the beautified text based on the diffences 
		 * 
		 */
		return day_diff == 0 && (
				sec_diff < 5		&& gettext("Just now")+'' ||
				sec_diff < 60		&& gettext("%(seconds)s seconds ago").format({ seconds: parseInt(sec_diff)}) ||
				minutes_diff < 60	&& ngettext("One minute ago", "%(minutes)s minutes ago", minutes_diff ).format({ minutes: minutes_diff})||
			hours_diff < 24		&& ngettext("One hour ago", "%(hours)s hours ago", hours_diff ).format({ hours: hours_diff}) )||
			day_diff < 7 		&& ngettext("Yesterday", "%(days)s days ago", day_diff ).format({ days: day_diff}) ||
			weeks_diff < 4 		&& gettext("%(weeks)s weeks ago").format({ weeks: weeks_diff}) ||
			weeks_diff > 4 		&& date.format('mm/dd/yyyy HH:MM');
	}
	return function(config) {
		if (config && config.PrettyDate) {
			var interval;
			$.dispatcher.on('after-render', function(){
					var self = this,
						render = function(){
							self.el.find('[data-date]').each(function(){
								$(this).text(prettyDate($(this).attr('data-date')));
							});
						}
					/*!
					 * First run the handler and then run the timer on the handler every 5 sec.
					 */
					render();
					clearInterval(interval);
					interval = setInterval(render, 5000);
			});
		}
	}
});