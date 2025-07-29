# modbox-omxplayer-wrapper

**Version:** 0.1  
**Author:** Marcelo Prestes  
**Email:** marcelo.prestes@gmail.com

## Description

`modbox-omxplayer-wrapper` is a **wrapper for `omxplayer`**, developed for embedded systems (such as Raspberry Pi), fully compatible with **Python 2.7**.  
It allows video playback control via subprocess, duration detection via `ffprobe`, and safe process management for the player.

## Requirements

- Python 2.7
- `omxplayer` installed
- `ffprobe` (provided by the `ffmpeg` package)

## Installation

### From local file

```bash
pip2 install modbox-omxplayer-wrapper-0.1.tar.gz
```

### (Optional) From PyPI

```bash
pip2 install modbox-omxplayer-wrapper
```

## Basic usage

```python
from modbox_omxplayer_wrapper import OMX

# Create and start playback immediately
player = OMX('/home/pi/videos/video.mp4', start=True)

# Check if it's playing
if player.is_running():
    print("The video is playing!")

# Stop playback
player.stop()
```

---

## Constructor parameters

```python
OMX(video_file, omx_parameters="", start=True, duration=None)
```

| Parameter         | Type     | Description                                                                  |
|-------------------|----------|------------------------------------------------------------------------------|
| `video_file`      | `str`    | Full path to the video file.                                                 |
| `omx_parameters`  | `str`    | Additional `omxplayer` CLI parameters (e.g. `--no-osd`).                     |
| `start`           | `bool`   | If `True`, starts playback immediately upon instantiation.                   |
| `duration`        | `float`  | Manually specify video duration in seconds. If omitted, uses `ffprobe`.      |

---

## Available methods

| Method             | Description                                                                  |
|--------------------|------------------------------------------------------------------------------|
| `play()`           | Starts playback if not already running.                                      |
| `stop()`           | Stops playback using `SIGKILL` for processes identified via `/proc`.         |
| `is_running()`     | Returns `True` if the player is currently running.                           |
| `get_duration()`   | Returns the estimated video duration (as a float).                           |

---

## Notes

- Uses `DBUS_SESSION_BUS_ADDRESS=/dev/null` to avoid conflicts.
- Avoids using `killall` by manually identifying processes based on the video filename.
- Ideal for integration with embedded media systems and kiosk interfaces.

---

## License

Distributed under the [MIT License](LICENSE).

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of this software, provided that the original copyright notice is retained.

This software is provided "as is", without any warranty. See the [LICENSE](LICENSE) file for more details.

