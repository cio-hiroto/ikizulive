$(function() {
    $.getJSON('json/data.json', function(data) {
        var $list = $('.twitter-embed-list');
        var $items = $list.find('.twitter-embed-item');
        var $dots = $('.twitter-carousel-dots');
        var $prev = $('.twitter-carousel-prev');
        var $next = $('.twitter-carousel-next');
        $dots.empty();
        var posts = data.twitter_posts;
        $items.each(function(idx){
            var post = posts[idx];
            if(post){
                var tweetUrl = post.url;
                var embedHtml = '<blockquote class="twitter-tweet"><a href="' + tweetUrl + '"></a></blockquote>';
                $(this).html(embedHtml);
            }else{
                $(this).html("");
            }
            var $dot = $('<span class="twitter-carousel-dot"></span>');
            if(idx === 0) $dot.addClass('active');
            $dots.append($dot);
        });
        // 事前レンダリング用に全itemへ.preloadクラスを付与
        $items.addClass('preload').show();
        if(window.twttr && window.twttr.widgets){
            twttr.widgets.load($list[0]);
        }
        // レンダリング後に1件だけ表示（preload解除）
        setTimeout(function(){
            $items.removeClass('preload');
            showSlide(0);
        }, 1200);
        var current = 0;
        var timer;
        var slideCount = posts.length;
        function showSlide(idx) {
            $list.find('.twitter-embed-item').removeClass('center active').hide();
            var count = $list.find('.twitter-embed-item').length;
            // 中央のみ表示
            $list.find('.twitter-embed-item').eq(idx).addClass('center active').show();
            $dots.find('.twitter-carousel-dot').removeClass('active');
            $dots.find('.twitter-carousel-dot').eq(idx).addClass('active');
        }
        function nextSlide() {
            current = (current + 1) % slideCount;
            showSlide(current);
        }
        function prevSlide() {
            current = (current - 1 + slideCount) % slideCount;
            showSlide(current);
        }
        function resetTimer() {
            clearInterval(timer);
            timer = setInterval(nextSlide, 6000);
        }
        $dots.on('click', '.twitter-carousel-dot', function() {
            var idx = $dots.find('.twitter-carousel-dot').index(this);
            current = idx;
            showSlide(current);
            resetTimer();
        });
        $next.on('click', function() {
            nextSlide();
            resetTimer();
        });
        $prev.on('click', function() {
            prevSlide();
            resetTimer();
        });
        // スワイプ対応
        var startX = null;
        $list.on('touchstart', function(e) {
            startX = e.originalEvent.touches[0].clientX;
        });
        $list.on('touchend', function(e) {
            if(startX === null) return;
            var endX = e.originalEvent.changedTouches[0].clientX;
            if(endX - startX > 50) {
                prevSlide();
                resetTimer();
            } else if(startX - endX > 50) {
                nextSlide();
                resetTimer();
            }
            startX = null;
        });
        showSlide(current);
        resetTimer();
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