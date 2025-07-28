from os import getenv, path, listdir, makedirs
from subprocess import run
import json, importlib

cfg_folder = getenv("CONFIG_FOLDER")
ai_model = 'gpt2-sd'

with open(path.join(cfg_folder, 'cfg.json'), 'r') as file:
    data = json.load(file)

with open(path.join(cfg_folder, 'models.json'), 'r') as file:
    models = json.load(file)["txt2txt"] 

makedirs(path.join(cfg_folder, "prompts"), exist_ok=True)

if models[ai_model]['extra_indexes']:
    run(f"pip install {' '.join(models[ai_model]['packages'])} --extra-index-url {','.join(models[ai_model]['extra_indexes'])}", shell=True)
else:
    run(f"pip install {' '.join(models[ai_model]['packages'])}", shell=True)

num = int(data["global"]["out_amount"])

models_str = json.dumps(models)

# Add current prompt
prompt_str = data["txt2txt"]["prompt"].replace('\n', ' ')
models_str = models_str.replace('{prompt}', prompt_str)
models = json.loads(models_str)

ctx = models[ai_model]["prompt_template"]

print('\nUsing helper: ' + models[ai_model]['helper'], flush=True)

helper = importlib.import_module(f"txt2txt-helpers.{models[ai_model]['helper']}")
result = helper.run(models[ai_model], ctx, num)

# Get all prompts
prompts_arr = []
justusedprompts = listdir(result)
prompts = [file for file in justusedprompts if file.endswith(".txt")]
for txt_file in prompts:
    file_path = path.join(result, txt_file)  # Construct the full file path
    with open(file_path, 'r') as file:
        prompt = file.read()
        prompts_arr.append(prompt)

# Construct nice output
prompts_list = []
for number in range(num):
    prompts_list.append(str(prompts_arr[number]).replace(" ", '*').replace("\n", '*'))
prompts_list = [f'"{element}"' for element in prompts_list]
prompts_json_str = json.dumps(prompts_list).replace(" ", "")

# Generate out file
prompts_list = []
for number in range(num):
    prompts_list.append(str(prompts_arr[number]).replace("\n", ' '))
prompt_path = path.join(path.abspath(cfg_folder), 'prompts.txt')
with open(prompt_path, 'w') as file:
        json.dump(prompts_list, file, indent=2)

run('echo out=' + prompts_json_str + ' >> $GITHUB_OUTPUT', shell=True)
print('\n\nGenerated prompt.txt file and set out to ' + prompts_json_str)

run('echo file=' + prompt_path + ' >> $GITHUB_OUTPUT', shell=True)
