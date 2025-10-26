// 安全な Splide 初期化
// 目的: ページ内の複数の .splide 要素を個別に初期化する。
//       既に #js-splide のようにIDで初期化済みのものは再初期化しない。
document.addEventListener('DOMContentLoaded', function () {
  // 共通オプション（必要に応じて調整）
  const commonOptions = {
    autoplay: true,
    type: 'fade',
    rewind: true,
    pauseOnHover: false,
    pauseOnFocus: false,
    interval: 4000,
    speed: 1000,
  };

  // 全ての .splide 要素を走査して個別にインスタンス化する
  document.querySelectorAll('.splide').forEach(function (el) {
    // もし特定のIDで既に別スクリプトが初期化している場合はスキップ
    if (el.id && document.querySelector('#' + el.id + '.splide[data-initialized]')) return;

    // 例: index.html内で #js-splide を手動初期化している場合は重複を避ける
    if (el.id === 'js-splide' && window.__JS_SPLIDE_INITIALIZED) {
      return;
    }

    try {
      const instance = new Splide(el, commonOptions);
      // set CSS variable for pagination progress so ::after can use var(--playing-rate)
      instance.on('autoplay:playing', function (rate) {
        try {
          var pagination = el.querySelector('.splide__pagination');
          if (pagination) pagination.style.setProperty('--playing-rate', (rate * 100) + '%');
        } catch (e) {
          // ignore
        }
      });
      instance.mount();
      // マークを付与して二重初期化を防ぐ
      el.setAttribute('data-initialized', 'true');
    } catch (e) {
      // 初期化失敗はconsoleへ出力して次へ
      console.error('Splide init failed for element:', el, e);
    }
  });
});