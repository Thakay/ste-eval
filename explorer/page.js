(function () {
  const D = JSON.parse(document.getElementById('data').textContent);
  const E2 = D.exp2 || null;
  const NAME = { base: 'Baseline', lite: 'Lite', scoped: 'Scoped', full: 'Full', bare: 'Bare', oneliner: 'One line' };
  const GEN = { 'claude-opus': 'Claude Opus 5.5', 'codex-sol': 'Codex gpt-6.1-sol' };
  const SHORT = { 'claude-opus': 'Claude', 'codex-sol': 'Codex' };
  const JN = { opus: 'Opus judge', sol: 'sol judge' };
  const TYPE = { procedure: 'Procedure', explanation: 'Explanation', tradeoff: 'Tradeoff', handoff: 'Handoff', incident: 'Incident', warning: 'Warning', 'code-review': 'Code review', discussion: 'Pushback' };
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const fmt = (x, d = 1) => (x == null ? '–' : Number(x).toFixed(d));
  const sgn = (x, d = 2) => (x > 0 ? '+' : x < 0 ? '−' : '±') + Math.abs(x).toFixed(d);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const $ = (id) => document.getElementById(id);
  const NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    if (tag === 'text' && !('fill' in attrs)) e.setAttribute('fill', css('--muted'));
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  /* Tooltip shared by every chart */
  const tip = $('tip');
  document.addEventListener('pointermove', (e) => {
    const t = e.target.closest && e.target.closest('[data-tip]');
    if (!t) { tip.classList.remove('on'); return; }
    tip.textContent = t.getAttribute('data-tip');
    tip.classList.add('on');
    const w = tip.offsetWidth, h = tip.offsetHeight;
    let x = e.clientX + 14, y = e.clientY + 14;
    if (x + w > innerWidth - 8) x = e.clientX - w - 14;
    if (y + h > innerHeight - 8) y = e.clientY - h - 14;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  });

  document.querySelectorAll('[data-armwords]').forEach((n) => { n.textContent = D.arm_words[n.dataset.armwords].toLocaleString() + ' words'; });

  /* Sentence-length ruler: top histogram vs mirrored bottom histogram, with STE's limits */
  function ruler(hostId, tallyId, top, bottom, topLab, botLab, topColor, botColor) {
    const host = $(hostId);
    if (!host) return;
    host.innerHTML = '';
    const W = Math.max(320, host.clientWidth), H = W < 560 ? 230 : 280;
    const padL = 8, padR = 8, mid = H / 2 + 6, top0 = 22, bot = H - 26;
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': `Sentence lengths, ${topLab} versus ${botLab}` }, host);
    const nt = top.reduce((a, b) => a + b, 0), nb = bottom.reduce((a, b) => a + b, 0);
    const pt = top.map((v) => v / nt), pb = bottom.map((v) => v / nb);
    const maxP = Math.max(...pt, ...pb);
    const n = 40, cw = (W - padL - padR) / n, bw = Math.max(2, cw - 2);
    const x = (i) => padL + (i - 1) * cw;
    const hUp = mid - top0 - 4, hDn = bot - mid - 18;
    for (let i = 1; i <= n; i++) {
      const lab = i === 40 ? '40+' : i;
      const ht = (pt[i] / maxP) * hUp, hb = (pb[i] / maxP) * hDn;
      if (top[i]) el('rect', { x: x(i) + 1, y: mid - 4 - ht, width: bw, height: Math.max(ht, 1), rx: 1.5, fill: css(topColor), 'data-tip': `${lab} words · ${topLab}: ${top[i]} sentences (${(pt[i] * 100).toFixed(1)}%)` }, svg);
      if (bottom[i]) el('rect', { x: x(i) + 1, y: mid + 14, width: bw, height: Math.max(hb, 1), rx: 1.5, fill: css(botColor), 'data-tip': `${lab} words · ${botLab}: ${bottom[i]} sentences (${(pb[i] * 100).toFixed(1)}%)` }, svg);
    }
    el('line', { x1: padL, x2: W - padR, y1: mid + 5, y2: mid + 5, stroke: css('--ink'), 'stroke-width': 1 }, svg);
    for (let i = 1; i <= n; i++) {
      const cx = x(i) + cw / 2, major = i % 5 === 0;
      el('line', { x1: cx, x2: cx, y1: mid + 5 - (major ? 5 : 3), y2: mid + 5 + (major ? 5 : 3), stroke: css('--muted'), 'stroke-width': 1 }, svg);
      if (major) el('text', { x: cx, y: H - 6, 'text-anchor': 'middle', 'font-size': 11 }, svg).textContent = i === 40 ? '40+' : i;
    }
    [[20, 'instruction limit'], [25, 'description limit']].forEach(([lim, txt]) => {
      const lx = x(lim) + cw;
      el('line', { x1: lx, x2: lx, y1: 4, y2: bot - 4, stroke: css('--accent'), 'stroke-width': 1.5, 'stroke-dasharray': '4 3' }, svg);
      el('text', { x: lx + 5, y: 13, 'font-size': 11, fill: css('--accent-ink') }, svg).textContent = `${lim} · ${txt}`;
    });
    el('text', { x: W - padR, y: mid - 12, 'text-anchor': 'end', 'font-size': 11 }, svg).textContent = topLab + ' ↑';
    el('text', { x: W - padR, y: mid + 30, 'text-anchor': 'end', 'font-size': 11 }, svg).textContent = botLab + ' ↓';
    const over = (h) => h.slice(26).reduce((p, c) => p + c, 0);
    $(tallyId).innerHTML =
      `<div><b>${over(top)} of ${nt.toLocaleString()}</b>${topLab} sentences over 25 words</div>` +
      `<div><b>${over(bottom)} of ${nb.toLocaleString()}</b>${botLab} sentences over 25 words</div>`;
  }

  /* Interval chart: rows of mean with a 95% interval, around a zero line */
  function intervalChart(hostId, rows, min, max, step, zeroLabel) {
    const host = $(hostId);
    if (!host) return;
    host.innerHTML = '';
    const W = Math.max(320, host.clientWidth), narrow = W < 560;
    const labW = narrow ? 92 : 150, valW = 58, rowH = 24, headH = 26, axisH = 26;
    let H = axisH + 6;
    rows.forEach((r) => { H += r.head ? headH : rowH; });
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img' }, host);
    const x0 = labW, x1 = W - valW;
    const sx = (v) => x0 + ((v - min) / (max - min)) * (x1 - x0);
    for (let v = min; v <= max + 1e-9; v += step) {
      const gx = sx(v);
      el('line', { x1: gx, x2: gx, y1: 4, y2: H - axisH + 2, stroke: css('--hair'), 'stroke-width': 1 }, svg);
      el('text', { x: gx, y: H - 8, 'text-anchor': 'middle', 'font-size': 11 }, svg).textContent = (v > 1e-9 ? '+' : v < -1e-9 ? '−' : '') + Math.abs(v).toFixed(1);
    }
    el('line', { x1: sx(0), x2: sx(0), y1: 2, y2: H - axisH + 2, stroke: css('--ink'), 'stroke-width': 1.5 }, svg);
    el('text', { x: sx(0) + 4, y: H - axisH - 2, 'font-size': 10 }, svg).textContent = zeroLabel || 'baseline';
    let y = 4;
    rows.forEach((r) => {
      if (r.head) { el('text', { x: 0, y: y + 17, 'font-size': 12, 'font-weight': 600, fill: css('--ink') }, svg).textContent = r.head; y += headH; return; }
      const cy = y + rowH / 2;
      el('text', { x: 10, y: cy + 4, 'font-size': 11.5 }, svg).textContent = r.label;
      el('line', { x1: sx(r.lo), x2: sx(r.hi), y1: cy, y2: cy, stroke: css('--' + r.arm), 'stroke-width': 2, 'stroke-linecap': 'round' }, svg);
      el('circle', { cx: sx(r.m), cy, r: 5, fill: css('--' + r.arm), stroke: css('--paper'), 'stroke-width': 2 }, svg);
      el('text', { x: W, y: cy + 4, 'text-anchor': 'end', 'font-size': 11.5, fill: css('--ink') }, svg).textContent = sgn(r.m);
      const sig = r.lo > 0 || r.hi < 0;
      el('rect', { x: 0, y, width: W, height: rowH, fill: 'transparent', 'data-tip': `${r.tipHead || ''}${r.label}: ${sgn(r.m)} (95% interval ${sgn(r.lo)} to ${sgn(r.hi)})${sig ? ' · clear of zero' : ' · crosses zero'}` }, svg);
      y += rowH;
    });
  }

  function legend(id, arms) { const n = $(id); if (n) n.innerHTML = arms.map((a) => `<span><i class="sw ${a}"></i>${NAME[a]}</span>`).join(''); }

  function chartModels() {
    const rows = [];
    D.gens.forEach((g) => {
      rows.push({ head: GEN[g] });
      ['lite', 'scoped', 'full'].forEach((a) => { const [m, lo, hi] = D.agg.per_model_deltas[`${g}|${a}`]; rows.push({ label: NAME[a], arm: a, m, lo, hi, tipHead: GEN[g] + ' · ' }); });
    });
    intervalChart('chart-models', rows, -1.2, 1, 0.4);
  }

  function chartDims() {
    const dims = [['esl', 'Second-language ease'], ['clarity', 'Clarity'], ['nuance', 'Nuance'], ['naturalness', 'Naturalness']];
    const rows = [];
    dims.forEach(([k, lab]) => {
      rows.push({ head: lab });
      ['lite', 'scoped', 'full'].forEach((a) => { const [m, lo, hi] = D.agg.deltas[a][k]; rows.push({ label: NAME[a], arm: a, m, lo, hi, tipHead: lab + ' · ' }); });
    });
    intervalChart('chart-dims', rows, -0.8, 0.8, 0.4);
  }

  function chartTax() {
    const host = $('chart-tax');
    if (!host) return;
    host.innerHTML = '';
    const s = D.agg.ste, th = D.agg.thinking;
    const pct = (a, b) => (a / b - 1) * 100;
    const metrics = [
      ['Prose words', (a) => pct(s[a].words, s.base.words)],
      ['Reply time', (a) => pct(s[a].seconds, s.base.seconds)],
      ['Thinking, Opus', (a) => pct(th['claude-opus'][a], th['claude-opus'].base)],
      ['Thinking, sol', (a) => pct(th['codex-sol'][a], th['codex-sol'].base)],
    ];
    const W = Math.max(320, host.clientWidth), narrow = W < 560;
    const labW = narrow ? 96 : 150, valW = 54, barH = 9, gap = 3, groupGap = 16, axisH = 24;
    const groupH = 3 * barH + 2 * gap;
    const H = metrics.length * groupH + (metrics.length - 1) * groupGap + axisH + 10;
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img' }, host);
    const min = -30, max = 90, x0 = labW, x1 = W - valW;
    const sx = (v) => x0 + ((v - min) / (max - min)) * (x1 - x0);
    for (let v = min; v <= max; v += 30) {
      el('line', { x1: sx(v), x2: sx(v), y1: 2, y2: H - axisH, stroke: css('--hair') }, svg);
      el('text', { x: sx(v), y: H - 7, 'text-anchor': 'middle', 'font-size': 11 }, svg).textContent = (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v) + '%';
    }
    el('line', { x1: sx(0), x2: sx(0), y1: 0, y2: H - axisH, stroke: css('--ink'), 'stroke-width': 1.5 }, svg);
    let y = 6;
    metrics.forEach(([lab, f]) => {
      el('text', { x: 0, y: y + groupH / 2 + 4, 'font-size': 11.5, fill: css('--ink') }, svg).textContent = lab;
      ['lite', 'scoped', 'full'].forEach((a, i) => {
        const v = f(a), by = y + i * (barH + gap);
        const xa = sx(Math.min(0, v)), xb = sx(Math.max(0, v));
        el('rect', { x: xa, y: by, width: Math.max(1, xb - xa), height: barH, rx: 2, fill: css('--' + a), 'data-tip': `${lab} · ${NAME[a]}: ${v > 0 ? '+' : '−'}${Math.abs(v).toFixed(0)}% vs baseline` }, svg);
        el('text', { x: v >= 0 ? xb + 4 : xa - 4, y: by + barH - 1, 'text-anchor': v >= 0 ? 'start' : 'end', 'font-size': 10 }, svg).textContent = (v > 0 ? '+' : '−') + Math.abs(v).toFixed(0) + '%';
      });
      y += groupH + groupGap;
    });
  }

  function tables() {
    const s = D.agg.ste;
    const cols = [['wps', 'Words per sentence', 1], ['over20', 'Over 20 words', 1, '%'], ['over25', 'Over 25 words', 1, '%'], ['passive', 'Passive', 1, '%'], ['fk', 'Grade level', 1], ['words', 'Prose words', 0]];
    const head = '<thead><tr><th>Rule set</th>' + cols.map((c) => `<th>${c[1]}</th>`).join('') + '</tr></thead><tbody>';
    const rows = D.arms.map((a) => `<tr><td><span style="display:inline-flex;gap:.45rem;align-items:center"><i class="sw ${a}"></i>${NAME[a]}</span></td>` + cols.map((c) => `<td>${fmt(s[a][c[0]], c[2])}${c[3] || ''}</td>`).join('') + '</tr>').join('');
    $('ste-table').innerHTML = '<caption class="note" style="caption-side:bottom;text-align:left;padding-top:.5rem">Means per reply across both models. Grade level is Flesch-Kincaid.</caption>' + head + rows + '</tbody>';
    const ob = D.agg.overall_by_judge;
    let j = '<thead><tr><th>Judge, replies from</th>' + D.arms.map((a) => `<th>${NAME[a]}</th>`).join('') + '</tr></thead><tbody>';
    [['opus', 'claude-opus'], ['sol', 'claude-opus'], ['opus', 'codex-sol'], ['sol', 'codex-sol']].forEach(([jj, g]) => {
      const r = ob[`${jj}|${g}`], best = Math.max(...D.arms.map((a) => r[a]));
      j += `<tr><td>${JN[jj]}, ${GEN[g]}</td>` + D.arms.map((a) => `<td class="${r[a] === best ? 'w' : ''}">${fmt(r[a], 2)}</td>`).join('') + '</tr>';
    });
    $('judge-table').innerHTML = '<caption class="note" style="caption-side:bottom;text-align:left;padding-top:.5rem">Mean overall score, 1 to 10. Bold marks the top rule set in each row. Each judge rates its own family higher; the arm effect inside each row is what matters.</caption>' + j + '</tbody>';
  }

  function sendoffCount() {
    let n = 0;
    Object.values(D.cells).forEach((c) => { const v = c.judges.opus; if (v && /sign-off|send-off|Spartan|warrior/i.test(v.note)) n++; });
    const s = $('sendoff'); if (s) s.textContent = n + ' of 128';
  }

  function taskList() {
    $('tasklist').innerHTML = D.tasks.map((t) => `<li><span class="id">${t.id}</span><span><b>${TYPE[t.type]}.</b> ${esc(t.why)}</span></li>`).join('');
  }

  function md(text) {
    if (window.marked && window.DOMPurify) {
      const html = DOMPurify.sanitize(marked.parse(text, { gfm: true }));
      return html.replace(/<table>/g, '<div class="tw"><table>').replace(/<\/table>/g, '</table></div>');
    }
    return `<pre style="white-space:pre-wrap">${esc(text)}</pre>`;
  }

  /* Reply viewer. One instance per experiment. */
  const viewers = [];
  function Viewer(mountId, ds, cfg) {
    const mount = $(mountId);
    if (!mount) return;
    const st = { gen: 'claude-opus', arm: cfg.compare[0], rep: ds.reps[0], task: 0, side: 'base' };
    try { Object.assign(st, JSON.parse(localStorage.getItem('ste-' + cfg.key) || '{}')); } catch (e) { /* storage unavailable */ }
    if (!cfg.compare.includes(st.arm)) st.arm = cfg.compare[0];
    if (!ds.reps.includes(st.rep)) st.rep = ds.reps[0];
    const id = (s) => `${cfg.key}-${s}`;
    const cell = (g, a, t, r) => ds.cells[`${g}|${a}|${t}|${r}`];
    const jAvg = (c, f) => (c.judges.opus[f] + c.judges.sol[f]) / 2;
    const radios = (name, items, cur) => items.map(([v, lab]) => `<input type="radio" name="${id(name)}" id="${id(name + '-' + v)}" value="${v}"${String(cur) === String(v) ? ' checked' : ''}><label for="${id(name + '-' + v)}">${lab}</label>`).join('');
    mount.innerHTML = `
      <div class="controls" role="group" aria-label="Viewer settings">
        <div class="ctl"><span class="eyebrow">Model</span><div class="seg">${radios('gen', D.gens.map((g) => [g, GEN[g]]), st.gen)}</div></div>
        ${cfg.compare.length > 1 ? `<div class="ctl"><span class="eyebrow">STE rule set</span><div class="seg">${radios('arm', cfg.compare.map((a) => [a, `<i class="sw ${a}"></i>${NAME[a]}`]), st.arm)}</div></div>` : ''}
        <div class="ctl"><span class="eyebrow">Run</span><div class="seg">${radios('rep', ds.reps.map((r) => [r, r]), st.rep)}</div></div>
      </div>
      <nav class="rail" id="${id('rail')}" aria-label="Tasks"></nav>
      <p class="legend-inline">${cfg.railNote}</p>
      <div id="${id('slide')}" tabindex="-1"></div>`;

    function save() { try { localStorage.setItem('ste-' + cfg.key, JSON.stringify(st)); } catch (e) { /* ignore */ } }

    function rail() {
      $(id('rail')).innerHTML = D.tasks.map((t, i) => {
        const b = cell(st.gen, cfg.control, t.id, st.rep), s = cell(st.gen, st.arm, t.id, st.rep);
        const d = jAvg(s, 'overall') - jAvg(b, 'overall');
        const mark = d > 0 ? '▲ ' + d.toFixed(1) : d < 0 ? '▼ ' + Math.abs(d).toFixed(1) : '= 0.0';
        return `<button type="button" data-i="${i}" aria-current="${i === st.task}" aria-label="${t.id} ${TYPE[t.type]}, ${NAME[st.arm]} minus ${NAME[cfg.control]} ${d.toFixed(1)}"><span class="t">${t.id}</span><span class="ty">${TYPE[t.type]}</span><span class="d">${mark}</span></button>`;
      }).join('');
    }

    function statBlock(c, other) {
      const ck = (j) => `${c.judges[j].checklist.reduce((p, x) => p + x, 0)}/${c.judges[j].checklist.length}`;
      const better = (v, ov) => (v > ov ? ' win' : '');
      const items = [
        ['Opus judge', `${c.judges.opus.overall}<small>/10 · #${c.judges.opus.rank}</small>`, better(c.judges.opus.overall, other.judges.opus.overall)],
        ['sol judge', `${c.judges.sol.overall}<small>/10 · #${c.judges.sol.rank}</small>`, better(c.judges.sol.overall, other.judges.sol.overall)],
        ['Checklist', `${ck('opus')}<small> · ${ck('sol')}</small>`, ''],
        ['Reading quiz', c.reader ? `${c.reader.score}<small>/${c.reader.of}</small>` : '–', ''],
        ['2nd-lang. ease', fmt(jAvg(c, 'esl'), 1) + '<small>/5</small>', better(jAvg(c, 'esl'), jAvg(other, 'esl'))],
        ['Naturalness', fmt(jAvg(c, 'naturalness'), 1) + '<small>/5</small>', better(jAvg(c, 'naturalness'), jAvg(other, 'naturalness'))],
        ['Nuance', fmt(jAvg(c, 'nuance'), 1) + '<small>/5</small>', better(jAvg(c, 'nuance'), jAvg(other, 'nuance'))],
        ['Prose words', c.words, ''],
        ['Words/sent.', fmt(c.wps, 1), ''],
        ['Passive', fmt(c.passive, 0) + '<small>%</small>', ''],
        ['Thinking', c.thinking.toLocaleString() + '<small> tok</small>', ''],
        ['Time', fmt(c.seconds, 0) + '<small> s</small>', ''],
      ];
      return '<div class="stats">' + items.map(([l, v, w]) => `<div class="stat"><div class="l">${l}</div><div class="v${w}">${v}</div></div>`).join('') + '</div>';
    }

    function card(arm, c, other) {
      const isCtl = arm === cfg.control;
      const flags = ['opus', 'sol'].flatMap((j) => [...c.judges[j].invented.map((x) => `${JN[j]}, invented: ${x}`), ...c.judges[j].errors.map((x) => `${JN[j]}, error: ${x}`)]);
      const [lab, sub] = isCtl ? cfg.controlLabel : cfg.armLabel(arm);
      return `<article class="card ${isCtl ? 'basec' : 'ste'}" style="--armc: var(--${arm})">
        <header><span class="lab"><i class="sw ${arm}"></i>${lab}</span><span class="sub">${esc(sub)}</span></header>
        ${statBlock(c, other)}
        <div class="reply">${md(c.text)}</div>
        <div class="notes">
          <div><span class="j">Opus judge</span>${esc(c.judges.opus.note)}</div>
          <div><span class="j">sol judge</span>${esc(c.judges.sol.note)}</div>
          ${flags.length ? `<details><summary>${flags.length} flagged by the judges</summary><ul>${flags.map((f) => `<li>${esc(f)}</li>`).join('')}</ul></details>` : ''}
        </div>
      </article>`;
    }

    function slide() {
      const t = D.tasks[st.task];
      const b = cell(st.gen, cfg.control, t.id, st.rep), s = cell(st.gen, st.arm, t.id, st.rep);
      const rankRow = (j) => {
        const order = ds.arms.map((a) => [a, cell(st.gen, a, t.id, st.rep).judges[j]]).sort((p, q) => p[1].rank - q[1].rank);
        return `<div class="rankrow"><span class="who">${JN[j]} ranked</span>${order.map(([a, v]) => `<span class="chip"><span class="pos">${v.rank}</span><i class="sw ${a}"></i>${NAME[a]} ${v.overall}</span>`).join('')}</div>`;
      };
      const glyph = (n) => (n === 2 ? '●' : n === 1 ? '◐' : '○');
      const grid = t.checklist.map((item, i) => `<tr><td>${esc(item)}</td>${ds.arms.map((a) => { const c = cell(st.gen, a, t.id, st.rep); const n = c.judges.opus.checklist[i] + c.judges.sol.checklist[i]; return `<td class="g" title="${NAME[a]}: ${n} of 2 judges" aria-label="${NAME[a]}: ${n} of 2 judges">${glyph(n)}</td>`; }).join('')}</tr>`).join('');
      $(id('slide')).innerHTML = `
        <div class="slidehead">
          <div><span class="eyebrow">${t.id} · ${TYPE[t.type]} · ${GEN[st.gen]} · run ${st.rep}</span><h3>${esc(TYPE[t.type])}</h3><p class="why">${esc(t.why)}</p></div>
          <div class="nav"><button type="button" data-go="-1" aria-label="Previous task">←</button><span class="count">${st.task + 1} / ${D.tasks.length}</span><button type="button" data-go="1" aria-label="Next task">→</button></div>
        </div>
        <div class="prompt"><span class="eyebrow" style="display:block;margin-bottom:.3rem">The prompt</span>${esc(t.prompt)}</div>
        <button type="button" class="prompt-toggle">Show the full prompt</button>
        <div class="rankings">${rankRow('opus')}${rankRow('sol')}</div>
        <div class="seg flip" role="group" aria-label="Which reply to show">${radios('side', [['base', cfg.controlLabel[0]], ['ste', cfg.armLabel(st.arm)[0]]], st.side)}</div>
        <div class="cards" data-side="${st.side === 'ste' ? 'ste' : 'base'}">${card(cfg.control, b, s)}${card(st.arm, s, b)}</div>
        <details class="checks"><summary>Checklist: which replies covered each point</summary>
          <div class="cgrid-wrap"><table class="cgrid"><thead><tr><th>What a good answer covers</th>${ds.arms.map((a) => `<th><i class="sw ${a}" style="vertical-align:-1px;margin-right:4px"></i>${NAME[a]}</th>`).join('')}</tr></thead><tbody>${grid}</tbody></table></div>
          <p class="legend-inline">● both judges · ◐ one judge · ○ neither</p>
        </details>`;
      const box = $(id('slide'));
      box.querySelectorAll('[data-go]').forEach((btn) => { btn.onclick = () => go(+btn.dataset.go); });
      const p = box.querySelector('.prompt'), tg = box.querySelector('.prompt-toggle');
      if (p.scrollHeight <= p.clientHeight + 4) tg.hidden = true;
      tg.onclick = () => { p.classList.toggle('open'); tg.textContent = p.classList.contains('open') ? 'Show less' : 'Show the full prompt'; };
    }

    function render() { rail(); slide(); save(); }
    function go(d) { st.task = (st.task + d + D.tasks.length) % D.tasks.length; render(); }
    mount.querySelectorAll('input[type=radio]').forEach((inp) => {
      inp.addEventListener('change', () => {
        const key = inp.name.slice(cfg.key.length + 1);
        st[key] = key === 'rep' ? +inp.value : inp.value;
        render();
      });
    });
    $(id('rail')).addEventListener('click', (e) => { const btn = e.target.closest('button[data-i]'); if (btn) { st.task = +btn.dataset.i; render(); } });
    // the flip toggle is redrawn with each slide, so listen on the slide box
    $(id('slide')).addEventListener('change', (e) => { if (e.target.name === id('side')) { st.side = e.target.value; render(); } });
    const v = { go, onScreen: false };
    new IntersectionObserver((es) => { v.onScreen = es[0].isIntersecting; }, { threshold: 0.2 }).observe(mount);
    viewers.push(v);
    render();
  }

  document.addEventListener('keydown', (e) => {
    if (e.target.matches('input, textarea, select') || e.altKey || e.metaKey || e.ctrlKey) return;
    const v = viewers.find((x) => x.onScreen);
    if (!v) return;
    if (e.key === 'ArrowRight') { v.go(1); e.preventDefault(); }
    if (e.key === 'ArrowLeft') { v.go(-1); e.preventDefault(); }
  });

  /* Round two */
  function exp2Charts() {
    if (!E2) return;
    const fields = [['overall', 'Overall (1 to 10)'], ['esl', 'Second-language ease'], ['clarity', 'Clarity'], ['nuance', 'Nuance'], ['naturalness', 'Naturalness']];
    const rows = [];
    fields.forEach(([k, lab]) => {
      rows.push({ head: lab });
      D.gens.forEach((g) => { const [m, lo, hi] = E2.agg.per_model_dims[`${g}|oneliner`][k]; rows.push({ label: SHORT[g], arm: 'oneliner', m, lo, hi, tipHead: lab + ' · ' }); });
    });
    intervalChart('chart-e2', rows, -1.2, 1.2, 0.4, 'bare');
  }

  function ladder() {
    const host = $('ladder-table');
    if (!host || !E2) return;
    const conds = [['bare', E2, 'Bare CLI'], ['oneliner', E2, 'Bare + one line'], ['base', D, 'My setup'], ['lite', D, 'My setup + Lite'], ['scoped', D, 'My setup + Scoped'], ['full', D, 'My setup + Full']];
    const cols = [['wps', 'Words / sentence', 1], ['over20', 'Over 20 words', 1, '%'], ['passive', 'Passive', 1, '%'], ['words', 'Prose words', 0], ['thinking', 'Thinking tokens', 0], ['seconds', 'Seconds', 0]];
    let h = '<caption class="note" style="caption-side:bottom;text-align:left;padding-top:.5rem">Means per reply. Metrics compare across both rounds because the tasks, models and metric script are the same. Judge scores do not, because each judge only compared replies within one round.</caption>';
    h += '<thead><tr><th>Condition</th>' + cols.map((c) => `<th>${c[1]}</th>`).join('') + '</tr></thead><tbody>';
    D.gens.forEach((g) => {
      h += `<tr><td colspan="${cols.length + 1}" style="font:600 .74rem var(--mono);color:var(--ink);padding-top:1rem;text-transform:uppercase;letter-spacing:.06em">${GEN[g]}</td></tr>`;
      conds.forEach(([a, src, lab]) => {
        const r = src.agg.ste_by_gen[g][a];
        h += `<tr${a === 'oneliner' ? ' class="pick"' : ''}><td><span style="display:inline-flex;gap:.45rem;align-items:center"><i class="sw ${a}"></i>${lab}</span></td>` + cols.map((c) => `<td>${c[0] === 'thinking' ? Math.round(r[c[0]]).toLocaleString() : fmt(r[c[0]], c[2])}${c[3] || ''}</td>`).join('') + '</tr>';
      });
    });
    host.innerHTML = h + '</tbody>';
  }

  function drawCharts() {
    ruler('hero-chart', 'tally', D.hist.base, D.hist.lite.map((v, i) => v + D.hist.scoped[i] + D.hist.full[i]), 'baseline', 'STE', '--base', '--ink');
    chartModels(); chartDims(); chartTax();
    if (E2) { ruler('e2-ruler', 'e2-tally', E2.hist.bare, E2.hist.oneliner, 'bare', 'one line', '--base', '--oneliner'); exp2Charts(); }
  }

  legend('leg1', ['lite', 'scoped', 'full']); legend('leg2', ['lite', 'scoped', 'full']); legend('leg3', ['lite', 'scoped', 'full']);
  taskList(); tables(); sendoffCount(); ladder();
  Viewer('viewer1', D, {
    key: 'v1', control: 'base', compare: ['lite', 'scoped', 'full'],
    railNote: 'Under each task: the STE rule set’s score minus the baseline’s, averaged over both judges for this run.',
    controlLabel: ['Without STE · Baseline', 'current setup'],
    armLabel: (a) => ['With STE · ' + NAME[a], D.arm_words[a].toLocaleString() + '-word rule file'],
  });
  if (E2) Viewer('viewer2', E2, {
    key: 'v2', control: 'bare', compare: ['oneliner'],
    railNote: 'Under each task: the one-liner’s score minus the bare reply’s, averaged over both judges for this run.',
    controlLabel: ['Bare CLI', 'no instructions at all'],
    armLabel: () => ['Bare + one line', '“' + E2.oneliner_text + '”'],
  });
  drawCharts();
  let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(drawCharts, 120); });
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', drawCharts);
  new MutationObserver(drawCharts).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawCharts);
})();
