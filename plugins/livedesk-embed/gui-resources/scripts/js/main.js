//require(['concat.min'], function(){
requirejs.config({
	paths: 	{
		'themeBase': '../../themes/base',

		'tmpl': 'core/require/tmpl',
		'css': 'core/require/css',
		'i18n': 'core/require/i18n',
		
		'jquery': [
			//'//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min',
			'core/jquery'
		],
		'dust': 'core/dust',
		'utils': 'core/utils',
		'gettext': 'core/gettext',
		'gizmo': 'core/gizmo'
	}
});
require([
	'jquery',
	'gizmo/view-events',
	'jquery/xdomainrequest',
	'plugins/button-pagination',
	'models/blog'
], function( $, Gizmo ){
	/*!
	 * Ensure that a element is there for liveblog to rezide.
	 * if the provided element isn't there or is a wrong one create one element just
	 *    above the script element
	 */
	if( !liveblog.el || ($(liveblog.el).length === 0)) {
		liveblog.el = $('<div></div>').insertBefore(liveblog.script);
	}

	var blog = new Gizmo.Register.Blog(), 
		embedConfig = {};
	blog.url.decorate('%s/' + liveblog.id);
	blog
		.xfilter('Description, Title, EmbedConfig, Language.Code')
		.sync({force: true}).done(function(){
			/*!
			 * Get configuration from blog
			 * replace this with blog/config when new X-Filter will be implemented.
			 */
			try {
				embedConfig = JSON.parse(blog.get('EmbedConfig'));
			} catch(e){}
			/*!
			 * Set defaults for language and theme.
			 */
			liveblog.language = liveblog.language? liveblog.language: blog.get('Language').Code;
			liveblog.theme 	 = liveblog.theme? liveblog.theme: embedConfig.theme;

			require([
				'utils/date-format',
				'views/blog',
				'utils/find-enviroment',
				'../../themes/'+liveblog.theme,
				'i18n!livedesk_embed'
			], function(dateFormat, BlogView, findEnviroment, theme){
				dateFormat.masks['post-date'] = _('mm/dd/yyyy HH:MM');
				dateFormat.masks['status-date'] = _('HH:MM');
				dateFormat.masks['closed-date'] = _('mm/dd/yyyy HH:MM');
				var run = function(){
					new BlogView({ el: liveblog.el, model: blog });
				}
				if(theme && theme.enviroments) {
					if(!liveblog.enviroment) {
						var enviroment = findEnviroment();
						liveblog.enviroment = theme.enviroments[enviroment]? theme.enviroments[enviroment] : theme.enviroments['default'];
					}
					require(['../../themes/' + liveblog.theme + '/' + liveblog.enviroment], function(){
						run();
					});
				} else {
					run();
				}
			});
	});
});
