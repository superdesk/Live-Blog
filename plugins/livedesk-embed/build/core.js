({
    closure: {
        CompilerOptions: {},
        CompilationLevel: 'SIMPLE_OPTIMIZATIONS',
        loggingLevel: 'WARNING'
    },
 	paths: {
		'themeBase': '../../../gui-themes/themes/base',

		'tmpl': 'core/require/tmpl',
		'css': 'core/require/css',
		'i18n': 'core/require/i18n',
		
		'jquery': 'core/jquery',
		'dust': 'core/dust',
		'utils': 'core/utils',
		'gettext': 'core/gettext',
		'gizmo': 'core/gizmo'
    },
	baseUrl: '../gui-resources/scripts/js',
	mainConfigFile: '../gui-resources/scripts/js/core.js',
	name: 'core',
	out: '../gui-resources/scripts/js/core.min.js',
	preserveLicenseComments: false,
	optimize: 'closure',
	excludeShallow: []
})