'use strict';
(()=> {
const $=id=>document.getElementById(id),data=window.VIEWER_DATA;
if(!window.L||!data){$('status').textContent='Could not load the map. Check your connection and reload.';return;}
const sequence=['RGB','SC_ST','SC_ST_QA','SW_ST','TPW','SW_QA'];
const copy={
RGB:'This is a Landsat true-color image, composed from the visible red, green, and blue bands. It provides the landscape context for the retrieval products that follow.',
SC_ST:'The Landsat single-channel method uses thermal infrared Band 10, together with atmospheric correction inputs and surface emissivity, to estimate land-surface temperature.',
SC_ST_QA:'The USGS single-channel uncertainty product includes a distance-to-cloud term. When the cloud mask incorrectly flags clear pixels, this term can create falsely elevated uncertainty near the flagged areas.',
SW_ST:'The split-window method uses the two thermal infrared channels, Bands 10 and 11—not near-infrared bands—to estimate land-surface temperature. It is planned for operational Landsat Collection 3 processing.',
TPW:'Atmospheric total precipitable water is a major source of split-window temperature uncertainty. Landsat 8 and 9 lack dedicated water-vapor absorption bands, so this workflow uses an XGBoost model with engineered and selected predictors from Bands 10 and 11, trained against coincident MODIS and ground-based AERONET water-vapor observations.',
SW_QA:'The estimated total precipitable water and its retrieval uncertainty are propagated through the split-window uncertainty model. This replaces the single-channel cloud-distance uncertainty term with an atmospheric, per-pixel uncertainty contribution.'};
const map=L.map('map',{scrollWheelZoom:false,minZoom:2,maxZoom:18});
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
L.control.scale({imperial:false}).addTo(map);
let i=0,j=0,active=sequence[i],scene=data.scenes[j],overlay=null,pending=null,revision=0;
const date=s=>s.date.slice(0,4)+'-'+s.date.slice(4,6)+'-'+s.date.slice(6,8);
function render(fit){
const current=++revision,p=data.products[active],layer=scene.layers[active];
if(pending){map.removeLayer(pending);pending=null;}if(overlay){map.removeLayer(overlay);overlay=null;}
$('story-step').textContent='STEP '+(i+1)+' OF '+sequence.length;$('title').textContent=p.label;$('description').textContent=copy[active];
$('scene-id').textContent=scene.id+' · '+date(scene)+' · Landsat '+(scene.id.startsWith('LC08')?'8':'9')+' · Path '+scene.pathrow.slice(0,3)+' / Row '+scene.pathrow.slice(3);
$('previous').disabled=i===0;$('next').disabled=i===sequence.length-1;$('legend-title').textContent=p.unit?p.label+' ('+p.unit+')':'True color · RGB';$('gradient').hidden=!p.unit;$('ticks').hidden=!p.unit;$('gradient').style.background='linear-gradient(to right,'+p.colors.join(',')+')';$('ticks').replaceChildren();
if(p.unit){for(const v of [p.min,(p.min+p.max)/2,p.max]){const el=document.createElement('span');el.textContent=v.toFixed(p.unit==='cm'?2:0);$('ticks').append(el);}}
$('legend-note').textContent=p.unit?'Fixed scale across all scenes. Values outside the scale use endpoint colors ('+(layer.stats.below_percent+layer.stats.above_percent).toFixed(1)+'% of valid source pixels).':'R = red band · G = green band · B = blue band';
$('status').textContent='Loading scene layer…';const next=L.imageOverlay(layer.image,layer.bounds,{opacity:1,alt:p.label+', '+date(scene),interactive:false});pending=next;
next.on('load',()=>{if(current!==revision)return;overlay=next;pending=null;$('status').textContent=p.label+' · '+date(scene);});next.on('error',()=>{if(current!==revision)return;map.removeLayer(next);pending=null;$('status').textContent='Layer failed to load. Select it again to retry.';});next.addTo(map);if(fit)map.fitBounds(scene.bounds,{padding:[20,20],animate:false});
}
$('previous').onclick=()=>{if(i===0)return;i--;active=sequence[i];render(false);};$('next').onclick=()=>{if(i===sequence.length-1)return;i++;active=sequence[i];render(false);};$('next-scene').onclick=()=>{j=(j+1)%data.scenes.length;scene=data.scenes[j];render(true);};render(true);
})();
