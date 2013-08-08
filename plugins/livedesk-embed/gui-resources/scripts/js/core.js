define([
	'jquery',
	'utils/date-format',
	'views/blog',
	'utils/find-enviroment',
	'plugins',
	'jquery/xdomainrequest',
	'i18n'
], function($, dateFormat, BlogViewDef, findEnviroment, plugins){
		dateFormat.masks['post-date'] = _('mm/dd/yyyy HH:MM');
		dateFormat.masks['status-date'] = _('HH:MM');
		dateFormat.masks['closed-date'] = _('mm/dd/yyyy HH:MM');
		dateFormat.i18n = {
			dayNames: _("Sun,Mon,Tue,Wed,Thu,Fri,Sat,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday").toString().split(","),
			monthNames: _("Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,January,February,March,April,May,June,July,August,September,October,November,December").toString().split(",")
		};
		return function(blog){
			console.log(plugins);
			$.each(plugins, function(key, value){
				value();
			})
			var BlogView = BlogViewDef();
			new BlogView({ el: liveblog.el, model: blog });
		}
});