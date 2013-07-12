var requirejs;
liveblog.version = 1 ;// = {Version};
liveblog.runner = function() {
	requirejs = {
		baseUrl: this.baseUrl,
		urlArgs: 'version=' + this.version
	}
	this.loadJs('//cdnjs.cloudflare.com/ajax/libs/require.js/2.1.6/require.min.js').setAttribute('data-main','main');
}
// liveblog.githubversion = function(reply) {
// 	this.version = reply && reply.data? reply.data[0].sha: this.version;
// 	requirejs.urlArgs = 'version=' + this.version;
// 	if(require)
// 		require.config( { urlArgs: requirejs.urlArgs } );
// }
// liveblog.branch = 'devel';
// liveblog.loadJs('https://api.github.com/repos/sourcefabric/superdesk/commits?callback=liveblog.githubversion&per_page=1&sha='+liveblog.branch);
liveblog.runner();