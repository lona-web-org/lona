window.addEventListener('load', function() {
    var mark_name = get_get_variable('mark') || get_get_variable('q');

    if(!mark_name) {
      return;
    }

    // set search to search word
    var form = document.querySelector('form#rtd-search-form input[name=q]');

    form.value = mark_name;

    // skip search index
    if(window.location.pathname == '/search.html') {
      return;
    };

    // mark matches on the current page
    var context = document.querySelector(search_ractive_target_selector);
    var mark = new Mark(context);

    mark.mark(mark_name, {
      caseSensitive: true,

      // scroll to first mark
      done: function(count) {

        if(count < 1) {
          return;
        };

        var mark = document.querySelector('mark');

        setTimeout(function(){
          mark.scrollIntoView();
        }, 500);
      },
    });
});
