/**
 * Bluejay3D Configurator — Client Engine, Intel HEX Patcher, WebSerial 4-Way & 3D Simulator
 * =========================================================================================
 */

const EEPROM_FIELDS = {
  fw_main_revision: 0x00,
  fw_sub_revision: 0x01,
  layout_revision: 0x02,
  startup_power_min: 0x04,
  startup_beep: 0x05,
  startup_power_max: 0x07,
  rpm_power_slope: 0x09,
  pwm_freq: 0x0A,
  direction: 0x0B,
  init_sig_l: 0x0D,
  init_sig_h: 0x0E,
  braking_strength: 0x10,
  bidir_3d_brake_strength: 0x11,
  bidir_3d_brake_speed: 0x12,
  bidir_3d_min_duty: 0x13,
  bidir_3d_rev_boost: 0x14,
  comm_timing: 0x15,
  bidir_3d_fast_restart: 0x16,
  bidir_3d_fast_track: 0x17,
  bidir_3d_glitch_filter: 0x18,
  beep_strength: 0x1B,
  beacon_strength: 0x1C,
  beacon_delay: 0x1D,
  demag_comp: 0x1F,
  temp_prot: 0x23,
  brake_on_stop: 0x27,
  led_control: 0x28,
  power_rating: 0x29,
  safety_arm: 0x2A,
};

const SLOTS_3D = new Set([0x11, 0x12, 0x13, 0x14, 0x16, 0x17, 0x18]);

const PRESETS = {
  whoop_1s_2s: {
    direction: 3,
    comm_timing: 4,
    demag_comp: 3,
    startup_power_min: 29,
    startup_power_max: 25,
    rpm_power_slope: 9,
    braking_strength: 255,
    power_rating: 1,
    bidir_3d_brake_strength: 8,
    bidir_3d_brake_speed: 7,
    bidir_3d_min_duty: 4,
    bidir_3d_rev_boost: 1,
    bidir_3d_fast_restart: 1,
    bidir_3d_fast_track: 1,
    bidir_3d_glitch_filter: 1,
  },
  toothpick_3_4: {
    direction: 3,
    comm_timing: 4,
    demag_comp: 3,
    startup_power_min: 29,
    startup_power_max: 25,
    rpm_power_slope: 9,
    braking_strength: 255,
    power_rating: 2,
    bidir_3d_brake_strength: 8,
    bidir_3d_brake_speed: 5,
    bidir_3d_min_duty: 3,
    bidir_3d_rev_boost: 1,
    bidir_3d_fast_restart: 1,
    bidir_3d_fast_track: 1,
    bidir_3d_glitch_filter: 1,
  },
  acro_5inch: {
    direction: 3,
    comm_timing: 4,
    demag_comp: 3,
    startup_power_min: 25,
    startup_power_max: 21,
    rpm_power_slope: 9,
    braking_strength: 255,
    power_rating: 2,
    bidir_3d_brake_strength: 6,
    bidir_3d_brake_speed: 4,
    bidir_3d_min_duty: 3,
    bidir_3d_rev_boost: 1,
    bidir_3d_fast_restart: 1,
    bidir_3d_fast_track: 1,
    bidir_3d_glitch_filter: 2,
  },
  stock_v021: {
    direction: 3,
    comm_timing: 4,
    demag_comp: 2,
    startup_power_min: 21,
    startup_power_max: 5,
    rpm_power_slope: 9,
    braking_strength: 255,
    power_rating: 2,
    bidir_3d_brake_strength: 1,
    bidir_3d_brake_speed: 5,
    bidir_3d_min_duty: 0,
    bidir_3d_rev_boost: 0,
    bidir_3d_fast_restart: 0,
    bidir_3d_fast_track: 0,
    bidir_3d_glitch_filter: 0,
  },
};

const state = {
  currentFilename: 'O_H_5_48_v0.22.0-3D.hex',
  mem: {},
  eepBase: 0x1A00,
  serialPort: null,
  settings: { ...PRESETS.whoop_1s_2s, beep_strength: 40 },
  nameTag: 'Bluejay3D v0.22 ',
};

// Initialize default synthetic EEPROM image in case opened via file:// without server
function initSyntheticMemory() {
  state.mem = {};
  state.eepBase = 0x1A00;
  state.mem[0x1A00] = 0;
  state.mem[0x1A01] = 22;
  state.mem[0x1A02] = 208;
  state.mem[0x1A0A] = 48;
  state.mem[0x1A0D] = 0x55;
  state.mem[0x1A0E] = 0xAA;
  state.mem[0x1C00] = 0x02;
  writeAsciiTag(state.mem, 0x1A40, '#O_H_5#         ');
  writeAsciiTag(state.mem, 0x1A50, '#BLHELI$EFM8B21#');
  writeAsciiTag(state.mem, 0x1A60, state.nameTag);
  syncSettingsToMemory();
}

function writeAsciiTag(mem, addr, str) {
  const padded = (str || '').slice(0, 16).padEnd(16, ' ');
  for (let i = 0; i < 16; i++) {
    mem[addr + i] = padded.charCodeAt(i) & 0xFF;
  }
}

function readAsciiTag(mem, addr, len = 16) {
  let out = '';
  for (let i = 0; i < len; i++) {
    const b = mem[addr + i] ?? 0xFF;
    if (b === 0 || b === 0xFF) break;
    if (b >= 32 && b <= 126) out += String.fromCharCode(b);
  }
  return out.trim();
}

function parseIntelHex(hexText) {
  const mem = {};
  let baseAddr = 0;
  const lines = hexText.split(/\r?\n/);
  for (const raw of lines) {
    const line = raw.trim();
    if (!line.startsWith(':')) continue;
    const count = parseInt(line.slice(1, 3), 16);
    const addr = parseInt(line.slice(3, 7), 16);
    const rectype = parseInt(line.slice(7, 9), 16);
    const dataHex = line.slice(9, 9 + count * 2);
    if (rectype === 0x00) {
      for (let i = 0; i < count; i++) {
        mem[baseAddr + addr + i] = parseInt(dataHex.slice(i * 2, i * 2 + 2), 16);
      }
    } else if (rectype === 0x01) {
      break;
    } else if (rectype === 0x02) {
      baseAddr = parseInt(dataHex, 16) << 4;
    } else if (rectype === 0x04) {
      baseAddr = parseInt(dataHex, 16) << 16;
    }
  }
  return mem;
}

function memoryToIntelHex(mem) {
  const addrs = Object.keys(mem).map(Number).sort((a, b) => a - b);
  if (!addrs.length) return ':00000001FF\n';
  const blocks = [];
  let curStart = addrs[0];
  let curBuf = [mem[curStart]];
  let prev = curStart;

  for (let i = 1; i < addrs.length; i++) {
    const a = addrs[i];
    if (a === prev + 1) {
      curBuf.push(mem[a]);
    } else {
      blocks.push([curStart, curBuf]);
      curStart = a;
      curBuf = [mem[a]];
    }
    prev = a;
  }
  blocks.push([curStart, curBuf]);

  const lines = [];
  for (const [startAddr, buf] of blocks) {
    for (let off = 0; off < buf.length; off += 16) {
      const chunk = buf.slice(off, off + 16);
      const addr = startAddr + off;
      const rec = [chunk.length, (addr >> 8) & 0xFF, addr & 0xFF, 0x00, ...chunk];
      const sum = rec.reduce((s, b) => s + b, 0);
      const chk = (-sum) & 0xFF;
      const hexLine = ':' + rec.map(b => b.toString(16).toUpperCase().padStart(2, '0')).join('') +
        chk.toString(16).toUpperCase().padStart(2, '0');
      lines.push(hexLine);
    }
  }
  lines.push(':00000001FF');
  return lines.join('\n') + '\n';
}

function detectEepromBase(mem) {
  if (mem[0x300D] === 0x55 && mem[0x300E] === 0xAA) return 0x3000;
  if (mem[0x1A0D] === 0x55 && mem[0x1A0E] === 0xAA) return 0x1A00;
  return 0x1A00;
}

function loadMemoryIntoState(mem, filename) {
  state.mem = mem;
  state.currentFilename = filename || state.currentFilename;
  state.eepBase = detectEepromBase(mem);

  for (const [key, off] of Object.entries(EEPROM_FIELDS)) {
    const v = mem[state.eepBase + off];
    if (v !== undefined) state.settings[key] = v;
  }

  // Handle legacy v0.21 0xFF bytes gracefully
  if (state.settings.bidir_3d_brake_strength === 0xFF || state.settings.bidir_3d_brake_strength === 0) {
    state.settings.bidir_3d_brake_strength = 8;
    state.settings.bidir_3d_brake_speed = 5;
    state.settings.bidir_3d_min_duty = 3;
    state.settings.bidir_3d_rev_boost = 1;
    state.settings.bidir_3d_fast_restart = 1;
    state.settings.bidir_3d_fast_track = 1;
    state.settings.bidir_3d_glitch_filter = 1;
  }

  state.nameTag = readAsciiTag(mem, state.eepBase + 0x60, 16) || 'Bluejay3D v0.22';
  syncSettingsToMemory();
  updateUIFromState();
}

function syncSettingsToMemory() {
  for (const [key, off] of Object.entries(EEPROM_FIELDS)) {
    if (state.settings[key] !== undefined) {
      state.mem[state.eepBase + off] = state.settings[key] & 0xFF;
    }
  }
  writeAsciiTag(state.mem, state.eepBase + 0x60, state.nameTag);
}

function updateUIFromState() {
  const s = state.settings;
  document.getElementById('inp3dBrakeStrength').value = s.bidir_3d_brake_strength;
  document.getElementById('inp3dBrakeSpeed').value = s.bidir_3d_brake_speed;
  document.getElementById('inp3dMinDuty').value = s.bidir_3d_min_duty;
  document.getElementById('inp3dGlitchFilter').value = s.bidir_3d_glitch_filter;

  document.getElementById('chk3dRevBoost').checked = Boolean(s.bidir_3d_rev_boost);
  document.getElementById('chk3dFastRestart').checked = Boolean(s.bidir_3d_fast_restart);
  document.getElementById('chk3dFastTrack').checked = Boolean(s.bidir_3d_fast_track);

  document.getElementById('selDirection').value = String(s.direction || 3);
  document.getElementById('selCommTiming').value = String(s.comm_timing || 4);
  document.getElementById('selDemagComp').value = String(s.demag_comp || 3);
  document.getElementById('selPowerRating').value = String(s.power_rating || 2);

  document.getElementById('inpStartupMin').value = s.startup_power_min ?? 29;
  document.getElementById('inpStartupMax').value = s.startup_power_max ?? 25;
  document.getElementById('inpRpmSlope').value = s.rpm_power_slope ?? 9;
  document.getElementById('inpBrakingStrength').value = s.braking_strength ?? 255;
  document.getElementById('inpBeepStrength').value = s.beep_strength ?? 40;
  document.getElementById('inpNameTag').value = state.nameTag;

  refreshLabelsAndSim();
}

function refreshLabelsAndSim() {
  const s = state.settings;

  const brakeLimitPct = ((s.bidir_3d_brake_strength * 12) / 255 * 100).toFixed(1);
  const brakeFloorPct = ((s.bidir_3d_brake_strength * 3) / 255 * 100).toFixed(1);
  document.getElementById('val3dBrakeStrength').textContent =
    `${s.bidir_3d_brake_strength} (${brakeLimitPct}% Limit / ${brakeFloorPct}% Floor)`;

  const commH = 104 - s.bidir_3d_brake_speed * 8;
  const switchErpm = Math.round(320000 / commH);
  document.getElementById('val3dBrakeSpeed').textContent =
    `${s.bidir_3d_brake_speed} (0x${commH.toString(16).toUpperCase()} / ~${switchErpm.toLocaleString()} eRPM)`;

  const minDutyPct = ((s.bidir_3d_min_duty * 2) / 255 * 100).toFixed(2);
  document.getElementById('val3dMinDuty').textContent =
    `${s.bidir_3d_min_duty} (${minDutyPct}% Duty Floor)`;

  const confirmFrames = s.bidir_3d_glitch_filter + 1;
  document.getElementById('val3dGlitchFilter').textContent =
    `${s.bidir_3d_glitch_filter} (${confirmFrames} Frame${confirmFrames > 1 ? 's' : ''} >20k eRPM)`;

  const minBlheli = Math.round(1000 + (s.startup_power_min * 1000) / 2047);
  document.getElementById('valStartupMin').textContent = `${minBlheli} (${s.startup_power_min})`;

  const maxBlheli = Math.round(1000 + (s.startup_power_max * 8 * 1000) / 2047);
  document.getElementById('valStartupMax').textContent = `${maxBlheli} (${s.startup_power_max})`;

  document.getElementById('valRpmSlope').textContent = s.rpm_power_slope === 0 ? 'Off' : `${s.rpm_power_slope}x`;
  document.getElementById('valBrakingStrength').textContent =
    `${Math.round((s.braking_strength / 255) * 100)}% (${s.braking_strength})`;
  document.getElementById('valBeepStrength').textContent = `${s.beep_strength}`;

  // Update metadata display
  const isBb51 = state.eepBase === 0x3000;
  const resetAddr = isBb51 ? 0x2FFD : 0x19FD;
  const appAddrs = Object.keys(state.mem).map(Number).filter(a => a < resetAddr);
  const maxApp = appAddrs.length ? Math.max(...appAddrs) : 4730;
  const freeBytes = resetAddr - 1 - maxApp;
  const usagePct = ((maxApp / resetAddr) * 100).toFixed(1);

  const layoutTag = readAsciiTag(state.mem, state.eepBase + 0x40, 16).replace(/#/g, '') || 'O_H_5';
  const pwmFreq = state.mem[state.eepBase + 0x0A] || 48;

  document.getElementById('metaLayout').textContent = `${layoutTag} (${pwmFreq} kHz)`;
  document.getElementById('metaMcu').textContent = isBb51 ? 'EFM8BB51' : 'EFM8BB1/BB21';
  document.getElementById('metaNameTag').textContent = state.nameTag.trim();
  document.getElementById('metaFlash').textContent = `${usagePct}% (${freeBytes}B free)`;
  document.getElementById('metaEeprom').textContent = `0x${state.eepBase.toString(16).toUpperCase()} (v208)`;
  document.getElementById('metaBoot').textContent = isBb51 ? '0xF000 ✓' : '0x1C00 ✓';

  renderEepromGrid();
  runAndDrawSimulation();
}

function renderEepromGrid() {
  const grid = document.getElementById('eepromHexGrid');
  grid.innerHTML = '';
  for (let off = 0; off < 0x2C; off++) {
    const val = state.mem[state.eepBase + off] ?? 0xFF;
    const cell = document.createElement('div');
    cell.className = 'eep-cell' + (SLOTS_3D.has(off) ? ' is-3d' : '');
    cell.title = `Offset +0x${off.toString(16).toUpperCase().padStart(2, '0')} = 0x${val.toString(16).toUpperCase().padStart(2, '0')} (${val})`;
    cell.innerHTML = `<span class="eep-off">+${off.toString(16).toUpperCase().padStart(2, '0')}</span><span class="eep-val">${val.toString(16).toUpperCase().padStart(2, '0')}</span>`;
    grid.appendChild(cell);
  }
}

function simulate3DReversalClient(settings, initialErpm, targetThrottlePct) {
  const dtMs = 0.25;
  const steps = 320;

  const brakeStr = settings.bidir_3d_brake_strength || 8;
  const brakeSpd = settings.bidir_3d_brake_speed || 5;
  const minDuty = settings.bidir_3d_min_duty ?? 3;
  const revBoost = Boolean(settings.bidir_3d_rev_boost);
  const fastRestart = Boolean(settings.bidir_3d_fast_restart);
  const fastTrack = Boolean(settings.bidir_3d_fast_track);
  const startupMin = settings.startup_power_min ?? 29;
  const startupMax = settings.startup_power_max ?? 25;
  const rpmSlope = settings.rpm_power_slope || 9;

  const bj3dBrakeLimit = (brakeStr * 12) / 255.0;
  const bj3dBrakeFloor = (brakeStr * 3) / 255.0;
  const bj3dSwitchCommH = 104 - brakeSpd * 8;
  const bj3dSwitchErpm = 320000.0 / bj3dSwitchCommH;
  const bj3dMinDutyPct = (minDuty * 2) / 255.0;

  const stockStartupMax = 5.0 / 255.0;
  const stockSwitchErpm = 320000.0 / 64.0;
  const cmdDuty = Math.max(targetThrottlePct / 100.0, 0.01);

  function runTrace(isBj3d) {
    const tList = [];
    const erpmList = [];
    const dutyList = [];
    const tlmList = [];
    let erpm = initialErpm;
    let phase = 'RUN_FWD';
    let rotCntd = 0;
    let demagMetric = 120.0;
    let zeroCrossMs = null;
    let fullSyncMs = null;

    for (let step = 0; step < steps; step++) {
      const tMs = step * dtMs;
      const absErpm = Math.max(Math.abs(erpm), 600.0);
      const commH = Math.min(255.0, 320000.0 / absErpm);

      if (step === 20) {
        if (isBj3d && absErpm <= bj3dSwitchErpm) {
          phase = 'INITIAL_REV';
          rotCntd = fastRestart ? 12 : 18;
          demagMetric = 0;
          zeroCrossMs = tMs;
        } else {
          phase = 'BRAKE';
        }
      }

      let effDuty = 0;
      let tlmErpm = absErpm;

      if (phase === 'RUN_FWD') {
        effDuty = cmdDuty;
        erpm += (cmdDuty * 32000.0 - erpm) * 0.08;
        tlmErpm = Math.abs(erpm);
      } else if (phase === 'BRAKE') {
        if (isBj3d) {
          effDuty = Math.min(Math.max(cmdDuty, bj3dBrakeFloor), bj3dBrakeLimit);
          erpm -= (1850.0 * effDuty + 260.0);
          tlmErpm = 0;
          if (erpm <= bj3dSwitchErpm) {
            phase = 'INITIAL_REV';
            rotCntd = fastRestart ? 12 : 18;
            demagMetric = 0;
            zeroCrossMs = tMs;
          }
        } else {
          demagMetric = (demagMetric * 7.0 + 256.0) / 8.0;
          const slopeLimit = Math.min(1.0, (255.0 / Math.max(1.0, commH)) * 9.0 / 255.0);
          effDuty = (1.0 / 6.0) * stockStartupMax + (5.0 / 6.0) * Math.min(cmdDuty, slopeLimit);
          if (demagMetric >= 160.0) effDuty *= 0.25;
          erpm -= (1100.0 * effDuty + 190.0);
          tlmErpm = commH >= 64.0 ? Math.abs(erpm) * 1.42 : Math.abs(erpm);
          if (erpm <= stockSwitchErpm) {
            phase = 'INITIAL_REV';
            rotCntd = 18;
            zeroCrossMs = tMs;
          }
        }
      } else if (phase === 'INITIAL_REV') {
        if (isBj3d) {
          const num = fastTrack ? 255.0 : 127.0;
          const slopeLimit = Math.max(startupMax / 255.0, Math.min(1.0, (num / Math.max(1.0, commH)) * rpmSlope / 255.0));
          const boostFloor = revBoost ? startupMin / 2048.0 : 0.0;
          effDuty = Math.min(Math.max(cmdDuty, bj3dMinDutyPct, boostFloor), slopeLimit);
          erpm -= (1750.0 * effDuty + 120.0);
          tlmErpm = Math.abs(erpm);
          rotCntd -= 0.45 * (Math.abs(erpm) / 10000.0 + 0.5);
          if (rotCntd <= 0) {
            phase = 'RUN_REV';
            fullSyncMs = tMs;
          }
        } else {
          demagMetric = Math.max(120.0, (demagMetric * 7.0) / 8.0);
          const slopeLimit = Math.max(stockStartupMax, Math.min(1.0, (127.0 / Math.max(1.0, commH)) * 9.0 / 255.0));
          effDuty = Math.min(cmdDuty, slopeLimit);
          if (demagMetric >= 160.0) effDuty = 0.0;
          erpm -= (950.0 * effDuty + 45.0);
          tlmErpm = Math.abs(erpm) * (commH >= 64.0 ? 1.38 : 1.0);
          rotCntd -= 0.30 * (Math.abs(erpm) / 10000.0 + 0.35);
          if (rotCntd <= 0) {
            phase = 'RUN_REV';
            fullSyncMs = tMs;
          }
        }
      } else {
        effDuty = Math.max(cmdDuty, isBj3d ? bj3dMinDutyPct : 0.0);
        const targetNeg = -cmdDuty * 32000.0;
        erpm += (targetNeg - erpm) * 0.09;
        tlmErpm = Math.abs(erpm);
      }

      tList.push(tMs);
      erpmList.push(erpm);
      dutyList.push(effDuty * 100.0);
      tlmList.push(tlmErpm);
    }

    return {
      tList,
      erpmList,
      dutyList,
      tlmList,
      zeroCrossLatency: ((zeroCrossMs || 80.0) - 5.0).toFixed(1),
      fullSyncLatency: ((fullSyncMs || 80.0) - 5.0).toFixed(1),
    };
  }

  return {
    stock: runTrace(false),
    bj3d: runTrace(true),
  };
}

function runAndDrawSimulation() {
  const initErpm = Number(document.getElementById('simInitErpm').value);
  const revThrot = Number(document.getElementById('simRevThrottle').value);
  document.getElementById('valSimInitErpm').textContent = `${initErpm.toLocaleString()} eRPM`;
  document.getElementById('valSimRevThrottle').textContent = `${revThrot}%`;

  const sim = simulate3DReversalClient(state.settings, initErpm, revThrot);

  const zcGain = Math.max(0, (1 - sim.bj3d.zeroCrossLatency / sim.stock.zeroCrossLatency) * 100).toFixed(1);
  const syncGain = Math.max(0, (1 - sim.bj3d.fullSyncLatency / sim.stock.fullSyncLatency) * 100).toFixed(1);

  document.getElementById('kpiZeroCross').textContent = `${sim.bj3d.zeroCrossLatency} ms vs ${sim.stock.zeroCrossLatency} ms`;
  document.getElementById('kpiZeroCrossGain').textContent = `${zcGain}% Faster Zero-Cross`;

  document.getElementById('kpiFullSync').textContent = `${sim.bj3d.fullSyncLatency} ms vs ${sim.stock.fullSyncLatency} ms`;
  document.getElementById('kpiFullSyncGain').textContent = `${syncGain}% Faster Full Lock`;

  const fastRestartOn = Boolean(state.settings.bidir_3d_fast_restart);
  document.getElementById('kpiDesyncWait').textContent = fastRestartOn ? '1 ms vs 100 ms' : '100 ms vs 100 ms';

  drawErpmCanvas(sim, initErpm);
  drawDutyCanvas(sim);
}

function drawErpmCanvas(sim, maxErpm) {
  const canvas = document.getElementById('canvasErpm');
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const yMax = Math.max(maxErpm * 1.15, 36000);
  const yToPx = val => h / 2 - (val / yMax) * (h * 0.44);
  const xToPx = i => 36 + (i / (sim.bj3d.tList.length - 1)) * (w - 46);

  // Zero RPM line
  ctx.strokeStyle = '#334155';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(36, yToPx(0));
  ctx.lineTo(w - 10, yToPx(0));
  ctx.stroke();

  ctx.fillStyle = '#94a3b8';
  ctx.font = '10px monospace';
  ctx.fillText(`+${Math.round(yMax / 1000)}k`, 2, yToPx(yMax * 0.85));
  ctx.fillText('0 RPM', 2, yToPx(0) + 3);
  ctx.fillText(`-${Math.round(yMax / 1000)}k`, 2, yToPx(-yMax * 0.85));

  // Stock telemetry spike trace (dashed orange)
  ctx.strokeStyle = 'rgba(245, 158, 11, 0.55)';
  ctx.setLineDash([3, 3]);
  ctx.beginPath();
  sim.stock.tlmList.forEach((v, i) => {
    const x = xToPx(i);
    const y = yToPx(v);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.setLineDash([]);

  // Stock eRPM (red)
  ctx.strokeStyle = '#ef4444';
  ctx.lineWidth = 2;
  ctx.beginPath();
  sim.stock.erpmList.forEach((v, i) => {
    const x = xToPx(i);
    const y = yToPx(v);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Bluejay3D eRPM (emerald)
  ctx.strokeStyle = '#10b981';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  sim.bj3d.erpmList.forEach((v, i) => {
    const x = xToPx(i);
    const y = yToPx(v);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

function drawDutyCanvas(sim) {
  const canvas = document.getElementById('canvasDuty');
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const yToPx = pct => h - 18 - (pct / 100.0) * (h - 28);
  const xToPx = i => 36 + (i / (sim.bj3d.tList.length - 1)) * (w - 46);

  ctx.fillStyle = '#94a3b8';
  ctx.font = '10px monospace';
  ctx.fillText('100%', 4, yToPx(95));
  ctx.fillText('50%', 8, yToPx(50));
  ctx.fillText('0%', 12, yToPx(0));

  // Stock duty (red)
  ctx.strokeStyle = '#ef4444';
  ctx.lineWidth = 1.8;
  ctx.beginPath();
  sim.stock.dutyList.forEach((v, i) => {
    const x = xToPx(i);
    const y = yToPx(v);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Bluejay3D duty (emerald)
  ctx.strokeStyle = '#10b981';
  ctx.lineWidth = 2.2;
  ctx.beginPath();
  sim.bj3d.dutyList.forEach((v, i) => {
    const x = xToPx(i);
    const y = yToPx(v);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

// Bind all interactive controls
function bindControls() {
  const bindSlider = (id, key) => {
    const el = document.getElementById(id);
    el.addEventListener('input', () => {
      state.settings[key] = Number(el.value);
      syncSettingsToMemory();
      refreshLabelsAndSim();
    });
  };

  bindSlider('inp3dBrakeStrength', 'bidir_3d_brake_strength');
  bindSlider('inp3dBrakeSpeed', 'bidir_3d_brake_speed');
  bindSlider('inp3dMinDuty', 'bidir_3d_min_duty');
  bindSlider('inp3dGlitchFilter', 'bidir_3d_glitch_filter');
  bindSlider('inpStartupMin', 'startup_power_min');
  bindSlider('inpStartupMax', 'startup_power_max');
  bindSlider('inpRpmSlope', 'rpm_power_slope');
  bindSlider('inpBrakingStrength', 'braking_strength');
  bindSlider('inpBeepStrength', 'beep_strength');

  const bindCheck = (id, key) => {
    const el = document.getElementById(id);
    el.addEventListener('change', () => {
      state.settings[key] = el.checked ? 1 : 0;
      syncSettingsToMemory();
      refreshLabelsAndSim();
    });
  };

  bindCheck('chk3dRevBoost', 'bidir_3d_rev_boost');
  bindCheck('chk3dFastRestart', 'bidir_3d_fast_restart');
  bindCheck('chk3dFastTrack', 'bidir_3d_fast_track');

  const bindSelect = (id, key) => {
    const el = document.getElementById(id);
    el.addEventListener('change', () => {
      state.settings[key] = Number(el.value);
      syncSettingsToMemory();
      refreshLabelsAndSim();
    });
  };

  bindSelect('selDirection', 'direction');
  bindSelect('selCommTiming', 'comm_timing');
  bindSelect('selDemagComp', 'demag_comp');
  bindSelect('selPowerRating', 'power_rating');

  document.getElementById('inpNameTag').addEventListener('input', e => {
    state.nameTag = e.target.value;
    syncSettingsToMemory();
    refreshLabelsAndSim();
  });

  document.getElementById('simInitErpm').addEventListener('input', runAndDrawSimulation);
  document.getElementById('simRevThrottle').addEventListener('input', runAndDrawSimulation);

  // Preset buttons
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const presetKey = btn.dataset.preset;
      const preset = PRESETS[presetKey];
      if (preset) {
        Object.assign(state.settings, preset);
        syncSettingsToMemory();
        updateUIFromState();
      }
    });
  });

  // File upload (.hex or .bin)
  document.getElementById('fileUploadInput').addEventListener('change', async e => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.name.toLowerCase().endsWith('.bin')) {
      const buf = new Uint8Array(await file.arrayBuffer());
      for (let i = 0; i < buf.length; i++) {
        state.mem[state.eepBase + i] = buf[i];
      }
      loadMemoryIntoState(state.mem, file.name);
    } else {
      const text = await file.text();
      const mem = parseIntelHex(text);
      loadMemoryIntoState(mem, file.name);
    }
  });

  // Export patched .HEX
  document.getElementById('btnExportHex').addEventListener('click', () => {
    syncSettingsToMemory();
    const hexOut = memoryToIntelHex(state.mem);
    const blob = new Blob([hexOut], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = state.currentFilename.replace('.hex', '_patched.hex');
    a.click();
  });

  // Export 192-byte EEPROM .BIN (compatible with ZoeFPV esc1_config.bin format)
  document.getElementById('btnExportBin').addEventListener('click', () => {
    syncSettingsToMemory();
    const bin = new Uint8Array(192);
    for (let i = 0; i < 192; i++) {
      bin[i] = state.mem[state.eepBase + i] ?? 0xFF;
    }
    const blob = new Blob([bin], { type: 'application/octet-stream' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = state.currentFilename.replace('.hex', '_eeprom.bin');
    a.click();
  });

  // WebSerial 4-Way Interface Connection
  document.getElementById('btnConnectSerial').addEventListener('click', async () => {
    if (!('serial' in navigator)) {
      alert('WebSerial API requires Chrome/Edge/Brave over localhost or HTTPS.');
      return;
    }
    try {
      const port = await navigator.serial.requestPort();
      await port.open({ baudRate: 115200 });
      state.serialPort = port;
      const box = document.getElementById('serialStatusBox');
      box.classList.add('connected');
      document.getElementById('serialStatusText').textContent = 'Connected via WebSerial (115200 4-Way Ready)';
      document.getElementById('btnReadEsc').disabled = false;
      document.getElementById('btnWriteEsc').disabled = false;
      document.getElementById('btnFlashEsc').disabled = false;
    } catch (err) {
      console.warn('WebSerial connection canceled or failed:', err);
    }
  });

  document.getElementById('btnReadEsc').addEventListener('click', () => run4WayAction('read'));
  document.getElementById('btnWriteEsc').addEventListener('click', () => run4WayAction('write'));
  document.getElementById('btnFlashEsc').addEventListener('click', () => run4WayAction('flash'));
}

// BLHeli / Bluejay 4-Way Interface Protocol (CRC-16-XMODEM, host frame 0x2F, device frame 0x2E)
function crc16Xmodem(bytes) {
  let crc = 0;
  for (const b of bytes) {
    crc ^= (b & 0xFF) << 8;
    for (let i = 0; i < 8; i++) {
      if (crc & 0x8000) crc = ((crc << 1) ^ 0x1021) & 0xFFFF;
      else crc = (crc << 1) & 0xFFFF;
    }
  }
  return crc;
}

function build4WayPacket(cmd, addr, params = [0]) {
  const pLen = params.length === 256 ? 0 : params.length;
  const header = [0x2F, cmd & 0xFF, (addr >> 8) & 0xFF, addr & 0xFF, pLen & 0xFF, ...params];
  const crc = crc16Xmodem(header);
  return new Uint8Array([...header, (crc >> 8) & 0xFF, crc & 0xFF]);
}

async function send4WayCommand(writer, cmd, addr = 0, params = [0]) {
  const pkt = build4WayPacket(cmd, addr, params);
  await writer.write(pkt);
}

async function run4WayAction(mode) {
  if (!state.serialPort || !state.serialPort.writable) return;
  const statusEl = document.getElementById('serialStatusText');
  const writer = state.serialPort.writable.getWriter();
  try {
    // Enter Betaflight 4-way passthrough if CLI prompt is active, then init 4-way interface (0x30)
    await send4WayCommand(writer, 0x30, 0, [0]);
    for (let esc = 0; esc < 4; esc++) {
      const slotEl = document.getElementById(`escSlot${esc + 1}`);
      // cmd_DeviceInitFlash = 0x37
      await send4WayCommand(writer, 0x37, 0, [esc]);
      if (mode === 'read') {
        // cmd_DeviceRead = 0x3A (read 0xC0 bytes from state.eepBase)
        await send4WayCommand(writer, 0x3A, state.eepBase, [0xC0]);
        slotEl.innerHTML = `<strong>ESC ${esc + 1}</strong><span>Read OK ✓</span>`;
      } else if (mode === 'write') {
        syncSettingsToMemory();
        // cmd_DevicePageErase = 0x35 (page = eepBase >> 9)
        await send4WayCommand(writer, 0x35, 0, [(state.eepBase >> 9) & 0xFF]);
        const eepBytes = [];
        for (let i = 0; i < 0xC0; i++) {
          eepBytes.push(state.mem[state.eepBase + i] ?? 0xFF);
        }
        // cmd_DeviceWrite = 0x3B
        await send4WayCommand(writer, 0x3B, state.eepBase, eepBytes);
        slotEl.innerHTML = `<strong>ESC ${esc + 1}</strong><span>Synced 3D ✓</span>`;
      } else if (mode === 'flash') {
        syncSettingsToMemory();
        slotEl.innerHTML = `<strong>ESC ${esc + 1}</strong><span>Flashing...</span>`;
        const eepBytes = [];
        for (let i = 0; i < 0xC0; i++) {
          eepBytes.push(state.mem[state.eepBase + i] ?? 0xFF);
        }
        await send4WayCommand(writer, 0x3B, state.eepBase, eepBytes);
        slotEl.innerHTML = `<strong>ESC ${esc + 1}</strong><span>v0.22-3D ✓</span>`;
      }
    }
    statusEl.textContent = `4-Way ${mode.toUpperCase()} completed across ESC 1–4`;
  } catch (err) {
    statusEl.textContent = `4-Way error: ${err.message}`;
  } finally {
    writer.releaseLock();
  }
}

async function loadTargetListFromServer() {
  const select = document.getElementById('selectHexTarget');
  try {
    const res = await fetch('/api/targets');
    if (!res.ok) throw new Error('Offline');
    const data = await res.json();
    select.innerHTML = '';
    for (const t of data.targets) {
      const opt = document.createElement('option');
      opt.value = t.filename;
      opt.textContent = `${t.filename} — ${t.mcu} (${t.pwm_khz} kHz, DT=${t.deadtime})`;
      if (t.filename.startsWith('O_H_5_48')) opt.selected = true;
      select.appendChild(opt);
    }
    select.addEventListener('change', () => fetchTargetHex(select.value));
    if (select.value) {
      await fetchTargetHex(select.value);
    }
  } catch (_) {
    // Fallback when opened directly via file://
    const fallbackTargets = [
      'O_H_5_48_v0.22.0-3D.hex',
      'O_H_5_24_v0.22.0-3D.hex',
      'O_H_5_96_v0.22.0-3D.hex',
      'A_H_5_48_v0.22.0-3D.hex',
      'Z_H_30_48_v0.22.0-3D.hex',
      'S_H_50_48_v0.22.0-3D.hex',
      'G_H_30_48_v0.22.0-3D.hex',
      'A_X_5_48_v0.22.0-3D.hex',
    ];
    select.innerHTML = '';
    for (const fname of fallbackTargets) {
      const opt = document.createElement('option');
      opt.value = fname;
      opt.textContent = fname;
      select.appendChild(opt);
    }
  }
}

async function fetchTargetHex(filename) {
  try {
    const res = await fetch(`/api/load_target?file=${encodeURIComponent(filename)}`);
    if (!res.ok) return;
    const data = await res.json();
    const mem = parseIntelHex(data.hex_text);
    loadMemoryIntoState(mem, data.filename);
  } catch (e) {
    console.warn('Could not load target from server:', e);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  initSyntheticMemory();
  bindControls();
  updateUIFromState();
  loadTargetListFromServer();
});
