from os import getenv, path, remove
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
from moviepy.editor import VideoFileClip

def run(model, image, gif, video):
    cfg_folder = getenv("CONFIG_FOLDER")
    runnum = getenv("runnum")
    
    print('\nGenerating video', flush=True)
    print("| Using:", flush=True)
    print("Model: " + model["model"], flush=True)

    savepath = path.join(path.abspath(cfg_folder), 'img2vid')

    pipe = StableVideoDiffusionPipeline.from_pretrained(model["model"])

    # Load the conditioning image
    image = load_image(image)
    image = image.resize((1024, 576))

    frames = pipe(image, num_inference_steps=model["inference_count"]).frames[0]
    export_to_video(frames, path.join(savepath,f"{runnum}.mp4"), fps=model["fps"])

    if gif["enable"]:
        videoClip = VideoFileClip(path.join(savepath,f"{runnum}.mp4"))
        videoClip.speedx(gif["speed"]/100).write_gif(path.join(savepath,f"{runnum}.gif"), program='ffmpeg', loop=0)

    if not video["enable"]: 
        remove(path.join(savepath,f"{runnum}.mp4"))
    
    return savepath
