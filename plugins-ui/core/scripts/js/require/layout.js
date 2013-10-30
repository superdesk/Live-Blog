(function(){
    define
    ({
        load: function (name, req, load, config)
        {
            var self = this;
            require(['dust', 'jquery', 'jquery/superdesk'], function(d, j, s){ self.process(window.dust, name, req, load, config, s); });
        },
        process: function(dust, name, req, load, config, superdesk) 
        {
            var path = req.toUrl( config.templatePaths.default + name + '.dust');
            $.ajax(path, {dataType: 'text'}).done(function(data)
            {
                var newName = name.replace("/", "_"),
                    text = dust.compile(data, newName);

                // before autoLayout to use navigation
                load.fromText(name, text);
                req([name], function(value){ load(value); });
                
                // add layout to stage if configured
                if( config.autoLayout )
                    $(config.autoLayout).tmpl( newName );
                
            });
        }
    });
}());