#!/usr/bin/env python3
import os
import json
import math

#######################
# Constants & Defaults
#######################

BASE_STACK_SIZE = 64
SHULKER_STACKS = 27     # Number of stacks per shulker box
DOUBLE_CHEST_STACKS = 54  # Number of stacks per double chest
RECIPES_FILE = "recipes.json"
CONFIG_FILE = "config.json"

DEFAULT_RECIPES = {
    # Simple recipes (one layer)
    "plank": {"inputs": {"log": 1}, "output": 4},
    "chest": {"inputs": {"plank": 8}, "output": 1},
    "hopper": {"inputs": {"chest": 1, "iron": 5}, "output": 1},
    "minecart": {"inputs": {"iron": 5}, "output": 1},
    "minecart_hopper": {"inputs": {"minecart": 1, "hopper": 1}, "output": 1},
    # Example multi-layer recipe for trapdoor:
    # Layer 1: logs -> planks; Layer 2: planks -> trapdoor
    "trapdoor": {
        "layers": [
            {"name": "planks", "inputs": {"logs": 1}, "output": 4},
            {"name": "trapdoor", "inputs": {"planks": 6}, "output": 2}
        ]
    },
    # Example multi-layer recipe for ladder:
    # Layer 1: logs -> planks; Layer 2: planks -> sticks; Layer 3: sticks -> ladders
    "ladder": {
        "layers": [
            {"name": "planks", "inputs": {"logs": 1}, "output": 4},
            {"name": "sticks", "inputs": {"planks": 2}, "output": 4},
            {"name": "ladders", "inputs": {"sticks": 6}, "output": 3}
        ]
    },
    # Example multi-layer recipe for grindstone (numbers are illustrative):
    "grindstone": {
        "layers": [
            {"name": "planks", "inputs": {"logs": 1}, "output": 4},
            {"name": "sticks", "inputs": {"planks": 6}, "output": 4},
            {"name": "grindstone", "inputs": {"stone slab": 1, "planks": 60, "sticks": 60}, "output": 1}
        ]
    },
    # Example recipe for scaffolding (illustrative)
    "scaffolding": {"inputs": {"bamboo": 6, "string": 13}, "output": 64}
}

DEFAULT_CONFIG = {
    "auto_conversion": True,
    "suffixes": {
        "stack": "s",
        "shulker": "sb",
        "double_chest": "dc"
    },
    "container_preference": "sb"
}

#######################
# Config Functions
#######################

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config
        except Exception as e:
            print("Error loading config:", e)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print("Error saving config:", e)

#######################
# Recipes Functions
#######################

def load_recipes():
    if os.path.exists(RECIPES_FILE):
        try:
            with open(RECIPES_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and "recipes" in data:
                return data["recipes"]
            else:
                return data
        except Exception as e:
            print("Error loading recipes file:", e)
            print("Using default recipes.")
    return DEFAULT_RECIPES.copy()

def save_recipes(recipes, config):
    try:
        data = {"recipes": recipes}
        with open(RECIPES_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving recipes:", e)

#######################
# Conversion Helpers
#######################

def parse_single_amount(s, config):
    s = s.strip().lower()
    suf_stack = config.get("suffixes", {}).get("stack", DEFAULT_CONFIG["suffixes"]["stack"])
    suf_shulker = config.get("suffixes", {}).get("shulker", DEFAULT_CONFIG["suffixes"]["shulker"])
    suf_dc = config.get("suffixes", {}).get("double_chest", DEFAULT_CONFIG["suffixes"]["double_chest"])
    if s.endswith(suf_shulker):
        try:
            num = float(s[:-len(suf_shulker)])
            return num * BASE_STACK_SIZE * SHULKER_STACKS
        except ValueError:
            raise ValueError("Invalid number for shulker boxes.")
    elif s.endswith(suf_dc):
        try:
            num = float(s[:-len(suf_dc)])
            return num * BASE_STACK_SIZE * DOUBLE_CHEST_STACKS
        except ValueError:
            raise ValueError("Invalid number for double chests.")
    elif s.endswith(suf_stack):
        try:
            num = float(s[:-len(suf_stack)])
            return num * BASE_STACK_SIZE
        except ValueError:
            raise ValueError("Invalid number for stacks.")
    else:
        try:
            return float(s)
        except ValueError:
            raise ValueError("Invalid amount format.")

def parse_combined_amount(s, config):
    parts = s.split(",")
    total = 0.0
    for part in parts:
        total += parse_single_amount(part, config)
    return total

def breakdown_to_stacks(total_items):
    stacks = total_items // BASE_STACK_SIZE
    items = total_items % BASE_STACK_SIZE
    return int(stacks), int(items)

def breakdown_to_shulkers(total_items):
    stacks, items = breakdown_to_stacks(total_items)
    shulkers = stacks // SHULKER_STACKS
    rem_stacks = stacks % SHULKER_STACKS
    return int(shulkers), int(rem_stacks), int(items)

def breakdown_to_double_chests(total_items):
    stacks, items = breakdown_to_stacks(total_items)
    dcs = stacks // DOUBLE_CHEST_STACKS
    rem_stacks = stacks % DOUBLE_CHEST_STACKS
    return int(dcs), int(rem_stacks), int(items)

def format_breakdown(total_items, auto_conv=True, container_override="sb"):
    total_items = int(total_items)
    if not auto_conv:
        return f"{total_items} item(s)"
    if container_override == "dc":
        dcs, rem_stacks, rem_items = breakdown_to_double_chests(total_items)
        parts = []
        if dcs:
            parts.append(f"{dcs} double chest(s)")
        if rem_stacks:
            parts.append(f"{rem_stacks} stack(s)")
        if rem_items:
            parts.append(f"{rem_items} item(s)")
        return ", ".join(parts) if parts else f"{total_items} item(s)"
    else:  # default "sb"
        shulkers, rem_stacks, rem_items = breakdown_to_shulkers(total_items)
        parts = []
        if shulkers:
            parts.append(f"{shulkers} shulker box(es)")
        if rem_stacks:
            parts.append(f"{rem_stacks} stack(s)")
        if rem_items:
            parts.append(f"{rem_items} item(s)")
        return ", ".join(parts) if parts else f"{total_items} item(s)"

#######################
# Conversion Menu Functions
#######################

def convert_items_to_stacks(config):
    try:
        raw = input("Enter the total amount (e.g. '100', '5{0}', '2{1}', '1{2}', or combined '30{0}, 15'): ".format(
            config.get("suffixes", {}).get("stack", DEFAULT_CONFIG["suffixes"]["stack"]),
            config.get("suffixes", {}).get("shulker", DEFAULT_CONFIG["suffixes"]["shulker"]),
            config.get("suffixes", {}).get("double_chest", DEFAULT_CONFIG["suffixes"]["double_chest"])))
        total_items = int(parse_combined_amount(raw, config))
        stacks, items = breakdown_to_stacks(total_items)
        if config["auto_conversion"]:
            print(f"{total_items} item(s) = {stacks} full stack(s) and {items} item(s) remaining.")
        else:
            print(f"{total_items} item(s)")
    except ValueError as e:
        print(e)

def convert_stacks_to_containers(config):
    try:
        raw = input("Enter the amount (e.g. '10', '3{0}', '1{1}', '1{2}', or '10{0}, 5'): ".format(
            config.get("suffixes", {}).get("stack", DEFAULT_CONFIG["suffixes"]["stack"]),
            config.get("suffixes", {}).get("shulker", DEFAULT_CONFIG["suffixes"]["shulker"]),
            config.get("suffixes", {}).get("double_chest", DEFAULT_CONFIG["suffixes"]["double_chest"])))
        total_items = int(parse_combined_amount(raw, config))
        stacks, items = breakdown_to_stacks(total_items)
        print(f"Total: {stacks} stack(s) and {items} item(s)")
        if config["auto_conversion"]:
            shulkers, rem_stacks, rem_items = breakdown_to_shulkers(total_items)
            print(f"As shulker boxes: {shulkers} shulker box(es), {rem_stacks} stack(s) and {rem_items} item(s) remaining.")
            dcs, rem_stacks_dc, rem_items_dc = breakdown_to_double_chests(total_items)
            print(f"As double chests: {dcs} double chest(s), {rem_stacks_dc} stack(s) and {rem_items_dc} item(s) remaining.")
    except ValueError as e:
        print(e)

#######################
# Crafting Helpers
#######################

def crafting_helper(config):
    try:
        print("Define your recipe conversion ratio:")
        input_required = float(input("Enter the number of input items required: "))
        output_result = float(input("Enter the number of output items produced: "))
        if input_required <= 0 or output_result <= 0:
            print("Values must be positive numbers.")
            return

        print("Choose an option:")
        print("1. Calculate required input items for a desired output amount.")
        print("2. Calculate obtainable outputs from available input items.")
        choice = input("Enter 1 or 2: ")

        user_input = input("Enter the desired amount (supports combined amounts, e.g. '30{0}, 15'): ".format(
            config.get("suffixes", {}).get("stack", DEFAULT_CONFIG["suffixes"]["stack"]))).strip()
        if user_input.endswith(config.get("suffixes", {}).get("double_chest", DEFAULT_CONFIG["suffixes"]["double_chest"])):
            container_override = "dc"
        elif user_input.endswith(config.get("suffixes", {}).get("shulker", DEFAULT_CONFIG["suffixes"]["shulker"])):
            container_override = "sb"
        else:
            container_override = config.get("container_preference", "sb")
        if choice == "1":
            desired_output = float(parse_combined_amount(user_input, config))
            required_inputs = (input_required / output_result) * desired_output
            print(f"You need approximately {int(round(required_inputs))} input item(s) to produce {int(round(desired_output))} output(s).")
            print("That is:", format_breakdown(required_inputs, config["auto_conversion"], container_override))
        elif choice == "2":
            available_inputs = float(input("Enter the number of available input items: "))
            produced_outputs = (output_result / input_required) * available_inputs
            print(f"You can produce approximately {int(round(produced_outputs))} output item(s) with {int(round(available_inputs))} input(s).")
            print("That is:", format_breakdown(produced_outputs, config["auto_conversion"], container_override))
        else:
            print("Invalid choice. Please select either 1 or 2.")
    except ValueError:
        print("Invalid input. Please enter numerical values.")

def compute_requirements(item, quantity, recipes):
    if item not in recipes or ("layers" in recipes[item]):
        return {item: quantity}
    recipe = recipes[item]
    factor = quantity / recipe["output"]
    req = {}
    for ing, ing_qty in recipe["inputs"].items():
        needed = ing_qty * factor
        sub_req = compute_requirements(ing, needed, recipes)
        for k, v in sub_req.items():
            req[k] = req.get(k, 0) + v
    return req

def compute_layered_requirements(layers, final_quantity):
    """
    Compute requirements using integer (ceiling) math at each layer.
    Process layers from final to first. For each layer:
      - Determine the number of crafts needed = ceil(required / output)
      - Calculate the total inputs = crafts * input quantity for each ingredient.
      - Propagate the required amount to earlier layers if that ingredient is produced there.
    Returns a list of computed layer dictionaries (in order).
    """
    n = len(layers)
    # Initialize required amounts for each layer's product.
    required = [0] * n
    required[-1] = final_quantity  # Final product required.
    computed = [None] * n
    # Process layers from last to first.
    for i in range(n-1, -1, -1):
        layer = layers[i]
        # Number of crafts needed, rounded up.
        crafts = math.ceil(required[i] / layer["output"])
        produced = crafts * layer["output"]
        layer_req = {ing: crafts * qty for ing, qty in layer["inputs"].items()}
        computed[i] = {"layer": i+1, "name": layer["name"], "crafts": crafts, "produced": produced, "requirements": layer_req}
        # Propagate requirements for ingredients produced by an earlier layer.
        for ing, amt in layer_req.items():
            # Check if any earlier layer produces this ingredient.
            for j in range(i):
                if layers[j]["name"] == ing:
                    required[j] += amt
    return computed

def advanced_crafting(recipes, config):
    print("\n--- Advanced Crafting Helper ---")
    print("Available recipes:")
    for k, v in recipes.items():
        if "layers" in v:
            layers = v["layers"]
            layers_str = " | ".join([f"Layer {i+1}: {layer['inputs']} -> {layer['output']} {layer['name']}(s)" for i, layer in enumerate(layers)])
            print(f"  {k} (multi-layer): {layers_str}")
        else:
            inputs_str = " + ".join(f"{amt} {ing}" for ing, amt in v["inputs"].items())
            print(f"  {k}: {inputs_str} -> {v['output']} {k}(s)")
        
    target = input("Enter the target item: ").strip().lower()
    quantity_input = input("Enter the desired amount (supports combined amounts, e.g. '30{0}, 15'): ".format(
        config.get("suffixes", {}).get("stack", DEFAULT_CONFIG["suffixes"]["stack"]))).strip()
    if quantity_input.endswith(config.get("suffixes", {}).get("double_chest", DEFAULT_CONFIG["suffixes"]["double_chest"])):
        container_override = "dc"
    elif quantity_input.endswith(config.get("suffixes", {}).get("shulker", DEFAULT_CONFIG["suffixes"]["shulker"])):
        container_override = "sb"
    else:
        container_override = config.get("container_preference", "sb")
    try:
        quantity = int(parse_combined_amount(quantity_input, config))
    except ValueError as e:
        print(e)
        return

    if target in recipes and "layers" in recipes[target]:
        layers = recipes[target]["layers"]
        layered_reqs = compute_layered_requirements(layers, quantity)
        print(f"\nTo craft {format_breakdown(quantity, config['auto_conversion'], container_override)} of '{target}', you need the following per layer:")
        for comp in layered_reqs:
            print(f"Layer {comp['layer']} ({comp['name']}):")
            print(f"  Crafts required: {comp['crafts']} (produces {comp['produced']} {comp['name']}(s))")
            for ing, amt in comp["requirements"].items():
                if not config["auto_conversion"]:
                    print(f"  {ing}: {int(round(amt))} item(s)")
                else:
                    print(f"  {ing}: {format_breakdown(amt, config['auto_conversion'], container_override)}")
    else:
        req = compute_requirements(target, quantity, recipes)
        print(f"\nTo craft {format_breakdown(quantity, config['auto_conversion'], container_override)} of '{target}', you need:")
        for ing, amt in req.items():
            if not config["auto_conversion"]:
                print(f"  {ing}: {int(round(amt))} item(s)")
            else:
                print(f"  {ing}: {format_breakdown(amt, config['auto_conversion'], container_override)}")
    print()

#######################
# Add Recipe Function
#######################

def add_recipe(recipes):
    print("\n--- Add a New Recipe ---")
    output_item = input("Enter the output item name: ").strip().lower()
    try:
        layers_count = int(input("How many layers does this recipe have? (Enter 1 for a simple recipe): "))
        if layers_count <= 0:
            print("Number of layers must be at least 1.")
            return
    except ValueError:
        print("Invalid number for layers.")
        return

    if layers_count == 1:
        try:
            output_qty = float(input("Enter the quantity produced by this recipe: "))
            if output_qty <= 0:
                print("Output quantity must be positive.")
                return
        except ValueError:
            print("Invalid output quantity.")
            return
        inputs_raw = input("Enter the input ingredients (format: ingredient:quantity, separated by commas): ").strip()
        inputs = {}
        try:
            for pair in inputs_raw.split(","):
                if ':' not in pair:
                    print(f"Skipping invalid input format: {pair}")
                    continue
                ing, qty = pair.split(":", 1)
                ing = ing.strip().lower()
                qty = float(qty.strip())
                if qty <= 0:
                    print(f"Quantity for {ing} must be positive.")
                    continue
                inputs[ing] = qty
        except ValueError:
            print("Invalid ingredient quantity.")
            return
        if not inputs:
            print("No valid ingredients were entered.")
            return
        recipes[output_item] = {"inputs": inputs, "output": output_qty}
    else:
        layers = []
        for i in range(1, layers_count+1):
            print(f"\n--- Layer {i} ---")
            layer_name = input("Enter the product name for this layer (for final layer, this is the final output name): ").strip().lower()
            try:
                layer_output = float(input("Enter the output quantity produced in this layer: "))
                if layer_output <= 0:
                    print("Output quantity must be positive.")
                    return
            except ValueError:
                print("Invalid output quantity.")
                return
            inputs_raw = input("Enter the input ingredients for this layer (format: ingredient:quantity, separated by commas): ").strip()
            inputs = {}
            try:
                for pair in inputs_raw.split(","):
                    if ':' not in pair:
                        print(f"Skipping invalid input format: {pair}")
                        continue
                    ing, qty = pair.split(":", 1)
                    ing = ing.strip().lower()
                    qty = float(qty.strip())
                    if qty <= 0:
                        print(f"Quantity for {ing} must be positive.")
                        continue
                    inputs[ing] = qty
            except ValueError:
                print("Invalid ingredient quantity.")
                return
            if not inputs:
                print("No valid ingredients were entered for this layer.")
                return
            layers.append({"name": layer_name, "inputs": inputs, "output": layer_output})
        recipes[output_item] = {"layers": layers}
    save_recipes(recipes, DEFAULT_CONFIG)
    print(f"Recipe for '{output_item}' added successfully.\n")

#######################
# Overworld/Nether Converter
#######################

def convert_coordinates():
    print("\n--- Overworld/Nether Converter ---")
    print("Choose conversion type:")
    print("1. Overworld to Nether")
    print("2. Nether to Overworld")
    choice = input("Enter 1 or 2: ").strip()
    try:
        x = float(input("Enter x coordinate: "))
        y = float(input("Enter y coordinate: "))
        z = float(input("Enter z coordinate: "))
    except ValueError:
        print("Invalid coordinate input.")
        return
    if choice == "1":
        conv_x = x / 8
        conv_z = z / 8
        print(f"Overworld ({x}, {y}, {z}) -> Nether ({conv_x:.2f}, {y:.2f}, {conv_z:.2f})")
    elif choice == "2":
        conv_x = x * 8
        conv_z = z * 8
        print(f"Nether ({x}, {y}, {z}) -> Overworld ({conv_x:.2f}, {y:.2f}, {conv_z:.2f})")
    else:
        print("Invalid choice.")

#######################
# Config Menu
#######################

def config_menu(config):
    while True:
        print("\n--- Configuration Menu ---")
        print(f"1. Toggle auto conversion (currently {'ON' if config['auto_conversion'] else 'OFF'})")
        print("2. Change suffixes")
        print("3. Change default container preference (currently '{}')".format(config.get("container_preference", "sb")))
        print("4. Reset suffixes to default")
        print("5. Back to main menu")
        choice = input("Select an option (1-5): ").strip()
        if choice == "1":
            config["auto_conversion"] = not config["auto_conversion"]
            print("Auto conversion is now", "ON" if config["auto_conversion"] else "OFF")
            save_config(config)
        elif choice == "2":
            new_stack = input("Enter new suffix for stacks (current: '{}'): ".format(config.get("suffixes", {}).get("stack", DEFAULT_CONFIG["suffixes"]["stack"]))).strip()
            new_shulker = input("Enter new suffix for shulker boxes (current: '{}'): ".format(config.get("suffixes", {}).get("shulker", DEFAULT_CONFIG["suffixes"]["shulker"]))).strip()
            new_dc = input("Enter new suffix for double chests (current: '{}'): ".format(config.get("suffixes", {}).get("double_chest", DEFAULT_CONFIG["suffixes"]["double_chest"]))).strip()
            if new_stack:
                config["suffixes"]["stack"] = new_stack
            if new_shulker:
                config["suffixes"]["shulker"] = new_shulker
            if new_dc:
                config["suffixes"]["double_chest"] = new_dc
            print("Suffixes updated.")
            save_config(config)
        elif choice == "3":
            pref = input("Enter default container preference ('sb' or 'dc'): ").strip().lower()
            if pref in ["sb", "dc"]:
                config["container_preference"] = pref
                print("Default container preference updated to", pref)
                save_config(config)
            else:
                print("Invalid preference. Please enter 'sb' or 'dc'.")
        elif choice == "4":
            config["suffixes"] = DEFAULT_CONFIG["suffixes"].copy()
            print("Suffixes reset to default.")
            save_config(config)
        elif choice == "5":
            break
        else:
            print("Invalid option.")

#######################
# Main Menu
#######################

def main():
    config = load_config()
    recipes = load_recipes()
    while True:
        print("\nMinecraft Calculator Helper")
        print("1. Convert items to stacks")
        print("2. Convert stacks to containers (shulkers/double chests)")
        print("3. Simple Crafting Helper (single recipe ratio)")
        print("4. Advanced Crafting Helper (layered recipes)")
        print("5. Add a new recipe")
        print("6. Overworld/Nether Converter")
        print("7. Configure settings")
        print("8. Exit")
        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            convert_items_to_stacks(config)
        elif choice == "2":
            convert_stacks_to_containers(config)
        elif choice == "3":
            crafting_helper(config)
        elif choice == "4":
            advanced_crafting(recipes, config)
        elif choice == "5":
            add_recipe(recipes)
        elif choice == "6":
            convert_coordinates()
        elif choice == "7":
            config_menu(config)
        elif choice == "8":
            print("Exiting. Happy crafting!")
            break
        else:
            print("Invalid option. Please choose from 1 to 8.")

if __name__ == '__main__':
    main()
