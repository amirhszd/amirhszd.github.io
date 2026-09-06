'use strict';
(()=>{
const $=id=>document.getElementById(id),data=window.VIEWER_DATA;
if(!window.L||!data){$('status').textContent='Could not load the map. Check your connection and reload.';return;}
const sequence=['RGB','SC_ST','SC_ST_QA','SW_ST','TPW','SW_QA'];
const descriptions={
RGB:'This is a Landsat true-color image, composed from the visible red, green, and blue bands. It provides the landscape context for the retrieval products that follow.',
SC_ST:'The Landsat single-channel method uses thermal infrared Band 10, together with atmospheric correction inputs and surface emissivity, to estimate land-surface temperature.',
SC_ST_QA:'The USGS single-channel uncertainty product includes a distance-to-cloud term. If cloud masking is imperfect, that term can produce elevated uncertainty in clear pixels near a cloud-mask boundary.',
SW_ST:'The split-window method uses Landsat thermal infrared Bands 10 and 11—not near-infrared bands—to estimate land-surface temperature. The paired thermal channels help account for atmospheric effects and are being considered for operational Landsat Collection 3 processing.',
TPW:'Atmospheric total precipitable water is a major control on split-window temperature uncertainty. Landsat 8 and 9 do not have dedicated water-vapor absorption bands, so this workflow models TPW from engineered and selected predictors derived from Bands 10 and 11, trained with coincident MODIS TPW and ground-based AERONET column-water-vapor observations.',
SW_QA:'The estimated TPW and its retrieval uncertainty are propagated through the split-window uncertainty model. This provides an atmospheric, per-pixel uncertainty contribution in place of a cloud-distance-based single-channel metric.'};
const map=L.map('map',{scrollWheelZoom:false,minZoom:2,maxZoom:18});
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map).on('tileerror',()=>{$('status').textContent='Basemap unavailable; scene imagery can still be viewed.';});
L.control.scale({imperial:false}).addTo(map);
let productIndex=0,sceneIndex=0,active=sequence[productIndex],scene=data.scenes[sceneIndex],overlay=null,pending=null,revision=0;
const date=s=>`${s.date.slice(0,4)}-${s.date.slice(4,6)}-${s.date.slice(6,8)}`;
function render(fit){
const current=++revision,p=data.products[active],layer=scene.layers[active];
if(pending){map.removeLayer(pending);pending=null;}
if(overlay){map.removeLayer(overlay);overlay=null;}
$('story-step').textContent=`STEP ${productIndex+1} OF ${sequence.length}`;$('title').textContent=p.label;$('description').textContent=descriptions[active];
$('scene-id').textContent=`${scene.id} · ${date(scene)} · Landsat ${scene.id.startsWith('LC08')?'8':'9'} · Path ${scene.pathrow.slice(0,3)} / Row ${scene.pathrow.slice(3)}`;
$('previous').disabled=productIndex===0;$('next').disabled=productIndex===sequence.length-1;
$('legend-title').textContent=p.unit?`${p.label} (${p.unit})`:'True color · RGB';
$('gradient').hidden=!p.unit;$('ticks').hidden=!p.unit;
$('gradient').style.background=`linear-gradient(to right,${p.colors.join(',')})`;
$('ticks').replaceChildren();
const lo=layer.stats.display_min,hi=layer.stats.display_max;
if(p.unit&&Number.isFinite(lo)&&Number.isFinite(hi)){for(const v of [lo,(lo+hi)/2,hi]){const el=document.createElement('span');el.textContent=v.toFixed(p.unit==='cm'?2:1);$('ticks').append(el);}}
$('legend-note').textContent=p.unit?`Display stretch: 2nd–98th percentile of valid pixels.${active==='TPW'?' Values at or below −0.5 cm are transparent no-data.':''}`:'R = red band · G = green band · B = blue band';
$('status').textContent='Loading scene layer…';
const next=L.imageOverlay(layer.image,layer.bounds,{opacity:1,alt:`${p.label}, ${date(scene)}`,interactive:false});pending=next;
next.on('load',()=>{if(current!==revision)return;overlay=next;pending=null;$('status').textContent=`${p.label} · ${date(scene)}`;});
next.on('error',()=>{if(current!==revision)return;map.removeLayer(next);pending=null;$('status').textContent='Layer failed to load. Select it again to retry.';});next.addTo(map);
if(fit){map.invalidateSize(false);map.fitBounds(scene.bounds,{padding:[20,20],animate:false});}
}
$('previous').onclick=()=>{if(productIndex===0)return;productIndex--;active=sequence[productIndex];render(false);};
$('next').onclick=()=>{if(productIndex===sequence.length-1)return;productIndex++;active=sequence[productIndex];render(false);};
$('next-scene').onclick=()=>{sceneIndex=(sceneIndex+1)%data.scenes.length;scene=data.scenes[sceneIndex];render(true);};
render(true);
window.addEventListener('load',()=>{map.invalidateSize(false);map.fitBounds(scene.bounds,{padding:[20,20],animate:false});});
})();
