from subprocess import run
run('pip install -U pillow~=10.2.0', shell=True)

from os import getenv, path
from PIL import Image
from io import BytesIO
import urllib.request, json, sys

settings_url = getenv("SETTINGS")
cfg_folder = getenv("CONFIG_FOLDER")

try:
    with open(path.join(cfg_folder, "settings.json"), 'r') as file:
        def_cfg = json.load(file)
    with open(path.join(cfg_folder, "models.json"), 'r') as file:
        def_models = json.load(file)

except:
    print("Error: Unable to get the default settings")
    sys.exit(1)

try:
    # Download JSON data from the URL
    response = urllib.request.urlopen(settings_url)
    data = response.read()

    # Load the JSON data
    settings_json = json.loads(data.decode('utf-8'))
    print("Settings file:")

except:
    print("Error: Unable to fetch data from the URL.")

    settings_json = def_cfg
    print("Using default settings file:")

# Print JSON file
print(json.dumps(settings_json, indent=2))

# Define useful functions
def replace_models_in_string(mtype, string):
    models_names = list(def_models[mtype].keys())
    models_names_str = ', '.join(f'"{name}"' for name in models_names)
    return string.replace('"{type.models}"'.replace("type", mtype), f"[{models_names_str}]")
def search_json(data, target_string):
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, (dict, list)):
                if search_json(value, target_string):
                    return True
            elif isinstance(value, str) and target_string in value:
                return True
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                if search_json(item, target_string):
                    return True
            elif isinstance(item, str) and target_string in item:
                return True
    return False
def process_integer_value(lower_limit, upper_limit, value, dividable=1):
    if not isinstance(value, int):
        value = lower_limit
    else:
        if value < lower_limit:
            value = lower_limit
        elif value > upper_limit:
            value = upper_limit
    while value % dividable != 0:
        value += 1
    return value
def process_type(variable, datatype):
    if not isinstance(variable, datatype):
            print(f"ERROR IN DEFAULT: {variable} is not proper value for field.")
            sys.exit(1)
def check_models(array, mtype, default=False):
    models_names = list(def_models[mtype].keys())
    for model in array:
        if not search_json(models_names, model):
            if default:
                print(f"ERROR IN DEFAULT: Some or all models in {mtype} were not found.")
                sys.exit(1)
            else:
                return False
    return True
def is_valid_image(path):
    try:
        with Image.open(path):
            return True
    except:
        try: 
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
            req = urllib.request.Request(path, headers=headers)
            response = urllib.request.urlopen(req)
            data = response.read()
            with Image.open(BytesIO(data)):
                return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False

# Check var types
ints = [def_cfg["global"]["out_amount"], def_cfg["txt2img"]["height"], def_cfg["txt2img"]["width"], def_cfg["txt2vid"]["gif"]["speed"], def_cfg["img2img"]["height"], def_cfg["img2img"]["width"], def_cfg["img2vid"]["gif"]["speed"], def_cfg["txt2img"]["upscale"]["scale"], def_cfg["img2img"]["upscale"]["scale"]]
strs = [def_cfg["txt2txt"]["prompt"], def_cfg["txt2img"]["prompt"], def_cfg["txt2vid"]["prompt"], def_cfg["img2img"]["prompt"], def_cfg["img2img"]["image"], def_cfg["img2vid"]["image"]]
bools = [def_cfg["global"]["clean_artifacts"], def_cfg["txt2txt"]["active"], def_cfg["txt2img"]["active"], def_cfg["txt2vid"]["active"], def_cfg["txt2vid"]["gif"]["enable"], def_cfg["txt2vid"]["video"]["enable"], def_cfg["txt2vid"]["video"]["music"], def_cfg["img2img"]["active"], def_cfg["txt2img"]["upscale"]["enable"], def_cfg["img2img"]["upscale"]["enable"], def_cfg["img2vid"]["active"], def_cfg["img2vid"]["gif"]["enable"], def_cfg["img2vid"]["video"]["enable"], def_cfg["img2vid"]["video"]["music"]]
for integer in ints: process_type(integer, int)
for string in strs: process_type(string, str)
for boolean in bools: process_type(boolean, bool)
# Integers values optimization
width_height_modules = [def_cfg["txt2img"], def_cfg["img2img"]]
for module in width_height_modules:
    module["width"] = process_integer_value(256, 1024, module["width"], 64)
    module["height"] = process_integer_value(256, 1024, module["height"], 64)
def_cfg["global"]["out_amount"] = process_integer_value(1, 10, def_cfg["global"]["out_amount"])
def_cfg["txt2img"]["upscale"]["scale"] = process_integer_value(2, 4, def_cfg["txt2img"]["upscale"]["scale"])
def_cfg["img2img"]["upscale"]["scale"] = process_integer_value(2, 4, def_cfg["img2img"]["upscale"]["scale"])
def_cfg["img2vid"]["gif"]["speed"] = process_integer_value(1, 1000, def_cfg["img2vid"]["gif"]["speed"])
def_cfg["txt2vid"]["gif"]["speed"] = process_integer_value(1, 1000, def_cfg["txt2vid"]["gif"]["speed"])
# Variable -> model type array
def_cfg_string = json.dumps(def_cfg)
model_types = ["txt2img", "img2img", "img2vid", "txt2vid"]
for model_type in model_types:
    def_cfg_string = replace_models_in_string(model_type, def_cfg_string)
def_cfg = json.loads(def_cfg_string)
# Check if all models are correct
for model_type in model_types:
    check_models(def_cfg[model_type]["matrix"]["models"], model_type, True)
# Check if variables used are proper
settings_types = model_types + ["txt2txt"]
for set_type in settings_types:
    if not def_cfg[set_type]["active"] and search_json(def_cfg, "{type.".replace("type", set_type)):
        print(f"ERROR IN DEFAULT: Used {set_type} variable without turning on module")
        sys.exit(1)


# Process loaded config file

# Integers values optimization
width_height_modules = [settings_json["txt2img"], settings_json["img2img"]]
for module in width_height_modules:
    module["width"] = process_integer_value(256, 1024, module["width"], 64)
    module["height"] = process_integer_value(256, 1024, module["height"], 64)
settings_json["txt2img"]["upscale"]["scale"] = process_integer_value(2, 4, settings_json["txt2img"]["upscale"]["scale"])
settings_json["img2img"]["upscale"]["scale"] = process_integer_value(2, 4, settings_json["img2img"]["upscale"]["scale"])
settings_json["global"]["out_amount"] = process_integer_value(1, 10, settings_json["global"]["out_amount"])
settings_json["img2vid"]["gif"]["speed"] = process_integer_value(1, 1000, settings_json["img2vid"]["gif"]["speed"])
settings_json["txt2vid"]["gif"]["speed"] = process_integer_value(1, 1000, settings_json["img2vid"]["gif"]["speed"])
# Variable -> model type array
settings_json_string = json.dumps(settings_json)
model_types = ["txt2img", "img2img", "img2vid", "txt2vid"]
for model_type in model_types:
    settings_json_string = replace_models_in_string(model_type, settings_json_string)
settings_json = json.loads(settings_json_string)

# Check if all models are correct, if not fallback to default
for model_type in model_types:
    if not check_models(settings_json[model_type]["matrix"]["models"], model_type):
        settings_json[model_type]["matrix"]["models"] = def_cfg[model_type]["matrix"]["models"]

# Check if variables used are proper
settings_types = model_types + ["txt2txt"]
for set_type in settings_types:
    if not settings_json[set_type]["active"] and search_json(settings_json, "{type.".replace("type", set_type)):
        print(f"ERROR IN CUSTOM: Used {set_type} variable without turning on module")
        sys.exit(1)

# Stabilize booleans
bools = [settings_json["global"]["clean_artifacts"], settings_json["txt2txt"]["active"], settings_json["txt2vid"]["active"], settings_json["txt2vid"]["gif"]["enable"], settings_json["txt2vid"]["video"]["enable"], settings_json["txt2vid"]["video"]["music"], settings_json["txt2img"]["active"], settings_json["img2img"]["active"], settings_json["txt2img"]["upscale"]["enable"], settings_json["img2img"]["upscale"]["enable"], settings_json["img2vid"]["active"], settings_json["img2vid"]["gif"]["enable"], settings_json["img2vid"]["video"]["enable"], settings_json["img2vid"]["video"]["music"]]        
for boolean in bools:
    if boolean != True: 
        boolean = False

# Stabilize strings
strs = [settings_json["txt2txt"]["prompt"]]
if settings_json["txt2txt"]["active"]:
    for string in strs:
        if not string.strip(): 
            print("INFO: Not found prompt for txt2txt, using random idea")
strs = [settings_json["txt2img"]["prompt"]]
if settings_json["txt2img"]["active"]:
    for string in strs:
        if not string.strip(): 
            print("ERROR: Not found prompt for txt2img")
            sys.exit(1)
strs = [settings_json["txt2vid"]["prompt"]]
if settings_json["txt2vid"]["active"]:
    for string in strs:
        if not string.strip(): 
            print("ERROR: Not found prompt for txt2vid")
            sys.exit(1)
strs = [settings_json["img2img"]["prompt"], settings_json["img2img"]["image"]]
if settings_json["img2img"]["active"]:
    for string in strs:
        if not string.strip(): 
            print("ERROR: Not found prompt or image for img2img")
            sys.exit(1)
strs = [settings_json["img2vid"]["image"]]
if settings_json["img2vid"]["active"]:
    for string in strs:
        if not string.strip(): 
            print("ERROR: Not found prompt or image for img2vid")
            sys.exit(1)

# Post-check some settings, ensure the program will run properly
if not settings_json["txt2txt"]["active"]:
    for key in settings_json["txt2txt"].keys():
        settings_json["txt2txt"][key] = False

if not settings_json["txt2img"]["active"]:
    for key in settings_json["txt2img"].keys():
        settings_json["txt2img"][key] = False
    settings_json["txt2img"]["matrix"] = {}
    settings_json["txt2img"]["matrix"]["models"] = [0]

if not settings_json["txt2vid"]["active"]:
    for key in settings_json["txt2vid"].keys():
        settings_json["txt2vid"][key] = False
    settings_json["txt2vid"]["matrix"] = {}
    settings_json["txt2vid"]["matrix"]["models"] = [0]

if not settings_json["img2img"]["active"]:
    for key in settings_json["img2img"].keys():
        settings_json["img2img"][key] = False
    settings_json["img2img"]["matrix"] = {}
    settings_json["img2img"]["matrix"]["models"] = [0]
elif not is_valid_image(settings_json["img2img"]["image"]) and (not settings_json["txt2img"]["active"] or not settings_json["img2img"]["image"] == "{txt2img.out}"):
    print("ERROR: Image url or path not valid for img2img")
    sys.exit(1)

if not settings_json["img2vid"]["active"]:
    for key in settings_json["img2vid"].keys():
        settings_json["img2vid"][key] = False
    settings_json["img2vid"]["matrix"] = {}
    settings_json["img2vid"]["matrix"]["models"] = [0]
elif not is_valid_image(settings_json["img2vid"]["image"]) and (not settings_json["txt2img"]["active"] or not settings_json["img2vid"]["image"] == "{txt2img.out}") and (not settings_json["img2img"]["active"] or not settings_json["img2vid"]["image"] == "{img2img.out}"):
    print("ERROR: Image url or path not valid for img2vid (warning, output from upscaler also unsupported)")
    sys.exit(1)

amount_array = [i for i in range(settings_json["global"]["out_amount"])]
run(f'echo amount={json.dumps(amount_array).replace(" ", "")} >> $GITHUB_OUTPUT', shell=True)

if settings_json["txt2txt"]["active"]:
    run('echo txt2txt={"active":true} >> $GITHUB_OUTPUT', shell=True)
else: run('echo txt2txt={"active":false} >> $GITHUB_OUTPUT', shell=True)

if settings_json["txt2img"]["active"]:
    quoted_list = [f'"{element}"' for element in settings_json["txt2img"]["matrix"]["models"]]
    run('echo txt2img={"active":true,"ai":REPLACE} >> $GITHUB_OUTPUT'.replace('REPLACE', json.dumps(quoted_list).replace(" ", "")), shell=True)
else: run('echo txt2img={"active":false,"ai":[0]} >> $GITHUB_OUTPUT', shell=True)

if settings_json["txt2vid"]["active"]:
    quoted_list = [f'"{element}"' for element in settings_json["txt2vid"]["matrix"]["models"]]
    run('echo txt2vid={"active":true,"ai":REPLACE} >> $GITHUB_OUTPUT'.replace('REPLACE', json.dumps(quoted_list).replace(" ", "")), shell=True)
else: run('echo txt2vid={"active":false,"ai":[0]} >> $GITHUB_OUTPUT', shell=True)

if settings_json["img2img"]["active"]:
    quoted_list = [f'"{element}"' for element in settings_json["img2img"]["matrix"]["models"]]
    run('echo img2img={"active":true,"ai":REPLACE} >> $GITHUB_OUTPUT'.replace('REPLACE', json.dumps(quoted_list).replace(" ", "")), shell=True)
else: run('echo img2img={"active":false,"ai":[0]} >> $GITHUB_OUTPUT', shell=True)

if settings_json["img2vid"]["active"]:
    quoted_list = [f'"{element}"' for element in settings_json["img2vid"]["matrix"]["models"]]
    run('echo img2vid={"active":true,"ai":REPLACE} >> $GITHUB_OUTPUT'.replace('REPLACE', json.dumps(quoted_list).replace(" ", "")), shell=True)
else: run('echo img2vid={"active":false,"ai":[0]} >> $GITHUB_OUTPUT', shell=True)

json_file_path = f"{cfg_folder}/cfg.json"
with open(json_file_path, 'w') as json_file:
    json.dump(settings_json, json_file, indent=4)

print(f'Checks completed, output saved as {json_file_path}')
