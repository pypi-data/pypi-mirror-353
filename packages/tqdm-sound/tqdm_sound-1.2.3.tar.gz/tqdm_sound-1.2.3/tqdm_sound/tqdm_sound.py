import json
import random
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple

import numpy as np
import sounddevice as sd
import soundfile as sf
from importlib import resources
from pynput import keyboard, mouse
from tqdm import tqdm


class TqdmSound:
    """
    Manages sound playback for progress bars without unsafe threading or I/O in callbacks.

    Attributes:
        theme: Sound theme directory name.
        volume: Normalized foreground volume [0-1].
        background_volume: Normalized background volume [0-1].
        activity_mute_seconds: Seconds after activity to mute.
        dynamic_settings_file: Optional Path to a JSON file controlling mute.
    """

    def __init__(
        self,
        theme: str = "ryoji_ikeda",
        volume: int = 100,
        background_volume: int = 50,
        activity_mute_seconds: Optional[int] = 0,
        dynamic_settings_file: Optional[str] = None,
    ) -> None:
        """
        Initialize sound manager.

        Args:
            theme: Name of the theme folder under sounds/.
            volume: Foreground volume percentage (0-100).
            background_volume: Background volume percentage (0-100).
            activity_mute_seconds: Mute duration after user input.
            dynamic_settings_file: Path to JSON file with {"is_muted": true/false}.

        Raises:
            ValueError: If volume parameters out of range.
            FileNotFoundError: If sound files or theme missing.
        """
        if not 0 <= volume <= 100:
            raise ValueError("Volume must be between 0 and 100")
        if not 0 <= background_volume <= 100:
            raise ValueError("Background volume must be between 0 and 100")

        self.volume = volume / 100 if volume is not None else 0
        self.background_volume = background_volume / 100 if background_volume is not None else 0
        self.theme = theme
        self.activity_mute_seconds = activity_mute_seconds
        self.dynamic_settings_file: Optional[Path] = (
            Path(dynamic_settings_file) if dynamic_settings_file else None
        )

        # Storage for sound-device buffers (float32 numpy arrays)
        self.sounds: Dict[str, Tuple[np.ndarray, int]] = {}
        self.click_sounds: list[Tuple[np.ndarray, int]] = []
        self.bg_data: Optional[np.ndarray] = None
        self.bg_samplerate: Optional[int] = None
        self.bg_stream: Optional[sd.OutputStream] = None

        # Load all sound assets into memory
        self._load_sounds()

        # Track last user activity
        self.last_activity_time: float = time.time()
        self.mouse_listener: Any
        self.keyboard_listener: Any
        self._setup_activity_monitors()

        # A flag that tells us whether we're muted.
        self._muted: bool = False
        self._stop_flag: bool = False
        self._mute_thread: Optional[threading.Thread] = None
        self._start_mute_watcher()

        self._bg_started: bool = False
        self._bg_pos: int = 0

    def __del__(self) -> None:
        self.close()

    def _load_sounds(self) -> None:
        """
        Load click effects, fixed tones, and background into memory as NumPy arrays.

        Raises:
            FileNotFoundError: If expected files/directories are missing.
        """
        base = Path(resources.files("tqdm_sound")).joinpath("sounds", self.theme)
        if not base.exists():
            raise FileNotFoundError(f"Theme directory {base} not found")

        # Click effects: load all click_*.wav
        for click_file in base.glob("click_*.wav"):
            data, sr = sf.read(str(click_file), dtype="float32")
            self.click_sounds.append((data, sr))

        # Fixed tones and background
        file_mapping = {
            "start": "start_tone.wav",
            "semi_major": "semi_major.wav",
            "mid": "mid_tone.wav",
            "end": "end_tone.wav",
            "program_end": "program_end_tone.wav",
            "background": "background_tone.wav",
        }
        for name, filename in file_mapping.items():
            path = base / filename
            if not path.exists():
                raise FileNotFoundError(f"Missing sound file: {path}")

            data, sr = sf.read(str(path), dtype="float32")

            if name == "background":
                self.bg_data = data
                self.bg_samplerate = sr
            else:
                self.sounds[name] = (data, sr)

    def _setup_activity_monitors(self) -> None:
        """
        Launch listeners to reset activity timestamp on mouse/keyboard events.
        """
        self.mouse_listener = mouse.Listener(
            on_move=self._update_activity,
            on_click=self._update_activity,
            on_scroll=self._update_activity,
        )

        self.keyboard_listener = keyboard.Listener(on_press=self._update_activity)
        self.mouse_listener.start()
        self.keyboard_listener.start()

        if self.activity_mute_seconds:
            # Allow immediate sound if mute configured
            self.last_activity_time = time.time() - self.activity_mute_seconds

    def _update_activity(self, *args: Any, **kwargs: Any) -> None:
        """
        Callback to record the time of latest user interaction.
        """
        self.last_activity_time = time.time()

    def _compute_muted_state(self) -> bool:
        """
        Check dynamic file flag and activity timeout to compute mute state.

        Returns:
            True if muted, False otherwise.
        """
        # Check dynamic settings file
        if self.dynamic_settings_file and self.dynamic_settings_file.exists():
            try:
                cfg = json.loads(self.dynamic_settings_file.read_text())
                if cfg.get("is_muted", False):
                    return True
            except Exception:
                pass

        # Check activity-based mute
        if (
            self.activity_mute_seconds is not None
            and (time.time() - self.last_activity_time) < self.activity_mute_seconds
        ):
            return True

        return False

    def _check_muted_flag(self) -> None:
        """
        Runs in a separate thread. Every 100 ms, update self._muted.
        """
        while not self._stop_flag:
            self._muted = self._compute_muted_state()
            time.sleep(0.1)

    def _start_mute_watcher(self) -> None:
        """
        Start the background thread that watches for mute changes.
        """
        self._mute_thread = threading.Thread(target=self._check_muted_flag, daemon=True)
        self._mute_thread.start()

    def _stop_mute_watcher(self) -> None:
        """
        Signal the mute watcher thread to stop and join it.
        """
        self._stop_flag = True
        if self._mute_thread:
            self._mute_thread.join(timeout=0.5)

    def set_volume(
        self,
        volume: float,
        mute: bool = False,
        background_volume: Optional[float] = None
    ) -> None:
        """
        Update normalized volumes or mute all sounds.

        Args:
            volume: Foreground volume (0-1).
            mute: If True, set volumes to zero.
            background_volume: Optional background volume override (0-1).
        """
        self.volume = 0.0 if mute else volume

        if background_volume is not None:
            self.background_volume = 0.0 if mute else background_volume

    def _play(
        self, data: np.ndarray, samplerate: int, override_volume: Optional[float] = None
    ) -> None:
        """
        Play a buffer via sounddevice, respecting mute flag and volume scaling.

        Args:
            data: NumPy array of audio samples.
            samplerate: Sample rate of data.
            override_volume: If provided, use this instead of self.volume.
        """
        if self._muted:
            return

        vol = self.volume if override_volume is None else override_volume
        if vol <= 0:
            return

        sd.play(data * vol, samplerate)

    def _mix_background_chunk(self, frames: int) -> np.ndarray:
        """
        Generate a chunk of background data of length `frames`, scaled and rolled.

        Args:
            frames: Number of samples to produce.

        Returns:
            A NumPy array of shape (frames, channels) or (frames,) scaled by background_volume.
        """
        if self.bg_data is None or self.bg_samplerate is None:
            return np.zeros((frames,))

        length = len(self.bg_data)
        # Extract slice and wrap around if needed
        if self._bg_pos + frames <= length:
            chunk = self.bg_data[self._bg_pos : self._bg_pos + frames]
        else:
            first_part = self.bg_data[self._bg_pos : length]
            second_len = frames - (length - self._bg_pos)
            second_part = self.bg_data[0:second_len]
            chunk = np.concatenate((first_part, second_part), axis=0)

        self._bg_pos = (self._bg_pos + frames) % length

        return chunk * self.background_volume  # type: ignore

    def _start_background_loop(self) -> None:
        """
        Begin continuous background playback via sounddevice callback.
        Subsequent calls have no effect until stopped.
        """
        if self._bg_started or self.bg_data is None or self.bg_samplerate is None:
            return

        self._bg_started = True
        self._bg_pos = 0

        channels = (
            self.bg_data.shape[1]
            if hasattr(self.bg_data, "ndim") and self.bg_data.ndim > 1
            else 1
        )

        def callback(outdata: np.ndarray, frames: int, time_info: Any, status: Any) -> None:
            if self._muted or self.background_volume <= 0:
                outdata.fill(0)
                return

            chunk = self._mix_background_chunk(frames)
            if channels > 1 and chunk.ndim == 1:
                # Duplicate mono to stereo (or more)
                chunk = np.tile(chunk[:, None], (1, channels))

            outdata[:] = chunk

        self.bg_stream = sd.OutputStream(
            samplerate=self.bg_samplerate, channels=channels, callback=callback
        )

        self.bg_stream.start()

    def _stop_background(self) -> None:
        """
        Cease background playback and reset state.
        """
        if self.bg_stream:
            self.bg_stream.stop()
            self.bg_stream.close()

        self._bg_started = False

    def play_sound(self, sound_name: str) -> None:
        """
        Play a named tone or start the background loop.

        Args:
            sound_name: One of 'start', 'semi_major', 'mid', 'end', 'program_end', 'background'.
        """
        if sound_name == "background":
            self._start_background_loop()
            return

        if self._muted:
            return

        pair = self.sounds.get(sound_name)
        if not pair:
            return

        data, sr = pair

        self._play(data, sr)

    def play_random_click(self) -> None:
        """
        Play one randomly chosen click effect via sounddevice.
        """
        if self._muted or not self.click_sounds:
            return

        data, sr = random.choice(self.click_sounds)

        self._play(data, sr)

    def play_final_end_tone(self, volume: Optional[int] = None) -> None:
        """
        Play the program_end tone.

        Args:
            volume: Optional override percent; if None, use self.volume.
        """
        if self._muted:
            return

        pair = self.sounds.get("program_end")
        if not pair:
            return

        data, sr = pair
        vol = volume / 100 if volume is not None else self.volume

        self._play(data, sr, override_volume=vol)

    def progress_bar(
        self,
        iterable: Iterable,
        desc: str,
        volume: Optional[int] = 100,
        background_volume: Optional[int] = 80,
        end_wait: float = 0.04,
        ten_percent_ticks: bool = False,
        play_end_sound: bool = True,
        **tqdm_kwargs: Any,
    ) -> "SoundProgressBar":
        """
        Wrap an iterable in a sound-enabled tqdm.

        Args:
            iterable: Any iterable to track.
            desc: Progress description.
            volume: Foreground volume percent override.
            background_volume: Background volume percent override.
            end_wait: Delay after completion.
            ten_percent_ticks: Enable ticks every 10%.
            play_end_sound: Plays a final tone at the end of the iteration.
            **tqdm_kwargs: Additional tqdm args.

        Returns:
            SoundProgressBar instance.
        """
        vol = volume / 100 if volume is not None else self.volume
        bg = background_volume / 100 if background_volume is not None else self.background_volume

        self.set_volume(vol, False, bg)

        try:
            total = len(iterable)  # type: ignore[arg-type]
        except (TypeError, AttributeError):
            total = None

        common: Dict[str, Any] = {
            "iterable": iterable,
            "desc": desc,
            "total": total,
            "volume": vol,
            "background_volume": bg,
            "end_wait": end_wait,
            "ten_percent_ticks": ten_percent_ticks,
            "play_end_sound": play_end_sound,
            "sound_manager": self,
        }

        common.update(tqdm_kwargs)

        return SoundProgressBar(**common)

    def close(self) -> None:
        """
        Stop listeners, background loop, and clean up. Called on destruction.
        """
        if hasattr(self, "mouse_listener") and self.mouse_listener.running:
            self.mouse_listener.stop()

        if hasattr(self, "keyboard_listener") and self.keyboard_listener.running:
            self.keyboard_listener.stop()

        self._stop_background()
        self._stop_mute_watcher()


class SoundProgressBar(tqdm):
    """
    tqdm subclass that triggers sounds at progress milestones.
    """

    def __init__(
        self,
        iterable: Iterable,
        desc: str,
        total: Optional[int] = None,
        volume: float = 1.0,
        background_volume: float = 1.0,
        end_wait: float = 0.04,
        ten_percent_ticks: bool = False,
        play_end_sound: bool = True,
        sound_manager: TqdmSound = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the sound progress bar.

        Args:
            iterable: Iterable to wrap.
            desc: Description text.
            total: Optional total count for tqdm (None if unknown).
            volume: Foreground volume (0-1).
            background_volume: Background volume (0-1).
            end_wait: Delay after finish.
            ten_percent_ticks: Sound ticks every 10%.
            play_end_sound: Plays a final tone at the end of the iteration.
            sound_manager: TqdmSound instance for playback.
            **kwargs: Other tqdm parameters.
        """
        self.sound_manager = sound_manager
        self.volume = volume
        self.background_volume = background_volume
        self.end_wait = end_wait
        self.ten_percent_ticks = ten_percent_ticks
        self.play_end_sound = play_end_sound
        self.mid_played = False
        self._played_milestones: set[int] = set()

        super().__init__(iterable=iterable, desc=desc, total=total, **kwargs)

    def _update_volume(self) -> None:
        """
        Respect mute-on-activity by updating volumes from the watcher thread.
        """
        is_muted = self.sound_manager._muted
        self.sound_manager.set_volume(self.volume, is_muted, self.background_volume)

    def _play_start_sequence(self) -> None:
        """
        Play the start tone and begin background loop.
        """
        self.sound_manager.play_sound("start")
        self.sound_manager.play_sound("background")
        # Initialize milestone tracking
        self._played_milestones = {0}

    def _play_iteration_milestones(self, index: int) -> None:
        """
        On each iteration, play a click plus optional mid-point or 10% ticks.

        Args:
            index: Current zero-based iteration count.
        """
        self._update_volume()
        self.sound_manager.play_random_click()

        if not self.total:
            return

        pct = int((index + 1) / self.total * 100)
        # Midpoint at 50%
        if not self.mid_played and pct >= 50:
            self.sound_manager.play_sound("mid")
            self.mid_played = True
            self._played_milestones.add(50)

        # Ticks every 10%
        if self.ten_percent_ticks:
            tick = (pct // 10) * 10
            if tick not in self._played_milestones and pct >= tick:
                self.sound_manager.play_sound("semi_major")
                self._played_milestones.add(tick)

    def _play_end_sequence(self) -> None:
        """
        Play the end tone, wait, and stop background loop.
        """
        if self.play_end_sound:
            self.sound_manager.play_sound("end")

        time.sleep(self.end_wait)

        self.sound_manager._stop_background()

    def __iter__(self) -> Iterator:
        """
        Iterate with sound callbacks:
        - start tone
        - background drone
        - click per iteration
        - mid-tone at 50%
        - optional ticks every 10%
        - end tone and stop drone

        Yields:
            Each item from the wrapped iterable.
        """

        self._play_start_sequence()

        try:
            for i, item in enumerate(super().__iter__()):
                self._play_iteration_milestones(i)
                yield item
        finally:
            self._play_end_sequence()
