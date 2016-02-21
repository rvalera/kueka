ko.bindingHandlers.datepicker = {
	init : function(element, valueAccessor, allBindingsAccessor) {
		var $el = $(element);

		// initialize datepicker with some optional options
		var options = allBindingsAccessor().datepickerOptions || {};
		$el.datepicker(options);

		// handle the field changing
		ko.utils.registerEventHandler(element, "change", function() {
			var observable = valueAccessor();
			observable($el.datepicker("getDate"));
		});

		// handle disposal (if KO removes by the template binding)
		ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
			$el.datepicker("destroy");
		});

	},
	update : function(element, valueAccessor) {
		var value = ko.utils.unwrapObservable(valueAccessor()), $el = $(element), current = $el
				.datepicker("getDate");

		if (value - current !== 0) {
			$el.datepicker("setDate", value);
		}
	}
};

ko.bindingHandlers.timeago = {
	update : function(element, valueAccessor) {
		var value = ko.utils.unwrapObservable(valueAccessor());
		var $this = $(element);

		$this.attr('title', value);

		if ($this.data('timeago')) {
			var datetime = $.timeago.datetime($this);
			var distance = (new Date().getTime() - datetime.getTime());
			var inWords = $.timeago.inWords(distance);

			$this.data('timeago', {
				'datetime' : datetime
			});
			$this.text(inWords);
		} else {
			$this.timeago();
		}
	}
};

ko.bindingHandlers.dataurl = {
	update : function(element, valueAccessor) {
		var value = ko.utils.unwrapObservable(valueAccessor());
		var $this = $(element);
		$this.attr('data-url', value);
		// para las pruebas...descomentar y comentar la linea anteior...
		// if(location.href.indexOf("/show?id=") == -1){
		// $this.attr('data-url', location.href.replace("/causes", "") + value);
		// }
		// else {
		// $this.attr('data-url', location.href);
		// }
	}
};

ko.bindingHandlers.dataonsuccess = {
	update : function(element, valueAccessor) {
		var value = ko.utils.unwrapObservable(valueAccessor());
		var $this = $(element);
		$this.attr('data-onsuccess', value);
	}
};

/*
 * Binding for enter on a text field
 */
// ko.bindingHandlers.executeOnEnter = {
//	init : function(element, valueAccessor, allBindingsAccessor, viewModel) {
//		var allBindings = allBindingsAccessor();
//		$(element).keypress(function(event) {
//			var keyCode = (event.which ? event.which : event.keyCode);
//			if (keyCode === 13) {
//				allBindings.executeOnEnter.call(viewModel);
//				return false;
//			}
//			return true;
//		});
//	}
//};

/*
 * Here's a custom Knockout binding that makes elements shown/hidden via jQuery's fadeIn()/fadeOut() methods
 * Could be stored in a separate utility library
 * */
ko.bindingHandlers.fadeVisible = {
	    init: function(element, valueAccessor) {
	        // Initially set the element to be instantly visible/hidden depending on the value
	        var value = valueAccessor();
	        $(element).toggle(ko.unwrap(value)); // Use "unwrapObservable" so we can handle values that may or may not be observable
	    },
	    update: function(element, valueAccessor) {
	        // Whenever the value subsequently changes, slowly fade the element in or out
	        var value = valueAccessor();
	        ko.unwrap(value) ? $(element).fadeIn() : $(element).fadeOut();
	    }
	};