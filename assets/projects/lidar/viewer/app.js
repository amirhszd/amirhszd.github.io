import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const canvas = document.querySelector("#scene");
const status = document.querySelector("#status");
const pointSize = document.querySelector("#point-size");
const scalarField = document.querySelector("#scalar-field");
const rotate = document.querySelector("#rotate");
const reset = document.querySelector("#reset");
const legendLow = document.querySelector("#legend-low");
const legendHigh = document.querySelector("#legend-high");
const tooltip = document.querySelector("#voxel-tooltip");

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

let material, points, colors, intensities, heights, contributions;
let scalarRanges = { intensity: [0, 1], height: [0, 1] };
const raycaster = new THREE.Raycaster();
raycaster.params.Points.threshold = 2.25;
const pointer = new THREE.Vector2();
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

function applyScalarField(){
  if(!points)return;
  const field=scalarField.value;
  const values=field==="height"?heights:intensities;
  const [min,max]=scalarRanges[field];
  for(let i=0;i<values.length;i++)colorForIntensity((values[i]-min)/(max-min||1),colors,i*3);
  points.geometry.attributes.color.needsUpdate=true;
  const label=field==="height"?"height":"intensity";
  legendLow.textContent=`Low ${label}`;
  legendHigh.textContent=`High ${label}`;
}

async function loadPointCloud(){
  const [metaResponse,dataResponse]=await Promise.all([fetch("metadata.json"),fetch("points.bin")]);
  if(!metaResponse.ok||!dataResponse.ok)throw new Error("Unable to load point-cloud data.");
  const metadata=await metaResponse.json();
  const buffer=await dataResponse.arrayBuffer();
  const view=new DataView(buffer);
  const count=buffer.byteLength/metadata.record_bytes;
  const positions=new Float32Array(count*3);
  colors=new Float32Array(count*3);
  intensities=new Float32Array(count);
  heights=new Float32Array(count);
  contributions=new Uint8Array(count*4);
  const min=metadata.bounds.min,max=metadata.bounds.max;
  scalarRanges={intensity:[min[3],max[3]],height:[min[2],max[2]]};
  const cx=(min[0]+max[0])/2,cy=(min[1]+max[1])/2,cz=(min[2]+max[2])/2;
  for(let i=0;i<count;i++){
    const offset=i*metadata.record_bytes;
    const x=view.getFloat32(offset,true),y=view.getFloat32(offset+4,true),z=view.getFloat32(offset+8,true),intensity=view.getFloat32(offset+12,true);
    positions[i*3]=x-cx;
    positions[i*3+1]=z-cz;
    positions[i*3+2]=-(y-cy);
    intensities[i]=intensity;
    heights[i]=z;
    for(let j=0;j<4;j++)contributions[i*4+j]=view.getUint8(offset+16+j);
    colorForIntensity(intensity,colors,i*3);
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute("position",new THREE.BufferAttribute(positions,3));
  geometry.setAttribute("color",new THREE.BufferAttribute(colors,3));
  geometry.computeBoundingSphere();
  material=new THREE.PointsMaterial({size:Number(pointSize.value),vertexColors:true,sizeAttenuation:true,transparent:true,opacity:.92});
  points=new THREE.Points(geometry,material);
  scene.add(points);
  const grid=new THREE.GridHelper(800,16,0x36555e,0x1d343b);grid.position.y=min[2]-cz-.5;scene.add(grid);
}

pointSize.addEventListener("input",()=>{if(material)material.size=Number(pointSize.value)});
scalarField.addEventListener("change",applyScalarField);
rotate.addEventListener("change",()=>{controls.autoRotate=rotate.checked});
reset.addEventListener("click",resetView);
let pendingPointer=null;
function updateTooltip(){
  const event=pendingPointer;pendingPointer=null;
  if(!event||!points)return;
  const rect=canvas.getBoundingClientRect();
  pointer.x=((event.clientX-rect.left)/rect.width)*2-1;
  pointer.y=-((event.clientY-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(pointer,camera);
  const hit=raycaster.intersectObject(points,false)[0];
  if(!hit){tooltip.hidden=true;return}
  const labels=["Bark","Leaf","Soil","Other"],i=hit.index;
  tooltip.innerHTML=`<strong>Voxel composition</strong>${labels.map((label,j)=>`<span><b>${label}</b><em>${(contributions[i*4+j]/255*100).toFixed(1)}%</em></span>`).join("")}`;
  tooltip.style.left=`${Math.max(12,Math.min(rect.width-175,event.clientX-rect.left+14))}px`;
  tooltip.style.top=`${Math.max(12,event.clientY-rect.top-35)}px`;
  tooltip.hidden=false;
}
canvas.addEventListener("pointermove",event=>{if(!pendingPointer)requestAnimationFrame(updateTooltip);pendingPointer=event});
canvas.addEventListener("pointerleave",()=>{pendingPointer=null;tooltip.hidden=true});
new ResizeObserver(()=>{
  const {clientWidth:width,clientHeight:height}=canvas;
  renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();
}).observe(canvas);
function animate(){controls.update();renderer.render(scene,camera);requestAnimationFrame(animate)}
loadPointCloud().catch(error=>{console.error(error);status.textContent=error.message});
animate();
