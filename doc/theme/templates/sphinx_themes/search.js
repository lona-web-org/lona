{% raw %}
    var _search_ractive_template = `
        <h1>Search{{#if query }} "{{query}}"{{/if}}</h1>
        {{#results}}
            <h2>{{.doc.title}}</h2>
            <a href="{{.ref}}?q={{query}}">{{.ref}}</a>
            {{#@index !== @last}}
                <hr/>
            {{/}}
        {{/results}}
    `;
{% endraw %}

window.addEventListener('load', function() {
    // setup ractive
    search_ractive = Ractive({
        target: search_ractive_target_selector,
        template: _search_ractive_template,
        data: {
            query: '',
            results: [],
        },
    });

    // setup search index
    var articles = [];

    {% for content in sort_by_search_index_weight(context.contents) %}
        articles.push({
            ref: '{{ content.output }}',
            title: {{ safe_dump(content.content_title or '') }},
            body: {{ safe_dump(content.content_body or '') }},
        });
    {% endfor %}

    // setup query
    var query = get_get_variable('q');

    if(query) {
        var results = [];

        for(var index in articles) {
            var article = articles[index];

            if(article['title'].includes(query) ||
               article['body'].includes(query)) {

                results.push({
                    doc: article,
                    ref: article.ref,
                });
            };
        };

        search_ractive.set({
            query: query,
            results: results,
        });
    };
});
