from os import path, getenv
from diffusers import LCMScheduler, AutoPipelineForText2Image

def run(model, ctx, w, h):
    cfg_folder = getenv("CONFIG_FOLDER")
    runnum = getenv("runnum")

    print('\nGenerating image for question: ' + ctx, flush=True)
    print("| Using:", flush=True)
    print("Model: " + model["model"], flush=True)
    print("With faster generation using: " + model["adapter"], flush=True)
    print("Dimensions: " + str(w) + "px x " + str(h) + "px", flush=True)

    savepath = path.join(path.abspath(cfg_folder), 'txt2img', f'{runnum}.jpg')

    pipe = AutoPipelineForText2Image.from_pretrained(model["model"])
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    # load and fuse lcm lora
    pipe.load_lora_weights(model["adapter"])
    pipe.fuse_lora()

    image = pipe(prompt=ctx, num_inference_steps=model["inference_count"], height=h, width=w, guidance_scale=0).images[0]
    image.save(savepath)

    return savepath