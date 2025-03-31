#!/usr/bin/env python3
import json
import math
from pathlib import Path # Use pathlib for cleaner path handling

#######################
# Constants & Defaults
#######################

BASE_STACK_SIZE = 64
SHULKER_STACKS = 27     # Number of stacks per shulker box
DOUBLE_CHEST_STACKS = 54  # Number of stacks per double chest

# Use Path objects for file paths
RECIPES_FILE = Path("recipes.json")
CONFIG_FILE = Path("config.json")

# Default recipes removed - start with an empty set
# Users will add their own via the menu or by creating recipes.json
DEFAULT_RECIPES = {}

DEFAULT_CONFIG = {
    "auto_conversion": True,
    "suffixes": {
        "stack": "s",
        "shulker": "sb",
        "double_chest": "dc"
    },
    "container_preference": "sb" # Default to shulker boxes for formatting
}

#######################
# Config Functions
#######################

def load_config() -> dict:
    """Loads configuration from JSON file, returning defaults on failure."""
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r") as f:
                config = json.load(f)
                # Basic validation - ensure essential keys exist, merge with defaults if needed
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict): # Handle nested dicts like 'suffixes'
                         for sub_key, sub_value in value.items():
                             if sub_key not in config[key]:
                                 config[key][sub_key] = sub_value
                return config
        except (json.JSONDecodeError, IOError, Exception) as e:
            print(f"Error loading config file ({CONFIG_FILE}): {e}. Using default config.")
    return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    """Saves the configuration dictionary to a JSON file."""
    try:
        with CONFIG_FILE.open("w") as f:
            json.dump(config, f, indent=4)
    except (IOError, Exception) as e:
        print(f"Error saving config file ({CONFIG_FILE}): {e}")

#######################
# Recipes Functions
#######################

def load_recipes() -> dict:
    """Loads recipes from JSON file, returning defaults (empty) on failure."""
    if RECIPES_FILE.exists():
        try:
            with RECIPES_FILE.open("r") as f:
                data = json.load(f)
            # Expect recipes under a "recipes" key, but handle flat dict for backward compatibility
            if isinstance(data, dict) and "recipes" in data:
                if isinstance(data["recipes"], dict):
                     return data["recipes"]
                else:
                    print(f"Warning: 'recipes' key in {RECIPES_FILE} does not contain a valid dictionary. Using empty recipes.")
                    return DEFAULT_RECIPES.copy()
            elif isinstance(data, dict): # Assume older format (flat dictionary)
                print(f"Warning: Using older recipe file format found in {RECIPES_FILE}. Consider nesting under a 'recipes' key.")
                return data
            else:
                 print(f"Error: Invalid format in {RECIPES_FILE}. Expected a dictionary. Using empty recipes.")
                 return DEFAULT_RECIPES.copy()
        except (json.JSONDecodeError, IOError, Exception) as e:
            print(f"Error loading recipes file ({RECIPES_FILE}): {e}. Using empty recipes.")
    # Return a copy to prevent modification of the default
    return DEFAULT_RECIPES.copy()

# Removed unused 'config' parameter
def save_recipes(recipes: dict):
    """Saves the recipes dictionary to a JSON file, nested under 'recipes' key."""
    try:
        # Always save wrapped in a "recipes" key for consistency
        data_to_save = {"recipes": recipes}
        with RECIPES_FILE.open("w") as f:
            json.dump(data_to_save, f, indent=4)
    except (IOError, Exception) as e:
        print(f"Error saving recipes file ({RECIPES_FILE}): {e}")

#######################
# Conversion Helpers
#######################

def get_suffixes(config: dict) -> dict:
    """Helper to safely get suffixes, falling back to defaults."""
    cfg_suffixes = config.get("suffixes", {})
    # Ensure all default suffix keys exist
    return {
        "stack": cfg_suffixes.get("stack", DEFAULT_CONFIG["suffixes"]["stack"]),
        "shulker": cfg_suffixes.get("shulker", DEFAULT_CONFIG["suffixes"]["shulker"]),
        "double_chest": cfg_suffixes.get("double_chest", DEFAULT_CONFIG["suffixes"]["double_chest"]),
    }

def parse_single_amount(s: str, config: dict) -> float:
    """Parses a single amount string (e.g., '10', '5s', '2sb') into total items."""
    s = s.strip().lower()
    suffixes = get_suffixes(config)
    suf_stack = suffixes["stack"]
    suf_shulker = suffixes["shulker"]
    suf_dc = suffixes["double_chest"]

    multiplier = 1.0
    value_str = s

    if s.endswith(suf_shulker):
        multiplier = BASE_STACK_SIZE * SHULKER_STACKS
        value_str = s[:-len(suf_shulker)]
    elif s.endswith(suf_dc):
        multiplier = BASE_STACK_SIZE * DOUBLE_CHEST_STACKS
        value_str = s[:-len(suf_dc)]
    elif s.endswith(suf_stack):
        multiplier = BASE_STACK_SIZE
        value_str = s[:-len(suf_stack)]

    try:
        num = float(value_str)
        if num < 0:
             raise ValueError("Amount cannot be negative.")
        return num * multiplier
    except ValueError:
        # Raise a more specific error message including the problematic input
        raise ValueError(f"Invalid amount format: '{s}'. Expected a number optionally followed by a suffix ({suf_stack}, {suf_shulker}, {suf_dc}).")


def parse_combined_amount(s: str, config: dict) -> float:
    """Parses a comma-separated string of amounts into a total item count."""
    parts = s.split(",")
    total = 0.0
    for part in parts:
        if part.strip(): # Avoid processing empty strings from stray commas
            total += parse_single_amount(part, config)
    return total

def breakdown_to_stacks(total_items: float) -> tuple[int, int]:
    """Calculates full stacks and remaining items."""
    total_items = math.floor(total_items) # Use floor for calculations based on whole items
    stacks = total_items // BASE_STACK_SIZE
    items = total_items % BASE_STACK_SIZE
    return stacks, items

def breakdown_to_shulkers(total_items: float) -> tuple[int, int, int]:
    """Calculates shulker boxes, remaining stacks, and remaining items."""
    stacks, items = breakdown_to_stacks(total_items)
    shulkers = stacks // SHULKER_STACKS
    rem_stacks = stacks % SHULKER_STACKS
    return shulkers, rem_stacks, items

def breakdown_to_double_chests(total_items: float) -> tuple[int, int, int]:
    """Calculates double chests, remaining stacks, and remaining items."""
    stacks, items = breakdown_to_stacks(total_items)
    dcs = stacks // DOUBLE_CHEST_STACKS
    rem_stacks = stacks % DOUBLE_CHEST_STACKS
    return dcs, rem_stacks, items

def format_breakdown(total_items: float, auto_conv: bool = True, container_preference: str = "sb") -> str:
    """Formats total items into a human-readable string with containers."""
    # Use ceiling for display if showing raw items, floor for breakdowns
    if not auto_conv:
        # Show ceiling of items if not breaking down, as you often need the 'partial' item
        return f"{math.ceil(total_items)} item(s)"

    # Use floor for breakdowns, as you can only use whole items for storage counts
    int_total_items = math.floor(total_items)
    if int_total_items <= 0:
        return "0 items"

    parts = []
    if container_preference == "dc":
        dcs, rem_stacks, rem_items = breakdown_to_double_chests(int_total_items)
        if dcs: parts.append(f"{dcs} double chest(s)")
        if rem_stacks: parts.append(f"{rem_stacks} stack(s)")
        if rem_items: parts.append(f"{rem_items} item(s)")
    else:  # Default "sb"
        shulkers, rem_stacks, rem_items = breakdown_to_shulkers(int_total_items)
        if shulkers: parts.append(f"{shulkers} shulker box(es)")
        if rem_stacks: parts.append(f"{rem_stacks} stack(s)")
        if rem_items: parts.append(f"{rem_items} item(s)")

    # If breakdown results in nothing (e.g., less than 1 item after floor), show original total (ceil)
    return ", ".join(parts) if parts else f"{math.ceil(total_items)} item(s)"

#######################
# Conversion Menu Functions
#######################

def convert_items_to_stacks(config: dict):
    """Menu function to convert raw item counts or container amounts to stacks/items."""
    suffixes = get_suffixes(config)
    prompt = (f"Enter the total amount (e.g., '100', '5{suffixes['stack']}', "
              f"'2{suffixes['shulker']}', '1{suffixes['double_chest']}', "
              f"or combined '30{suffixes['stack']}, 15'): ")
    try:
        raw_input = input(prompt)
        total_items = parse_combined_amount(raw_input, config)
        stacks, items = breakdown_to_stacks(total_items)

        # Always show the exact total items parsed
        print(f"Total items: {total_items:.2f}" if total_items % 1 != 0 else f"Total items: {int(total_items)}")

        if config.get("auto_conversion", True):
            print(f"Equals: {stacks} full stack(s) and {items} item(s).")
        else:
            # If auto-conversion is off, maybe still show raw item count clearly
            print(f"(Raw item breakdown: {stacks} stacks, {items} items)")

    except ValueError as e:
        print(f"Error: {e}")

def convert_stacks_to_containers(config: dict):
    """Menu function to convert amounts into shulker and double chest breakdowns."""
    suffixes = get_suffixes(config)
    prompt = (f"Enter the amount (e.g., '10', '3{suffixes['stack']}', "
              f"'1{suffixes['shulker']}', '1{suffixes['double_chest']}', "
              f"or '10{suffixes['stack']}, 5'): ")
    try:
        raw_input = input(prompt)
        total_items = parse_combined_amount(raw_input, config)
        stacks, items = breakdown_to_stacks(total_items)

        print(f"Total items: {total_items:.2f}" if total_items % 1 != 0 else f"Total items: {int(total_items)}")
        print(f"Equals: {stacks} stack(s) and {items} item(s)")

        if config.get("auto_conversion", True):
            shulkers, rem_stacks_sb, rem_items_sb = breakdown_to_shulkers(total_items)
            print(f" -> Shulker Boxes: {shulkers} shulker box(es), {rem_stacks_sb} stack(s), {rem_items_sb} item(s).")

            dcs, rem_stacks_dc, rem_items_dc = breakdown_to_double_chests(total_items)
            print(f" -> Double Chests: {dcs} double chest(s), {rem_stacks_dc} stack(s), {rem_items_dc} item(s).")

    except ValueError as e:
        print(f"Error: {e}")

#######################
# Crafting Helpers
#######################

def crafting_helper(config: dict):
    """Simple crafting calculator based on a single input/output ratio."""
    try:
        print("\n--- Simple Crafting Helper ---")
        print("Define your recipe conversion ratio:")
        # Use parse_combined_amount to allow flexible input like "1s" or "64"
        input_required = parse_combined_amount(input("Enter the number of input items required (e.g., '8', '1s'): "), config)
        output_result = parse_combined_amount(input("Enter the number of output items produced (e.g., '1', '4'): "), config)

        if input_required <= 0 or output_result <= 0:
            print("Error: Input and output amounts must be positive.")
            return

        print("\nChoose calculation type:")
        print("1. Calculate required INPUT for a desired OUTPUT.")
        print("2. Calculate achievable OUTPUT from available INPUT.")
        choice = input("Enter 1 or 2: ").strip()

        suffixes = get_suffixes(config)
        auto_conv = config.get("auto_conversion", True)
        container_pref = config.get("container_preference", "sb")

        if choice == "1":
            prompt = (f"Enter the DESIRED OUTPUT amount (e.g., '100', '5{suffixes['stack']}', "
                      f"'2{suffixes['shulker']}'): ")
            user_input = input(prompt).strip()
            # Determine container override based *only* on the primary suffixes
            container_override = container_pref # Default
            if user_input.lower().endswith(suffixes['double_chest']):
                container_override = "dc"
            elif user_input.lower().endswith(suffixes['shulker']):
                container_override = "sb"

            desired_output = parse_combined_amount(user_input, config)
            if desired_output <= 0:
                 print("Error: Desired output must be positive.")
                 return
            # Use ceil for required inputs - you need the whole item
            required_inputs = math.ceil((input_required / output_result) * desired_output)

            print(f"\nTo produce {format_breakdown(desired_output, auto_conv, container_override)} output,")
            print(f"you need {format_breakdown(required_inputs, auto_conv, container_override)} input item(s).")
            if not auto_conv: # Also show raw number if auto-conversion is off
                 print(f"(Approximately {required_inputs} raw input items)")


        elif choice == "2":
            prompt = (f"Enter the AVAILABLE INPUT amount (e.g., '500', '10{suffixes['stack']}', "
                      f"'3{suffixes['shulker']}'): ")
            available_inputs = parse_combined_amount(input(prompt), config)
            if available_inputs < 0:
                 print("Error: Available input cannot be negative.")
                 return

            # Use floor for produced outputs - you can only make whole items/batches
            produced_outputs = math.floor((output_result / input_required) * available_inputs)

            print(f"\nWith {format_breakdown(available_inputs, auto_conv, container_pref)} input item(s),") # Use default pref for input display
            # Use default pref for output display too, unless input specified container? Stick to default for clarity.
            print(f"you can produce {format_breakdown(produced_outputs, auto_conv, container_pref)} output item(s).")
            if not auto_conv: # Also show raw number
                 print(f"(Approximately {produced_outputs} raw output items)")

        else:
            print("Invalid choice. Please select either 1 or 2.")

    except ValueError as e:
        print(f"Error: Invalid input. {e}")
    except ZeroDivisionError:
        print("Error: Cannot calculate with zero input or output items.")

def compute_requirements(item: str, quantity: float, recipes: dict) -> dict:
    """Recursively compute base material requirements for a simple (non-layered) recipe."""
    # Base case: Item is a raw material (not in recipes) or handled by layered compute
    if item not in recipes or "layers" in recipes[item]:
        return {item: quantity}

    recipe = recipes[item]
    # Check for valid output quantity to prevent division by zero
    if recipe["output"] <= 0:
        print(f"Warning: Recipe for '{item}' has non-positive output ({recipe['output']}). Cannot calculate requirements.")
        return {item: quantity} # Treat as base material if recipe is invalid

    # Calculate how many times the recipe needs to be crafted (can be fractional here)
    crafting_factor = quantity / recipe["output"]
    requirements = {}

    for ingredient, ing_quantity in recipe["inputs"].items():
        needed = ing_quantity * crafting_factor
        # Recursively find requirements for the ingredient
        sub_requirements = compute_requirements(ingredient, needed, recipes)
        # Add the sub-requirements to the main list
        for sub_ing, sub_qty in sub_requirements.items():
            requirements[sub_ing] = requirements.get(sub_ing, 0) + sub_qty

    return requirements

def compute_layered_requirements(layers: list[dict], final_quantity: float) -> list[dict]:
    """
    Compute requirements using integer (ceiling) math at each layer.
    Processes layers backward, calculating crafts needed and propagating ingredient requirements.
    Returns a list of computed layer dictionaries (in processing order).
    """
    n = len(layers)
    # required_amount[i] stores how much of the product of layer i is needed by subsequent layers/final output
    required_amount = {layers[i]["name"]: 0.0 for i in range(n)}
    # The final product's requirement is the user's desired quantity
    final_product_name = layers[-1]["name"]
    required_amount[final_product_name] = final_quantity

    computed_layers = [None] * n # To store results for each layer

    # Process layers from last to first (n-1 down to 0)
    for i in range(n - 1, -1, -1):
        layer = layers[i]
        layer_name = layer["name"]
        layer_output_qty = layer["output"]
        total_required_for_this_layer = required_amount[layer_name]

        if layer_output_qty <= 0:
             print(f"Warning: Layer {i+1} ('{layer_name}') has non-positive output ({layer_output_qty}). Skipping calculation for this layer's inputs.")
             computed_layers[i] = {
                 "layer": i + 1, "name": layer_name, "crafts": 0,
                 "produced": 0, "requirements": {}, "error": "Zero/Negative Output"
             }
             continue # Skip input calculation for this broken layer

        # Calculate the number of crafts needed (ceiling division)
        crafts_needed = math.ceil(total_required_for_this_layer / layer_output_qty)
        # Calculate the actual amount produced by these crafts
        actual_produced = crafts_needed * layer_output_qty

        # Calculate the input ingredients needed for these crafts
        layer_input_requirements = {}
        for ingredient, ing_quantity in layer["inputs"].items():
            layer_input_requirements[ingredient] = crafts_needed * ing_quantity

        # Store the computed information for this layer
        computed_layers[i] = {
            "layer": i + 1,
            "name": layer_name,
            "crafts": crafts_needed,
            "produced": actual_produced, # Amount actually made (>= required amount)
            "requirements": layer_input_requirements
        }

        # Propagate the requirements for this layer's inputs to earlier layers
        for ingredient, required_qty in layer_input_requirements.items():
            # Check if this ingredient is produced by any *earlier* layer
            for j in range(i): # Only look at layers 0 to i-1
                if layers[j]["name"] == ingredient:
                    required_amount[ingredient] += required_qty
                    break # Stop checking once found

    # Filter out potential None entries if errors occurred, though should be handled
    return [comp for comp in computed_layers if comp is not None]


def advanced_crafting(recipes: dict, config: dict):
    """Calculates requirements for simple or multi-layered recipes."""
    print("\n--- Advanced Crafting Helper ---")
    if not recipes:
        print("No recipes loaded. Add recipes using option 5.")
        return

    print("Available recipes:")
    for name, data in recipes.items():
        try:
            if "layers" in data:
                # Display multi-layer recipe structure
                layers = data['layers']
                final_product = layers[-1]['name']
                first_inputs = layers[0]['inputs']
                first_input_str = " + ".join(f"{amt} {ing}" for ing, amt in first_inputs.items())
                print(f"  {name} (multi-layer): ... -> {data['layers'][-1]['output']} {final_product}(s)")
            elif "inputs" in data and "output" in data:
                # Display simple recipe structure
                inputs_str = " + ".join(f"{amt} {ing}" for ing, amt in data["inputs"].items())
                print(f"  {name}: {inputs_str} -> {data['output']} {name}(s)")
            else:
                print(f"  {name}: (Invalid format in recipes file)")
        except Exception as e:
             print(f"  {name}: (Error displaying recipe - {e})") # Catch errors during display

    target = input("\nEnter the target item name: ").strip().lower()
    if target not in recipes:
        print(f"Error: Recipe for '{target}' not found.")
        return

    suffixes = get_suffixes(config)
    prompt = (f"Enter the desired amount (e.g., '100', '5{suffixes['stack']}', "
              f"'2{suffixes['shulker']}'): ")
    quantity_input = input(prompt).strip()

    # Determine container override preference for display
    container_pref = config.get("container_preference", "sb")
    container_override = container_pref # Default
    if quantity_input.lower().endswith(suffixes['double_chest']):
        container_override = "dc"
    elif quantity_input.lower().endswith(suffixes['shulker']):
        container_override = "sb"

    try:
        quantity = parse_combined_amount(quantity_input, config)
        if quantity <= 0:
             print("Error: Desired quantity must be positive.")
             return
    except ValueError as e:
        print(f"Error: {e}")
        return

    auto_conv = config.get("auto_conversion", True)
    recipe_data = recipes[target]

    print("-" * 20) # Separator

    if "layers" in recipe_data:
        # --- Multi-Layer Recipe Calculation ---
        layers = recipe_data["layers"]
        try:
            layered_reqs_computed = compute_layered_requirements(layers, quantity)

            print(f"To craft {format_breakdown(quantity, auto_conv, container_override)} of '{target}':")

            # Display layer-by-layer breakdown
            base_materials = {} # Collect materials not produced by any layer
            for comp in layered_reqs_computed:
                print(f"\nLayer {comp['layer']} ({comp['name']}):")
                print(f"  Crafts needed: {comp['crafts']} (produces {format_breakdown(comp['produced'], auto_conv, container_override)})")
                if "error" in comp:
                    print(f"  Error calculating inputs: {comp['error']}")
                    continue

                print("  Inputs required for this layer:")
                for ing, amt in comp["requirements"].items():
                     # Check if this ingredient is produced by an earlier layer
                     is_intermediate = any(layer["name"] == ing for layer in layers[:comp['layer']-1])
                     if not is_intermediate:
                         # If not produced earlier, it's a base material for this path
                         base_materials[ing] = base_materials.get(ing, 0) + amt
                         # Display requirement for this layer
                         print(f"    - {ing}: {format_breakdown(amt, auto_conv, container_override)}")
                     else:
                          # If intermediate, just note it's needed (amount comes from earlier layer)
                           print(f"    - {ing}: (Produced in Layer {next(idx+1 for idx, l in enumerate(layers) if l['name'] == ing)})")


            # Display final summary of base materials
            print("\n--- Total Base Materials Required ---")
            if not base_materials:
                 print("  (No base materials identified - check layer inputs)")
            else:
                for ing, amt in sorted(base_materials.items()): # Sort for consistent output
                    print(f"  {ing}: {format_breakdown(amt, auto_conv, container_override)}")

        except Exception as e:
            print(f"\nAn error occurred during layered calculation: {e}")
            # Provide more context if possible, e.g., which layer failed if traceable

    else:
        # --- Simple Recipe Calculation (Recursive) ---
        try:
            base_requirements = compute_requirements(target, quantity, recipes)
            print(f"To craft {format_breakdown(quantity, auto_conv, container_override)} of '{target}', you need:")
            if not base_requirements:
                 print("  (No requirements calculated - check recipe or inputs)")
            else:
                for ingredient, amount in sorted(base_requirements.items()): # Sort for consistency
                    # Use ceiling for final display of base items
                    print(f"  {ingredient}: {format_breakdown(amount, auto_conv, container_override)}")
        except Exception as e:
            print(f"\nAn error occurred during simple calculation: {e}")

    print("-" * 20 + "\n") # Separator


#######################
# Add Recipe Function
#######################

def add_recipe(recipes: dict):
    """Guides the user to add a new simple or multi-layered recipe."""
    print("\n--- Add a New Recipe ---")
    output_item = input("Enter the FINAL output item name (e.g., 'iron_ingot', 'hopper'): ").strip().lower()
    if not output_item:
        print("Error: Output item name cannot be empty.")
        return
    if output_item in recipes:
        overwrite = input(f"Recipe for '{output_item}' already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Recipe addition cancelled.")
            return

    try:
        layers_count_str = input("How many crafting steps (layers) does this recipe have? (Enter 1 for simple crafting like Plank -> Chest): ").strip()
        layers_count = int(layers_count_str)
        if layers_count <= 0:
            print("Error: Number of layers must be at least 1.")
            return
    except ValueError:
        print("Error: Invalid number entered for layers.")
        return

    new_recipe_data = {}
    try: # Wrap the whole input process for better error handling
        if layers_count == 1:
            # --- Simple Recipe Input ---
            print(f"\n--- Defining Simple Recipe for '{output_item}' ---")
            output_qty_str = input(f"Enter the quantity of '{output_item}' produced per craft: ").strip()
            output_qty = float(output_qty_str)
            if output_qty <= 0:
                print("Error: Output quantity must be positive.")
                return

            inputs_raw = input("Enter input ingredients (format: ingredient:quantity, ingredient:quantity, ... e.g., plank:8): ").strip()
            inputs = {}
            if not inputs_raw:
                 print("Error: No ingredients entered.")
                 return

            for pair in inputs_raw.split(","):
                pair = pair.strip()
                if not pair: continue # Skip empty parts
                if ':' not in pair:
                    raise ValueError(f"Invalid input format '{pair}'. Use 'ingredient:quantity'.")
                ing, qty_str = pair.split(":", 1)
                ing = ing.strip().lower()
                qty = float(qty_str.strip())
                if not ing: raise ValueError("Ingredient name cannot be empty.")
                if qty <= 0: raise ValueError(f"Quantity for '{ing}' must be positive.")
                inputs[ing] = qty

            if not inputs:
                print("Error: No valid ingredients were parsed.")
                return
            new_recipe_data = {"inputs": inputs, "output": output_qty}

        else:
            # --- Multi-Layered Recipe Input ---
            print(f"\n--- Defining {layers_count}-Layer Recipe for '{output_item}' ---")
            layers = []
            produced_items = set() # Keep track of items produced in earlier layers
            for i in range(1, layers_count + 1):
                print(f"\n--- Layer {i} ---")
                is_final_layer = (i == layers_count)
                layer_product_prompt = f"Enter the item produced in this layer"
                if is_final_layer:
                     layer_product_prompt += f" (should be the final item: '{output_item}'): "
                else:
                     layer_product_prompt += f" (e.g., 'stick', 'iron_gear'): "

                layer_name = input(layer_product_prompt).strip().lower()
                if not layer_name: raise ValueError("Layer product name cannot be empty.")
                if is_final_layer and layer_name != output_item:
                     print(f"Warning: Final layer product '{layer_name}' does not match overall recipe name '{output_item}'. Using '{layer_name}'.")
                     # Or force match: layer_name = output_item

                if layer_name in produced_items:
                     print(f"Warning: Item '{layer_name}' was already produced in an earlier layer. Ensure this is intended.")

                layer_output_qty_str = input(f"Enter the quantity of '{layer_name}' produced per craft in this layer: ").strip()
                layer_output_qty = float(layer_output_qty_str)
                if layer_output_qty <= 0: raise ValueError("Layer output quantity must be positive.")

                inputs_raw = input(f"Enter INPUT ingredients for Layer {i} (format: ing:qty, ing:qty): ").strip()
                inputs = {}
                if not inputs_raw: raise ValueError(f"No ingredients entered for Layer {i}.")

                for pair in inputs_raw.split(","):
                     pair = pair.strip()
                     if not pair: continue
                     if ':' not in pair: raise ValueError(f"Invalid input format '{pair}'. Use 'ingredient:quantity'.")
                     ing, qty_str = pair.split(":", 1)
                     ing = ing.strip().lower()
                     qty = float(qty_str.strip())
                     if not ing: raise ValueError("Ingredient name cannot be empty.")
                     if qty <= 0: raise ValueError(f"Quantity for '{ing}' must be positive.")
                     # Check if input is the product of this *same* layer - invalid
                     if ing == layer_name: raise ValueError(f"Ingredient '{ing}' cannot be the same as the product of the same layer.")
                     inputs[ing] = qty

                if not inputs: raise ValueError(f"No valid ingredients were parsed for Layer {i}.")

                layers.append({"name": layer_name, "inputs": inputs, "output": layer_output_qty})
                produced_items.add(layer_name) # Add this layer's product to known produced items

            # Final check: ensure the last layer's name matches the overall recipe name (or update recipe name)
            if layers[-1]["name"] != output_item:
                 print(f"Adjusting recipe name to match final layer product: '{layers[-1]['name']}'")
                 output_item = layers[-1]['name'] # Update the key under which recipe is saved

            new_recipe_data = {"layers": layers}

        # --- Save the new/updated recipe ---
        recipes[output_item] = new_recipe_data
        save_recipes(recipes) # Call save_recipes without the unused config param
        print(f"\nRecipe for '{output_item}' added/updated successfully.")

    except ValueError as e:
        print(f"\nError adding recipe: {e}. Aborting.")
    except Exception as e: # Catch other potential issues
        print(f"\nAn unexpected error occurred: {e}. Aborting recipe addition.")


#######################
# Overworld/Nether Converter
#######################

def convert_coordinates():
    """Converts coordinates between Overworld and Nether."""
    print("\n--- Overworld <-> Nether Converter ---")
    print("Select conversion direction:")
    print("1. Overworld to Nether")
    print("2. Nether to Overworld")
    choice = input("Enter 1 or 2: ").strip()

    try:
        x_str = input("Enter X coordinate: ").strip()
        y_str = input("Enter Y coordinate: ").strip()
        z_str = input("Enter Z coordinate: ").strip()
        x = float(x_str)
        y = float(y_str) # Y coordinate is not converted
        z = float(z_str)
    except ValueError:
        print("Error: Invalid coordinate input. Please enter numbers.")
        return

    if choice == "1":
        # Overworld to Nether: Divide X and Z by 8
        conv_x = x / 8
        conv_z = z / 8
        print(f"\nOverworld ({x:.2f}, {y:.2f}, {z:.2f})")
        print(f"  -> Nether ({conv_x:.2f}, {y:.2f}, {conv_z:.2f})")
    elif choice == "2":
        # Nether to Overworld: Multiply X and Z by 8
        conv_x = x * 8
        conv_z = z * 8
        print(f"\nNether ({x:.2f}, {y:.2f}, {z:.2f})")
        print(f"  -> Overworld ({conv_x:.2f}, {y:.2f}, {conv_z:.2f})")
    else:
        print("Error: Invalid choice. Please select 1 or 2.")

#######################
# Config Menu
#######################

def config_menu(config: dict):
    """Displays menu for configuring script settings."""
    while True:
        print("\n--- Configuration Menu ---")
        current_suffixes = get_suffixes(config) # Get current or default suffixes
        print(f"1. Toggle Auto Conversion       (Currently: {'ON' if config.get('auto_conversion', True) else 'OFF'})")
        print(f"2. Change Suffixes              (Current: Stack='{current_suffixes['stack']}', Shulker='{current_suffixes['shulker']}', DC='{current_suffixes['double_chest']}')")
        print(f"3. Change Default Container Pref(Currently: '{config.get('container_preference', 'sb')}' - used for formatting output)")
        print("4. Reset Suffixes to Default")
        print("5. Back to Main Menu")

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            config["auto_conversion"] = not config.get("auto_conversion", True)
            print("Auto conversion toggled", "ON" if config["auto_conversion"] else "OFF")
            save_config(config)
        elif choice == "2":
            print("Enter new suffixes (leave blank to keep current):")
            new_stack = input(f"  Suffix for Stacks (current: '{current_suffixes['stack']}'): ").strip()
            new_shulker = input(f"  Suffix for Shulker Boxes (current: '{current_suffixes['shulker']}'): ").strip()
            new_dc = input(f"  Suffix for Double Chests (current: '{current_suffixes['double_chest']}'): ").strip()

            # Ensure suffixes dict exists
            if "suffixes" not in config:
                config["suffixes"] = {}

            if new_stack: config["suffixes"]["stack"] = new_stack
            if new_shulker: config["suffixes"]["shulker"] = new_shulker
            if new_dc: config["suffixes"]["double_chest"] = new_dc

            # Validate that suffixes are distinct (optional but recommended)
            updated_suffixes = get_suffixes(config)
            suffix_values = list(updated_suffixes.values())
            if len(suffix_values) != len(set(suffix_values)):
                 print("Warning: Suffixes are not unique! This may cause parsing issues.")

            print("Suffixes updated.")
            save_config(config)
        elif choice == "3":
            pref = input("Enter default container preference ('sb' for Shulker, 'dc' for Double Chest): ").strip().lower()
            if pref in ["sb", "dc"]:
                config["container_preference"] = pref
                print("Default container preference updated.")
                save_config(config)
            else:
                print("Invalid preference. Please enter 'sb' or 'dc'.")
        elif choice == "4":
            config["suffixes"] = DEFAULT_CONFIG["suffixes"].copy()
            print("Suffixes reset to default values.")
            save_config(config)
        elif choice == "5":
            break
        else:
            print("Invalid option. Please choose from 1 to 5.")

#######################
# Main Menu
#######################

def display_main_menu():
    """Prints the main menu options."""
    print("\n--- Minecraft Calculator Helper ---")
    print("1. Convert Items/Containers to Stacks/Items")
    print("2. Convert Items/Stacks to Container Breakdown")
    print("3. Simple Crafting Helper (Ratio-based)")
    print("4. Advanced Crafting Helper (Recipe-based)")
    print("5. Add/Edit Recipe")
    print("6. Overworld <-> Nether Coordinate Converter")
    print("7. Configure Settings")
    print("8. Exit")
    print("-------------------------------------")

def main():
    """Main function to run the calculator."""
    config = load_config()
    recipes = load_recipes()

    # Initial check for recipes file - inform user if empty
    if not recipes and not RECIPES_FILE.exists():
         print(f"Welcome! No recipes found ({RECIPES_FILE}).")
         print("Use option '5' to add your first recipe.")
    elif not recipes:
         print(f"Warning: Recipe file ({RECIPES_FILE}) loaded but contains no recipes or is invalid.")
         print("Use option '5' to add recipes.")


    while True:
        display_main_menu()
        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            convert_items_to_stacks(config)
        elif choice == "2":
            convert_stacks_to_containers(config)
        elif choice == "3":
            crafting_helper(config)
        elif choice == "4":
            advanced_crafting(recipes, config) # Pass loaded recipes
        elif choice == "5":
            add_recipe(recipes) # Modifies recipes dict in-place and saves
        elif choice == "6":
            convert_coordinates()
        elif choice == "7":
            config_menu(config) # Modifies config dict in-place and saves
        elif choice == "8":
            print("\nExiting. Happy Crafting!")
            break
        else:
            print("Invalid option. Please choose from 1 to 8.")

        input("\nPress Enter to continue...") # Pause screen

if __name__ == '__main__':
    main()
