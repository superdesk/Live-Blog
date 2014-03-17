// @TODO: this is a hack and it should be removed
//     when the namespace requirejs is implementd.
delete require.amd;
// end @TODO
require.config({
	paths: 	{
		'themeBase': '../../themes/base',
		
		'require': 'core/require',

		'tmpl': 'core/require/tmpl',
		'css': 'core/require/css',
		'i18n': 'core/require/i18n',
		
		'jquery-loader': 'core/jquery-loader',
		'jquery-path': 'core/jquery',
		'dust': 'core/dust',
		'utils': 'core/utils',
		'gettext': 'core/gettext',
		'gizmo': 'core/gizmo',

		'iscroll': 'core/iscroll'
	},
	shim: {
		'iscroll':  { 'exports': 'IScroll' }
	}
});
require(['jquery-loader','core.min'], function(){
	require([
		'jquery',
		'gizmo/view-events',
		'jquery-path/xdomainrequest',
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
			embedConfig = {},
			min = require.specified("core")? '.min': '';
		blog.url.decorate('%s/' + liveblog.id);
		blog
			.xfilter('Description, Title, EmbedConfig, Language.Code')
			.sync({force: true, preprocessTime: 330}).done(function(){
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
				require.config({
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
						require.undef('theme');
						require.undef('themeFile');
						require.config({
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