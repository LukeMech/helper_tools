from os import getenv, path, makedirs, remove
from math import ceil
from subprocess import run
import json, importlib

cfg_folder = getenv("CONFIG_FOLDER")
ai = getenv("ai")
runnum = getenv("runnum")

with open(path.join(cfg_folder, 'cfg.json'), 'r') as file:
    config = json.load(file)

with open(path.join(cfg_folder, 'models.json'), 'r') as file:
    models = json.load(file)

if config["txt2img"]["active"]:
    config = json.loads(json.dumps(config).replace("{txt2img.out}", path.join(cfg_folder, 'txt2img', f'{runnum}.jpg')))
if config["img2img"]["active"]:
    config = json.loads(json.dumps(config).replace("{img2img.out}", path.join(cfg_folder, 'img2img', f'{runnum}.jpg')))

config = config["img2vid"]
    
makedirs(path.join(cfg_folder, "img2vid"), exist_ok=True)

if models["img2vid"][ai]['extra_indexes']:
    run(f"pip install {' '.join(models['img2vid'][ai]['packages'])} --extra-index-url {','.join(models['img2vid'][ai]['extra_indexes'])}", shell=True)
else:
    run(f"pip install {' '.join(models['img2vid'][ai]['packages'])}", shell=True)

print('\nUsing helper: ' + models['img2vid'][ai]['helper'], flush=True)
    
helper = importlib.import_module(f"img2vid-helpers.{models['img2vid'][ai]['helper']}")
vid_path = helper.run(models["img2vid"][ai], config["image"], config["gif"], config["video"])

if config["video"]["music"] and config["video"]["enable"]:
    from moviepy.editor import VideoFileClip, AudioFileClip
    
    helper = importlib.import_module(f"vid-helpers.img2txt.{models['img2txt']['helper']}")
    prompt = helper.run(models['img2txt']['model'], config["image"])
    music_duration = ceil(models["img2vid"][ai]['frames']/models["img2vid"][ai]['fps'])

    helper = importlib.import_module(f"vid-helpers.music.{models['music']['helper']}")
    musicfile_path = helper.run(models['music']["model"], prompt, music_duration)

    video_clip = VideoFileClip(path.join(vid_path,f"{runnum}.mp4"))
    audio_clip = AudioFileClip(musicfile_path)
    video_clip = video_clip.set_audio(audio_clip)
    remove(path.join(vid_path,f"{runnum}.mp4"))
    remove(musicfile_path)
    video_clip.write_videofile(path.join(vid_path,f"{runnum}.mp4"))

run(f'echo out={vid_path} >> $GITHUB_OUTPUT', shell=True)
print(f'Generated video and saved to {vid_path}')
