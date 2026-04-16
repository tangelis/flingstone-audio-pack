const cues = [
  {
    id: "01",
    title: "Rubber Stretch",
    file: "assets/01_rubber_stretch.wav",
    type: "aim",
    description: "A creaky, rising elastic pull for aiming tension."
  },
  {
    id: "02",
    title: "Projectile Release",
    file: "assets/02_projectile_release.wav",
    type: "action",
    description: "Short snap and whoosh for the slingshot launch."
  },
  {
    id: "03",
    title: "Blocks Falling",
    file: "assets/03_blocks_falling.wav",
    type: "impact",
    description: "Layered stone crashes and debris for collapse moments."
  },
  {
    id: "04",
    title: "Core Hit",
    file: "assets/04_core_hit.wav",
    type: "special",
    description: "A bright bell-like strike for the special target block."
  },
  {
    id: "05",
    title: "Small Explosion",
    file: "assets/05_small_explosion.wav",
    type: "impact",
    description: "Compact pop and dusty burst for minor blasts."
  },
  {
    id: "06",
    title: "Big Explosion",
    file: "assets/06_big_explosion.wav",
    type: "impact",
    description: "Deep boom with collapse layers for major destruction."
  },
  {
    id: "07",
    title: "Background Music Loop",
    file: "assets/07_background_music_loop.wav",
    type: "music",
    description: "Bouncy loopable theme for gameplay."
  },
  {
    id: "08",
    title: "UI Button Click",
    file: "assets/08_ui_button_click.wav",
    type: "ui",
    description: "Short, clean menu tap with a soft thock."
  },
  {
    id: "09",
    title: "Slow Motion Zoom",
    file: "assets/09_slow_motion_zoom.wav",
    type: "vfx",
    description: "Whooshy time-dilation cue for dramatic zooms."
  },
  {
    id: "10",
    title: "Points Increase",
    file: "assets/10_points_increase.wav",
    type: "ui",
    description: "Fast rising dings for score tally moments."
  },
  {
    id: "11",
    title: "Victory Sound",
    file: "assets/11_victory_sound.wav",
    type: "reward",
    description: "Short fanfare for level completion."
  },
  {
    id: "12",
    title: "Unsuccessful Sound",
    file: "assets/12_unsuccessful_sound.wav",
    type: "fail",
    description: "A compact, playful fail sting."
  },
  {
    id: "13",
    title: "Clock Running Out",
    file: "assets/13_clock_running_out.wav",
    type: "tension",
    description: "Ticking sequence that accelerates into urgency."
  },
  {
    id: "14",
    title: "Bonus Powerup",
    file: "assets/14_bonus_powerup.wav",
    type: "reward",
    description: "Sparkly rising reward cue for pickups."
  }
];

const grid = document.getElementById("sound-grid");
const title = document.getElementById("active-title");
const description = document.getElementById("active-description");
const player = document.getElementById("main-player");
const playButton = document.getElementById("play-button");
const prevButton = document.getElementById("prev-button");
const nextButton = document.getElementById("next-button");
const cycleButton = document.getElementById("cycle-button");

let selectedIndex = 0;
let playingIndex = null;
let cycleMode = false;

function renderCards() {
  grid.innerHTML = "";
  cues.forEach((cue, index) => {
    const card = document.createElement("article");
    card.className = "card";
    card.dataset.index = String(index);
    card.innerHTML = `
      <div class="card-top">
        <span class="card-index">CUE ${cue.id}</span>
        <span class="card-chip">${cue.type}</span>
      </div>
      <h3>${cue.title}</h3>
      <p>${cue.description}</p>
      <div class="card-actions">
        <button class="mini" data-action="select" data-index="${index}">Select</button>
        <button class="mini" data-action="play" data-index="${index}">Play</button>
      </div>
    `;
    grid.appendChild(card);
  });
  updateVisualState();
}

function updateVisualState() {
  const cards = Array.from(document.querySelectorAll(".card"));
  cards.forEach((card, index) => {
    card.classList.toggle("selected", index === selectedIndex);
    card.classList.toggle("playing", index === playingIndex);
  });
  const cue = cues[selectedIndex];
  title.textContent = cue.title;
  description.textContent = cue.description;
  if (player.dataset.file !== cue.file) {
    player.src = cue.file;
    player.dataset.file = cue.file;
  }
  playButton.textContent = player.paused || playingIndex !== selectedIndex ? "Play selected" : "Pause";
  cycleButton.textContent = cycleMode ? "Stop play all" : "Play all cues";
}

function selectCue(index) {
  selectedIndex = (index + cues.length) % cues.length;
  updateVisualState();
}

function playCue(index) {
  selectedIndex = (index + cues.length) % cues.length;
  playingIndex = selectedIndex;
  updateVisualState();
  player.currentTime = 0;
  player.play().catch(() => {});
}

function nextCue(autoPlay = false) {
  selectCue(selectedIndex + 1);
  if (autoPlay) {
    playCue(selectedIndex);
  }
}

function prevCue() {
  selectCue(selectedIndex - 1);
}

grid.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  const index = Number(button.dataset.index);
  if (button.dataset.action === "select") {
    selectCue(index);
  } else if (button.dataset.action === "play") {
    playCue(index);
  }
});

playButton.addEventListener("click", () => {
  if (playingIndex === selectedIndex && !player.paused) {
    player.pause();
    return;
  }
  playCue(selectedIndex);
});

prevButton.addEventListener("click", prevCue);
nextButton.addEventListener("click", () => nextCue(false));

cycleButton.addEventListener("click", () => {
  cycleMode = !cycleMode;
  if (cycleMode) {
    playCue(selectedIndex);
  } else {
    player.pause();
  }
  updateVisualState();
});

player.addEventListener("play", () => {
  playingIndex = selectedIndex;
  updateVisualState();
});

player.addEventListener("pause", () => {
  if (!cycleMode) {
    playingIndex = null;
    updateVisualState();
  }
});

player.addEventListener("ended", () => {
  if (cycleMode) {
    selectedIndex = (selectedIndex + 1) % cues.length;
    playCue(selectedIndex);
  } else {
    playingIndex = null;
    updateVisualState();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.target.tagName === "INPUT" || event.target.tagName === "TEXTAREA") {
    return;
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    nextCue(false);
  } else if (event.key === "ArrowLeft") {
    event.preventDefault();
    prevCue();
  } else if (event.code === "Space") {
    event.preventDefault();
    if (playingIndex === selectedIndex && !player.paused) {
      player.pause();
    } else {
      playCue(selectedIndex);
    }
  }
});

renderCards();
