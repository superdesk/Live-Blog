requirejs.config({
	paths: 	{
		'themeBase': '../../themes/base',

		'tmpl': 'core/require/tmpl',
		'css': 'core/require/css',
		'i18n': 'core/require/i18n',
		
		'jquery': 'core/jquery',
		'dust': 'core/dust',
		'utils': 'core/utils',
		'gettext': 'core/gettext',
		'gizmo': 'core/gizmo'
	}
});
require(['core.min'], function(){
	require([
		'jquery',
		'gizmo/view-events',
		'jquery/xdomainrequest',
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
				requirejs.config({
					paths: 	{
						'theme': '../../themes/' + liveblog.theme//+'.min'
					}
				});
				require([
					'theme',
					'utils/find-enviroment',
					'core',
					'i18n!livedesk_embed'
				], function(theme, findEnviroment, core){
					if(theme && theme.enviroments) {
						if(!liveblog.enviroment) {
							var enviroment = findEnviroment();
							liveblog.enviroment = theme.enviroments[enviroment]? theme.enviroments[enviroment] : theme.enviroments['default'];
						}
						requirejs.undef('theme');
						requirejs.config({
							paths: 	{
								'theme': '../../themes/'+liveblog.theme + '/' + liveblog.enviroment
							}
						});
						require(['theme'], function(){
							core(blog);
						});
					} else {
						core(blog);
					}
				});
		});
	});
});