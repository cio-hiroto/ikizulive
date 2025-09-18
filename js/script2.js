const splide = new Splide(".splide", {
  autoplay: true, // 自動再生
  type: "fade", // ループ
  rewind: true, // スライダーの終わりまで行ったら先頭に巻き戻す（デフォルトはfalse）
  pauseOnHover: false, // カーソルが乗ってもスクロールを停止させない
  pauseOnFocus: false, // 矢印をクリックしてもスクロールを停止させない
  interval: 4000, // 自動再生の間隔
  speed: 1000, // スライダーの移動時間
}).mount();

splide.on( 'autoplay:playing', function ( rate ) {
  const progressBar = document.querySelector( '.splide__progress__bar' );
  progressBar.style.width = rate * 100 + '%';
} );

splide.mount();