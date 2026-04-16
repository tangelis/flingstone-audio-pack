const cues = [
  {
    id: "01",
    title: "Rubber Stretch",
    type: "aim",
    variants: [
      { label: "A", name: "Tight garage band", file: "assets/01_rubber_stretch_a.wav", description: "Dry, close-mic elastic tension with rising squeak and pouch texture." },
      { label: "B", name: "Cartoon tension arc", file: "assets/01_rubber_stretch_b.wav", description: "Big rubbery bwoing with playful balloon-strain exaggeration." },
      { label: "C", name: "Hero tension bow", file: "assets/01_rubber_stretch_c.wav", description: "Richer cinematic pull with creak, whine, and stretched-body tension." },
      { label: "D", name: "Glitch tension braid", file: "assets/01_rubber_stretch_d.wav", description: "Warped electronic tension with unstable bend and textured friction." }
    ]
  },
  {
    id: "02",
    title: "Projectile Release",
    type: "action",
    variants: [
      { label: "A", name: "Snap launch", file: "assets/02_projectile_release_a.wav", description: "Short snap and air tail, tight and direct." },
      { label: "B", name: "Slingshot crack", file: "assets/02_projectile_release_b.wav", description: "Harder release with a toy-metal ring-off." },
      { label: "C", name: "Whip trail", file: "assets/02_projectile_release_c.wav", description: "Premium high-speed whip with a brighter, cleaner launch arc." },
      { label: "D", name: "Circuit lash", file: "assets/02_projectile_release_d.wav", description: "Sharper electronic snap with a fractured synthetic tail." }
    ]
  },
  {
    id: "03",
    title: "Blocks Falling",
    type: "impact",
    variants: [
      { label: "A", name: "Quarry pile", file: "assets/03_blocks_falling_a.wav", description: "Heavy limestone thuds with debris and weight." },
      { label: "B", name: "Arcade masonry", file: "assets/03_blocks_falling_b.wav", description: "Shorter, punchier arcade collapse." },
      { label: "C", name: "Temple cascade", file: "assets/03_blocks_falling_c.wav", description: "Deeper topple with longer rumble and premium collapse tail." },
      { label: "D", name: "Machine rubble", file: "assets/03_blocks_falling_d.wav", description: "Broken rhythmic collapse with stuttering electronic grit." }
    ]
  },
  {
    id: "04",
    title: "Core Hit",
    type: "special",
    variants: [
      { label: "A", name: "Crystal bell strike", file: "assets/04_core_hit_a.wav", description: "Bright, glassy chime that instantly reads as special." },
      { label: "B", name: "Forged metal resonance", file: "assets/04_core_hit_b.wav", description: "Hammered-metal ping with ancient energy." },
      { label: "C", name: "Arcane prism", file: "assets/04_core_hit_c.wav", description: "Charged resonator hit with magical weight under the sparkle." },
      { label: "D", name: "Fractured signal core", file: "assets/04_core_hit_d.wav", description: "A spectral, glitch-laced special hit with electronic resonance." }
    ]
  },
  {
    id: "05",
    title: "Small Explosion",
    type: "impact",
    variants: [
      { label: "A", name: "Compressed pop", file: "assets/05_small_explosion_a.wav", description: "Quick pop, air puff, and tiny debris sprinkle." },
      { label: "B", name: "Dusty kaboom", file: "assets/05_small_explosion_b.wav", description: "Mini boom with a browner, muffled body." },
      { label: "C", name: "Spark burst", file: "assets/05_small_explosion_c.wav", description: "Sharper premium burst with cleaner transient detail." },
      { label: "D", name: "Bit burst", file: "assets/05_small_explosion_d.wav", description: "Tight electronic blast with chopped transient fragments." }
    ]
  },
  {
    id: "06",
    title: "Big Explosion",
    type: "impact",
    variants: [
      { label: "A", name: "Subwoofer siege", file: "assets/06_big_explosion_a.wav", description: "Deep chesty boom with collapse layers." },
      { label: "B", name: "Triumph detonation", file: "assets/06_big_explosion_b.wav", description: "Huge slam with brighter debris and win-state flair." },
      { label: "C", name: "Catapult rupture", file: "assets/06_big_explosion_c.wav", description: "Longest, richest blast with pressure wave and ruin tail." },
      { label: "D", name: "Glitch detonation", file: "assets/06_big_explosion_d.wav", description: "Heavy electronic rupture with broken-air stutters and long debris." }
    ]
  },
  {
    id: "07",
    title: "Background Music Loop",
    type: "music",
    variants: [
      { label: "A", name: "Bouncy tribal drive", file: "assets/07_background_music_loop_a.wav", description: "Mallet-led loop with drums and bass groove." },
      { label: "B", name: "Adventure swing", file: "assets/07_background_music_loop_b.wav", description: "Family-adventure orchestral swing." },
      { label: "C", name: "Stone-runner quest", file: "assets/07_background_music_loop_c.wav", description: "A fuller hybrid loop with more premium mobile-game polish." },
      { label: "D", name: "Warp lattice run", file: "assets/07_background_music_loop_d.wav", description: "A strange, detailed glitch-electronic loop with off-kilter motion." }
    ]
  },
  {
    id: "08",
    title: "UI Button Click",
    type: "ui",
    variants: [
      { label: "A", name: "Glassy tap", file: "assets/08_ui_button_click_a.wav", description: "Bright premium tap with almost no tail." },
      { label: "B", name: "Soft mechanical press", file: "assets/08_ui_button_click_b.wav", description: "Warmer plastic thock and micro spring release." },
      { label: "C", name: "Gem confirm", file: "assets/08_ui_button_click_c.wav", description: "A clean, premium UI tick with extra clarity." },
      { label: "D", name: "Micro glitch confirm", file: "assets/08_ui_button_click_d.wav", description: "Detailed electronic click with a tiny fractured tail." }
    ]
  },
  {
    id: "09",
    title: "Slow Motion Zoom",
    type: "vfx",
    variants: [
      { label: "A", name: "Time-dilation hum", file: "assets/09_slow_motion_zoom_a.wav", description: "Low whoosh folding into a syrupy tonal hum." },
      { label: "B", name: "Camera wind shear", file: "assets/09_slow_motion_zoom_b.wav", description: "Rising air shear with tape-like drag and pulse." },
      { label: "C", name: "Gravity warp", file: "assets/09_slow_motion_zoom_c.wav", description: "A wider-feeling gravity bend with richer halo and tail." },
      { label: "D", name: "Phase melt", file: "assets/09_slow_motion_zoom_d.wav", description: "Warped electronic slowdown with smeared echo and unstable pitch." }
    ]
  },
  {
    id: "10",
    title: "Points Increase",
    type: "ui",
    variants: [
      { label: "A", name: "Coin ladder", file: "assets/10_points_increase_a.wav", description: "Rapid rising ding ladder that tightens as it climbs." },
      { label: "B", name: "Arcade meter fill", file: "assets/10_points_increase_b.wav", description: "Short ticks with milestone chimes." },
      { label: "C", name: "Combo cascade", file: "assets/10_points_increase_c.wav", description: "A richer chain of reward tones with a polished finish." },
      { label: "D", name: "Fractal tally", file: "assets/10_points_increase_d.wav", description: "Glitchy reward ladder with chopped echoes and synthetic sparkle." }
    ]
  },
  {
    id: "11",
    title: "Victory Sound",
    type: "reward",
    variants: [
      { label: "A", name: "Brass fanfare sting", file: "assets/11_victory_sound_a.wav", description: "Classic upward fanfare with sparkle." },
      { label: "B", name: "Chime + horn lift", file: "assets/11_victory_sound_b.wav", description: "Friendlier unlock-style win cue." },
      { label: "C", name: "Hero crown cadence", file: "assets/11_victory_sound_c.wav", description: "The richest win sting, with a polished regal lift." },
      { label: "D", name: "Fractured coronation", file: "assets/11_victory_sound_d.wav", description: "A strange premium win sting with chopped shimmer and bloom." }
    ]
  },
  {
    id: "12",
    title: "Unsuccessful Sound",
    type: "fail",
    variants: [
      { label: "A", name: "Sad trombone micro-sting", file: "assets/12_unsuccessful_sound_a.wav", description: "Short cartoon fail without being punishing." },
      { label: "B", name: "Soft deflate", file: "assets/12_unsuccessful_sound_b.wav", description: "Gentle slide and muted thud." },
      { label: "C", name: "Wooden shrug", file: "assets/12_unsuccessful_sound_c.wav", description: "A softer premium fail with clonk-and-sigh personality." },
      { label: "D", name: "Bent circuit sigh", file: "assets/12_unsuccessful_sound_d.wav", description: "A restrained glitch-fail cue with broken pitch and thunk." }
    ]
  },
  {
    id: "13",
    title: "Clock Running Out",
    type: "tension",
    variants: [
      { label: "A", name: "Mechanical pendulum stress", file: "assets/13_clock_running_out_a.wav", description: "Ticking with subtle final tension bed." },
      { label: "B", name: "Digital urgency", file: "assets/13_clock_running_out_b.wav", description: "Dry modern ticks with sharper urgency." },
      { label: "C", name: "Final heartbeat", file: "assets/13_clock_running_out_c.wav", description: "A more dramatic panic timer with ticking and pulse." },
      { label: "D", name: "Stutter panic", file: "assets/13_clock_running_out_d.wav", description: "Glitch-ticked countdown with fractured repeats and anxious bed." }
    ]
  },
  {
    id: "14",
    title: "Bonus Powerup",
    type: "reward",
    variants: [
      { label: "A", name: "Magic shimmer grab", file: "assets/14_bonus_powerup_a.wav", description: "Sparkly gliss and bell clusters." },
      { label: "B", name: "Energy charge-in", file: "assets/14_bonus_powerup_b.wav", description: "Power-up zip into a warmer harmonic payoff." },
      { label: "C", name: "Legendary pickup", file: "assets/14_bonus_powerup_c.wav", description: "The richest reward bloom, with a premium pickup finish." },
      { label: "D", name: "Quantum pickup", file: "assets/14_bonus_powerup_d.wav", description: "Detailed synthetic reward bloom with glittering glitch texture." }
    ]
  }
];

const grid = document.getElementById("sound-grid");
const soundpackSelect = document.getElementById("soundpack-select");
const title = document.getElementById("active-title");
const variantLabel = document.getElementById("active-variant-label");
const variantName = document.getElementById("active-variant-name");
const description = document.getElementById("active-description");
const player = document.getElementById("main-player");
const playButton = document.getElementById("play-button");
const prevButton = document.getElementById("prev-button");
const nextButton = document.getElementById("next-button");
const cycleButton = document.getElementById("cycle-button");

let selectedCueIndex = 0;
let selectedPackIndex = 0;
let playingKey = null;
let cycleMode = false;

function normalizeCueIndex(index) {
  return (index + cues.length) % cues.length;
}

function getSelection(cueIndex = selectedCueIndex) {
  const cueIndexSafe = normalizeCueIndex(cueIndex);
  const cue = cues[cueIndexSafe];
  const variantIndex = selectedPackIndex;
  const variant = cue.variants[selectedPackIndex];
  return {
    cueIndex: cueIndexSafe,
    variantIndex,
    cue,
    variant,
    key: `${cueIndexSafe}-${variantIndex}`
  };
}

function cycleQueue() {
  return cues.map((cue, cueIndex) => {
    const variantIndex = selectedPackIndex;
    return {
      cueIndex,
      variantIndex,
      key: `${cueIndex}-${variantIndex}`,
      file: cue.variants[variantIndex].file
    };
  });
}

function selectCue(cueIndex) {
  selectedCueIndex = normalizeCueIndex(cueIndex);
  updateVisualState();
}

function setSoundpack(packIndex, options = {}) {
  const { preservePlayback = false } = options;
  selectedPackIndex = (packIndex + cues[0].variants.length) % cues[0].variants.length;
  soundpackSelect.value = String(selectedPackIndex);

  if (preservePlayback && (playingKey !== null || cycleMode)) {
    playSelection(selectedCueIndex, selectedPackIndex);
    return;
  }

  updateVisualState();
}

function playSelection(cueIndex = selectedCueIndex, variantIndex = selectedPackIndex) {
  selectedCueIndex = normalizeCueIndex(cueIndex);
  selectedPackIndex = variantIndex;
  soundpackSelect.value = String(selectedPackIndex);
  const { variant, key } = getSelection();
  playingKey = key;
  updateVisualState();
  player.currentTime = 0;
  player.play().catch(() => {});
}

function moveCueSelection(delta) {
  selectCue(selectedCueIndex + delta);
}

function renderCards() {
  grid.innerHTML = "";
  cues.forEach((cue, cueIndex) => {
    const card = document.createElement("article");
    card.className = "card";
    card.dataset.cueIndex = String(cueIndex);

    card.innerHTML = `
      <div class="card-top" data-action="select-cue" data-cue-index="${cueIndex}" tabindex="0" role="button" aria-label="Select ${cue.title}">
        <span class="card-index">CUE ${cue.id}</span>
        <span class="card-chip">${cue.type}</span>
      </div>
      <h3 data-action="select-cue" data-cue-index="${cueIndex}">${cue.title}</h3>
      <div class="card-meta">
        <span class="variant-pill card-pack-pill" data-card-variant-label="${cueIndex}">Variant A</span>
        <span class="card-pack-name" data-card-variant-name="${cueIndex}">Tight garage band</span>
      </div>
      <p class="card-description" data-card-description="${cueIndex}">Dry, close-mic elastic tension with rising squeak and pouch texture.</p>
      <div class="card-actions">
        <button class="mini" data-action="play-cue" data-cue-index="${cueIndex}">Play cue</button>
      </div>
    `;

    grid.appendChild(card);
  });
  updateVisualState();
}

function updateVisualState() {
  const { cue, variant, key } = getSelection();
  title.textContent = cue.title;
  variantLabel.textContent = `Variant ${variant.label}`;
  variantName.textContent = variant.name;
  description.textContent = variant.description;
  soundpackSelect.value = String(selectedPackIndex);

  if (player.dataset.file !== variant.file) {
    player.src = variant.file;
    player.dataset.file = variant.file;
  }

  document.querySelectorAll(".card").forEach((card, cueIndex) => {
    const cueSelected = cueIndex === selectedCueIndex;
    const cuePlaying = playingKey === `${cueIndex}-${selectedPackIndex}`;
    card.classList.toggle("selected", cueSelected);
    card.classList.toggle("playing", cuePlaying);
    const cardVariant = cues[cueIndex].variants[selectedPackIndex];
    const labelNode = card.querySelector("[data-card-variant-label]");
    const nameNode = card.querySelector("[data-card-variant-name]");
    const descriptionNode = card.querySelector("[data-card-description]");
    if (labelNode) {
      labelNode.textContent = `Variant ${cardVariant.label}`;
    }
    if (nameNode) {
      nameNode.textContent = cardVariant.name;
    }
    if (descriptionNode) {
      descriptionNode.textContent = cardVariant.description;
    }
  });

  playButton.textContent = player.paused || playingKey !== key ? "Play selected" : "Pause";
  cycleButton.textContent = cycleMode ? "Stop play all" : "Play all cues";
}

grid.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (button?.dataset.action === "play-cue") {
    playSelection(Number(button.dataset.cueIndex), selectedPackIndex);
    return;
  }

  const cueTarget = event.target.closest("[data-action='select-cue']");
  if (cueTarget) {
    selectCue(Number(cueTarget.dataset.cueIndex));
  }
});

playButton.addEventListener("click", () => {
  const { key } = getSelection();
  if (playingKey === key && !player.paused) {
    player.pause();
    return;
  }
  playSelection();
});

prevButton.addEventListener("click", () => moveCueSelection(-1));
nextButton.addEventListener("click", () => moveCueSelection(1));

cycleButton.addEventListener("click", () => {
  cycleMode = !cycleMode;
  if (cycleMode) {
    playSelection(selectedCueIndex, selectedPackIndex);
  } else {
    player.pause();
  }
  updateVisualState();
});

player.addEventListener("play", () => {
  playingKey = getSelection().key;
  updateVisualState();
});

player.addEventListener("pause", () => {
  if (!cycleMode) {
    playingKey = null;
    updateVisualState();
  }
});

player.addEventListener("ended", () => {
  if (!cycleMode) {
    playingKey = null;
    updateVisualState();
    return;
  }
  const sequence = cycleQueue();
  const currentIndex = sequence.findIndex((entry) => entry.key === getSelection().key);
  const next = sequence[(currentIndex + 1) % sequence.length];
  playSelection(next.cueIndex, next.variantIndex);
});

document.addEventListener("keydown", (event) => {
  if (event.target.tagName === "INPUT" || event.target.tagName === "TEXTAREA") {
    return;
  }

  if (event.key === "ArrowRight") {
    event.preventDefault();
    moveCueSelection(1);
  } else if (event.key === "ArrowLeft") {
    event.preventDefault();
    moveCueSelection(-1);
  } else if (event.code === "Space") {
    event.preventDefault();
    const { key: selectionKey } = getSelection();
    if (playingKey === selectionKey && !player.paused) {
      player.pause();
    } else {
      playSelection();
    }
  }
});

grid.addEventListener("keydown", (event) => {
  const cueTarget = event.target.closest("[data-action='select-cue']");
  if (!cueTarget) {
    return;
  }
  if (event.code === "Enter" || event.code === "Space") {
    event.preventDefault();
    selectCue(Number(cueTarget.dataset.cueIndex));
  }
});

soundpackSelect.addEventListener("change", (event) => {
  const nextPackIndex = Number(event.target.value);
  const shouldKeepPlayback = cycleMode || (playingKey === getSelection().key && !player.paused);
  setSoundpack(nextPackIndex, { preservePlayback: shouldKeepPlayback });
});

renderCards();
