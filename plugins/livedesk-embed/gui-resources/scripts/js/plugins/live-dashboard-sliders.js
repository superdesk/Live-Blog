define([
	'jquery',
	'plugins',
  'bxslider',
	'dispatcher'
], function($, plugins){
  return plugins["live-dashboard-sliders"] = function(config){
    // TODO: change it so the slider names don't need to be provided in here in a config
    // file or directly taken from the DOM.
    var self = this;

    self.sliderConfig = {
      hideControlOnEnd: true,
      infiniteLoop: false,
      //easing: 'ease-out',
      //adaptativeHeight: true,
    };
    self.sliders = {
      fullSize: null,
      text: null
    };

    self.reloadSlider = function(slider){
      slider.reloadSlider(self.sliderConfig);
      slider.goToSlide(slider.getSlideCount() - 1);
    };

		$.dispatcher.on('posts-view.rendered', function(){
      $(function(){
        for (slider in self.sliders){
          self.sliders[slider] = $('[data-gimme="' + slider + '.posts.slider"]').bxSlider(self.sliderConfig);
          self.sliders[slider].goToSlide(self.sliders[slider].getSlideCount() - 1);
        }
      });
		});

    $.dispatcher.on('posts-view.added-auto-fullSize', function(){
      self.reloadSlider(self.sliders.fullSize);
		});
		$.dispatcher.on('posts-view.added-auto-text', function(){
      self.reloadSlider(self.sliders.text);
    });
  };
});
