import oomlout_ai_roboclick as robo
import copy

def main(**kwargs):
    action = kwargs.get("action", "")
    image_detail = action.get("image_detail", "colorful bubble letters")
    file_name = action.get("file_name", "initial_generated_test.png")
    aspect_ratio = action.get("aspect_ratio", "3:2 landscape")
    mode_ai_wait = action.get("mode_ai_wait", "fast_button_state")
    character_1 = action.get("character_1", "unicorn")
    character_2 = action.get("character_2", "fairy")
    character_3 = action.get("character_3", "mermaid")
    color_scheme = action.get("color_scheme", "rainbow")
    action = {}
    #action["command"] = "query"
    prompt = f"""
You are a RESEARCHER. Your job is to perform in-depth, exhaustive research on the meaning, imagery, symbolism, mood, and visual associations of a short phrase, then convert that research into world-class image direction and a final, production-ready image-generation prompt.

CRITICAL BEHAVIOR RULES:
- you will be given a description of text that must be in the image

With these lines do:
1) Phrase Deep Research (exhaustive):
- Define the phrase(s) plainly and interpret figurative meanings.
- Identify emotional tone, energy level, and “vibe” (cozy, dramatic, mischievous, triumphant, spooky, etc.).
- List associated imagery, objects, locations, weather, time-of-day, colors, materials, metaphors, and cultural references (keep it child-safe).
- Suggest 3-6 “visual motifs” that could decorate a scene without distracting from the main text.
- Identify any potentially confusing or ambiguous readings and pick the most visually powerful interpretation.

2) Composition Research (make it read perfectly):
- Prioritize legibility: the text must be the hero.
- Plan a clean “readability halo” behind the text (low detail, soft contrast) so the bubble letters pop.
- Place {character_3} and {character_1} and {character_2} as framing elements that guide the eye toward the text (corners/sides), never blocking letters.
- Keep the background themed from the phrase but compositionally quieter behind the text.
- Propose 3 composition options (A/B/C) and pick the best one with a brief justification.

3) Bubble Lettering Research (make it awesome):
- Describe bubble-letter construction: thick rounded forms, consistent stroke, strong outline, subtle 3D puffiness (if allowed), and high contrast.
- Provide a color strategy derived from the phrase {color_scheme} 
- Specify exact legibility rules: large scale, centered, no overlapping props, no extra text anywhere, correct spelling exactly once.

DELIVERABLES (OUTPUT IN THIS EXACT STRUCTURE):
A) “Research Findings” — concise but rich bullets summarizing the phrase's imagery + mood + motif palette.
B) “Composition Plan” — your chosen option, with placement notes for: text, {character_3}, {character_1}, {character_2}, background theme elements, and readability halo.
C) “Bubble Letter Specs” — clear instructions to maximize readability (fill, outline, thickness, spacing, lighting).
D) “Final Image Prompt” — a single, complete prompt ready to paste into an image generator.
- MUST include the exact text content: LINE 1 and LINE 2 (if LINE 2 is NONE, use only LINE 1).
- MUST say: bubble letters, centered, very large, high contrast, with a clean readability halo.
- MUST include: themed background derived from the phrase + {character_3} + {character_1} + {character_2} as adornments.
- MUST forbid: any additional text, logos, watermarks, illegible typography, or props covering letters.
- Make the final prompt specific, visual, and unambiguous.

{image_detail}
"""
    action["text"] = prompt
    action["method"] = "paste"
    action["delay"] = 60
    if mode_ai_wait != "":
        action["mode_ai_wait"] = mode_ai_wait
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["action"] = copy.deepcopy(action)
    robo.ai_query(**kwargs2)
    

    
    action = {}
    prompt = f"""
You are an IMAGE PROMPT ENGINEER.

CONTEXT:
You have just been given a research package created by a researcher (it includes: Research Findings, Composition Plan, Bubble Letter Specs, and possibly a draft “Final Image Prompt”). Your job is to convert that research into a precise, production-ready IMAGE SPECIFICATION that an image generator can follow reliably.

CRITICAL RULES:
- Do NOT redo the research. Use only what was provided.
- Do NOT ask any questions unless the research is missing the exact text for LINE 1 and LINE 2.
- Do NOT mention what this will be used for.
- Prioritize legibility and spelling accuracy of the text above all else.
- The text must appear EXACTLY ONCE (no duplicates, no extra words).
- No other text anywhere (no labels, logos, watermarks, signatures).
- {character_3}, {character_1}, and {character_2} must be included as adornments/framing elements and must NOT overlap or obscure any letters.

TASK:
1) Parse the provided research and extract the final decisions:
- Intended mood/vibe
- Themed environment derived from the phrase
- Selected composition option and placement logic
- Bubble-letter styling and strict readability constraints
- Any color/material/lighting guidance

2) Produce a single “Image Specification” with the following sections (use these exact headings):
A) TEXT CONTENT (verbatim)
- LINE 1: "<exact text>"
- LINE 2: "<exact text or NONE>"
- Layout: one line / two line stack; centered; scale rules
- Spelling rules: exact once, no additional text
B) TYPOGRAPHY / BUBBLE LETTER REQUIREMENTS
- Bubble form rules, outline thickness, fill strategy, contrast strategy
- Readability halo rules (how to keep the area behind text clean)
- Forbidden typography behaviors (warping into unreadable shapes, clutter, shadows that reduce contrast)
C) COMPOSITION / CAMERA
- Framing plan: where text sits, where {character_3} sit, where {character_1} sit, where {character_2} sit
- Camera angle, focal length feel, depth of field guidance
- Negative space plan: how to keep center uncluttered
D) SCENE / BACKGROUND THEME
- Environment derived from the phrase (props, motifs, time of day, weather)
- “Quiet zone” behind text: what must be minimized/removed in that region
E) CHARACTER / PROP REQUIREMENTS
- Unicorn design cues (friendly, child-safe, chibi/cute) and placement
- Fairy design cues (tiny glowing, friendly) and placement
- Any other allowed props (only if explicitly supported by the research)
F) LIGHTING / COLOR
- Lighting mood and key light direction
- Palette guidance derived from research (while preserving text contrast)
G) QUALITY / SAFETY / CONSTRAINTS
- Child-safe content only
- No brands, no copyrighted characters, no extra text
- Ensure no letter occlusion; ensure correct spelling and legibility

3) Then output a single “Final Image-Generator Prompt” that faithfully implements the specification in clear natural language.
- Must explicitly include the exact LINE 1 and LINE 2 text.
- Must clearly instruct “text is very large, centered, bubble letters” and “clean readability halo behind text.”
- Must specify {character_3} + {character_1} + {character_2} framing the text, never overlapping letters.
- Must include a short NEGATIVE PROMPT / DO-NOT list at the end (no extra text, no watermarks, no logos, no overlapping letters, no unreadable typography).

OUTPUT FORMAT:
- Return ONLY two blocks in this order:
1) IMAGE SPECIFICATION (structured with headings A-G)
2) FINAL IMAGE-GENERATOR PROMPT (single prompt + short negative list)

BEGIN: Transform the research you were just given into the two required outputs now.

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
    prompt = f"""
You are an IMAGE PROMPT TYPE SETTER.

CONTEXT:
You have just been given an “Image Specification” (with sections A–G) and a “Final Image-Generator Prompt” created by an Image Prompt Engineer. Your job is NOT to re-research or reinterpret. Your job is to translate the provided specification into a SINGLE, exhaustive, production-ready JSON object that an image generation system can follow reliably.

CRITICAL RULES:
- Use ONLY the information present in the provided spec/prompt. Do not invent new scene elements, characters, props, slogans, or extra text.
- Do NOT ask any questions unless the exact text (LINE 1 / LINE 2) is missing.
- The text must appear EXACTLY ONCE in the image. No other text anywhere.
- Unicorns and fairies must be included as framing/adornment elements and MUST NOT overlap or obscure any letters.
- Prioritize legibility: bubble letters are the hero; the “readability halo” behind text must be enforced.
- Return STRICT VALID JSON ONLY. No markdown, no comments, no trailing commas, no extra keys outside the schema you output.

OUTPUT REQUIREMENTS:
1) Produce ONE JSON object with the exact top-level keys below, in the exact order:
{{
"role",
"version",
"input_summary",
"text",
"typography",
"composition",
"scene",
"characters",
"props",
"lighting",
"color",
"camera",
"quality",
"constraints",
"negative_prompt",
"final_prompt"
}}

2) Every section must be exhaustive and explicit. Prefer explicit defaults rather than leaving ambiguity.
3) If a field is unknown because it was not specified, set it to null and note it in "input_summary.missing_fields".

SCHEMA DETAILS (MUST FOLLOW):
- "role": string, must be "image_prompt_type_setter"
- "version": string, e.g. "1.0"
- "input_summary":
- "source": string (e.g. "image_spec_v1")
- "assumptions": array of strings (only assumptions explicitly forced by the spec; otherwise empty)
- "missing_fields": array of strings (anything not provided that would normally matter)
- "text":
- "line1": string (verbatim, case-sensitive)
- "line2": string or null (null if LINE 2 is NONE)
- "layout": object {{ "mode": "one_line"|"two_line_stack", "alignment": "center", "scale_priority": "maximum_legibility" }}
- "exactly_once": true
- "no_other_text": true
- "typography":
- "style": "bubble_letters"
- "placement": object {{ "position": "center", "safe_margin": "generous", "do_not_overlap": true }}
- "fill": object {{ "strategy": string, "colors": array or null }}
- "outline": object {{ "enabled": true, "color": string or null, "thickness": string }}
- "depth_effect": object {{ "allowed": boolean, "style": string or null }}
- "readability_halo": object {{ "enabled": true, "description": string, "background_simplification": string }}
- "legibility_rules": array of strings
- "composition":
- "primary_focus": "text"
- "framing_elements": array (e.g., unicorns, fairies)
- "text_clear_zone": string (describe what must be kept empty/low-detail)
- "layout_notes": array of strings (explicit placements)
- "scene":
- "theme_derived_from_text": string (from spec)
- "environment": string
- "time_of_day": string or null
- "weather": string or null
- "background_detail_level": "controlled" (center quiet, edges decorative)
- "allowed_motifs": array of strings (only those present in spec)
- "characters":
- "unicorns": object {{ "count": integer or null, "style_notes": array, "placement_notes": array }}
- "fairies": object {{ "count": integer or null, "style_notes": array, "placement_notes": array }}
- "prohibited_characters": array of strings
- "props":
- "allowed": array of strings
- "prohibited": array of strings
- "lighting":
- "mood": string or null
- "key_light_direction": string or null
- "contrast_priority": "text_legibility"
- "color":
- "palette_guidance": array of strings
- "text_contrast_rules": array of strings
- "camera":
- "angle": string or null
- "framing": string or null
- "depth_of_field": string or null
- "quality":
- "style": string (e.g., "cute chibi CGI" if present in spec; otherwise null)
- "render_notes": array of strings
- "constraints":
- "child_safe": true
- "no_logos": true
- "no_watermarks": true
- "no_brands": true
- "no_copyrighted_characters": true
- "no_text_occlusion": true
- "spelling_must_match": true
- "negative_prompt":
- array of strings (explicit “do not” items)
- "final_prompt":
- string (a single consolidated prompt assembled from the JSON, including the exact text and key constraints)

PROCESS:
- Read the provided Image Specification (A-G) and Final Image-Generator Prompt.
- Populate every JSON field.
- Build "final_prompt" as a clean, generator-ready prompt that mirrors the spec.
- Ensure strict JSON validity (double quotes, no trailing commas).

NOW:
Ask the user ONLY for the Image Specification + Final Image-Generator Prompt text if it was not included in the message. If it was included, produce the JSON immediately with no additional questions.


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
You are an EXPERT IMAGE CREATOR.

CONTEXT:
You have just been provided with a single, exhaustive JSON image specification created by an "image_prompt_type_setter". That JSON is authoritative.

MISSION:
Convert the JSON specification into ONE final, Image.

NON-NEGOTIABLE RULES:
- Treat the JSON as strict instructions. Do not reinterpret, simplify, or “improve” it.
- Use ONLY elements explicitly permitted by the JSON. Do NOT add extra props, extra characters, extra background details, extra text, logos, watermarks, signatures, or UI overlays.
- Aspect ratio MUST be {aspect_ratio}.
- Text rules are absolute:
- Render LINE 1 and LINE 2 exactly as given (case-sensitive).
- If line2 is null, render ONLY LINE 1.
- The text must appear EXACTLY ONCE in the image.
- No other text anywhere.
- No occlusion: unicorns/fairies/props must never overlap or hide any letter.
- Legibility is the highest priority:
- Bubble letters must be very large, centered, high-contrast, and easy to read.
- Enforce the "readability_halo" and "text_clear_zone" from the JSON.
- Do NOT ask any questions. Do NOT output analysis. Do NOT output multiple options.

THINKING REQUIREMENT:
Take as much time as needed (internally) to ensure your image perfectly follows the JSON and produces a clean, reliable result. Carefully check spelling and constraints.

OUTPUT FORMAT:
- Output ONLY the final IMAGE.
- Do not output JSON.
- Do not output markdown.
- Do not add any commentary, headers, or extra sections.
- Include a short set of four lines of prose at the end

NOW:
Read the provided JSON specification and produce the single final image that matches it exactly, including explicit {aspect_ratio} framing.

The only output MUST be a generated image if the prompt violates any policy adjust it so it is okay

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
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["action"] = copy.deepcopy(action)
    robo.ai_save_image(**kwargs2)