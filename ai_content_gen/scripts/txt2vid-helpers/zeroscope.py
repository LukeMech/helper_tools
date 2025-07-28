from os import getenv, path, remove
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video
from moviepy.editor import VideoFileClip
from PIL import Image

def run(model, ctx, gif, video):
    cfg_folder = getenv("CONFIG_FOLDER")
    runnum = getenv("runnum")
    
    print('\nGenerating video from prompt: ' + ctx, flush=True)
    print("| Using:", flush=True)
    print("Model: " + model["model"], flush=True)

    savepath = path.join(path.abspath(cfg_folder), 'txt2vid')

    pipe = DiffusionPipeline.from_pretrained(model["model"])
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

    frames = pipe(ctx, num_inference_steps=model["inference_count"], num_frames=model["frames"], height=320, width=576).frames
    
    # upscale
    pipe = DiffusionPipeline.from_pretrained(model["upscaler"])
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

    video_frames = [Image.fromarray(f).resize((1024, 576)) for f in frames]
    frames = pipe(ctx, video=video_frames, num_inference_steps=model["inference_count"], strength=0.6).frames
    
    export_to_video(frames, path.join(savepath,f"{runnum}.mp4"), fps=model["fps"])

    if gif["enable"]:
        videoClip = VideoFileClip(path.join(savepath,f"{runnum}.mp4"))
        videoClip.speedx(gif["speed"]/100).write_gif(path.join(savepath,f"{runnum}.gif"), program='ffmpeg', loop=0)

    if not video["enable"]: 
        remove(path.join(savepath,f"{runnum}.mp4"))
    
    return savepath
