import ipywidgets as widgets
from IPython.display import display, HTML
import random
import json # Import for parsing JSON from Gemini API

# --- Gemini API Setup ---
# To use the Gemini API, you'll need an API key. If you don't already have one,
# create a key in Google AI Studio (https://aistudio.google.com/app/apikey).
# In Colab, add the key to the secrets manager (the "🔑" icon in the left panel).
# Give it the name `GOOGLE_API_KEY`.
import google.generativeai as genai
from google.colab import userdata

try:
    GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Warning: Gemini API not configured. Please set GOOGLE_API_KEY in Colab secrets. Error: {e}")
    print("Using only hardcoded data for generation.")
    gemini_model = None # Set to None if API setup fails

# --- Helper for Gemini API calls ---
def call_gemini(prompt, model=gemini_model, max_retries=3):
    if not model:
        return ""
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API call failed (attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                import time
                time.sleep(2 ** i) # Exponential backoff
    return "" # Return empty string on persistent failure

# --- Data Generation Functions using Gemini API ---
def get_more_hero_names(count=20):
    prompt = f"Generate {count} unique and creative one-word or two-word superhero names, each on a new line. Do not number them. Only return the names."
    response_text = call_gemini(prompt)
    return [name.strip() for name in response_text.split('\n') if name.strip()]

def get_more_real_names(count=20):
    prompt = f"Generate {count} unique, modern, and diverse first and last civilian names, each on a new line. Do not number them. Only return the names."
    response_text = call_gemini(prompt)
    return [name.strip() for name in response_text.split('\n') if name.strip()]

def get_more_origins(count=5):
    prompt = f"""Generate {count} unique superhero origin stories. Each origin must be a single paragraph, similar in style to the following example, and include exactly '{{real_name}}' and '{{hero_name}}' as placeholders.
    Example: "Before they wore a mask, {{real_name}} was a quiet, painfully introverted college student... they took up the identity of '{{hero_name}}' to make sure nobody else in this city is ever left to feel helpless or ignored."
    Provide each origin on a new line. Do not number them.
    """
    response_text = call_gemini(prompt)
    # Split by two newlines to separate paragraphs, then filter and strip
    return [p.strip() for p in response_text.split('\n\n') if p.strip()]

def get_more_powers(count=5):
    prompt = f"""Generate {count} unique power profiles for superheroes. Each profile should consist of two distinct powers, 'p1' and 'p2'. Format each profile as a JSON object on a new line, like this:
    {{\"p1\": \"Power Description 1\", \"p2\": \"Power Description 2\"}}
    Only return the JSON objects, one per line. Do not add any other text or numbering.
    """
    response_text = call_gemini(prompt)
    generated_powers = []
    for line in response_text.split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                data = json.loads(line)
                if 'p1' in data and 'p2' in data:
                    generated_powers.append(data)
            except json.JSONDecodeError:
                continue # Skip malformed JSON lines
    return generated_powers

def get_more_weaknesses(count=10):
    prompt = f"Generate {count} unique and compelling fatal weaknesses for a superhero, each a single sentence on a new line. Do not number them. Only return the weaknesses."
    response_text = call_gemini(prompt)
    return [w.strip() for w in response_text.split('\n') if w.strip()]

def get_more_vibes(count=5):
    prompt = f"""Generate {count} unique superhero aesthetic vibe profiles. Each profile should include a 'color_theme' (valid hex code, e.g., #RRGGBB), 'shadow_color' (RGBA for shadow, e.g., rgba(R,G,B,0.25)), 'suit' description, and 'emblem' description. Format each profile as a JSON object on a new line, like this:
    {{\"color_theme\": \"#RRGGBB\", \"shadow_color\": \"rgba(R,G,B,0.25)\", \"suit\": \"Description of suit\", \"emblem\": \"Description of emblem\"}}
    Ensure all hex codes are valid, and RGBA values use 0.25 for alpha. Only return the JSON objects, one per line. Do not add any other text or numbering.
    """
    response_text = call_gemini(prompt)
    generated_vibes = []
    for line in response_text.split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                data = json.loads(line)
                if all(k in data for k in ['color_theme', 'shadow_color', 'suit', 'emblem']):
                    generated_vibes.append(data)
            except json.JSONDecodeError:
                continue # Skip malformed JSON lines
    return generated_vibes

# --- Initial Hardcoded Databases (used to seed expanded lists) ---
origins_db = {
    "The Classic Underdog (Introverted Student)": (
        "Before they wore a mask, {real_name} was a quiet, painfully introverted college student. "
        "Constantly ignored by classmates, struggling to pay rent, and feeling entirely invisible, "
        "their only escape was working late hours in a quiet jewelry workshop. But everything changed "
        "the night a freak laboratory accident exposed them to concentrated radiation. Instead of breaking "
        "them, the energy permanently altered their genetic code. No longer just a broke student hiding in "
        "the back of lecture halls, they took up the identity of '{hero_name}' to make sure nobody else in this "
        "city is ever left to feel helpless or ignored."
    ),
    "The Repentant Villain (Redemption Arc)": (
        "The world once knew {real_name} as a feared, ruthless criminal mastermind who brought chaos to "
        "the streets. They used their incredible talents for greed and power, never caring who got hurt. "
        "But during their last major heist, a terrible tragedy made them face the horrific consequences of "
        "their actions. Crushed by immense guilt and determined to balance their moral ledger, they abandoned "
        "their criminal empire and swore a solemn oath. Rebranding themselves as '{hero_name}', they now use "
        "their formidable abilities to protect the innocent—constantly fighting to earn the public's forgiveness."
    ),
    "The Reluctant Legacy (Quiet Artisan)": (
        "{real_name} never wanted to be a hero. They were a simple, reclusive artisan who preferred "
        "the company of raw gemstones and delicate metals to people. However, fate had other plans. While "
        "unearthing a hidden vault, {real_name} triggered an ancient cosmic relic that bonded directly with "
        "their soul. Thrust into a war they didn't ask for, the quiet designer had to build a protective "
        "suit and assume the mantle of '{hero_name}', learning to carry the heavy weight of a hero's duty."
    )
}

vibes_db = {
    "Cyberpunk / Tech Vibe": {
        "color_theme": "#00E5FF",  # Neon Cyan
        "shadow_color": "rgba(0,229,255,0.25)",
        "suit": "Matte-black carbon weave armored with glowing, electric neon circuits.",
        "emblem": "A sharp, geometric digital circuit grid."
    },
    "Mystic Jewel Vibe": {
        "color_theme": "#E040FB",  # Iridescent Violet
        "shadow_color": "rgba(224,64,251,0.25)",
        "suit": "Polished, obsidian-black plates inlaid with shifting, prismatic gemstone crystalline structures.",
        "emblem": "An intricate, multi-faceted diamond star."
    },
    "Cosmic Flare Vibe": {
        "color_theme": "#00FF66",  # Cosmic Emerald/Stellar Green
        "shadow_color": "rgba(0,255,102,0.25)",
        "suit": "Starlight-forged chrome plating reflecting deep, cosmic nebulas.",
        "emblem": "A pulsing, high-energy supernova crest."
    }
}

powers_db = {
    "Hard-Light Constructs & Phase-Shifting": {
        "p1": "Refractive Hard-Light Constructs: Can instantly freeze light particles into solid, ultra-dense geometric shields, weapons, or climbing paths.",
        "p2": "Chromatic Phase-Shifting: Vibrates atomic structure to perfectly match light frequencies, becoming invisible and walking smoothly through solid walls."
    },
    "Quantum Energy Infusion & Absorption": {
        "p1": "Molecular Laser Burst: Discharges high-concentration energy beams directly from the suit's chest emblem or palms.",
        "p2": "Kinetic Absorption Field: Absorbs the force of physical impacts and bullets, recycling that energy to temporarily multiply physical strength."
    },
    "Abyssal Shadow Wielding & Gravity Bend": {
        "p1": "Event Horizon Manipulation: Bends local gravity to levitate, redirect projectiles, or slow down incoming physical threats.",
        "p2": "Void Passage: Manifests localized pockets of dark matter, allowing them to teleport short distances through shadows."
    }
}

weaknesses_db = {
    "Photon Deprivation (Total Darkness)": "Absolute Blackout: The power source relies entirely on ambient light. In a complete, pitch-black void, all abilities instantly shut down, leaving them entirely human.",
    "High-Frequency Sonic Resonance": "Crystalline Disruption: Intense sound waves or high-frequency acoustic weapons shatter their physical energy constructs and destabilize their physical form.",
    "Emotional Chaos (Volatile Overload)": "Instability Failure: Intense feelings of guilt, panic, or rage cause the energy matrix to wildly crack, short-circuiting their suit and injuring themselves."
}

# --- Expanded Data Pools ---
all_hero_names = ["Prism", "Nightshade", "Vanguard", "Echo", "Titan", "Spectra", "Chronos", "Flux", "Nexus"]
all_real_names = ["Kiran Vance", "Lena Petrova", "Marcus Thorne", "Elara Singh", "Jian Li", "Sofia Vargas", "Ben Carter", "Chloe Dubois"]
all_origins_templates = list(origins_db.values())
all_vibes_data = list(vibes_db.values())
all_powers_data = list(powers_db.values())
all_weaknesses_data = list(weaknesses_db.values())

# Number of additional items to generate for each category using LLM
NUM_ADDITIONAL_GENERATIONS_SIMPLE = 25 # For names, weaknesses
NUM_ADDITIONAL_GENERATIONS_COMPLEX = 5  # For origins, powers, vibes (due to parsing complexity and length)

# Generate additional data using LLM and extend global lists
print("Populating expanded hero databases...")
if gemini_model:
    try:
        # Extend initial hardcoded lists with LLM-generated content
        generated_hero_names = get_more_hero_names(NUM_ADDITIONAL_GENERATIONS_SIMPLE)
        if generated_hero_names: all_hero_names.extend(generated_hero_names)

        generated_real_names = get_more_real_names(NUM_ADDITIONAL_GENERATIONS_SIMPLE)
        if generated_real_names: all_real_names.extend(generated_real_names)

        generated_origins = get_more_origins(NUM_ADDITIONAL_GENERATIONS_COMPLEX)
        if generated_origins: all_origins_templates.extend(generated_origins)

        generated_powers = get_more_powers(NUM_ADDITIONAL_GENERATIONS_COMPLEX)
        if generated_powers: all_powers_data.extend(generated_powers)

        generated_weaknesses = get_more_weaknesses(NUM_ADDITIONAL_GENERATIONS_SIMPLE)
        if generated_weaknesses: all_weaknesses_data.extend(generated_weaknesses)

        generated_vibes = get_more_vibes(NUM_ADDITIONAL_GENERATIONS_COMPLEX)
        if generated_vibes: all_vibes_data.extend(generated_vibes)

        print(f"Successfully generated additional items for each category.")
        print(f"Total hero names: {len(all_hero_names)}")
        print(f"Total real names: {len(all_real_names)}")
        print(f"Total origins: {len(all_origins_templates)}")
        print(f"Total powers: {len(all_powers_data)}")
        print(f"Total weaknesses: {len(all_weaknesses_data)}")
        print(f"Total vibes: {len(all_vibes_data)}")
    except Exception as e:
        print(f"Error during LLM data generation: {e}. Using only initial hardcoded data and partially generated data.")
else:
    print("Gemini API not available. Using only initial hardcoded data.")

# Global variable to store the last generated HTML
last_generated_html = ""

# 5. CORE ENGINE CODE
def generate_hero_dossier(hero_name, real_name, origin_text_formatted, vibe_data, power_data, weakness_text):

    # Dynamic HTML with live color-switching depending on the chosen theme!
    html_content = f"""
    <div style="border: 4px solid {vibe_data['color_theme']}; padding: 30px; border-radius: 16px; background-color: #0E0E10; color: #EAEAEA; font-family: 'Courier New', Courier, monospace; max-width: 700px; box-shadow: 0px 6px 20px {vibe_data['shadow_color']}; line-height: 1.6; margin: 15px auto;">

        <div style="text-align: center; border-bottom: 2px solid {vibe_data['color_theme']}; padding-bottom: 12px; margin-bottom: 20px;">
            <h1 style="color: {vibe_data['color_theme']}; margin: 0; text-transform: uppercase; letter-spacing: 3px; font-size: 1.8em;">
                ⚔️ SYSTEM HERO DATABASE ⚔️
            </h1>
            <span style="font-size: 0.8em; color: #888; letter-spacing: 2px;">SECURE PROTOCOL // CLASSIFIED INFORMATION</span>
        </div>

        <p style="font-size: 1.1em; margin-bottom: 10px;">
            <strong>SUPERHERO ID:</strong> <span style="color: {vibe_data['color_theme']}; font-weight: bold; font-size: 1.25em; text-shadow: 0 0 5px {vibe_data['color_theme']};">{hero_name}</span>
        </p>
        <p style="font-size: 1.1em; margin-bottom: 20px;">
            <strong>SECRET IDENTITY / CIVILIAN ALIAS:</strong> <span style="color: #FFFFFF; font-weight: bold;">{real_name}</span>
        </p>

        <div style="background-color: #16161A; padding: 18px; border-radius: 8px; border-left: 5px solid {vibe_data['color_theme']}; margin-bottom: 20px;">
            <h3 style="color: {vibe_data['color_theme']}; margin-top: 0; margin-bottom: 8px; text-transform: uppercase; font-size: 1em; letter-spacing: 1px;">📖 Origin Profile</h3>
            <p style="margin: 0; font-size: 0.95em; text-align: justify; font-style: italic; color: #D0D0D5;">
                "{origin_text_formatted}"
            </p>
        </div>

        <div style="margin-bottom: 20px;">
            <h3 style="color: #00FF66; margin-bottom: 8px; text-transform: uppercase; font-size: 1em; letter-spacing: 1px;">🧬 Wielded Power Profile</h3>
            <ul style="padding-left: 20px; margin: 0; font-size: 0.9em;">
                <li style="margin-bottom: 8px;">{power_data['p1']}</li>
                <li style="margin-bottom: 8px;">{power_data['p2']}</li>
            </ul>
        </div>

        <div style="background-color: #240E0E; padding: 12px; border-radius: 6px; border: 1px solid #FF3D00; margin-bottom: 20px;">
            <h3 style="color: #FF3D00; margin-top: 0; margin-bottom: 5px; text-transform: uppercase; font-size: 0.95em; letter-spacing: 1px;">⚠️ System Flaw / Weakness</h3>
            <p style="margin: 0; font-size: 0.9em; color: #FFA0A0;">
                {weakness_text}
            </p>
        </div>

        <div style="border-top: 1px dashed #444; padding-top: 15px;">
            <h3 style="color: #FFB300; margin-top: 0; margin-bottom: 8px; text-transform: uppercase; font-size: 1em; letter-spacing: 1px;">🎨 Visual Armor Spec</h3>
            <p style="margin: 3px 0; font-size: 0.9em;"><strong>Suit Composition:</strong> {vibe_data['suit']}</p>
            <p style="margin: 3px 0; font-size: 0.9em;"><strong>Chest Emblem:</strong> {vibe_data['emblem']}</p>
        </div>

        <div style="margin-top: 25px; text-align: center; font-size: 0.75em; color: #555; letter-spacing: 2px;">
            // AGENT REHABILITATION PROGRAM STATUS: ACTIVE //
        </div>
    </div>
    """
    return html_content # Return the HTML content

def generate_random_hero_dossier(b):
    global last_generated_html # Declare intent to modify the global variable

    # Randomly select choices from expanded pools
    hero_name = random.choice(all_hero_names)
    real_name = random.choice(all_real_names)

    selected_origin_template = random.choice(all_origins_templates)
    origin_text_formatted = selected_origin_template.format(real_name=real_name, hero_name=hero_name)

    vibe_data = random.choice(all_vibes_data)
    power_data = random.choice(all_powers_data)
    weakness_text = random.choice(all_weaknesses_data)

    # Generate the dossier and store the HTML
    generated_html = generate_hero_dossier(hero_name, real_name, origin_text_formatted, vibe_data, power_data, weakness_text)
    last_generated_html = generated_html # Store it globally

    # Display the generated HTML in the output area
    output_area.clear_output()
    with output_area:
        display(HTML(generated_html))

# 6. CREATING USER INTERFACE CONTROLS
random_gen_button = widgets.Button(
    description='🎲 Generate Random Hero',
    button_style='info',
    layout=widgets.Layout(width='70%', margin='10px 0px 10px 15%')
)
random_gen_button.on_click(generate_random_hero_dossier)

output_area = widgets.Output()

# Organize Dashboard Layout
ui_layout = widgets.VBox([
    widgets.HTML("<h2 style='color:#00E5FF; font-family:monospace;'>🛠️ Superhero Blueprint Creator</h2>"),
    widgets.HTML("<p style='font-family:monospace; color:#888;'>Click 'Generate Random Hero' to create a new hero profile!</p>"),
    random_gen_button
])

# Deploy Live to Screen
display(ui_layout, output_area)

# Generate an initial random hero when the cell is run
generate_random_hero_dossier(None)
