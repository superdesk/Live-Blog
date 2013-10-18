define([
	'jquery',
	'plugins',
  'bxslider',
	'dispatcher'
], function($, plugins){
  return plugins["live-dashboard-sliders"] = function(config){
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

    self.postAdded = function(sliderName){
      slider = self.sliders[sliderName];
      if (slider) {
        self.reloadSlider(slider);
      } else {
        self.createSlider(sliderName);
      }
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
      self.postAdded('fullSize');
    });

		$.dispatcher.on('posts-view.added-auto-text', function(){
      self.postAdded('text');
    });
  };
});
