import subprocess
import json
import time


class FFMedia:
    def __init__(self, file, verbose=False):
        self.verbose = verbose
        self.codec_vid = "libx264"
        self.codec_aud = "aac"
        self.codec_sub = "mov_text"
        self.crf = "23"
        self.preset = "faster"
        self.movflags = "+faststart"
        self.max_muxing_queue_size = "9999"
        self.dsh = "----------------------------------------"
        self.file = file
        self.size_mb = 0
        self.duration = 0
        self.audiodata = []
        self.videodata = []
        self.subtitles = []
        self.title = None
        self.fetch()
    
    
    def fetch(self):
        if self.verbose: print(self.dsh)
        if self.verbose: print("Fetching the file:-")
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries",
            "format=duration,filename,size:stream=index,codec_type,codec_name,width,height:stream_tags=language,title",
            "-of", "json", self.file
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            info = json.loads(result.stdout)
            size_bytes = int(info["format"]["size"])
            self.size_mb = size_bytes / (1024 * 1024)
            self.duration = float(info.get("format", {}).get("duration", 0.0))
            for stream in info.get("streams", []):
                codec_type = stream.get("codec_type")
                index = stream.get("index")
                codec_name = stream.get("codec_name")
                width = stream.get("width")
                height = stream.get("height")
                tags = stream.get("tags", {})
                language = tags.get("language", "und")
                title = tags.get("title", "Unnamed")
                track_info = {
                    "index": index,
                    "codec": codec_name,
                    "width": width,
                    "height": height,
                    "language": language.lower(),
                    "title": title,
                    "name": None
                }
                if codec_type == "audio":
                    self.audiodata.append(track_info)
                elif codec_type == "video":
                    self.videodata.append(track_info)
                elif codec_type == "subtitle":
                    self.subtitles.append(track_info)
            if self.verbose: print(f"Filename: {self.file}")
            if self.verbose: print(f"Total size in mb: {self.size_mb}")
            if self.verbose: print(f"Total duration: {self.duration}")
            if self.verbose: print(f"Total audio tracks: {len(self.audiodata)}")
            if self.verbose: print(f"Total video tracks: {len(self.videodata)}")
            if self.verbose: print(f"Total subtitle tracks: {len(self.subtitles)}")
            if self.verbose: print(self.dsh)
            return info
        except Exception as e:
            if self.verbose: print("Error:", e)
            if self.verbose: print(self.dsh)
        return False
    
    def name(self, aud_name, vid_name, sub_name, title=None):
        for aud in self.audiodata:
            aud["name"] = aud_name
        for vid in self.videodata:
            vid["name"] = vid_name
        for sub in self.subtitles:
            sub["name"] = sub_name
        self.title = title
        return self.file
    
    def thumbnail(self, timestamp="00:00:05", file=None, replace=False):
        if self.verbose: print(self.dsh)
        if file is None:
            file=self.file
        if self.verbose: print(f"Creating a thumbnail at {timestamp}:-")
        t = "ffmpeg"
        t += " -hide_banner -loglevel error -nostats"
        if replace:
            t += " -y"
        t += f" -ss {timestamp} -i \"{file}\" -vframes 1 -q:v 2 \"{file}.jpg\""
        try:
            subprocess.run(t, shell=True, check=True)
        except Exception as e:
            if self.verbose: print("Error:", e)
            if self.verbose: print(self.dsh)
            return False
        if self.verbose: print("Thumbnail creation finished")
        if self.verbose: print(self.dsh)
        return f"\"{file}.jpg\""
    
    def encode(self, output, ss=None, to=None, thumb=None, replace=False, progress_callback=None, callback_interval=1):
        if self.verbose: print(self.dsh)
        if self.verbose: print("Encoding the file:-")
        if self.file==output:
            raise ValueError("output=input error\nTask Cancelled")
            if self.verbose: print(self.dsh)
            return False
        f = ["ffmpeg"]
        f += ["-hide_banner"]
        f += ["-progress", "pipe:1"]
        f += ["-i", self.file]
        if ss is not None:
            f += ["-ss", ss]
        if to is not None:
            f += ["-to", to]
        name = self.title or self.videodata[0]["title"]
        f += ["-metadata", f"title={name}"]
        f += ["-map", "0:v:0"]
        for idx,i in enumerate(self.audiodata):
            f += ["-map", f"0:a:{idx}"]
        for idx,i in enumerate(self.subtitles):
            f += ["-map", f"0:s:{idx}"]
        name = self.videodata[0]["name"] or self.videodata[0]["title"] or "Unnamed"
        f += ["-metadata:s:v:0", f"title={name}"]
        for idx, i in enumerate(self.audiodata):
            name = i["name"] or i["title"] or "Unnamed"
            f += [f"-metadata:s:a:{idx}", f"title={name}"]
            f += [f"-metadata:s:a:{idx}", f"language={i["language"]}"]
        for idx, i in enumerate(self.subtitles):
            name = i["name"] or i["title"] or "Unnamed"
            f += [f"-metadata:s:s:{idx}", f"title={name}"]
            f += [f"-metadata:s:s:{idx}", f"language={i["language"]}"]
        f += ["-c", "copy", "-c:v", self.codec_vid, "-c:a", self.codec_aud, "-c:s", self.codec_sub,
            "-crf", self.crf, "-preset", self.preset, "-movflags", self.movflags, 
            "-max_muxing_queue_size", self.max_muxing_queue_size]
        if replace:
            f += ["-y"]
        f += [output]
        try:
            process = subprocess.Popen(f,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True, bufsize=1
            )
            progress = {}
            last = 0
            while True:
                line = process.stdout.readline()
                if line == "":
                    break
                line = line.strip()
                if line == "": 
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    progress[key] = value
                    if key == "progress":
                        now = time.time()
                        if progress_callback and (now - last) >= callback_interval:
                            progress_callback(progress.copy(),process)
                            last = now
                if progress.get("progress") == "end":
                    break
            process.wait()
        except Exception as e:
            if self.verbose: print("Error:", e)
            if self.verbose: print(self.dsh)
            return False
        if self.verbose: print("Encoding finished")
        if thumb is not None:
            self.thumbnail(thumb,output,replace)
        else:
            if self.verbose: print(self.dsh)
        return output
    
    def split(self, output, ss=None, to=None, thumb=None, replace=False, progress_callback=None, callback_interval=1):
        if self.verbose: print(self.dsh)
        if self.verbose: print("Splitting the file:-")
        if self.file==output:
            raise ValueError("output=input error\nTask Cancelled")
            if self.verbose: print(self.dsh)
            return False
        f = ["ffmpeg"]
        f += ["-hide_banner"]
        f += ["-progress", "pipe:1"]
        f += ["-i", self.file]
        if ss is not None:
            f += ["-ss", ss]
        if to is not None:
            f += ["-to", to]
        f += ["-map", "0"]
        f += ["-c", "copy"]
        if replace:
            f += ["-y"]
        f += [output]
        try:
            process = subprocess.Popen(f,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True, bufsize=1
            )
            progress = {}
            last = 0
            while True:
                line = process.stdout.readline()
                if line == "":
                    break
                line = line.strip()
                if line == "": 
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    progress[key] = value
                    if key == "progress":
                        now = time.time()
                        if progress_callback and (now - last) >= callback_interval:
                            progress_callback(progress.copy(),process)
                            last = now
                if progress.get("progress") == "end":
                    break
            process.wait()
        except Exception as e:
            if self.verbose: print("Error:", e)
            if self.verbose: print(self.dsh)
            return False
        if self.verbose: print("Splitting finished")
        if thumb is not None:
            self.thumbnail(thumb,output,replace)
        else:
            if self.verbose: print(self.dsh)
        return output
    
    def split_parts(self, output, parts=2, safe_time=5, reencode=False, thumb=None, replace=False, progress_callback=None, callback_interval=1):
        if self.verbose: print(self.dsh)
        if self.verbose: print("Splitting file into parts:-")
        part_duration = self.duration/parts
        if self.verbose: print(f"Total parts: {parts}\nPart duration: {part_duration}s")
        if not isinstance(output, list):
            out = output
            output = []
            for i in range(parts):
                output.append(f"{i+1}_{out}")
        for i in range(parts):
            ss = str(max(0, i * part_duration - safe_time))
            to = str(min(self.duration, (i+1)*part_duration))
            if reencode:
                self.encode(
                    output = output[i],
                    ss = ss,
                    to = to,
                    thumb = thumb,
                    replace = replace,
                    progress_callback = lambda progress,process, i=i: progress_callback(progress, process, i),
                    callback_interval = callback_interval,
                )
            else:
                self.split(
                    output = output[i],
                    ss = ss,
                    to = to,
                    thumb = thumb,
                    replace = replace,
                    progress_callback = lambda progress,process, i=i: progress_callback(progress, process, i),
                    callback_interval = callback_interval
                )
        if self.verbose: print("Splitting file into parts finished")
        if self.verbose: print(self.dsh)
        return output
    
    def custom_ffmedia(self, customisation, thumb=None, replace=False, progress_callback=None, callback_interval=1):
        if self.verbose: print(self.dsh)
        if self.verbose: print("Custom FFM usage:-")
        if customisation[0] not in ["ffmpeg","ffprobe","ffplay"]:
            raise ValueError(f"Unspecified input; {customisation[0]} is not a valid FFMedia library")
        if self.verbose: print(f"CMD | {customisation}")
        try:
            process = subprocess.Popen(customisation,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True, bufsize=1
            )
            progress = {}
            last = 0
            while True:
                line = process.stdout.readline()
                if line == "":
                    break
                line = line.strip()
                if line == "": 
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    progress[key] = value
                    if key == "progress":
                        now = time.time()
                        if progress_callback and (now - last) >= callback_interval:
                            progress_callback(progress.copy(),process)
                            last = now
                if progress.get("progress") == "end":
                    break
            process.wait()
        except Exception as e:
            if self.verbose: print("Error:", e)
            if self.verbose: print(self.dsh)
            return False
        if self.verbose: print("Custom FFMedia usage finished")
        if thumb is not None:
            self.thumbnail(thumb,output,replace)
        else:
            if self.verbose: print(self.dsh)
        return True
    
    def custom_ffm(self, customisation, thumb=None, replace=False, progress_callback=None, callback_interval=1):
        return self.custom_ffmedia(self, customisation, thumb=thumb, replace=replace, progress_callback=progress_callback, callback_interval=callback_interval)

