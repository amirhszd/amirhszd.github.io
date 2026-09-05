'use strict';
(()=>{
const $=id=>document.getElementById(id),data=window.VIEWER_DATA;
if(!window.L||!data){$('status').textContent='Could not load the map. Check your connection and reload.';return;}
const descriptions={
RGB:'True-color imagery provides landscape context for interpreting the temperature and atmospheric layers. Compare the same location across products.',
SC_ST:'Surface temperature from the Landsat Level-2 single-channel product. Switch to split-window temperature to compare spatial patterns using the same Kelvin scale.',
SW_ST:'Split-window surface temperature supplied by the research pipeline. The color scale matches the single-channel layer; differences in color can therefore be compared directly.',
SC_ST_QA:'Single-channel surface-temperature uncertainty from the USGS ST_QA product. Brighter colors indicate larger uncertainty, not warmer surfaces.',
SW_QA:'Split-window surface-temperature uncertainty. Compare against single-channel uncertainty on the same scale. The supplied split-window product is capped at 10 K.',
TPW:'Estimated total precipitable water: the equivalent depth of liquid water in the atmospheric column, expressed in centimeters. Small negative predictions are retained and are nonphysical estimates; zero values are retained as supplied.'};
const map=L.map('map',{scrollWheelZoom:false,minZoom:2,maxZoom:18});
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map).on('tileerror',()=>{$('status').textContent='Basemap unavailable; scene imagery can still be viewed.';});
L.control.scale({imperial:false}).addTo(map);
let active='RGB',scene=data.scenes[0],overlay=null,pending=null,revision=0;
const date=s=>`${s.date.slice(0,4)}-${s.date.slice(4,6)}-${s.date.slice(6,8)}`;
for(const [i,s] of data.scenes.entries()){const o=document.createElement('option');o.value=i;o.textContent=`${date(s)} · Landsat ${s.id.startsWith('LC08')?'8':'9'} · path ${s.pathrow.slice(0,3)} / row ${s.pathrow.slice(3)}`;$('scene').append(o);}
for(const [key,p] of Object.entries(data.products)){const b=document.createElement('button');b.type='button';b.textContent=p.label;b.dataset.key=key;b.onclick=()=>{active=key;render(false);};$('products').append(b);}
function render(fit){
const current=++revision,p=data.products[active],layer=scene.layers[active];
if(pending){map.removeLayer(pending);pending=null;}
if(overlay){map.removeLayer(overlay);overlay=null;}
$('title').textContent=p.label;$('description').textContent=descriptions[active];
$('observation').textContent=layer.stats?`${date(scene)} · Median of valid source pixels: ${layer.stats.median.toFixed(2)} ${p.unit}. Valid source range: ${layer.stats.min.toFixed(2)}–${layer.stats.max.toFixed(2)} ${p.unit}.`:`${date(scene)} · RGB is already stretched to 8-bit values in the supplied data; it has no temperature or TPW units.`;
for(const b of $('products').children)b.setAttribute('aria-pressed',String(b.dataset.key===active));
$('legend-title').textContent=p.unit?`${p.label} (${p.unit})`:'True color · RGB';
$('gradient').hidden=!p.unit;$('ticks').hidden=!p.unit;
$('gradient').style.background=`linear-gradient(to right,${p.colors.join(',')})`;
$('ticks').replaceChildren();
if(p.unit){for(const v of [p.min,(p.min+p.max)/2,p.max]){const el=document.createElement('span');el.textContent=v.toFixed(p.unit==='cm'?2:0);$('ticks').append(el);}}
$('legend-note').textContent=p.unit?`Fixed scale across all scenes. Values outside the scale use endpoint colors (${(layer.stats.below_percent+layer.stats.above_percent).toFixed(1)}% of valid source pixels).`:'R = red band · G = green band · B = blue band';
$('status').textContent='Loading scene layer…';
const next=L.imageOverlay(layer.image,layer.bounds,{opacity:Number($('opacity').value),alt:`${p.label}, ${date(scene)}`,interactive:false});pending=next;
next.on('load',()=>{if(current!==revision)return;overlay=next;pending=null;$('status').textContent=`${p.label} · ${date(scene)}`;});
next.on('error',()=>{if(current!==revision)return;map.removeLayer(next);pending=null;$('status').textContent='Layer failed to load. Select it again to retry.';});next.addTo(map);
if(fit)map.fitBounds(scene.bounds,{padding:[20,20],animate:false});
}
$('scene').onchange=()=>{scene=data.scenes[Number($('scene').value)];render(true);};
$('fit').onclick=()=>map.fitBounds(scene.bounds,{padding:[20,20]});
$('opacity').oninput=()=>{if(overlay)overlay.setOpacity(Number($('opacity').value));if(pending)pending.setOpacity(Number($('opacity').value));};
render(true);
})();
