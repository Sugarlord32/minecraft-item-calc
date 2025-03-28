#!/usr/bin/env python3
import os
import json
import math

# Constants for conversions
BASE_STACK_SIZE = 64
SHULKER_STACKS = 27  # Number of stacks per shulker box
DOUBLE_CHEST_STACKS = 54  # Number of stacks per double chest
RECIPES_FILE = "recipes.json"

def load_recipes():
    """Load recipes from a JSON file if it exists, otherwise return default recipes."""
    default_recipes = {
        "plank": {"inputs": {"log": 1}, "output": 4},
        "chest": {"inputs": {"plank": 8}, "output": 1},
        "hopper": {"inputs": {"chest": 1, "iron": 5}, "output": 1},
        "minecart": {"inputs": {"iron": 5}, "output": 1},
        "minecart_hopper": {"inputs": {"minecart": 1, "hopper": 1}, "output": 1}
    }
    if os.path.exists(RECIPES_FILE):
        try:
            with open(RECIPES_FILE, "r") as f:
                recipes = json.load(f)
            return recipes
        except Exception as e:
            print("Error loading recipes file:", e)
            print("Using default recipes.")
    return default_recipes

def save_recipes(recipes):
    """Save the recipes dictionary to a JSON file."""
    try:
        with open(RECIPES_FILE, "w") as f:
            json.dump(recipes, f, indent=4)
    except Exception as e:
        print("Error saving recipes:", e)

def parse_single_amount(s):
    """
    Parse a string amount that can have suffixes:
      - No suffix: items (e.g. "100" -> 100 items)
      - 's' suffix: stacks (e.g. "5s" -> 5 * 64 items)
      - 'sb' suffix: shulker boxes (e.g. "2sb" -> 2 * 27 * 64 items)
      - 'dc' suffix: double chests (e.g. "1dc" -> 1 * 54 * 64 items)
    Returns a float representing the number of items.
    """
    s = s.strip().lower()
    if s.endswith("sb"):
        try:
            num = float(s[:-2])
            return num * BASE_STACK_SIZE * SHULKER_STACKS
        except ValueError:
            raise ValueError("Invalid number for shulker boxes.")
    elif s.endswith("dc"):
        try:
            num = float(s[:-2])
            return num * BASE_STACK_SIZE * DOUBLE_CHEST_STACKS
        except ValueError:
            raise ValueError("Invalid number for double chests.")
    elif s.endswith("s"):
        try:
            num = float(s[:-1])
            return num * BASE_STACK_SIZE
        except ValueError:
            raise ValueError("Invalid number for stacks.")
    else:
        try:
            return float(s)
        except ValueError:
            raise ValueError("Invalid amount format.")

def parse_combined_amount(s):
    """
    Parse an input string that may contain multiple amounts separated by commas,
    e.g. "30s, 15" means 30 stacks + 15 items.
    Returns the total as a float (in items).
    """
    parts = s.split(",")
    total = 0.0
    for part in parts:
        total += parse_single_amount(part)
    return total

def breakdown_to_stacks(total_items):
    """
    Breaks total_items (an integer number of items) into full stacks and remaining items.
    Returns a tuple: (stacks, items)
    """
    stacks = total_items // BASE_STACK_SIZE
    items = total_items % BASE_STACK_SIZE
    return int(stacks), int(items)

def breakdown_to_shulkers(total_items):
    """
    Breaks total_items into shulker boxes, remaining stacks, and remaining items.
    """
    stacks, items = breakdown_to_stacks(total_items)
    shulkers = stacks // SHULKER_STACKS
    rem_stacks = stacks % SHULKER_STACKS
    return int(shulkers), int(rem_stacks), int(items)

def breakdown_to_double_chests(total_items):
    """
    Breaks total_items into double chests, remaining stacks, and remaining items.
    """
    stacks, items = breakdown_to_stacks(total_items)
    dcs = stacks // DOUBLE_CHEST_STACKS
    rem_stacks = stacks % DOUBLE_CHEST_STACKS
    return int(dcs), int(rem_stacks), int(items)

def format_breakdown(total_items):
    """
    Formats total_items into a hierarchical breakdown.
    The hierarchy is: double chests > shulker boxes > stacks > items.
    Only levels with at least 1 unit are displayed.
    """
    total_items = int(total_items)
    stacks, items = breakdown_to_stacks(total_items)
    if stacks >= DOUBLE_CHEST_STACKS:
        dcs, rem_stacks, rem_items = breakdown_to_double_chests(total_items)
        # For the remaining stacks, try to break into shulkers if possible.
        if rem_stacks >= SHULKER_STACKS:
            shulkers, rem_stacks2, rem_items = breakdown_to_shulkers(rem_stacks * BASE_STACK_SIZE + rem_items)
            parts = []
            if dcs:
                parts.append(f"{dcs} double chest(s)")
            if shulkers:
                parts.append(f"{shulkers} shulker box(es)")
            if rem_stacks2:
                parts.append(f"{rem_stacks2} stack(s)")
            if rem_items:
                parts.append(f"{rem_items} item(s)")
            return ", ".join(parts)
        else:
            parts = []
            if dcs:
                parts.append(f"{dcs} double chest(s)")
            if rem_stacks:
                parts.append(f"{rem_stacks} stack(s)")
            if rem_items:
                parts.append(f"{rem_items} item(s)")
            return ", ".join(parts)
    elif stacks >= SHULKER_STACKS:
        shulkers, rem_stacks, rem_items = breakdown_to_shulkers(total_items)
        parts = []
        if shulkers:
            parts.append(f"{shulkers} shulker box(es)")
        if rem_stacks:
            parts.append(f"{rem_stacks} stack(s)")
        if rem_items:
            parts.append(f"{rem_items} item(s)")
        return ", ".join(parts)
    elif stacks >= 1:
        stacks, items = breakdown_to_stacks(total_items)
        parts = []
        if stacks:
            parts.append(f"{stacks} stack(s)")
        if items:
            parts.append(f"{items} item(s)")
        return ", ".join(parts)
    else:
        return f"{total_items} item(s)"

# Simple Conversion Helpers

def convert_items_to_stacks():
    """Converts a number of items into full stacks and remainder.
       You can input using suffixes or combined inputs.
    """
    try:
        raw = input("Enter the total amount (e.g. '100', '5s', '2sb', '1dc', or combined '30s, 15'): ")
        total_items = int(parse_combined_amount(raw))
        stacks, items = breakdown_to_stacks(total_items)
        print(f"{total_items} item(s) = {stacks} full stack(s) and {items} item(s) remaining.")
    except ValueError as e:
        print(e)

def convert_stacks_to_containers():
    """Converts a number of items (entered with any suffixes/combined) into:
       - A shulker box breakdown: shulker boxes, stacks, and items.
       - A double chest breakdown: double chests, stacks, and items.
    """
    try:
        raw = input("Enter the amount (e.g. '10', '3s', '1sb', '1dc', or '10s, 5'): ")
        total_items = int(parse_combined_amount(raw))
        # Breakdown into full stacks & items (for reference)
        stacks, items = breakdown_to_stacks(total_items)
        print(f"Total: {stacks} stack(s) and {items} item(s)")
        # Shulker box breakdown
        shulkers, rem_stacks, rem_items = breakdown_to_shulkers(total_items)
        print(f"As shulker boxes: {shulkers} shulker box(es), {rem_stacks} stack(s) and {rem_items} item(s) remaining.")
        # Double chest breakdown
        dcs, rem_stacks_dc, rem_items_dc = breakdown_to_double_chests(total_items)
        print(f"As double chests: {dcs} double chest(s), {rem_stacks_dc} stack(s) and {rem_items_dc} item(s) remaining.")
    except ValueError as e:
        print(e)

# Simple Crafting Helper

def crafting_helper():
    """
    Provides a simple crafting calculation.
    You define a recipe ratio and then either:
      1. Calculate required input items for a desired output amount.
      2. Calculate obtainable outputs from available input items.
    The result is displayed using a breakdown (stacks and items, etc.).
    """
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

        if choice == "1":
            desired_output = float(input("Enter the desired number of outputs: "))
            required_inputs = (input_required / output_result) * desired_output
            print(f"You need approximately {int(round(required_inputs))} input item(s) to produce {int(round(desired_output))} output(s).")
            print("That is:", format_breakdown(required_inputs))
        elif choice == "2":
            available_inputs = float(input("Enter the number of available input items: "))
            produced_outputs = (output_result / input_required) * available_inputs
            print(f"You can produce approximately {int(round(produced_outputs))} output item(s) with {int(round(available_inputs))} input(s).")
            print("That is:", format_breakdown(produced_outputs))
        else:
            print("Invalid choice. Please select either 1 or 2.")
    except ValueError:
        print("Invalid input. Please enter numerical values.")

# Advanced Crafting Helper with layered recipes

def compute_requirements(item, quantity, recipes):
    """
    Recursively computes the base (non-craftable) ingredient requirements
    for a given item and quantity.
    If an ingredient does not appear in recipes, it is assumed to be base.
    Returns a dictionary mapping ingredient names to required amounts (in items).
    """
    if item not in recipes:
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

def advanced_crafting(recipes):
    """
    Advanced crafting helper for layered and multiple recipes.
    It displays available recipes, then asks for a target item and a desired amount.
    It computes and displays the required base ingredients,
    with each amount given in a breakdown (double chests, shulker boxes, stacks and items).
    """
    print("\n--- Advanced Crafting Helper ---")
    print("Available recipes:")
    for k, v in recipes.items():
        inputs_str = " + ".join(f"{amt} {ing}" for ing, amt in v["inputs"].items())
        print(f"  {k}: {inputs_str} -> {v['output']} {k}(s)")
        
    target = input("Enter the target item: ").strip().lower()
    quantity_input = input("Enter the desired amount (supports combined amounts, e.g. '30s, 15'): ").strip()
    try:
        quantity = int(parse_combined_amount(quantity_input))
    except ValueError as e:
        print(e)
        return
    
    requirements = compute_requirements(target, quantity, recipes)
    print(f"\nTo craft {format_breakdown(quantity)} of '{target}', you need:")
    for ing, amt in requirements.items():
        # Only display levels if the highest container is at least 1
        print(f"  {ing}: {format_breakdown(amt)}")
    print()

def add_recipe(recipes):
    """
    Allows the user to add a new recipe to the recipes dictionary.
    The user inputs:
      - The name of the output item.
      - The quantity produced.
      - The input ingredients as a comma-separated list of 'ingredient: quantity' pairs.
    The new recipe is added and the updated recipes are saved.
    """
    print("\n--- Add a New Recipe ---")
    output_item = input("Enter the output item name: ").strip().lower()
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
    save_recipes(recipes)
    print(f"Recipe for '{output_item}' added successfully.\n")

def main():
    recipes = load_recipes()
    while True:
        print("\nMinecraft Calculator Helper")
        print("1. Convert items to stacks")
        print("2. Convert stacks to containers (shulkers/double chests)")
        print("3. Simple Crafting Helper (single recipe ratio)")
        print("4. Advanced Crafting Helper (layered recipes)")
        print("5. Add a new recipe")
        print("6. Exit")
        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            convert_items_to_stacks()
        elif choice == "2":
            convert_stacks_to_containers()
        elif choice == "3":
            crafting_helper()
        elif choice == "4":
            advanced_crafting(recipes)
        elif choice == "5":
            add_recipe(recipes)
        elif choice == "6":
            print("Exiting. Happy crafting!")
            break
        else:
            print("Invalid option. Please choose from 1 to 6.")

if __name__ == '__main__':
    main()
