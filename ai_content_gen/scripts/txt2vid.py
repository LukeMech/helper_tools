from os import getenv, path, makedirs, remove
from subprocess import run
from math import ceil
import json, importlib

cfg_folder = getenv("CONFIG_FOLDER")
num = int(getenv("num"))
ai = getenv("ai")
runnum = getenv("runnum")

with open(path.join(cfg_folder, 'cfg.json'), 'r') as file:
    config = json.load(file)

with open(path.join(cfg_folder, 'models.json'), 'r') as file:
    models = json.load(file) 

if config["txt2txt"]["active"]:
    txt2txt = json.loads(getenv("txt2txt").replace('*', ' '))
    config = json.loads(json.dumps(config).replace("{txt2txt.out}", txt2txt[num]))
config = config["txt2vid"]

ctx = config["prompt"]
makedirs(path.join(cfg_folder, "txt2vid"), exist_ok=True)

if models["txt2vid"][ai]['extra_indexes']:
    run(f"pip install {' '.join(models['txt2vid'][ai]['packages'])} --extra-index-url {','.join(models['txt2vid'][ai]['extra_indexes'])}", shell=True)
else:
    run(f"pip install {' '.join(models['txt2vid'][ai]['packages'])}", shell=True)

print('\nUsing helper: ' + models['txt2vid'][ai]['helper'], flush=True)

helper = importlib.import_module(f"txt2vid-helpers.{models['txt2vid'][ai]['helper']}")
vid_path = helper.run(models["txt2vid"][ai], config["prompt"], config["gif"], config["video"])

if config["video"]["music"] and config["video"]["enable"]:
    from moviepy.editor import VideoFileClip, AudioFileClip
    
    music_duration = ceil(models["txt2vid"][ai]['frames']/models["txt2vid"][ai]['fps'])
    helper = importlib.import_module(f"vid-helpers.music.{models['music']['helper']}")
    musicfile_path = helper.run(models['music']["model"], config["prompt"], music_duration)

    video_clip = VideoFileClip(path.join(vid_path,f"{runnum}.mp4"))
    audio_clip = AudioFileClip(musicfile_path)
    video_clip = video_clip.set_audio(audio_clip)
    remove(path.join(vid_path,f"{runnum}.mp4"))
    remove(musicfile_path)
    video_clip.write_videofile(path.join(vid_path,f"{runnum}.mp4"))

run(f'echo out={vid_path} >> $GITHUB_OUTPUT', shell=True)
print(f'Generated video and saved to {vid_path}')
