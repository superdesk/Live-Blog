define([
	'jquery',
	'plugins',
  'bxslider',
	'dispatcher'
], function($, plugins){
  return plugins["live-dashboard-sliders"] = function(config){
    // TODO: change it so the slider names are provided in a config
    // file instead of here or directly taken from the DOM.
    var self = this;

    self.sliderConfig = {
      fullSize: {
        hideControlOnEnd: true,
        infiniteLoop: false
      },
      text: {
        pager: false,
        hideControlOnEnd: true,
        infiniteLoop: false
      },
    };
    self.sliders = {
      fullSize: null,
      text: null
    };

    self.createSlider = function(slider){
      self.sliders[slider] = $('[data-gimme="' + slider + '.posts.slider"]').bxSlider(self.sliderConfig[slider]);
      self.sliders[slider].goToSlide(self.sliders[slider].getSlideCount() - 1);
    },

    self.reloadSlider = function(slider){
      slider.reloadSlider();
      slider.goToSlide(slider.getSlideCount() - 1);
    };

		$.dispatcher.on('posts-view.rendered', function(){
      $(function(){
        for (slider in self.sliders){
          var list = $('[data-gimme="' + slider + '.posts.slider"]');
          if (list.children().length > 0){
            self.createSlider(slider);
          }
        }
      });
		});

    $.dispatcher.on('posts-view.added-auto-fullSize', function(){
      slider = self.sliders.fullSize;
      if (slider) {
        self.reloadSlider(slider);
      } else {
        self.createSlider('fullSize');
      }
		});
		$.dispatcher.on('posts-view.added-auto-text', function(){
      slider = self.sliders.text;
      if (slider) {
        self.reloadSlider(slider);
      } else {
        self.createSlider('text');
      }
    });
  };
});
