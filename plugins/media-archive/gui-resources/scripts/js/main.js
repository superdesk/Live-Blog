define([config.guiJs('media-archive', 'list')], function(list)
{
    listView = new (list.ListView)(); 
    return { init: function(){ listView.activate(); } };
});