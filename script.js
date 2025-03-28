const btn = document.getElementById('request-permission');

let cube, scene, camera, renderer;

init3D();

// Функция запуска 3D-сцены
function init3D() {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 3;

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  const geometry = new THREE.BoxGeometry();
  const material = new THREE.MeshStandardMaterial({ color: 0x00bcd4 });
  cube = new THREE.Mesh(geometry, material);
  scene.add(cube);

  const light = new THREE.PointLight(0xffffff, 1);
  light.position.set(5, 5, 5);
  scene.add(light);

  animate();
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

// Функция обновления куба при повороте телефона
function handleOrientation(event) {
  const alpha = THREE.MathUtils.degToRad(event.alpha || 0); // вокруг Z
  const beta = THREE.MathUtils.degToRad(event.beta || 0);   // вокруг X
  const gamma = THREE.MathUtils.degToRad(event.gamma || 0); // вокруг Y

  // Обновляем вращение куба
  cube.rotation.x = beta;
  cube.rotation.y = gamma;
  cube.rotation.z = alpha;
}

// Обработка нажатия на кнопку разрешения
btn.addEventListener('click', () => {
  if (typeof DeviceOrientationEvent?.requestPermission === 'function') {
    // iOS
    DeviceOrientationEvent.requestPermission()
      .then(permissionState => {
        if (permissionState === 'granted') {
          window.addEventListener('deviceorientation', handleOrientation);
          btn.style.display = 'none';
        } else {
          alert('Доступ к ориентации запрещён');
        }
      })
      .catch(console.error);
  } else {
    // Android или поддерживающие устройства
    window.addEventListener('deviceorientation', handleOrientation);
    btn.style.display = 'none';
  }
});
