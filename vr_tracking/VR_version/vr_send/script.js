// Настройка Three.js
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 1000);
let renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
// Фиксированное позиционирование холста на заднем плане
renderer.domElement.style.position = 'fixed';
renderer.domElement.style.top = '0';
renderer.domElement.style.left = '0';
renderer.domElement.style.zIndex = '0';
document.body.appendChild(renderer.domElement);

// Добавление освещения
let light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(0, 1, 1).normalize();
scene.add(light);

// Создание куба
let geometry = new THREE.BoxGeometry();
let material = new THREE.MeshStandardMaterial({ color: 0x00ffcc });
let cube = new THREE.Mesh(geometry, material);
scene.add(cube);

camera.position.z = 3;

// Переменная для хранения ориентации устройства
let deviceQuat = new THREE.Quaternion();

// Функция анимации
function animate() {
  requestAnimationFrame(animate);
  cube.quaternion.slerp(deviceQuat, 0.1);

  // Отображение углов для отладки
  let euler = new THREE.Euler().setFromQuaternion(cube.quaternion, 'YXZ');
  document.getElementById("yaw").textContent = (THREE.MathUtils.radToDeg(euler.y)).toFixed(1);
  document.getElementById("pitch").textContent = (THREE.MathUtils.radToDeg(euler.x)).toFixed(1);
  document.getElementById("roll").textContent = (THREE.MathUtils.radToDeg(euler.z)).toFixed(1);

  renderer.render(scene, camera);
}
animate();

// Обработка изменения размеров окна
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Сервер и элементы управления
const server_url = "https://naval-marco-cards-viking.trycloudflare.com";
const output = document.getElementById('output');
const startButton = document.getElementById('startButton');

// Функция для отслеживания ориентации устройства и отправки данных на сервер
function listenToOrientation(password) { 
  window.addEventListener('deviceorientation', function (event) {
    let alpha = event.alpha ? THREE.MathUtils.degToRad(event.alpha) : 0; // ось Z
    let beta = event.beta ? THREE.MathUtils.degToRad(event.beta) : 0;    // ось X
    let gamma = event.gamma ? THREE.MathUtils.degToRad(event.gamma) : 0; // ось Y

    let euler = new THREE.Euler();
    euler.set(beta, alpha, -gamma, 'YXZ');
    deviceQuat.setFromEuler(euler);

    // Отправка данных на сервер
    fetch(`${server_url}/update`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        y: alpha,
        p: beta,
        r: gamma,
        ps: password
      })
    });
  }, true);
}

// Обработка нажатия кнопки
startButton.addEventListener('click', () => {
  const inputField = document.getElementById("myInput");
  let password = inputField.value; // сохраняем пароль

  fetch(`${server_url}/data?text=${password}`)
    .then(res => res.text())
    .then(data => {
      if (data.includes("Password is correct")) {
        output.innerHTML = "✅ Доступ разрешён";
        listenToOrientation(password);
      } else {
        output.innerHTML = "❌ Неверный пароль";
      }
    });
});