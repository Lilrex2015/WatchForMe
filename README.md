This project is completed

# WatchForMe
A lightweight, GUI-based automation tool built with Python and Selenium to monitor the TalkToMe.com members/programs page for specific value thresholds (e.g., rates). It refreshes the page when values are below targets, clicks a "Connect" button when a target is reached, and plays a customizable sound alert. Designed for personal use in monitoring dynamic web content, with pause/resume functionality and logging.

Changelog
This page tracks the key updates, features, and fixes for the TalkToMe Bot project. Updates are listed in reverse chronological order (newest first). For full commit history, check the Releases or Commits tabs on GitHub.
[v1.3.0] - 2025-11-12
Added

MP3 Audio Support: Switched from winsound to pygame.mixer for cross-platform compatibility and .mp3 playback. Now supports both .mp3 and .wav files.
Default sound file updated to sound_effect/ding.mp3 (place this file in the project directory).
Updated file browser dialog to filter for *.mp3 *.wav.

Dependency Update: Added pygame to requirements (pip install pygame).

Changed

Sound Playback Logic: play_alert_sound method now initializes mixer only when needed and handles non-blocking playback for .mp3 files.
Default Sound Fallback: If no custom file is selected, it checks for sound_effect/ding.mp3. Logs a warning if missing.

Fixed

Audio Compatibility: Resolved issues with .mp3 files not playing (previous winsound limitation).

Installation Notes

Run pip install pygame before building the executable with PyInstaller.
For the .exe build: pyinstaller --onefile --add-data "sound_effect;sound_effect" talktome_bot.py (ensures ding.mp3 is bundled).

Added Dist folder with the .exe so users can run program from desktop.

[v1.2.0] - 2025-11-05
Added

Mute Checkbox: New "Mute Sound" checkbox in the Settings frame to disable audio alerts without removing the file path.
Defaults to unchecked (sound enabled).

Default Sound Fallback: If no custom sound file is specified, defaults to sound_effect/ding.wav (requires the folder and file in the project root).
Path Validation: Checks if the default sound file exists; skips playback with a log message if not found.

Changed

GUI Layout: Adjusted the Sound File Path row to accommodate the mute checkbox (reduced entry width to 25 chars).
Playback Threading: Ensured sound plays asynchronously to avoid blocking the GUI.

Fixed

Empty Path Handling: Previously, empty paths would error; now falls back gracefully.

[v1.1.0] - 2025-10-28
Added

Variable Refresh Timer: Configurable "Max Refresh Interval" (default: 30 seconds) with random delays between 1 and the max value.
Uses random.uniform(1, max_interval) after refreshes or errors.
GUI label updated to "Max Refresh Interval (seconds):".

Sound Alert Feature: Plays a .wav file (via winsound on Windows) when the target value is reached (after clicking Connect).
New "Sound File Path (.wav):" field with Browse button (uses filedialog).
Non-blocking playback with SND_ASYNC.


Changed

Retry Logic: Replaced fixed retry_interval with variable random delays for more human-like behavior.
Error Handling: Applies random delays after exceptions too.

Dependencies

No new pip installs (uses built-in winsound).

[v1.0.0] - 2025-10-15
Added

Initial Release: Core GUI-based bot with Selenium automation.
Monitors <a.vc_rate> for values like "$0.XX".
Refreshes on values in {0.40, 0.50}; clicks <button.api_vc_connect> on target (default: 0.60).
Manual login prompt after browser opens.
Controls: Start/Pause/Resume/Stop/Test Connect.
Real-time logging via redirected stdout to scrolled text widget.

Settings: URL, Target Value, Max Retries (default: 1000).
Threading: Runs automation in a daemon thread to keep GUI responsive.

Prerequisites

pip install selenium
ChromeDriver in PATH.
