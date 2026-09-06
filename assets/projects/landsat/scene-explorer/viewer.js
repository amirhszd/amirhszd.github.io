'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const data = window.VIEWER_DATA;
  if (!data) {
    $('status').textContent = 'Could not load viewer data. Please reload.';
    return;
  }

  const sequence = ['RGB', 'SC_ST', 'SC_ST_QA', 'SW_ST', 'TPW', 'SW_QA'];
  const copy = {
    RGB: 'This is a Landsat RGB true-color composite, displaying the visible red, green, and blue bands to provide landscape context.',
    SC_ST: 'The Single-Channel (SC) algorithm utilizes Landsat\'s thermal infrared Band 10, combined with atmospheric profiles and surface emissivity, to retrieve land surface temperature.',
    SC_ST_QA: 'The Single-Channel uncertainty algorithm is highly sensitive to cloud proximity. Because cloud masking can fail or misidentify clear pixels, this uncertainty estimation is prone to false positives.',
    SW_ST: 'The Split-Window (SW) algorithm takes advantage of two adjacent thermal infrared channels (Bands 10 and 11) to estimate land surface temperature, correcting for atmospheric attenuation. It is planned for implementation in the USGS EROS workflow for Collection 3.',
    TPW: 'Atmospheric water vapor is a major factor impacting split-window surface temperature retrieval, but Landsat 8/9 lacks dedicated water vapor bands. By pairing coincident MODIS Total Precipitable Water (TPW) with ground-based AERONET solar-photometer measurements as ground truth, machine learning models can utilize feature engineering and selection on Landsat thermal Bands 10/11 to accurately estimate per-pixel TPW.',
    SW_QA: 'The estimated TPW is directly integrated into the analytical uncertainty propagation of the Split-Window algorithm. This replaces the cloud-distance-based Single-Channel uncertainty metric, offering a more robust, physically based, and spatially continuous assessment of temperature uncertainty.'
  };

  let i = 0; // Active layer index (0-5)
  let j = 0; // Active scene index (0-3)

  const date = s => s.date.slice(0, 4) + '-' + s.date.slice(4, 6) + '-' + s.date.slice(6, 8);

  // Initialize and preload all 24 images
  const viewport = $('viewport');
  const imageElements = {}; // key: sceneIndex_layerIndex

  let loadedCount = 0;
  const totalImages = data.scenes.length * sequence.length;

  data.scenes.forEach((scene, sIdx) => {
    sequence.forEach((layerKey, lIdx) => {
      const layer = scene.layers[layerKey];
      const p = data.products[layerKey];
      
      const img = document.createElement('img');
      img.src = layer.image;
      img.alt = `${p.label} - ${scene.id}`;
      img.className = 'raster-image';
      img.dataset.sceneIndex = sIdx;
      img.dataset.layerIndex = lIdx;
      
      img.onload = () => {
        loadedCount++;
        if (loadedCount === totalImages) {
          $('status').style.opacity = '0';
          setTimeout(() => { $('status').style.display = 'none'; }, 400);
        } else {
          $('status').textContent = `Loading layers (${Math.round((loadedCount / totalImages) * 100)}%)...`;
        }
      };
      img.onerror = () => {
        // Fallback or ignore
        loadedCount++;
      };

      viewport.appendChild(img);
      imageElements[`${sIdx}_${lIdx}`] = img;
    });
  });

  // Safe fallback if some images are cached and onload is not fired synchronously or is slow
  setTimeout(() => {
    if (loadedCount < totalImages) {
      $('status').style.opacity = '0';
      setTimeout(() => { $('status').style.display = 'none'; }, 400);
    }
  }, 3000);

  function render() {
    const scene = data.scenes[j];
    const active = sequence[i];
    const layer = scene.layers[active];
    const p = data.products[active];

    // Toggle active class on images
    Object.keys(imageElements).forEach(key => {
      const img = imageElements[key];
      const [sIdx, lIdx] = key.split('_').map(Number);
      if (sIdx === j && lIdx === i) {
        img.classList.add('active');
      } else {
        img.classList.remove('active');
      }
    });

    // Update Top-Left story text box
    $('story-step').textContent = `STEP ${i + 1} OF ${sequence.length}`;
    $('title').textContent = p.label;
    $('description').textContent = copy[active];

    // Update Bottom-Left Scene ID
    $('scene-id').innerHTML = `<strong>Scene:</strong> ${scene.id.slice(0, 25)}...<br><strong>Date:</strong> ${date(scene)} (Landsat ${scene.id.startsWith('LC08') ? '8' : '9'})<br><strong>Path/Row:</strong> ${scene.pathrow.slice(0, 3)} / ${scene.pathrow.slice(3)}`;

    // Update Buttons state
    $('previous').disabled = i === 0;
    $('next').disabled = i === sequence.length - 1;

    // Update Colorbar / Legend
    $('legend-title').textContent = p.unit ? `${p.label} (${p.unit})` : 'True Color · RGB';
    
    const gradientEl = $('gradient');
    const ticksEl = $('ticks');
    const noteEl = $('legend-note');

    if (p.unit) {
      gradientEl.style.display = 'block';
      ticksEl.style.display = 'flex';
      gradientEl.style.background = `linear-gradient(to right, ${p.colors.join(',')})`;
      
      ticksEl.replaceChildren();
      const tickValues = [p.min, (p.min + p.max) / 2, p.max];
      tickValues.forEach(v => {
        const span = document.createElement('span');
        span.textContent = v.toFixed(p.unit === 'cm' ? 2 : 0);
        ticksEl.appendChild(span);
      });

      const outOfBoundsPct = ((layer.stats.below_percent || 0) + (layer.stats.above_percent || 0));
      noteEl.textContent = `Endpoint clipping: ${outOfBoundsPct.toFixed(2)}% of pixels.`;
      noteEl.style.display = 'block';
    } else {
      gradientEl.style.display = 'none';
      ticksEl.style.display = 'none';
      noteEl.textContent = 'R = red band · G = green band · B = blue band';
      noteEl.style.display = 'block';
    }
  }

  // Button Click Handlers
  $('previous').onclick = () => {
    if (i > 0) {
      i--;
      render();
    }
  };

  $('next').onclick = () => {
    if (i < sequence.length - 1) {
      i++;
      render();
    }
  };

  $('next-scene').onclick = () => {
    j = (j + 1) % data.scenes.length;
    render();
  };

  // Initial render
  render();
})();
