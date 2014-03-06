({
    closure: {
        CompilerOptions: {},
        CompilationLevel: 'SIMPLE_OPTIMIZATIONS',
        loggingLevel: 'WARNING'
    },
 	paths: {
		'themeBase': '../../../gui-themes/themes/base',

		'require': 'core/require',
		'requireLib': 'core/require',

		'tmpl': 'core/require/tmpl',
		'css': 'core/require/css',
		'i18n': 'core/require/i18n',
		'jquery': 'core/jquery',
		'jquery-path': 'core/jquery',
		'dust': 'core/dust',
		'utils': 'core/utils',
		'gettext': 'core/gettext',
		'gizmo': 'core/gizmo'
    },
	baseUrl: '../gui-resources/scripts/js',
	mainConfigFile: '../gui-resources/scripts/js/main.js',
	name: 'main',
	out: '../gui-resources/scripts/js/build/main.min.js',
	preserveLicenseComments: false,
	//optimize: 'closure',
	optimize: 'none',
	namespace: 'liveblog',
	include: ['requireLib', 'core'],
	excludeShallow: ['jquery']
})