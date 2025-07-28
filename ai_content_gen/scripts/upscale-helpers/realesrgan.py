from os import makedirs, path, getenv
import subprocess, urllib.request

def run(model, image, scale):
    cfg_folder = getenv("CONFIG_FOLDER")
    runnum = getenv("runnum")

    subprocess.run(f"pip install {' '.join(model['packages'])} --extra-index-url {','.join(model['extra_indexes'])}", shell=True)

    from tqdm import tqdm
    
    print('\nUpscaling image by ' + str(scale) + 'x', flush=True)
    print("| Using:", flush=True)
    print("Model from: " + model["dld_url"], flush=True)
    print("Script from: " + model["script"], flush=True)

    makedirs("./tmp/x", exist_ok=True)
    ext=model["dld_url"].split(".")[-1]
    with urllib.request.urlopen(model["dld_url"]) as response, open('./tmp/'+"model."+ext, 'wb') as output_file:
        print('Downloading [' + model["dld_url"] + "]...", flush=True)
        # Get the total file size in bytes
        file_size = int(response.getheader('Content-Length', 0))
        # Initialize the tqdm progress bar
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
        # Download and write to the local file with progress update
        while True:
            buffer = response.read(8192)  # Adjust the buffer size as needed
            if not buffer:
                break
            output_file.write(buffer)
            progress_bar.update(len(buffer))
        # Close the progress bar
        progress_bar.close()
        output_file.write(response.read())

    with urllib.request.urlopen(model["script"]) as response, open('./tmp/script.py', 'wb') as output_file:
        print('Downloading [' + model["script"] + "]...", flush=True)
        # Get the total file size in bytes
        file_size = int(response.getheader('Content-Length', 0))
        # Initialize the tqdm progress bar
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
        # Download and write to the local file with progress update
        while True:
            buffer = response.read(8192)  # Adjust the buffer size as needed
            if not buffer:
                break
            output_file.write(buffer)
            progress_bar.update(len(buffer))
        # Close the progress bar
        progress_bar.close()
        output_file.write(response.read())

    savepath = path.join(path.abspath('.'), 'out', f'{runnum}.jpg')
    subprocess.run(f'python ./tmp/script.py -i {image} --model_path ./tmp/model.{ext} -o ./out/ --fp32 -s {str(scale)}', shell=True, check=True)
    subprocess.run(f'mv ./out/*.jpg {savepath}', shell=True, check=True)
    
    return savepath