define('jquery/i18n',['gettext', 'utils/str', 'jquery', 'jquery/utils'],function(Gettext, str, $){

	i18n = function(){
		this.init();
	}
	i18n.prototype = {
		gt: {},
		dataUrl: {},
		mapper: ["gettext","ngettext","pgettext","dgettext","npgettext","dngettext","dpgettext","dnpgettext","dcnpgettext"],
		mapperGenerator: function(self,param) {
			return function() {
				return new str(self[param].apply(self, arguments));
			}
		},
		init: function(){
			this.gt = new Gettext();
			Gettext.context_glue = ":";
			//this.gt.try_load_lang_json(this.dataUrl);
			aux = $.combineObj(this.mapper, this.mapperGenerator)
			$.mergeObj(this, this.gt, $.combineObj(this.mapper, this.mapperGenerator) );		
		},
		load: function(catalog){
			this.gt.parse_locale_data(catalog);
			return this;
		},	
		install: function(){
			$.mergeObj(window,this, 
				this.mapper,
				{
					   _: "gettext",
					"C_": "pgettext",
					"N_": function() { return function(msgid) { return new str(msgid);}},
					"NC_": function() { return function(msgctxt, msgid) { return new str(msgid);}},
				});
		},
	}
	I18n = new i18n;
	I18n.install();

	$.extend($, {i18n: I18n});

});