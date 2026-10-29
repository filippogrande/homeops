async function api(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

async function refresh(name) {
  const badge = document.querySelector(`.state[data-name="${name}"]`);
  if (!badge) {
    return;
  }
  try {
    const status = await api(`/api/services/${name}/status`);
    badge.textContent = status.health;
    badge.dataset.health = status.health;
  } catch (error) {
    badge.textContent = 'errore';
  }
}

async function render() {
  const services = await api('/api/services');
  const container = document.getElementById('services');
  container.innerHTML = '';
  for (const service of services) {
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <header>
        <h2>${service.name}</h2>
        <span class="state" data-name="${service.name}">...</span>
      </header>
      <div class="actions">
        <button data-action="update">Aggiorna</button>
        <button data-action="start">Avvia</button>
        <button data-action="stop">Ferma</button>
        <button data-action="logs">Log</button>
      </div>
      <pre class="logs" hidden></pre>
    `;
    container.appendChild(card);
    refresh(service.name);
  }
  document.getElementById('status-line').textContent = 'pronto';
}

document.addEventListener('click', async (event) => {
  const button = event.target.closest('button[data-action]');
  if (!button) {
    return;
  }
  const card = button.closest('.card');
  const name = card.querySelector('h2').textContent;
  const action = button.dataset.action;
  button.disabled = true;
  try {
    if (action === 'logs') {
      const result = await api(`/api/services/${name}/logs?tail=100`);
      const pre = card.querySelector('.logs');
      pre.textContent = result.logs;
      pre.hidden = !pre.hidden;
    } else {
      await api(`/api/services/${name}/${action}`, { method: 'POST' });
      await refresh(name);
    }
  } catch (error) {
    alert(`Errore ${name}: ${error.message}`);
  } finally {
    button.disabled = false;
  }
});

render().catch((error) => {
  document.getElementById('status-line').textContent = `errore: ${error.message}`;
});
