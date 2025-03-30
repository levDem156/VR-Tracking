let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 1000);
let renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Свет
let light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(0, 1, 1).normalize();
scene.add(light);

// Куб
let geometry = new THREE.BoxGeometry();
let material = new THREE.MeshStandardMaterial({ color: 0x00ffcc, wireframe: false });
let cube = new THREE.Mesh(geometry, material);
scene.add(cube);

camera.position.z = 3;

// Вращение через quaternion
let deviceQuat = new THREE.Quaternion();

function animate() {
  requestAnimationFrame(animate);

  cube.quaternion.slerp(deviceQuat, 0.1); // Плавное вращение

  // Получаем углы для отладки
  let euler = new THREE.Euler().setFromQuaternion(cube.quaternion, 'YXZ');
  document.getElementById("yaw").textContent = (THREE.MathUtils.radToDeg(euler.y)).toFixed(1);
  document.getElementById("pitch").textContent = (THREE.MathUtils.radToDeg(euler.x)).toFixed(1);
  document.getElementById("roll").textContent = (THREE.MathUtils.radToDeg(euler.z)).toFixed(1);

  renderer.render(scene, camera);
}

// Обработка поворота экрана
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});











const server_url = "https://naval-marco-cards-viking.trycloudflare.com"

const output = document.getElementById('output');
const startButton = document.getElementById('startButton');

function listenToOrientation(password) { 
      
    window.addEventListener('deviceorientation', function (event) {

        let alpha = event.alpha ? THREE.MathUtils.degToRad(event.alpha) : 0; // Z
        let beta = event.beta ? THREE.MathUtils.degToRad(event.beta) : 0;    // X
        let gamma = event.gamma ? THREE.MathUtils.degToRad(event.gamma) : 0; // Y
    
        let euler = new THREE.Euler();
        euler.set(beta, alpha, -gamma, 'YXZ');
    
        deviceQuat.setFromEuler(euler);

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

startButton.addEventListener('click', () => {
    const inputField = document.getElementById("myInput");
    let password = inputField.value; // сохраняем в переменную
    
    fetch(`${server_url}/data?text=${password}`)
        .then(res => res.text())
        .then(data => {
            console.log(data);
            if (data.includes("Password is correct")) {
                output.innerHTML = "✅ Доступ разрешён";
                listenToOrientation(password);
            } else {
                output.innerHTML = "❌ Неверный пароль";
            }
        });
});
