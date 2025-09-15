// スライダー機能（jQuery・ドットナビ対応）
$(function() {
    var $slides = $('.slide');
    var $dots = $('.slider-dots .dot');
    var current = 0;
    var timer;
    function showSlide(idx) {
        $slides.removeClass('active');
        $slides.eq(idx).addClass('active');
        $dots.removeClass('active');
        $dots.eq(idx).addClass('active');
    }
    function nextSlide() {
        current = (current + 1) % $slides.length;
        showSlide(current);
    }
    function prevSlide() {
        current = (current - 1 + $slides.length) % $slides.length;
        showSlide(current);
    }
    $dots.on('click', function(e) {
        var idx = $dots.index(this);
        current = idx;
        showSlide(current);
        resetTimer();
        e.stopPropagation();
    });
    function resetTimer() {
        clearInterval(timer);
    timer = setInterval(nextSlide, 11000); // 11秒ごとに切り替え
    }
    showSlide(current);
    timer = setInterval(nextSlide, 11000); // 11秒ごとに切り替え
});


    $(function() {
        // メニュー開閉
        $('#hamburger').on('click', function(e) {
            $('#sideMenu').toggleClass('open');
            e.stopPropagation();
        });

        // サイドメニュー内クリックは閉じない
        $('#sideMenu').on('click', function(e) {
            e.stopPropagation();
        });

        // ドキュメントのどこかをクリックしたら閉じる
        $(document).on('click', function() {
            $('#sideMenu').removeClass('open');
        });
    });