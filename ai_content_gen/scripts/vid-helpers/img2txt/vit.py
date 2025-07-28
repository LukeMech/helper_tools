from transformers import pipeline

def get_valid_prompt(text: str) -> str:
  dot_split = text.split('.')[0]
  n_split = text.split('\n')[0]

  return {
    len(dot_split) < len(n_split): dot_split,
    len(n_split) > len(dot_split): n_split,
    len(n_split) == len(dot_split): dot_split   
  }[True]

def run(model, image):
    print('Generating prompt for music generator...' ,flush=True)
    
    pipe = pipeline("image-to-text", model=model)
    response = pipe(image)[0]
    print('\n\nResponse: ' + str(response), flush=True)

    resp = get_valid_prompt(response['generated_text'])
    print("\n\nFormatted to: " + resp, flush=True)

    return resp
