

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