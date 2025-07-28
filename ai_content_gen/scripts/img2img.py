from os import getenv, path, makedirs
from subprocess import run
from io import BytesIO
import json, importlib, urllib.request

cfg_folder = getenv("CONFIG_FOLDER")
ai = getenv("ai")
num = int(getenv("num"))
runnum = getenv("runnum")

with open(path.join(cfg_folder, 'cfg.json'), 'r') as file:
    config = json.load(file)

with open(path.join(cfg_folder, 'models.json'), 'r') as file:
    models = json.load(file)

if config["txt2img"]["active"]:
    config = json.loads(json.dumps(config).replace("{txt2img.out}", path.join(cfg_folder, 'txt2img', f'{runnum}.jpg')))
if config["txt2txt"]["active"]:
    txt2txt = json.loads(getenv("txt2txt").replace('*', ' '))
    config = json.loads(json.dumps(config).replace("{txt2txt.out}", txt2txt[num]))
config = config["img2img"]
    
makedirs(path.join(cfg_folder, "img2img"), exist_ok=True)

if models["img2img"][ai]['extra_indexes']:
    run(f"pip install {' '.join(models['img2img'][ai]['packages'])} --extra-index-url {','.join(models['img2img'][ai]['extra_indexes'])}", shell=True)
else:
    run(f"pip install {' '.join(models['img2img'][ai]['packages'])}", shell=True)

print('\nUsing helper: ' + models['img2img'][ai]['helper'], flush=True)

helper = importlib.import_module(f"img2img-helpers.{models['img2img'][ai]['helper']}")
path = helper.run(models["img2img"][ai], config["image"], config["prompt"], config["width"], config["height"])

if config["upscale"]["enable"]:
    helper = importlib.import_module(f"upscale-helpers.{models['upscale']['helper']}")
    path = helper.run(models['upscale'], path, config["upscale"]["scale"])

run(f'echo out={path} >> $GITHUB_OUTPUT', shell=True)
print(f'Generated image and saved to {path}')
