requirejs.config({
	paths: 	{
		'themeBase': '../../themes/base',
		
		'require': 'core/require',

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
			min = require.specified("core")? '.min': '';
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
					blog.data['EmbedConfig'] = embedConfig;
				} catch(e){
					blog.data['EmbedConfig'] = {};
				}
				/*!
				 * Set defaults for language and theme.
				 */
				liveblog.language = liveblog.language? liveblog.language: blog.get('Language').Code;
				liveblog.theme 	 = liveblog.theme? liveblog.theme: embedConfig.theme;
				requirejs.config({
					paths: 	{
						'themeFile': '../../themes/' + liveblog.theme + min,
						'theme': '../../themes/' + liveblog.theme
					}
				});
				require([
					'themeFile',
					
					'utils/find-enviroment',
					'core',
					'i18n!livedesk_embed'
				], function(theme, findEnviroment, core, plugins){
					if(theme && theme.enviroments) {
						if(!liveblog.enviroment) {
							var enviroment = findEnviroment();
							liveblog.enviroment = theme.enviroments[enviroment]? theme.enviroments[enviroment] : theme.enviroments['default'];
						} else {

						}
						requirejs.undef('theme');
						requirejs.undef('themeFile');
						requirejs.config({
							paths: 	{
								'themeFile': '../../themes/'+liveblog.theme + '/' + liveblog.enviroment + min,
								'theme': '../../themes/'+liveblog.theme + '/' + liveblog.enviroment
						    }
						});
						require(['themeFile'], function(){
							core(blog);
						});
					} else {
						core(blog);
					}
				});
		});
	});
});