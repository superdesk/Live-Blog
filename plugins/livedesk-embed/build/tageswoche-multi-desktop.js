({
    closure: {
        CompilerOptions: {},
        CompilationLevel: 'SIMPLE_OPTIMIZATIONS',
        loggingLevel: 'WARNING'
    },
 	paths: {
 		'theme': '../../../gui-themes/themes/tageswoche-multi/desktop',
 		'themeFile': '../../../gui-themes/themes/tageswoche-multi/desktop',
		'themeBase': '../../../gui-themes/themes/base',
		
		'require': 'core/require',
		
		'tmpl': 'core/require/tmpl',
		'css': 'core/require/css',
		'normalize': 'core/require/normalize',
		'i18n': 'core/require/i18n',
		
		'jquery-path': 'core/jquery',		
		'jquery': 'core/jquery',
		'dust': 'core/dust',
		'utils': 'core/utils',
		'gettext': 'core/gettext',
		'gizmo': 'core/gizmo',
		
		'twitterWidgets': 'empty:'
    },
	baseUrl: '../gui-resources/scripts/js',
	mainConfigFile: '../gui-themes/themes/tageswoche-multi/desktop.js',
	name: 'themeFile',
	out: '../gui-themes/themes/tageswoche-multi/desktop.min.js',
	preserveLicenseComments: false,
	optimize: 'closure',
	exclude: [
		'twitterWidgets'
	],
	excludeShallow: [
		'jquery',
		'jquery/utils',
		'jquery/i18n',
		'jquery/cookie',
		'jquery/tmpl',
		'tmpl',

		'gettext',
		'dispatcher',

		'utils/str',
		'utils/utf8',
		'utils/utf8-pass',
		'utils/twitter',
		'utils/json_parse',
		'utils/extend',
		'utils/class',

		'dust',
		'dust/core',
		'dust/dust',
		'dust/parser',
		'dust/compiler',
		'dust/dust-helpers',
		'dust/i18n_parse',

		'gizmo',
		'gizmo/superdesk',

		'css',
		'require/css',
		'require/normalize',

		'require/tmpl',
		'tmpl!themeBase/item/base',

		'twitterWidgets'
	]
})