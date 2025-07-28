from transformers import pipeline
import os, random, re

def get_valid_prompt(text: str) -> str:
  dot_split = text.split('.')[0]
  n_split = text.split('\n')[0]

  return {
    len(dot_split) < len(n_split): dot_split,
    len(n_split) > len(dot_split): n_split,
    len(n_split) == len(dot_split): dot_split   
  }[True]

def run(model, ctx, num):
    cfg_folder = os.getenv('CONFIG_FOLDER')

    pipe = pipeline('text-generation', model=model["model"])

    with open(os.path.join(cfg_folder, "ideas.txt"), "r") as f:
        line = f.readlines()

    print('\nGenerating output... ', flush=True)
    for count in range(10):

        if ctx == "":
            ctx: str = line[random.randrange(0, len(line))].replace("\n", "").lower().capitalize()
            ctx: str = re.sub(r"[,:\-–.!;?_]", '', ctx)
            print(ctx)
    
        response = pipe(ctx, max_length=(len(ctx) + random.randint(25, 50)), do_sample=True, num_return_sequences=num)
        response_list = []
        print('\n\nResponse: ' + str(response), flush=True)
        for x in response:
            resp = get_valid_prompt(x['generated_text'])
            if resp != ctx and len(resp) > (len(ctx) + 4) and resp.endswith((":", "-", "—")) is False:
                response_list.append(resp)

        if response_list[0].strip() != "":
            break 
        else:
            print('\nRetrying...')
        if count == 9:
            break
            
    for number in range(num):
        
        result = response_list[number]

        with open(os.path.join(cfg_folder, 'prompts', f'prompt-{number}.txt'), 'w') as file:
            file.write(result)
            
        print("\n\nFormatted to: " + result, flush=True)

    return os.path.join(cfg_folder, 'prompts')
