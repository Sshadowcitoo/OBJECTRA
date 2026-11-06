const $id = id => document.getElementById(id);
const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
const colors = ['#438d78', '#b14f62', '#bd9346', '#657cb1', '#9774a4'];
const qualitySizes = {fast: 320, balanced: 480, detail: 640};
const qualityLabels = {fast: 'Rápido', balanced: 'Equilibrado', detail: 'Detalle'};
let stream = null, running = false, busy = false, token = null, generation = 0;
let originalUrl = null;
let quality = 'fast', boxes = [], clearBoxesTimer = null, controller = null, activeQuality = null;

const status = message => { $id('status').textContent = message; };

const icon = name => {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  const use = document.createElementNS(svg.namespaceURI, 'use');
  use.setAttribute('href', `#i-${name}`); 
  svg.append(use); 
  svg.setAttribute('aria-hidden', 'true');
  return svg;
};

function systemState(title, description) {
  $id('system-state').textContent = title;
  $id('system-description').textContent = description;
}

function cameraState(text, live = false) {
  $id('camera-state').replaceChildren();
  const dot = document.createElement('span'); 
  dot.className = 'dot';
  $id('camera-state').append(dot, document.createTextNode(text));
  $id('camera-state').classList.toggle('is-live', live);
}

function drawBoxes() {
  const canvas = $id('overlay'), context = canvas.getContext('2d');
  const width = $id('viewer').clientWidth, height = $id('viewer').clientHeight;
  canvas.width = width * devicePixelRatio; 
  canvas.height = height * devicePixelRatio;
  context.scale(devicePixelRatio, devicePixelRatio); 
  context.clearRect(0, 0, width, height);

  if (!running || !$id('show-boxes').checked || !$id('camera').videoWidth) return;

  const vw = $id('camera').videoWidth, vh = $id('camera').videoHeight;
  const scale = Math.min(width / vw, height / vh);
  const displayW = vw * scale, displayH = vh * scale;
  const offsetX = (width - displayW) / 2, offsetY = (height - displayH) / 2;

  for (const detection of boxes) {
    if (!detection.box) continue;
    const [x1, y1, x2, y2] = detection.box;
    const x = offsetX + x1 * displayW, y = offsetY + y1 * displayH;
    const w = (x2 - x1) * displayW, h = (y2 - y1) * displayH;
    const color = colors[detection.class_id % colors.length];

    context.strokeStyle = color; 
    context.lineWidth = 2; 
    context.strokeRect(x, y, w, h);

    const label = `${detection.name} ${Math.round(detection.confidence * 100)}%`;
    context.font = '600 12px Segoe UI, sans-serif';
    const labelW = Math.min(context.measureText(label).width + 14, width);
    const labelX = Math.max(0, Math.min(x, width - labelW));
    const labelY = Math.max(0, y - 25);

    context.fillStyle = color; 
    context.fillRect(labelX, labelY, labelW, 23);
    context.fillStyle = '#fff'; 
    context.fillText(label, labelX + 7, labelY + 16, labelW - 12);
  }
}

function resetResults() {
  token = null; 
  boxes = []; 
  clearTimeout(clearBoxesTimer); 
  drawBoxes();
  $id('save').disabled = true; 
  $id('snapshot').disabled = true; 
  $id('save-note').hidden = true;
  $id('count').textContent = '0'; 
  $id('result-total').textContent = '0';
  $id('result-summary').textContent = 'Esperando el próximo análisis';
  $id('timing').textContent = '-'; 
  $id('analysis-rate').textContent = 'Esperando análisis';
  $id('detections').replaceChildren();

  const empty = document.createElement('li'); 
  empty.className = 'empty-results';
  const title = document.createElement('strong'); 
  title.textContent = 'Esperando resultados';
  const detail = document.createElement('span'); 
  detail.textContent = 'El primer análisis de cada calidad incluye la carga del modelo.';
  empty.append(icon('target'), title, detail); 
  $id('detections').append(empty);
}

async function post(url, data, signal) {
  const response = await fetch(url, { method: 'POST', body: data, signal, headers: {'X-CSRFToken': csrf} });
  if (!response.headers.get('content-type')?.includes('application/json')) {
    throw new Error('El servidor no está disponible. Revisa que la aplicación siga encendida.');
  }
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'No se pudo completar la operación.');
  return result;
}

async function renderDetections(result, currentGeneration) {
  const image = new Image(); 
  image.src = result.image;
  try { await image.decode(); } catch {}

  if (generation !== currentGeneration) return;
  $id('detections').replaceChildren();

  const groups = groupDetections(result.detections);
  $id('result-summary').textContent = `${result.detections.length} objetos · ${groups.length} categorías`;

  for (const group of groups) {
    const detection = group.items[0];
    const item = document.createElement('li'); 
    item.className = 'detection-item grouped-detection';
    item.style.setProperty('--item-color', colors[detection.class_id % colors.length]);

    if (detection.box && image.naturalWidth) {
      const [x1, y1, x2, y2] = detection.box;
      const crop = document.createElement('canvas'); 
      crop.width = 96; 
      crop.height = 96;
      crop.getContext('2d').drawImage(
        image, 
        Math.max(0, x1) * image.width, 
        Math.max(0, y1) * image.height, 
        Math.max(.001, x2 - x1) * image.width, 
        Math.max(.001, y2 - y1) * image.height, 
        0, 0, 96, 96
      );
      const thumbnail = document.createElement('img'); 
      thumbnail.src = crop.toDataURL('image/jpeg', .7); 
      thumbnail.className = 'object-thumbnail'; 
      thumbnail.alt = ''; 
      item.append(thumbnail);
    } else { 
      item.append(icon('box')); 
    }

    const info = document.createElement('div'); 
    info.className = 'object-info';
    const name = document.createElement('strong'); 
    name.textContent = detection.name;
    const quantity = document.createElement('span'); 
    quantity.className = 'category-quantity';
    quantity.textContent = `${group.items.length} ${group.items.length === 1 ? 'objeto' : 'objetos'}`;
    
    const titleRow = document.createElement('div'); 
    titleRow.className = 'object-title-row'; 
    titleRow.append(name, quantity);

    const percentage = Math.round(group.confidence * 100);
    const confidence = document.createElement('small'); 
    confidence.className = 'confidence-caption';
    const label = document.createElement('span'); 
    label.textContent = group.items.length > 1 ? 'Confianza media' : 'Confianza';
    const value = document.createElement('b'); 
    value.textContent = `${percentage} %`;
    confidence.append(label, value);

    const meter = document.createElement('div'); 
    meter.className = 'confidence-meter';
    meter.setAttribute('role', 'progressbar'); 
    meter.setAttribute('aria-label', `${detection.name}: ${label.textContent.toLowerCase()}`);
    meter.setAttribute('aria-valuemin', '0'); 
    meter.setAttribute('aria-valuemax', '100'); 
    meter.setAttribute('aria-valuenow', String(percentage));
    
    const fill = document.createElement('span'); 
    fill.style.width = `${percentage}%`; 
    meter.append(fill);

    info.append(titleRow, confidence, meter);
    const check = document.createElement('span'); 
    check.className = 'object-check'; 
    check.append(icon('check'));
    item.append(info, check); 
    $id('detections').append(item);
  }

  if (!result.detections.length) {
    const empty = document.createElement('li'); 
    empty.className = 'empty-results';
    const title = document.createElement('strong'); 
    title.textContent = 'Sin objetos detectados';
    const hint = document.createElement('span'); 
    hint.textContent = 'Prueba otra posición, mejora la iluminación o reduce la confianza mínima.';
    empty.append(icon('target'), title, hint); 
    $id('detections').append(empty);
  }
}

async function analyze(blob, currentGeneration, source = 'upload') {
  busy = true; 
  const requestedQuality = quality;
  controller = new AbortController();
  const timeout = setTimeout(() => controller?.abort(), 120000);
  const startTime = performance.now();

  try {
    const data = new FormData(); 
    data.append('frame', blob, 'frame.jpg');
    data.append('confidence', Number($id('confidence').value) / 100); 
    data.append('quality', requestedQuality); 
    data.append('source', source);

    const result = await post('/api/detect/', data, controller.signal);
    if (currentGeneration !== generation || (source === 'camera' && requestedQuality !== quality)) return;

    const elapsed = performance.now() - startTime;
    if (originalUrl) URL.revokeObjectURL(originalUrl);
    originalUrl = URL.createObjectURL(blob);

    $id('comparison-before').src = originalUrl;
    $id('result').src = result.image; 
    $id('result').hidden = false;
    $id('comparison').hidden = running;
    $id('placeholder').hidden = true; 
    
    boxes = result.detections;
    drawBoxes(); 
    clearTimeout(clearBoxesTimer);
    clearBoxesTimer = setTimeout(() => { boxes = []; drawBoxes(); }, 2500);

    $id('count').textContent = result.detections.length; 
    $id('result-total').textContent = result.detections.length;
    $id('timing').textContent = `${result.processing_ms} ms`;
    $id('analysis-rate').textContent = `${(1000 / Math.max(1, elapsed)).toFixed(1)} análisis/s · ${qualityLabels[requestedQuality]}`;

    token = result.can_save ? result.token : null;
    $id('save').disabled = !token; 
    $id('snapshot').disabled = !token;
    $id('save-note').hidden = Boolean(token); 
    $id('back-welcome').hidden = false;
    activeQuality = requestedQuality;

    await renderDetections(result, currentGeneration);
    if (currentGeneration !== generation) return;

    status(running ? 'Cámara en vivo. Las cajas corresponden al último análisis recibido.' : (token ? 'Análisis completado. Puedes guardar este resultado.' : 'Ejemplo analizado. Explora la comparación; esta imagen no se guarda.'));
    systemState(running ? 'Detección activa' : 'Análisis completado', `${qualityLabels[requestedQuality]} ${qualitySizes[requestedQuality]} px`);
    cameraState(running ? 'Detectando...' : 'Imagen analizada', running);

  } catch (error) {
    if (currentGeneration === generation) {
      const message = error.name === 'AbortError' ? 'El análisis tardó demasiado. Prueba el modo Rápido.' : error.message;
      if (source === 'camera') {
        if (requestedQuality !== quality) return;
        boxes = [];
        clearTimeout(clearBoxesTimer);
        drawBoxes();
        status(`Cámara en vivo. ${message}`);
        systemState('Análisis no disponible', 'La cámara sigue activa. Reintentando el análisis…');
        cameraState('En vivo', true);
        return false;
      }
      stop();
      status(message);
      systemState('Análisis no disponible', 'No se pudo completar el análisis');
      cameraState('Sin análisis');
    }
  } finally {
    clearTimeout(timeout); 
    controller = null; 
    busy = false;
    $id('start').disabled = running; 
    $id('file').disabled = running;
  }
}

function stop() {
  running = false; 
  generation += 1; 
  controller?.abort();
  stream?.getTracks().forEach(track => track.stop()); 
  stream = null;
  $id('camera').srcObject = null; 
  $id('camera').hidden = true;
  $id('live-label').hidden = true; 
  $id('comparison').hidden = !token; 
  $id('placeholder').hidden = Boolean(token);

  boxes = []; 
  clearTimeout(clearBoxesTimer); 
  drawBoxes();
  $id('start').disabled = busy; 
  $id('stop').disabled = true; 
  $id('file').disabled = busy;

  cameraState('En pausa'); 
  systemState('Cámara detenida', token ? 'Último resultado disponible' : 'Listo para iniciar');
  $id('viewer-caption').textContent = token ? 'Último resultado analizado' : 'Vista de cámara';
}

async function loop(currentGeneration) {
  if (!running || currentGeneration !== generation) return;
  const iterationStart = performance.now();
  let retryDelay = 16;

  if (!busy && $id('camera').readyState >= 2) {
    const canvas = $id('frame'), video = $id('camera');
    const frameQuality = quality;
    canvas.width = qualitySizes[frameQuality];
    canvas.height = Math.round(canvas.width * video.videoHeight / video.videoWidth);
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', frameQuality === 'fast' ? .65 : .8));
    if (blob && running && currentGeneration === generation && frameQuality === quality) {
      const analyzed = await analyze(blob, currentGeneration, 'camera');
      if (analyzed === false) retryDelay = 3000;
    }
  }

  if (running && currentGeneration === generation) {
    setTimeout(() => loop(currentGeneration), Math.max(retryDelay, 100 - (performance.now() - iterationStart)));
  }
}

$id('start').addEventListener('click', async () => {
  if (busy || running) return;
  const currentGeneration = ++generation; 
  $id('start').disabled = true;
  status('Solicitando acceso a la cámara...');

  try {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error('Abre la aplicación desde localhost para usar la cámara.');
    const newStream = await navigator.mediaDevices.getUserMedia({video: {width: {ideal: 640}, height: {ideal: 480}, frameRate: {ideal: 30}}, audio: false});
    if (currentGeneration !== generation) { 
      newStream.getTracks().forEach(track => track.stop()); 
      return; 
    }
    stream = newStream; 
    $id('camera').srcObject = stream; 
    $id('camera').hidden = false;
    await $id('camera').play(); 
    running = true; 
    resetResults(); 
    $id('comparison').hidden = true;
    $id('placeholder').hidden = true; 
    $id('live-label').hidden = false;
    $id('stop').disabled = false; 
    $id('file').disabled = true; 
    $id('back-welcome').hidden = false;
    $id('viewer-caption').textContent = 'Video en vivo · análisis independiente';
    status('Cámara activa. Cargando detector; el primer análisis puede tardar.');
    systemState('Preparando análisis', 'Video en vivo disponible'); 
    cameraState('Cargando modelo...', true); 
    loop(currentGeneration);
  } catch (error) { 
    stop(); 
    status(error.message || 'No se pudo acceder a la cámara.'); 
  }
});

$id('stop').addEventListener('click', () => { 
  stop(); 
  status('Cámara detenida. Puedes guardar el último resultado analizado.'); 
});

$id('file').addEventListener('change', async () => {
  const file = $id('file').files[0]; 
  if (!file || busy) return;
  if (file.size > 2 * 1024 * 1024) { 
    status('Selecciona una imagen de hasta 2 MB.'); 
    return; 
  }
  stop(); 
  resetResults(); 
  $id('comparison').hidden = true; 
  $id('placeholder').hidden = false;
  $id('start').disabled = true; 
  $id('file').disabled = true;
  cameraState('Analizando imagen...'); 
  systemState('Procesando imagen', qualityLabels[quality]); 
  status('Analizando imagen...');
  await analyze(file, generation); 
  $id('file').value = '';
});

async function loadExample() {
  if (busy || running) return;
  stop(); 
  resetResults(); 
  busy = true;
  $id('explore').disabled = true; 
  $id('explore').setAttribute('aria-busy', 'true');
  const currentGeneration = generation;

  cameraState('Analizando ejemplo...'); 
  systemState('Procesando ejemplo', qualityLabels[quality]);
  $id('viewer-caption').textContent = 'Imagen de ejemplo · análisis real';
  status('Analizando la imagen de ejemplo con el detector. La primera carga puede tardar.');
  $id('start').disabled = true; 
  $id('file').disabled = true;

  try {
    const response = await fetch($id('comparison').dataset.sampleUrl);
    if (!response.ok) throw new Error('No se pudo cargar la imagen de ejemplo.');
    const blob = await response.blob();
    if (currentGeneration !== generation) return;
    await analyze(blob, currentGeneration, 'example');
  } catch (error) {
    if (currentGeneration === generation) {
      status(error.message); 
      cameraState('Ejemplo no disponible'); 
      systemState('No se pudo analizar', 'Intenta nuevamente');
    }
  } finally {
    busy = false; 
    $id('start').disabled = running; 
    $id('file').disabled = running;
    $id('explore').disabled = false; 
    $id('explore').removeAttribute('aria-busy');
  }
}

async function saveResult() {
  if (!token) return;
  const selectedToken = token; 
  $id('save').disabled = true; 
  $id('snapshot').disabled = true;

  try { 
    const data = new FormData(); 
    data.append('token', selectedToken); 
    await post('/api/save/', data); 
    status('Captura guardada en el historial. Se guardó el último frame analizado.'); 
  } catch (error) { 
    status(error.message); 
  } finally { 
    $id('save').disabled = !token; 
    $id('snapshot').disabled = !token; 
  }
}

$id('save').addEventListener('click', saveResult);
$id('snapshot').addEventListener('click', saveResult);
$id('confidence').addEventListener('input', () => { 
  $id('confidence-value').textContent = `${$id('confidence').value} %`; 
});
$id('show-boxes').addEventListener('change', drawBoxes);

for (const button of document.querySelectorAll('[data-quality]')) {
  button.addEventListener('click', () => {
    quality = button.dataset.quality;
    for (const option of document.querySelectorAll('[data-quality]')) {
      option.classList.toggle('selected', option === button); 
      option.setAttribute('aria-pressed', String(option === button));
    }
    $id('quality-help').textContent = `${qualityLabels[quality]}: análisis a ${qualitySizes[quality]} px. La primera ejecución de cada modo carga su modelo; más detalle puede reducir la velocidad.`;
    if (running && activeQuality !== quality) { 
      boxes = []; 
      drawBoxes(); 
      status(`Cambiando a ${qualityLabels[quality]}... El siguiente análisis aplicará esta calidad.`); 
      cameraState('Cambiando calidad...', true); 
    }
  });
}

$id('fullscreen').addEventListener('click', async () => {
  try { 
    if (document.fullscreenElement) await document.exitFullscreen(); 
    else await $id('viewer').requestFullscreen(); 
  } catch { 
    status('Tu navegador no permite ampliar esta vista.'); 
  }
});

window.addEventListener('resize', drawBoxes); 
document.addEventListener('fullscreenchange', drawBoxes);
window.addEventListener('pagehide', stop);

function updateComparison(value) {
  const position = Math.max(0, Math.min(100, Number(value)));
  $id('comparison').style.setProperty('--split', `${position}%`);
  $id('comparison-slider').value = position;
  $id('comparison-slider').setAttribute('aria-valuetext', `${Math.round(position)} % sin detección y ${Math.round(100 - position)} % con detección`);
}

$id('comparison-slider').addEventListener('input', event => updateComparison(event.target.value));

function dragComparison(event) {
  const rect = $id('comparison').getBoundingClientRect();
  if (rect.width) updateComparison(((event.clientX - rect.left) / rect.width) * 100);
}

$id('comparison').addEventListener('pointerdown', event => {
  if (event.button !== 0) return;
  $id('comparison-slider').focus({preventScroll: true});
  $id('comparison').setPointerCapture(event.pointerId); 
  dragComparison(event);
});

$id('comparison').addEventListener('pointermove', event => {
  if ($id('comparison').hasPointerCapture(event.pointerId)) dragComparison(event);
});

for (const type of ['pointerup', 'pointercancel']) {
  $id('comparison').addEventListener(type, event => {
    if ($id('comparison').hasPointerCapture(event.pointerId)) $id('comparison').releasePointerCapture(event.pointerId);
  });
}

window.addEventListener('pagehide', () => { if (originalUrl) URL.revokeObjectURL(originalUrl); });
$id('explore').addEventListener('click', loadExample);

$id('back-welcome').addEventListener('click', () => {
  stop(); 
  resetResults();
  $id('comparison').hidden = true; 
  $id('placeholder').hidden = false;
  $id('back-welcome').hidden = true;
  $id('result-summary').textContent = 'Resultados del último análisis';
  $id('analysis-rate').textContent = 'Sin análisis aún';
  $id('viewer-caption').textContent = 'Vista de cámara';
  cameraState('En espera'); 
  systemState('Listo para iniciar', 'Cámara apagada');
  status('Bienvenido de nuevo. Explora el ejemplo o utiliza tu propia cámara o imagen.');
  if (originalUrl) URL.revokeObjectURL(originalUrl); 
  originalUrl = null;
  $id('comparison-before').removeAttribute('src'); 
  $id('result').removeAttribute('src');
  updateComparison(50);
  $id('explore').focus({preventScroll: true});
});
