$(function() {
    $.getJSON('json/data.json', function(data) {
        var $list = $('.twitter-embed-list');
        $list.empty();
        data.twitter_posts.forEach(function(post) {
            var tweetUrl = post.url;
            var embedHtml =
                '<blockquote class="twitter-tweet"><a href="' + tweetUrl + '"></a></blockquote>';
            var $item = $('<div class="twitter-embed-item"></div>').html(embedHtml);
            $list.append($item);
        });
        function loadTwitterWidgets() {
            if (window.twttr && window.twttr.widgets) {
                window.twttr.widgets.load();
            }
        }
        if (window.twttr && window.twttr.widgets) {
            window.twttr.widgets.load();
        } else {
            $.getScript('https://platform.twitter.com/widgets.js', loadTwitterWidgets);
        }
    });
});