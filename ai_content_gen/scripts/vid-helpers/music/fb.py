from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from os import getenv, path

def get_valid_prompt(text: str) -> str:
  dot_split = text.split('.')[0]
  n_split = text.split('\n')[0]

  return {
    len(dot_split) < len(n_split): dot_split,
    len(n_split) > len(dot_split): n_split,
    len(n_split) == len(dot_split): dot_split   
  }[True]

def run(model, ctx, duration):
    cfg_folder = getenv("CONFIG_FOLDER")

    print('Generating music...' ,flush=True)
    
    savepath = path.join(path.abspath(cfg_folder), 'img2vid', 'out')
    model = MusicGen.get_pretrained(model)
    
    model.set_generation_params(duration=duration)

    wav = model.generate([ctx])[0]       
    audio_write(savepath, wav.cpu(), model.sample_rate, strategy="loudness")

    savepath = savepath+'.wav'
    return savepath
