window.addEventListener('load', function () {
  const sliderId = 'slider_element'; // ← HTMLのidに合わせる
  const track = document.getElementById(sliderId);

  if (!track) {
    console.error(`ID "${sliderId}" の要素が見つかりません。HTML構造を確認してください。`);
    return;
  }

  // JSONデータを取得
  fetch('/json/data.json')
    .then(response => response.json())
    .then(tweets => {
      // 既存の中身をクリア
      track.innerHTML = '';

      // splide__listを作成
      const list = document.createElement('div');
      list.classList.add('splide__list');

      // 各ツイートをスライドとして生成
      tweets.forEach(tweet => {
        const slide = document.createElement('div');
        slide.classList.add('splide__slide');
        slide.innerHTML = `
          <blockquote class="twitter-tweet">
            <p lang="ja" dir="ltr"><a href="${tweet.url}"></a></p>
          </blockquote>
        `;
        list.appendChild(slide);
      });

      // track内に追加
      track.appendChild(list);

      // Splideを初期化（親の .splide を指定）
      const parentSplide = track.closest('.splide');
      if (!parentSplide) {
        console.error(`"${sliderId}" の親に .splide が見つかりません。`);
        return;
      }

      new Splide(parentSplide, {
        type: 'loop',
        perPage: 1,
        pagination: true,
        arrows: true,
      }).mount();

      // Twitter埋め込みを再読み込み
      if (window.twttr && window.twttr.widgets) {
        window.twttr.widgets.load();
      } else {
        const script = document.createElement('script');
        script.src = 'https://platform.twitter.com/widgets.js';
        script.async = true;
        document.body.appendChild(script);
      }
    })
    .catch(error => {
      console.error('JSONの読み込みに失敗しました:', error);
    });
});
