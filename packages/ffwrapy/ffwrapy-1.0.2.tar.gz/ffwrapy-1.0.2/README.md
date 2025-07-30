# ffwrapy

**ffwrapy** is a  fast, flexible Python wrapper for FFmpeg, FFprobe, and FFplay — fetch metadata, encode, split, and run custom commands easily with real-time progress tracking.

---

## Features

- Fetch media info (duration, size, streams) via FFprobe
- Encode with custom codecs, presets, and metadata via FFmpeg
- Split files or split into parts (with/without re-encoding)
- Generate thumbnails from videos
- Custom command execution for ffmpeg, ffprobe, ffplay
- Track naming and title setting
- Progress callback support for long operations (encoding, splitting, etc)
- Pure `subprocess` (no dependencies except Python & FFmpeg)

---

## Requirements

- Python 3.x
- FFmpeg, FFprobe, and FFplay installed and available in the system PATH

NOTE: Only FFprobe required at initialisation; FFmpeg required only during associated tasks like encoding, splitting, etc; FFplay required only during custom command processing

```bash
ffmpeg -version
ffprobe -version
ffplay -version
```

---

## Installation

```bash
pip install ffwrapy
```

---

## Usage

### Initialization

```python
from ffwrapy import FFMedia as FFM
media = FFM(
    file="input.mp4",   # Input file
    verbose=True        # To trigger any print statements in the script; Default: False
    )
```

### Fetching Media Info

```python
print(media.size_mb)      # File size in MB
print(media.duration)     # Duration in seconds
print(media.audiodata)    # Audio tracks info
print(media.videodata)    # Video tracks info
print(media.subtitles)    # Subtitle tracks info
```

### Preparing to Encode

```python
# Naming Tracks and Title
media.name(
    aud_name="ffwrapy_aud",    # Name for all audio tracks 
    vid_name="ffwrapy_vid",    # Name for all video tracks 
    sub_name="ffwrapy_sub",    # Name for all subtitle tracks 
    title="ffwrapy title"      # Name for the output video title 
    )   # Default : <the name as defined in input file ie media>

# Defining Preset and Codecs
media.codec_vid = "libx264"     	# Name for video codec;     Default : "libx264"
media.codec_aud = "aac"         	# Name for audio codec;     Default : "aac"
media.codec_sub = "mov_text"   		# Name for subtitle codec;  Default : "mov_text"
media.crf = "23"                	# Value for crf (0-51);     Default : "23"
media.preset = "faster"         	# Preset to be used;        Default : "faster"
media.movflags = "+faststart"   	# Value for moov atom;      Default : "+faststart"
media.max_muxing_queue_size = "99"	# Max size for mux queue;   Default : "9999"
```

### Encoding

```python
media.encode(
    output="output.mp4",    # Name for output encoded file
    thumb="00:00:05",       # Timestamp in "HH:MM:SS" format to generate output.jpg from the processed video at the given time
    replace=True,           # Overwrite output if exists
    )
```
- `output` Name for output encoded file
- `ss`: Start time (string or seconds); Default : None (ie from beginning)
- `to`: End time (string or seconds); Default : None (ie till ending)
- `thumb`: Timestamp in "HH:MM:SS" format to generate output.jpg from the processed video at the given time; Default : None (ie no thumbnail generated)
- `replace`: Overwrite output if exists; Default : False
- `progress_callback`: Callback function to track progress; Args : (progress as a dict), (process object); Default : None
- `callback_interval`: The interval (in seconds) between each callback; Default : 1

### Splitting

```python
media.split(
    output="output_clip.mp4",   # Name for output splitted file
    ss="00:01:00",              # Start time (string or seconds)
    to="00:02:00",              # End time (string or seconds)
    replace=True,               # Overwrite output if exists
    )
```
- `output` Name for output splitted file
- `ss`: Start time (string or seconds); Default : None (ie from beginning)
- `to`: End time (string or seconds); Default : None (ie till ending)
- `thumb`: Timestamp in "HH:MM:SS" format to generate output.jpg from the processed video at the given time; Default : None (ie no thumbnail generated)
- `replace`: Overwrite output if exists; Default : False
- `progress_callback`: Callback function to track progress; Args : (progress as a dict), (process object); Default : None
- `callback_interval`: The interval (in seconds) between each callback; Default : 1

### Splitting into Parts

```python
media.split_parts(
    output = "part.mp4",    # Base name for the output
    parts=3,                # Number of parts to split into
    safe_time=5,            # Repetion duration (in seconds) between each part to conserve any diversion
    reencode=False,         # Whether to reencode the file
    )
```
- `output` Base name for the output; if a string is provided, forms an array with each element as 'i_out' where i is the part name and out is the provided string; if an array is provided, the elements of array are used as the part name
- `parts` Number of parts to split into; Default : 2
- `safe_time` Repetion duration (in seconds) between each part to conserve any diversion; Default : 5
- `reencode=True` Whether to reencode the file (accurate but takes time), reencode uses .encode() otherwise .split() is used which is quick but may not be accurate; Default : False
- `thumb`: Timestamp in "HH:MM:SS" format to generate output.jpg from the processed video at the given time; Default : None (ie no thumbnail generated)
- `replace`: Overwrite output if exists; Default : False
- `progress_callback`: Callback function to track progress; Args : (progress as dict), (process object), (serial number of part as int); Default : None
- `callback_interval`: The interval (in seconds) between each callback; Default : 1

### Thumbnail Generation

```python
media.thumbnail(
    replace=True    # Overwrite output if exists
    )
```
- `timestamp` The timestamp in the input file at which thumbnail is to be generated; Default : "00:00:05"
- `file` The input filename whose thumbnail is to be generated; Default: None (ie media.file)
- `replace`: Overwrite output if exists; Default : False

### Custom FFmpeg/FFprobe/FFplay Command

```python
media.custom_ffmedia(
    customisation=["ffprobe", "-hide_banner", media.file]
    )
media.custom_ffm(
    customisation=["ffprobe", "-hide_banner", media.file]
    )   # Same as .custom_ffmedia()

media.custom_ffmedia(
    customisation=["ffplay", media.file]
    )
media.custom_ffm(
    customisation=["ffplay", media.file]
    )  # Same as .custom_ffmedia()
```
- `customisation` The custom cmd array for FFmpeg/FFprobe/FFplay Command
- `thumb`: Timestamp in "HH:MM:SS" format to generate output.jpg from the processed video at the given time; Default : None (ie no thumbnail generated)
- `replace`: Overwrite output if exists; Default : False
- `progress_callback`: Callback function to track progress; Args : (progress as dict), (process object); Default : None
- `callback_interval`: The interval (in seconds) between each callback; Default : 1
---

## Example Workflow

```python
from ffwrapy import FFMedia as FFM
media = FFM("movie.ts", verbose=True)
media.name("HIN", "Main", "HIN Subs", title="Demo Movie")
media.encode("movie.mkv", thumb="00:00:05")
media_encoded = FFM("movie.mkv")
media_encoded.split("movie_clip.mp4", ss="00:10:00", to="00:15:00")
media_encoded.split_parts("movie_part.mp4", parts=4)
media_encoded.thumbnail()
media_encoded.custom_ffmedia(["ffmpeg", "-i", media_encoded.file, "-vn", "-acodec", "copy", "audio.aac"])
```

---

## Notes

- All operations use subprocess calls to FFmpeg/FFprobe/FFplay; ensure these are installed and accessible.
- Error handling is basic; adapt for production use as needed.
- Extend or modify the class for advanced workflows.

---

## License

**Apache License 2.0**

This library is open-source and free to use under the [Apache 2.0 License](./LICENSE).

---

## Contributing

Contributions, suggestions, and feature requests are welcome! Feel free to submit an issue or PR.

---

## Author

Developed by [भाग्य ज्योति (Bhagya Jyoti)](https://github.com/BhagyaJyoti22006)

---

**Happy media processing!**