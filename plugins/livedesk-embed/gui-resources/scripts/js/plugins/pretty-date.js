define([
    'jquery',
    'plugins',
    'dispatcher'
], function($, plugins, dispatcher){
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
            minutes_hour_diff = minutes_diff - 60 * hours_diff,
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
				sec_diff < 2		&& gettext("Just now")+'' ||
				sec_diff < 60		&& gettext("%(seconds)s seconds ago").format({ seconds: parseInt(sec_diff)}) ||
				minutes_diff < 60	&& ngettext("One minute ago", "%(minutes)s minutes ago", minutes_diff ).format({ minutes: minutes_diff})||
			hours_diff < 24		&& ngettext("One hour and %(minutes)s ago at %(time)s", "%(hours)s hours and %(minutes)s ago at %(time)s", hours_diff ).format({
                hours: hours_diff,
                minutes: ngettext("one minute", "%(minutes)s minutes", minutes_hour_diff ).format({ minutes: minutes_hour_diff}),
                time: date.format(pgettext('minutes','HH:MM:ss'))
            }) )||
			day_diff < 7 		&& ngettext("Yesterday at %(time)s", "%(days)s days ago at %(time)s", day_diff ).format({
                days: day_diff,
                time: date.format(pgettext('days','HH:MM:ss'))
            }) ||
			weeks_diff < 4 		&& gettext("%(weeks)s weeks ago at %(time)s and %(data)s").format({
                weeks: weeks_diff,
                time: date.format(pgettext('weeks','HH:MM:ss')),
                data: date.format(pgettext('weeks','mm/dd/yyyy HH:MM'))
            }) ||
			weeks_diff > 4 		&& date.format(pgettext('months','mm/dd/yyyy HH:MM'));
	}
	return plugins['pretty-date'] = function(config) {
			var interval, render = function(){};
            $.dispatcher.on('rendered-before.blog-view', function() {
                var self = this;
                render = function(){
                    self.el.find('[data-date]').each(function(){
                        $(this).text(prettyDate($(this).attr('data-date')));
                    });
                    self.el.find('[data-gimme="blog.status"]').each(function(){
                        var time = $(this).find('[data-update-date]').attr('data-update-date'),
                            pdate = prettyDate(time),
                            t = '<time data-update-date="'+time+'">';
                        t += ngettext('updated now', 'updated %(pretty)s', (pdate === gettext("Just now")+''))
                                .format({
                                    pretty: pdate
                                });
                        t += "</time>";
                        $(this).html(t);
                    });                    
                }                
            });
			$.dispatcher.on('rendered-after.blog-view add-all.posts-view update-status.blog-view', function(){
					/*!
					 * First run the handler and then run the timer on the handler every 5 sec.
					 */
					render();
					clearInterval(interval);
					interval = setInterval(render, 1000);
			});
	}
});