import oomlout_ai_roboclick as robo
import copy

def main(**kwargs):
    action = kwargs.get("action", "")
    mode_ai_wait = action.get("mode_ai_wait", None)
    image_detail = action.get("image_detail", "colorful bubble letters")
    file_destination = action.get("file_destination", "")
    if file_destination == "":
        #try file_name
        file_destination = action.get("file_name", "")
        if file_destination == "":
            #try filename
            file_destination = action.get("filename", "initial_generated_test.png")
    

    action = {}
    kwargs2 = copy.deepcopy(kwargs)
    action["description"] = f"making a icon logo for {image_detail} using AI"
    kwargs2["action"] = copy.deepcopy(action)
    robo.ai_new_chat(**kwargs2)

    action = {}
    #action["command"] = "query"
    prompt = f"""
Create a prompt for generating a 1-colour (black on white) chibi-style
mascot illustration designed for a 40x40 mm thermal label that visually
represents a given recipe name (recipe_name). The artwork should feature
one central cute anthropomorphic mascot themed to the recipe (for example
a smiling sausage, happy bowl of curry, or cheerful casserole pot) with
up to two simple surrounding icons that fit the meal's personality (such
as a heart puff, herb sprig, spoon, bowl, or local motif). Use pure black
on white only with no grey, shading, gradients, or text. Keep bold linework
(outer 3.5-4.5 pt, inner 2-2.5 pt at 300 dpi), centered composition with
3-4 mm margins and no border. Style should be kawaii, playful, sticker-like,
minimal detail, high contrast, screen-print inspired, with composition
filling about 70-80 % of the square and background icons arranged loosely
for balance. The output should be a ready-to-paste image-generation prompt
with (recipe_name) as a placeholder variable. Take all the time you need
"""
    action["text"] = prompt
    action["method"] = "paste"
    action["delay"] = 120
    if mode_ai_wait != "":
        action["mode_ai_wait"] = mode_ai_wait
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["action"] = copy.deepcopy(action)
    robo.ai_query(**kwargs2)
    
    action = {}
    prompt = f"""
That is so so great! please do it for {image_detail}.
Take all the time you need
"""
    action["text"] = prompt
    action["method"] = "paste"
    action["delay"] = 240
    
    if mode_ai_wait != "":
        action["mode_ai_wait"] = mode_ai_wait
    kwargs2["action"] = copy.deepcopy(action)
    robo.ai_query(**kwargs2)

    action = {}
    action["command"] = "query"
    prompt = f"""
You are a star that's perfect! now pelase geenrate the image remember
square proportions and take as much time as you need
"""
    action["text"] = prompt
    action["method"] = "paste"
    action["delay"] = 240
    if mode_ai_wait != "":
        action["mode_ai_wait"] = mode_ai_wait
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["action"] = copy.deepcopy(action)
    robo.ai_query(**kwargs2)


    action = {}
    #- command: 'save_image'
    action["file_name"] = f"initial_generated.png"
    if mode_ai_wait != "":
        action["mode_ai_wait"] = mode_ai_wait
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["action"] = copy.deepcopy(action)
    robo.ai_save_image(**kwargs2)