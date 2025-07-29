(function($) {
$.fn.j01LiveSearch = function(o) {
    o = $.extend({
        resultExpression: '#j01LiveSearchResult',
        methodName: 'getJ01LiveSearchResult',
        url: null,
        minQueryLenght: 2,
        maxReSearch: 0,
        requestId: 'j01LiveSearch',
        callback: setLiveSearchResult,
        onAfterRender: false
    }, o || {});

    var searchInputElement = false;
    var searchText = false;
    var currentSearchText = null;
    var reSearchCounter = 0;
    var loading = false;

    function resetLiveSearch() {
        loading = false;
    }

    function setLiveSearchResult(response) {
        var content = response.content;
        if (searchText && currentSearchText != searchText) {
            // search again
            if (reSearchCounter < o.maxReSearch) {
                reSearchCounter += 1;
                doLiveSearch();
            }
            loading = false;
            return false;
        }
        reSearchCounter = 0;
        ele = $(o.resultExpression);
        ele.empty();
        ele.html(content);
        ele.show();
        if (o.onAfterRender){
            o.onAfterRender(ele);
        }
        loading = false;
    }

    function doLiveSearch() {
        // do not search if text is given but to short
        if (searchText && searchText.length < o.minQueryLenght) {
            loading = false;
            return false;
        }
        // search only if not text or min length searchText is given and
        // load only if not a request is pending and there is not cache
        if(!loading) {
            // search if we are not loding and text is given with the correct
            // length and also search if no text is given (reset)
            loading = true;
            currentSearchText = searchText;
            // do livesearch call
        	var proxy = getJSONRPCProxy(o.url);
        	proxy.addMethod(o.methodName, o.callback, o.requestId);
        	proxy[o.methodName](searchText);
        }
    }

    return this.each(function() {
        $(this).keyup(function() {
            searchInputElement = $(this);
        	searchText = $(this).val();
        	doLiveSearch();
        });
    });
};
})(jQuery);
