define(['jquery/superdesk'], function(superdesk)
{
//    var ItemView,
//        MainView,
//        SideView,
//        ScratchpadView,
    var MediaArchive = function()
    {
    	$('#area-main').load(superdesk.apiUrl+'/content/lib/media-archive/test.html')
    }
    return MediaArchive;
});