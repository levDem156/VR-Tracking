// Проверка поддержки API
if (window.DeviceOrientationEvent) {
    console.log("API поддерживается");
} else {
    alert("DeviceOrientation не поддерживается вашим устройством");
    return;
}

if (window.DeviceOrientationEvent) {
    console.log("DeviceOrientation поддерживается");

    // Запрос разрешения (на iOS 13+ требуется явное разрешение)
    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
        DeviceOrientationEvent.requestPermission()
            .then(permissionState => {
                if (permissionState === 'granted') {
                    startListening();
                } else {
                    console.log("Доступ к датчикам отклонён");
                }
            })
            .catch(console.error);
    } else {
        // На устройствах, где разрешение не требуется (например, Android)
        startListening();
    }
} else {
    console.log("DeviceOrientation не поддерживается вашим устройством");
}

// Функция для начала отслеживания ориентации
function startListening() {
    window.addEventListener('deviceorientation', (event) => {
        console.log("Событие работает", event);

        // Alpha: поворот вокруг оси Z (0–360°, направление компаса)
        const alpha = event.alpha;
        // Beta: наклон по оси X (-180–180°, вперед-назад)
        const beta = event.beta;
        // Gamma: наклон по оси Y (-90–90°, влево-вправо)
        const gamma = event.gamma;

        // Вывод данных в консоль
        console.log(`Alpha (Z): ${alpha.toFixed(2)}°`);
        console.log(`Beta (X): ${beta.toFixed(2)}°`);
        console.log(`Gamma (Y): ${gamma.toFixed(2)}°`);

        // Пример использования: обновление текста на странице
        document.getElementById('orientation')?.innerHTML = `
            Z (Alpha): ${alpha.toFixed(2)}°<br>
            X (Beta): ${beta.toFixed(2)}°<br>
            Y (Gamma): ${gamma.toFixed(2)}°
        `;
    });
}
