import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const canvas = document.querySelector("#scene");
const status = document.querySelector("#status");
const pointSize = document.querySelector("#point-size");
const rotate = document.querySelector("#rotate");
const reset = document.querySelector("#reset");

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x081016);
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x081016, 0.00135);
const camera = new THREE.PerspectiveCamera(42, 1, 0.5, 4000);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.45;

let material;
const initialCamera = new THREE.Vector3(520, 360, 570);
function resetView(){camera.position.copy(initialCamera);controls.target.set(0,0,0);controls.update()}
resetView();

function colorForIntensity(t, colors, offset){
  const a=t<.5?t*2:(t-.5)*2;
  const start=t<.5?[.05,.2,.45]:[.05,.75,.5];
  const end=t<.5?[.05,.75,.5]:[1,.83,.15];
  colors[offset]=start[0]+(end[0]-start[0])*a;
  colors[offset+1]=start[1]+(end[1]-start[1])*a;
  colors[offset+2]=start[2]+(end[2]-start[2])*a;
}

async function loadPointCloud(){
  const [metaResponse,dataResponse]=await Promise.all([fetch("metadata.json"),fetch("points.bin")]);
  if(!metaResponse.ok||!dataResponse.ok)throw new Error("Unable to load point-cloud data.");
  const metadata=await metaResponse.json();
  const raw=new Float32Array(await dataResponse.arrayBuffer());
  const count=raw.length/4;
  const positions=new Float32Array(count*3);
  const colors=new Float32Array(count*3);
  const min=metadata.bounds.min,max=metadata.bounds.max;
  const cx=(min[0]+max[0])/2,cy=(min[1]+max[1])/2,cz=(min[2]+max[2])/2;
  for(let i=0;i<count;i++){
    positions[i*3]=raw[i*4]-cx;
    positions[i*3+1]=raw[i*4+2]-cz;
    positions[i*3+2]=-(raw[i*4+1]-cy);
    colorForIntensity(raw[i*4+3],colors,i*3);
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute("position",new THREE.BufferAttribute(positions,3));
  geometry.setAttribute("color",new THREE.BufferAttribute(colors,3));
  geometry.computeBoundingSphere();
  material=new THREE.PointsMaterial({size:Number(pointSize.value),vertexColors:true,sizeAttenuation:true,transparent:true,opacity:.92});
  scene.add(new THREE.Points(geometry,material));
  const grid=new THREE.GridHelper(800,16,0x36555e,0x1d343b);grid.position.y=min[2]-cz-.5;scene.add(grid);
  status.textContent=`${metadata.sample_points.toLocaleString()} sampled voxels from ${metadata.source_points.toLocaleString()} total`;
}

pointSize.addEventListener("input",()=>{if(material)material.size=Number(pointSize.value)});
rotate.addEventListener("change",()=>{controls.autoRotate=rotate.checked});
reset.addEventListener("click",resetView);
new ResizeObserver(()=>{
  const {clientWidth:width,clientHeight:height}=canvas;
  renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();
}).observe(canvas);
function animate(){controls.update();renderer.render(scene,camera);requestAnimationFrame(animate)}
loadPointCloud().catch(error=>{console.error(error);status.textContent=error.message});
animate();
