// SPort - real-time port monitor
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

// =====================================================================
// i18n
// =====================================================================
const I18N = {
  en: {
    'brand.subtitle': 'real-time port monitor',
    'stat.listening': 'listening',
    'stat.processes': 'processes',
    'stat.multiport': 'multi-port',
    'search.placeholder': 'Search by port, process name, PID, or address…',
    'filter.all': 'All',
    'filter.tcp': 'TCP',
    'filter.udp': 'UDP',
    'filter.common': 'Common ports',
    'filter.duplicate': 'Multi-port',
    'toolbar.autorefresh': 'Auto-refresh',
    'toolbar.refresh': 'Refresh',
    'col.port': 'Port',
    'col.protocol': 'Protocol',
    'col.address': 'Address',
    'col.pid': 'PID',
    'col.process': 'Process',
    'col.user': 'User',
    'col.tag': 'Tag',
    'col.action': 'Action',
    'col.action.detail': 'Detail',
    'col.action.kill': 'Kill',
    'col.action.protected': 'Protected process',
    'col.action.allInterfaces': 'Binding to all interfaces',
    'col.action.ports': 'ports',
    'empty.noresults': 'No matches for the current filter.',
    'empty.noports': 'No listening ports found.',
    'empty.allHidden': 'All ports are system services. Toggle off \u201cHide system\u201d to see them.',
    'empty.loading': 'Loading ports…',
    'dup.warn': 'Process is using multiple ports',
    'confirm.terminate': 'Are you sure you want to terminate "{name}" (PID {pid})?',
    'confirm.force': 'Are you sure you want to force kill "{name}" (PID {pid})?',
    'toast.killSuccess': '\u2713 {action} {name} (PID {pid})',
    'toast.killError': '\u2717 {error}',
    'toast.scanFailed': 'Scan failed: {error}',
    'toast.processGone': 'Process {pid} no longer exists',
    'detail.error.accessDenied': 'Access denied',
    'detail.error.adminHint': 'This is a protected system process. Run SPort as Administrator to view full details.',
    'detail.error.kernelTitle': 'Kernel-protected process',
    'detail.error.kernelHint': 'This process is protected by Windows itself. Even Administrator access is blocked for it \u2014 this is a Windows security feature, not an SPort limitation.',
    'detail.warn.partialTitle': 'Limited information',
    'detail.warn.partialHint': 'This is a protected Windows process. SPort has only partial access; some fields (memory, command line, owner) cannot be retrieved.',
    'detail.status.protected': 'Protected',
    'detail.field.port': 'Port',
    'footer.hint': 'Press / to search \u00b7 R to refresh \u00b7 Esc to clear',
    'footer.tagline': 'SPort \u00b7 runs locally \u00b7 no data leaves your machine',
    'live': 'LIVE',
    'live.paused': 'PAUSED',
    'updated': 'updated {time}',
    'scanning': 'scanning\u2026',
    'kill.action.terminate': 'terminate',
    'kill.action.kill': 'force kill',
    'kill.done.terminate': 'terminated',
    'kill.done.kill': 'force-killed',
    'detail.title': 'Process detail',
    'detail.field.process': 'Process',
    'detail.field.pid': 'PID',
    'detail.field.status': 'Status',
    'detail.field.user': 'User',
    'detail.field.memory': 'Memory',
    'detail.field.cpu': 'CPU',
    'detail.field.started': 'Started',
    'detail.field.cwd': 'CWD',
    'detail.field.cmdline': 'Command',
    'detail.field.exe': 'Executable',
    'detail.unknown': '\u2014',
    'lang.toggle': 'Language',
    'modal.close': 'Close',
    'modal.refresh': 'Refresh',
    'toolbar.hideSystem': 'Hide system',
    'toolbar.settings': 'Filter settings',
    'stat.hidden': 'hidden',
    'settings.title': 'Filter settings',
    'settings.builtinLabel': 'Built-in system processes',
    'settings.customLabel': 'Your additions',
    'settings.addPlaceholder': 'Add process name (e.g. myapp.exe)',
    'settings.add': 'Add',
    'settings.remove': 'Remove',
    'settings.empty': 'No custom additions',
    'settings.reset': 'Reset to defaults',
    'settings.processCount': '{count} process',
    'settings.processCountPlural': '{count} processes',
    'settings.userCount': '{count} account',
    'settings.userCountPlural': '{count} accounts',
  },
  zh: {
    'brand.subtitle': '实时端口监控',
    'stat.listening': '监听中',
    'stat.processes': '进程',
    'stat.multiport': '多端口',
    'search.placeholder': '搜索端口、进程名、PID 或地址…',
    'filter.all': '全部',
    'filter.tcp': 'TCP',
    'filter.udp': 'UDP',
    'filter.common': '常用端口',
    'filter.duplicate': '多端口',
    'toolbar.autorefresh': '自动刷新',
    'toolbar.refresh': '刷新',
    'col.port': '端口',
    'col.protocol': '协议',
    'col.address': '地址',
    'col.pid': 'PID',
    'col.process': '进程',
    'col.user': '用户',
    'col.tag': '标签',
    'col.action': '操作',
    'col.action.detail': '详情',
    'col.action.kill': '结束',
    'col.action.protected': '受保护进程',
    'col.action.allInterfaces': '绑定全部接口',
    'col.action.ports': '个端口',
    'empty.noresults': '当前筛选无匹配项。',
    'empty.noports': '未发现监听中的端口。',
    'empty.allHidden': '所有端口都是系统服务。关闭「隐藏系统端口」即可显示。',
    'empty.loading': '加载端口中…',
    'dup.warn': '进程占用了多个端口',
    'confirm.terminate': '确认要结束 "{name}" (PID {pid}) 吗?',
    'confirm.force': '确认要强制结束 "{name}" (PID {pid}) 吗?',
    'toast.killSuccess': '\u2713 已{action} {name} (PID {pid})',
    'toast.killError': '\u2717 {error}',
    'toast.scanFailed': '扫描失败: {error}',
    'toast.processGone': '进程 {pid} 已不存在',
    'detail.error.accessDenied': '权限不足',
    'detail.error.adminHint': '这是受保护的系统进程。请以管理员身份运行 SPort 以查看完整信息。',
    'detail.error.kernelTitle': '内核保护进程',
    'detail.error.kernelHint': '此进程受 Windows 内核自身保护。即使以管理员身份运行也会被阻止 \u2014 这是 Windows 的安全机制，不是 SPort 的限制。',
    'detail.warn.partialTitle': '信息有限',
    'detail.warn.partialHint': '这是 Windows 受保护的进程。SPort 只能获取部分信息（内存、命令行、所有者等无法读取）。',
    'detail.status.protected': '受保护',
    'detail.field.port': '端口',
    'footer.hint': '按 / 搜索 \u00b7 R 刷新 \u00b7 Esc 清除',
    'footer.tagline': 'SPort \u00b7 本地运行 \u00b7 数据不离开本机',
    'live': '实时',
    'live.paused': '已暂停',
    'updated': '更新于 {time}',
    'scanning': '扫描中…',
    'kill.action.terminate': '结束',
    'kill.action.kill': '强制结束',
    'kill.done.terminate': '结束',
    'kill.done.kill': '强制结束',
    'detail.title': '进程详情',
    'detail.field.process': '进程',
    'detail.field.pid': 'PID',
    'detail.field.status': '状态',
    'detail.field.user': '用户',
    'detail.field.memory': '内存',
    'detail.field.cpu': 'CPU',
    'detail.field.started': '启动时间',
    'detail.field.cwd': '工作目录',
    'detail.field.cmdline': '命令行',
    'detail.field.exe': '可执行文件',
    'detail.unknown': '\u2014',
    'lang.toggle': '语言',
    'modal.close': '关闭',
    'modal.refresh': '刷新',
    'toolbar.hideSystem': '隐藏系统端口',
    'toolbar.settings': '过滤设置',
    'stat.hidden': '已隐藏',
    'settings.title': '过滤设置',
    'settings.builtinLabel': '内置系统进程',
    'settings.customLabel': '自定义添加',
    'settings.addPlaceholder': '添加进程名 (如 myapp.exe)',
    'settings.add': '添加',
    'settings.remove': '移除',
    'settings.empty': '暂无自定义',
    'settings.reset': '恢复默认',
    'settings.processCount': '{count} 个进程',
    'settings.processCountPlural': '{count} 个进程',
    'settings.userCount': '{count} 个账户',
    'settings.userCountPlural': '{count} 个账户',
  },
};

const COMMON_PORTS_I18N = {
  en: {
    80: 'HTTP', 443: 'HTTPS', 3000: 'React/Node', 3306: 'MySQL',
    4000: 'Node alt', 5000: 'Flask/Python', 5173: 'Vite', 5432: 'PostgreSQL',
    6379: 'Redis', 8000: 'Django/FastAPI', 8080: 'HTTP alt', 8443: 'HTTPS alt',
    9000: 'PHP-FPM', 9090: 'Prometheus', 9200: 'Elasticsearch',
    27017: 'MongoDB', 28017: 'MongoDB Web', 50000: 'SAP', 33060: 'MySQL X',
  },
  zh: {
    80: 'HTTP', 443: 'HTTPS', 3000: 'React/Node', 3306: 'MySQL 数据库',
    4000: 'Node 备选', 5000: 'Flask/Python', 5173: 'Vite', 5432: 'PostgreSQL',
    6379: 'Redis 缓存', 8000: 'Django/FastAPI', 8080: 'HTTP 备选', 8443: 'HTTPS 备选',
    9000: 'PHP-FPM', 9090: 'Prometheus', 9200: 'Elasticsearch',
    27017: 'MongoDB', 28017: 'MongoDB Web', 50000: 'SAP', 33060: 'MySQL X 协议',
  },
};

// One-time migration from legacy `portfix.*` localStorage keys to `sport.*`
// (rename from Portfix → SPort). Runs once on page load; old keys are removed.
(function migrateLegacyKeys() {
  try {
    for (const k of ['lang', 'hideSystem', 'customSystem']) {
      const nk = `sport.${k}`;
      const ok = `portfix.${k}`;
      if (localStorage.getItem(nk) == null && localStorage.getItem(ok) != null) {
        localStorage.setItem(nk, localStorage.getItem(ok));
        localStorage.removeItem(ok);
      }
    }
  } catch {}
})();

let currentLang = (() => {
  try {
    const saved = localStorage.getItem('sport.lang');
    if (saved && I18N[saved]) return saved;
  } catch {}
  return 'zh';
})();

// Filter state: hide-system toggle + custom additions
let hideSystem = (() => {
  try { return localStorage.getItem('sport.hideSystem') === 'true'; }
  catch { return false; }
})();

let customSystem = (() => {
  try {
    const raw = localStorage.getItem('sport.customSystem');
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr.filter(x => typeof x === 'string') : [];
  } catch { return []; }
})();

let builtinSystem = { processes: [], users: [] };

function saveCustomSystem() {
  try { localStorage.setItem('sport.customSystem', JSON.stringify(customSystem)); } catch {}
}

function isSystemRow(row) {
  if (row.is_system) return true;
  if (!row.process) return false;
  const proc = row.process.toLowerCase();
  const base = proc.endsWith('.exe') ? proc.slice(0, -4) : proc;
  for (const c of customSystem) {
    const cL = c.toLowerCase();
    const cBase = cL.endsWith('.exe') ? cL.slice(0, -4) : cL;
    if (proc === cL || base === cBase) return true;
  }
  return false;
}

function t(key, params = {}) {
  let s = (I18N[currentLang] && I18N[currentLang][key])
    || (I18N.en[key])
    || key;
  return s.replace(/\{(\w+)\}/g, (_, k) => params[k] !== undefined ? params[k] : `{${k}}`);
}

function applyI18n() {
  document.documentElement.lang = currentLang === 'zh' ? 'zh-CN' : 'en';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    el.title = t(el.dataset.i18nTitle);
  });
  document.querySelectorAll('[data-i18n-aria]').forEach(el => {
    el.setAttribute('aria-label', t(el.dataset.i18nAria));
  });
}

function setLanguage(lang) {
  if (!I18N[lang]) return;
  currentLang = lang;
  try { localStorage.setItem('sport.lang', lang); } catch {}
  document.querySelectorAll('.lang-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.lang === lang);
    b.setAttribute('aria-pressed', b.dataset.lang === lang ? 'true' : 'false');
  });
  applyI18n();
  // Re-render to update port tags, toasts confirmation text, etc.
  render(state.data);
}

function commonPortName(port) {
  return (COMMON_PORTS_I18N[currentLang] && COMMON_PORTS_I18N[currentLang][port])
    || (COMMON_PORTS_I18N.en[port])
    || '';
}

// =====================================================================
// App state
// =====================================================================
const els = {
  rows: $('#rows'),
  search: $('#search'),
  chips: $$('.chip'),
  autorefresh: $('#autorefresh'),
  interval: $('#interval'),
  btnRefresh: $('#btn-refresh'),
  lastScan: $('#last-scan'),
  liveInd: $('.live-indicator'),
  liveText: $('.live-text'),
  hideSystem: $('#hide-system'),
  stat: {
    total: $('#stat-total'),
    tcp: $('#stat-tcp'),
    udp: $('#stat-udp'),
    procs: $('#stat-procs'),
    dups: $('#stat-dups'),
    hidden: $('#stat-hidden'),
  },
  modal: $('#detail-modal'),
  modalBody: $('#detail-body'),
  modalClose: $('#modal-close'),
  settingsModal: $('#settings-modal'),
  settingsBody: $('#settings-body'),
  settingsClose: $('#settings-close'),
  settingsBtn: $('#btn-settings'),
  customInput: $('#custom-input'),
  customAdd: $('#custom-add'),
  customList: $('#custom-list'),
  builtinList: $('#builtin-list'),
  userList: $('#user-list'),
};

const state = {
  data: { items: [], summary: {}, duplicates: {} },
  filter: 'all',
  sort: { key: 'port', dir: 'asc' },
  search: '',
  timer: null,
  previousKeys: new Set(),
};

// =====================================================================
// API
// =====================================================================
async function fetchPorts() {
  try {
    const r = await fetch('/api/ports');
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    showToast(t('toast.scanFailed', { error: e.message }), 'error');
    return null;
  }
}

async function killProcess(pid, force = false) {
  const r = await fetch('/api/kill', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pid, force }),
  });
  return r.json();
}

// =====================================================================
// Render
// =====================================================================
function rowKey(r) { return `${r.protocol}:${r.address}:${r.port}:${r.pid}`; }

function render(data) {
  if (!data) return;
  const prev = state.previousKeys;
  const next = new Set(data.items.map(rowKey));

  state.data = data;
  const hiddenCount = data.summary.hidden ?? data.items.filter(r => isSystemRow(r)).length;
  els.stat.total.textContent = data.summary.total ?? 0;
  els.stat.tcp.textContent = data.summary.tcp ?? 0;
  els.stat.udp.textContent = data.summary.udp ?? 0;
  els.stat.procs.textContent = data.summary.processes ?? 0;
  els.stat.dups.textContent = data.summary.duplicate_pids ?? 0;
  if (els.stat.hidden) {
    els.stat.hidden.textContent = hiddenCount;
    els.stat.hidden.classList.toggle('mute', !hideSystem || hiddenCount === 0);
    els.stat.hidden.classList.toggle('active', hideSystem && hiddenCount > 0);
  }
  els.lastScan.textContent = t('updated', { time: formatTime(data.summary.scanned_at) });

  let items = data.items.slice();

  if (state.search) {
    const q = state.search.toLowerCase();
    items = items.filter(r =>
      String(r.port).includes(q) ||
      r.process.toLowerCase().includes(q) ||
      String(r.pid).includes(q) ||
      r.address.toLowerCase().includes(q) ||
      (r.common && r.common.toLowerCase().includes(q))
    );
  }

  if (state.filter === 'tcp') items = items.filter(r => r.protocol === 'TCP');
  else if (state.filter === 'udp') items = items.filter(r => r.protocol === 'UDP');
  else if (state.filter === 'common') items = items.filter(r => commonPortName(r.port));
  else if (state.filter === 'duplicate') items = items.filter(r => data.duplicates[r.pid]);

  if (hideSystem) items = items.filter(r => !isSystemRow(r));

  const { key, dir } = state.sort;
  const mult = dir === 'asc' ? 1 : -1;
  items.sort((a, b) => {
    const va = a[key], vb = b[key];
    if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * mult;
    return String(va || '').localeCompare(String(vb || ''), currentLang === 'zh' ? 'zh-CN' : 'en') * mult;
  });

  if (items.length === 0) {
    let emptyKey;
    if (data.items.length === 0) emptyKey = 'empty.noports';
    else if (hideSystem && hiddenCount > 0) emptyKey = 'empty.allHidden';
    else emptyKey = 'empty.noresults';
    els.rows.innerHTML = `<tr><td colspan="8" class="empty">${t(emptyKey)}</td></tr>`;
    state.previousKeys = next;
    return;
  }

  const dupLabelPorts = t('col.action.ports');
  const allIfacesTitle = t('col.action.allInterfaces');

  const html = items.map(r => {
    const isNew = !prev.has(rowKey(r));
    const isDup = data.duplicates[r.pid];
    const common = commonPortName(r.port);
    const tag = common
      ? `<span class="common-tag" title="${escapeAttr(common)}">${escapeHtml(common)}</span>`
      : (isDup ? `<span class="dup-warn" title="${escapeAttr(t('dup.warn'))}">\u26a0 ${data.duplicates[r.pid]} ${dupLabelPorts}</span>` : '<span style="color:var(--text-mute)">\u2014</span>');

    const addrDisplay = (r.address === '0.0.0.0' || r.address === '::')
      ? `<span style="color:var(--warn)" title="${escapeAttr(allIfacesTitle)}">*${escapeHtml(r.address)}</span>`
      : escapeHtml(r.address);

    const killDisabled = r.is_blocked || !r.pid;
    const killTitle = killDisabled ? t('col.action.protected') : '';

    return `
      <tr class="${isNew ? 'flash' : ''} ${isDup ? 'duplicate-pid' : ''}" data-pid="${r.pid}">
        <td><span class="port">${r.port}</span></td>
        <td><span class="proto-tag ${r.protocol.toLowerCase()}">${r.protocol}</span></td>
        <td class="addr">${addrDisplay}</td>
        <td class="pid">${r.pid || '\u2014'}</td>
        <td>
          <div class="proc">${escapeHtml(r.process)}</div>
          ${r.exe ? `<div class="proc-sub" title="${escapeAttr(r.exe)}">${escapeHtml(truncate(r.exe, 60))}</div>` : ''}
        </td>
        <td class="user">${escapeHtml(r.username || '\u2014')}</td>
        <td>${tag}</td>
        <td class="col-act">
          <button class="btn btn-ghost" data-action="detail" data-pid="${r.pid}">${t('col.action.detail')}</button>
          <button class="btn btn-ghost btn-danger" data-action="kill" data-pid="${r.pid}" data-name="${escapeAttr(r.process)}" ${killDisabled ? `disabled title="${escapeAttr(killTitle)}"` : ''}>${t('col.action.kill')}</button>
        </td>
      </tr>`;
  }).join('');

  els.rows.innerHTML = html;
  state.previousKeys = next;
}

function formatTime(iso) {
  if (!iso) return '\u2014';
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString(currentLang === 'zh' ? 'zh-CN' : 'en-US', { hour12: false });
  } catch { return '\u2014'; }
}

function truncate(s, n) {
  if (!s || s.length <= n) return s;
  return s.slice(0, n - 1) + '\u2026';
}

function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function escapeAttr(s) { return escapeHtml(s); }

// =====================================================================
// Events
// =====================================================================
els.search.addEventListener('input', (e) => {
  state.search = e.target.value.trim();
  render(state.data);
});

els.chips.forEach(chip => {
  chip.addEventListener('click', () => {
    els.chips.forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.filter = chip.dataset.filter;
    render(state.data);
  });
});

$$('th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.sort;
    if (state.sort.key === key) {
      state.sort.dir = state.sort.dir === 'asc' ? 'desc' : 'asc';
    } else {
      state.sort = { key, dir: 'asc' };
    }
    $$('th[data-sort]').forEach(t => t.classList.remove('sorted'));
    th.classList.add('sorted');
    const ind = th.querySelector('.sort-ind');
    if (ind) ind.textContent = state.sort.dir === 'asc' ? '\u25b2' : '\u25bc';
    render(state.data);
  });
});

els.btnRefresh.addEventListener('click', refresh);

els.autorefresh.addEventListener('change', () => {
  if (els.autorefresh.checked) startAuto();
  else stopAuto();
  els.liveText.textContent = t(els.autorefresh.checked ? 'live' : 'live.paused');
});

els.interval.addEventListener('change', () => {
  if (els.autorefresh.checked) startAuto();
});

if (els.hideSystem) {
  els.hideSystem.checked = hideSystem;
  els.hideSystem.addEventListener('change', () => {
    hideSystem = els.hideSystem.checked;
    try { localStorage.setItem('sport.hideSystem', String(hideSystem)); } catch {}
    render(state.data);
  });
}

els.rows.addEventListener('click', async (e) => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  const pid = parseInt(btn.dataset.pid, 10);
  const name = btn.dataset.name || '?';
  const tr = btn.closest('tr');
  const rowData = tr ? {
    pid,
    port: tr.querySelector('.port')?.textContent || '',
    protocol: tr.querySelector('.proto-tag')?.textContent || '',
    process: tr.querySelector('.proc')?.textContent || '',
    exe: tr.querySelector('.proc-sub')?.title || '',
    user: tr.querySelector('.user')?.textContent || '',
  } : null;

  if (btn.dataset.action === 'kill') {
    handleKill(pid, name, false);
  } else if (btn.dataset.action === 'detail') {
    showDetail(pid, rowData);
  }
});

async function handleKill(pid, name, force) {
  const msg = t(force ? 'confirm.force' : 'confirm.terminate', { name, pid });
  if (!confirm(msg)) return;
  const r = await killProcess(pid, force);
  if (r.ok) {
    const action = t('kill.done.' + (r.action || 'terminate'));
    showToast(t('toast.killSuccess', { action, name: r.name, pid }), 'success');
    setTimeout(refresh, 400);
  } else {
    showToast(t('toast.killError', { error: r.error || 'Failed' }), 'error');
  }
}

async function showDetail(pid, rowData = null) {
  try {
    const r = await fetch(`/api/process/${pid}`);
    if (r.status === 404) { showToast(t('toast.processGone', { pid }), 'info'); return; }
    if (r.status === 403) {
      showAccessDeniedModal(pid, rowData);
      return;
    }
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const p = await r.json();

    if (p.partial) {
      showPartialInfoModal(p, rowData);
      return;
    }

    const unk = t('detail.unknown');
    const fields = [
      { label: t('detail.field.process'), value: p.name || unk, mono: true },
      { label: t('detail.field.pid'), value: String(p.pid), mono: true },
      { label: t('detail.field.status'), value: p.status || unk, mono: true, badge: true },
      { label: t('detail.field.user'), value: p.username || unk, mono: true },
      { label: t('detail.field.memory'), value: `${p.memory_mb} MB`, mono: true },
      { label: t('detail.field.cpu'), value: `${p.cpu_percent}%`, mono: true },
      { label: t('detail.field.started'), value: p.create_time ? new Date(p.create_time * 1000).toLocaleString(currentLang === 'zh' ? 'zh-CN' : 'en-US') : unk, mono: true },
      { label: t('detail.field.cwd'), value: p.cwd || unk, mono: true },
      { label: t('detail.field.cmdline'), value: (p.cmdline && p.cmdline.length) ? p.cmdline.join(' ') : unk, mono: true, full: true },
      { label: t('detail.field.exe'), value: p.exe || unk, mono: true, full: true },
    ];

    els.modalBody.innerHTML = fields.map(f => `
      <div class="detail-row ${f.full ? 'detail-row-full' : ''}">
        <div class="detail-label">${escapeHtml(f.label)}</div>
        <div class="detail-value ${f.mono ? 'mono' : ''} ${f.badge ? 'badge' : ''}">${escapeHtml(f.value)}</div>
      </div>`).join('');

    openModal();
  } catch (e) {
    showToast(t('toast.scanFailed', { error: e.message }), 'error');
  }
}

// =====================================================================
// Modal
// =====================================================================
function openModal() {
  els.modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  els.modal.classList.remove('open');
  document.body.style.overflow = '';
}
function showAccessDeniedModal(pid, rowData) {
  const unk = t('detail.unknown');
  const ctxRows = [];
  ctxRows.push({ label: t('detail.field.pid'), value: String(pid), mono: true });
  if (rowData) {
    if (rowData.port) {
      ctxRows.push({ label: t('detail.field.port'), value: `${rowData.port} (${rowData.protocol || '?'})`, mono: true });
    }
    if (rowData.process && rowData.process !== '?' && rowData.process !== unk) {
      ctxRows.push({ label: t('detail.field.process'), value: rowData.process, mono: true });
    }
  }

  els.modalBody.innerHTML = `
    <div class="detail-error-banner">
      <div class="detail-error-icon" aria-hidden="true">\u26a0</div>
      <div class="detail-error-content">
        <div class="detail-error-title">${escapeHtml(t('detail.error.kernelTitle'))}</div>
        <div class="detail-error-hint">${escapeHtml(t('detail.error.kernelHint'))}</div>
      </div>
    </div>
    ${ctxRows.map(f => `
      <div class="detail-row">
        <div class="detail-label">${escapeHtml(f.label)}</div>
        <div class="detail-value ${f.mono ? 'mono' : ''}">${escapeHtml(f.value)}</div>
      </div>`).join('')}`;
  openModal();
}

function showPartialInfoModal(p, rowData) {
  const unk = t('detail.unknown');
  const fields = [
    { label: t('detail.field.process'), value: p.name || unk, mono: true },
    { label: t('detail.field.pid'), value: String(p.pid), mono: true },
    { label: t('detail.field.status'), value: t('detail.status.protected'), mono: true, badge: 'protected' },
  ];
  if (rowData && rowData.port) {
    fields.push({ label: t('detail.field.port'), value: `${rowData.port} (${rowData.protocol || '?'})`, mono: true });
  }
  if (p.exe) {
    fields.push({ label: t('detail.field.exe'), value: p.exe, mono: true, full: true });
  }

  els.modalBody.innerHTML = `
    <div class="detail-warn-banner">
      <div class="detail-warn-icon" aria-hidden="true">\u26a0</div>
      <div class="detail-warn-content">
        <div class="detail-warn-title">${escapeHtml(t('detail.warn.partialTitle'))}</div>
        <div class="detail-warn-hint">${escapeHtml(t('detail.warn.partialHint'))}</div>
      </div>
    </div>
    ${fields.map(f => `
      <div class="detail-row ${f.full ? 'detail-row-full' : ''}">
        <div class="detail-label">${escapeHtml(f.label)}</div>
        <div class="detail-value ${f.mono ? 'mono' : ''} ${f.badge ? 'badge-' + f.badge : ''}">${escapeHtml(f.value)}</div>
      </div>`).join('')}`;
  openModal();
}
els.modalClose.addEventListener('click', closeModal);
els.modal.addEventListener('click', (e) => {
  if (e.target === els.modal) closeModal();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && els.modal.classList.contains('open')) closeModal();
});

// =====================================================================
// Settings modal (filter list editor)
// =====================================================================
function openSettingsModal() {
  renderSettingsList();
  els.settingsModal.classList.add('open');
  document.body.style.overflow = 'hidden';
  setTimeout(() => els.customInput?.focus(), 50);
}
function closeSettingsModal() {
  els.settingsModal.classList.remove('open');
  document.body.style.overflow = '';
}

function renderSettingsList() {
  if (els.builtinList) {
    const procs = builtinSystem.processes || [];
    els.builtinList.innerHTML = procs.length
      ? procs.map(p => `<span class="settings-chip builtin">${escapeHtml(p)}</span>`).join('')
      : `<span class="settings-empty">\u2014</span>`;
  }
  if (els.userList) {
    const users = builtinSystem.users || [];
    els.userList.innerHTML = users.length
      ? users.map(u => `<span class="settings-chip builtin user">${escapeHtml(u)}</span>`).join('')
      : `<span class="settings-empty">\u2014</span>`;
  }
  if (els.customList) {
    els.customList.innerHTML = customSystem.length
      ? customSystem.map(c => `
        <span class="settings-chip custom">
          ${escapeHtml(c)}
          <button class="settings-chip-remove" data-remove="${escapeAttr(c)}" data-i18n-aria="settings.remove" title="${escapeAttr(t('settings.remove'))}" type="button">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </span>`).join('')
      : `<span class="settings-empty" data-i18n="settings.empty">${escapeHtml(t('settings.empty'))}</span>`;
  }
}

function addCustomProcess(name) {
  name = name.trim();
  if (!name) return false;
  const lower = name.toLowerCase();
  const exists = customSystem.some(c => c.toLowerCase() === lower);
  if (exists) return false;
  customSystem.push(name);
  saveCustomSystem();
  return true;
}

function removeCustomProcess(name) {
  const idx = customSystem.findIndex(c => c.toLowerCase() === name.toLowerCase());
  if (idx >= 0) {
    customSystem.splice(idx, 1);
    saveCustomSystem();
  }
}

if (els.settingsBtn) els.settingsBtn.addEventListener('click', openSettingsModal);
if (els.settingsClose) els.settingsClose.addEventListener('click', closeSettingsModal);
if (els.settingsModal) els.settingsModal.addEventListener('click', (e) => {
  if (e.target === els.settingsModal) closeSettingsModal();
});
if (els.customAdd) els.customAdd.addEventListener('click', () => {
  if (!els.customInput) return;
  const v = els.customInput.value;
  if (addCustomProcess(v)) {
    els.customInput.value = '';
    renderSettingsList();
    render(state.data);
  }
});
if (els.customInput) els.customInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    els.customAdd?.click();
  }
});
if (els.customList) els.customList.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-remove]');
  if (!btn) return;
  removeCustomProcess(btn.dataset.remove);
  renderSettingsList();
  render(state.data);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && els.settingsModal && els.settingsModal.classList.contains('open')) closeSettingsModal();
});

async function loadBuiltinSystem() {
  try {
    const r = await fetch('/api/system-processes');
    if (!r.ok) return;
    const j = await r.json();
    builtinSystem = j;
  } catch {}
}

// =====================================================================
// Auto-refresh
// =====================================================================
function startAuto() {
  stopAuto();
  const ms = parseInt(els.interval.value, 10) || 2000;
  state.timer = setInterval(refresh, ms);
  els.liveInd.classList.remove('paused');
  els.liveText.textContent = t('live');
}
function stopAuto() {
  if (state.timer) clearInterval(state.timer);
  state.timer = null;
  els.liveInd.classList.add('paused');
  els.liveText.textContent = t('live.paused');
}

async function refresh() {
  const data = await fetchPorts();
  if (data) render(data);
}

// =====================================================================
// Toast
// =====================================================================
function showToast(msg, type = 'info') {
  const wrap = $('#toast-wrap');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  wrap.appendChild(t);
  setTimeout(() => {
    t.classList.add('fade');
    setTimeout(() => t.remove(), 300);
  }, 3000);
}

// =====================================================================
// Keyboard
// =====================================================================
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') {
    if (e.key === 'Escape') {
      e.target.blur();
      if (e.target.id === 'search') {
        e.target.value = '';
        state.search = '';
        render(state.data);
      }
    }
    return;
  }
  if (e.key === '/') {
    e.preventDefault();
    els.search.focus();
  } else if (e.key === 'r' || e.key === 'R') {
    refresh();
  } else if (e.key === ' ') {
    e.preventDefault();
    els.autorefresh.checked = !els.autorefresh.checked;
    els.autorefresh.dispatchEvent(new Event('change'));
  }
});

// =====================================================================
// Init
// =====================================================================
function init() {
  // Set initial language button state
  document.querySelectorAll('.lang-btn').forEach(b => {
    const active = b.dataset.lang === currentLang;
    b.classList.toggle('active', active);
    b.setAttribute('aria-pressed', active ? 'true' : 'false');
    b.addEventListener('click', () => setLanguage(b.dataset.lang));
  });

  // Apply i18n to all static elements
  applyI18n();

  // Init sort indicator
  $$('th[data-sort]').forEach(th => {
    if (th.dataset.sort === state.sort.key) {
      th.classList.add('sorted');
      const ind = th.querySelector('.sort-ind');
      if (ind) ind.textContent = state.sort.dir === 'asc' ? '\u25b2' : '\u25bc';
    }
  });

  // Initial state
  els.lastScan.textContent = t('scanning');
  loadBuiltinSystem();
  refresh();
  startAuto();
}

init();
