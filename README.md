Для считывания положения телефона в пространстве использовал:

window.addEventListener('deviceorientation', (event) => {
    const alpha = event.alpha || 0; // Z
    const beta = event.beta || 0;   // X
    const gamma = event.gamma || 0; // Y
});

Работает только на телефоне и с протоколом https.

Сервер запусил на rasPi, с flask. для api добавил https канал с помощью cloudflared.
