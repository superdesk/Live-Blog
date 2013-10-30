define
([
    'jquery', 'jquery/superdesk', 'gizmo/superdesk',  
    'tmpl!error',
], 
function($, superdesk, giz)
{
    var ErrorApp = 
    {
        require: function(args)
        {
            var data = {};
            if(args.status) switch(args.status)
            {
                case 404: data.Error = _('Resource not found'); break;
                default: data.Error = _('An error occurred');
            }
            $.tmpl('error', data, function(e, o)
            {
                var o = $(o);
                $('#area-main').append(o);
                $('.close', o).on('click', function(){ $(o).remove(); });
                setTimeout(function(){ $(o).remove(); }, 3000);
            });
        }
    };
    
    return ErrorApp;
});