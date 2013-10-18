Live dashboard is a embedded theme for Live Blog with a more visual approach.

It consists of two sliders, one on top for visual posts (images or post with big images, videos) and one on the bottom for text-like posts.

From the implementation point of view it is integrated in the livedesk-embed structure.

- in the theme folder (livedesk-embed/gui-themes/themes/live-dashboard) you can modify the templates used to display the posts.

- you can find the css styles in base-theme.less, also in the theme folder.

- two specific Gizmo views are used for this theme: livedesk-embed/gui-resources/scripts/js/views/live-dashboard-blog.js and livedesk-embed/gui-resources/scripts/js/views/live-dashboard-posts.js

- the jquery.bxslider plugin is used for displaying the sliders.

- two plugins are used in the theme:
	- livedesk-embed/gui-resources/scripts/js/plugins/live-dashboard-sliders.js: start and reload of the sliders, you can update here the config of the sliders.
	- livedesk-embed/gui-resources/scripts/js/plugins/dashboard-twitter-widgets.js: used to display the twitter cards in embedded tweets. The twitter-widgets.js plugin doesn't work in this theme because due to a bug twitter cards are only load on scrolling, not on display. Whenever this is fixed it may be possible to use this plugin instead of dashboard-twitter-widgets.js.

- don't forget to add the updated templates, css files and plugins in the theme javascript files (live-dashboard-blog.js and live-dashboard-blog.min.js in livedesk-embed/gui-themes/themes/)
