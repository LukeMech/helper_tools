from os import getenv, path, makedirs
from subprocess import run
import json, importlib

cfg_folder = getenv("CONFIG_FOLDER")
num = int(getenv("num"))
ai = getenv("ai")

with open(path.join(cfg_folder, 'cfg.json'), 'r') as file:
    config = json.load(file)

with open(path.join(cfg_folder, 'models.json'), 'r') as file:
    models = json.load(file)

if config["txt2txt"]["active"]:
    txt2txt = json.loads(getenv("txt2txt").replace('*', ' '))
    config = json.loads(json.dumps(config).replace("{txt2txt.out}", txt2txt[num]))
config = config["txt2img"]

ctx = config["prompt"]
makedirs(path.join(cfg_folder, "txt2img"), exist_ok=True)

if models["txt2img"][ai]['extra_indexes']:
    run(f"pip install {' '.join(models['txt2img'][ai]['packages'])} --extra-index-url {','.join(models['txt2img'][ai]['extra_indexes'])}", shell=True)
else:
    run(f"pip install {' '.join(models['txt2img'][ai]['packages'])}", shell=True)

print('\nUsing helper: ' + models["txt2img"][ai]['helper'], flush=True)

helper = importlib.import_module(f"txt2img-helpers.{models['txt2img'][ai]['helper']}")
path = helper.run(models["txt2img"][ai], ctx, config["width"], config["height"])

if config["upscale"]["enable"]:
    helper = importlib.import_module(f"upscale-helpers.{models['upscale']['helper']}")
    path = helper.run(models['upscale'], path, config["upscale"]["scale"])

run(f'echo out={path} >> $GITHUB_OUTPUT', shell=True)
print(f'Generated image and saved to {path}')