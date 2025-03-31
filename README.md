# Minecraft Item Calc
(calc is slang for calculator)
(README done with AI assistance for readability, reformatting, clarification and spell-checking)

A versatile command-line Python tool designed to simplify various calculations frequently encountered in Minecraft, particularly useful for technical players or large-scale projects.

**(Note: This project, including parts of the script and this README, was developed with assistance from an AI language model.)**

## Features

*   **Item/Container Conversion:**
    *   Convert raw item counts into stacks and remaining items.
    *   Break down large item quantities into the equivalent number of Shulker Boxes or Double Chests, plus remaining stacks/items.
    *   Parse flexible input amounts using suffixes (e.g., `100`, `5s`, `2sb`, `1dc`, `10s, 5`).
*   **Crafting Calculation:**
    *   **Simple Mode:** Calculate required inputs or potential outputs based on a simple input:output ratio you provide on the fly.
    *   **Advanced Mode:** Calculate the total base materials needed for complex items using pre-defined recipes stored in `recipes.json`. Supports both simple (single-step) and multi-layered (multi-step) recipes.
*   **Recipe Management:**
    *   Add new crafting recipes (both simple and multi-layered) to your personal `recipes.json` file via an interactive menu.
    *   Recipes are saved persistently.
*   **Coordinate Conversion:**
    *   Quickly convert coordinates between the Overworld and the Nether (dividing/multiplying X and Z by 8).
*   **Configuration:**
    *   Customize unit suffixes (`s`, `sb`, `dc`).
    *   Toggle automatic conversion formatting (show items vs. detailed breakdown).
    *   Set preferred container type (`sb` or `dc`) for formatting output.
    *   Settings are saved persistently in `config.json`.

## Requirements

*   **Python 3:** (Tested with Python 3.6+). No external libraries are needed.

## Installation

1.  Download the `minecalc.py` (or whatever you name the script file) script from this repository.
2.  Place it in a convenient directory on your computer.

## Usage

1.  Open a terminal or command prompt.
2.  Navigate to the directory where you saved the script.
3.  Run the script using Python:
    ```bash
    python minecalc.py
    ```
4.  The script will present a menu with options (1-8). Enter the number corresponding to the action you want to perform.
5.  Follow the on-screen prompts for each feature.
6.  Press Enter after completing an action to return to the main menu (or choose option 8 to exit).

   (You can also just double click the file to open it if you have Python configured that way)

## Configuration (`config.json`)

The script uses a `config.json` file in the same directory to store your preferences. This file is created automatically if it doesn't exist. You can edit it directly (be careful with JSON syntax) or use **Option 7** in the script's menu.

*   `auto_conversion` (boolean): `true` to automatically format large numbers into containers/stacks, `false` to show raw item counts primarily.
*   `suffixes` (object): Defines the short suffixes used for input and recognized in amounts.
    *   `stack`: Suffix for a stack (default: `"s"`).
    *   `shulker`: Suffix for a Shulker Box (default: `"sb"`).
    *   `double_chest`: Suffix for a Double Chest (default: `"dc"`).
*   `container_preference` (string): `"sb"` or `"dc"`. Determines which container type is prioritized when formatting output if `auto_conversion` is `true`.

## Recipes (`recipes.json`)

The script uses a `recipes.json` file to store crafting recipes for the **Advanced Crafting Helper (Option 4)**.

*   **Important:** This file starts **empty** by default! You need to add recipes yourself using **Option 5** in the script.
*   The file structure contains a top-level `"recipes"` key, which holds an object (dictionary) where keys are the lowercase item names (the final product) and values are the recipe definitions.

**Recipe Formats:**

1.  **Simple Recipe:** For single-step crafting.
    ```json
    {
      "recipes": {
        "chest": {
          "inputs": { "plank": 8 },
          "output": 1
        },
        "furnace": {
            "inputs": { "cobblestone": 8 },
            "output": 1
        }
      }
    }
    ```

2.  **Multi-Layered Recipe:** For recipes requiring intermediate crafting steps. The `layers` array is processed *backwards* by the calculator, but should be defined in crafting order. The `name` in each layer defines the item *produced* by that layer. The final layer's `name` should generally match the main recipe key.
    ```json
    {
      "recipes": {
        "hopper": {
          "layers": [
            {
              "name": "plank",
              "inputs": { "log": 1 },
              "output": 4
            },
            {
              "name": "chest",
              "inputs": { "plank": 8 },
              "output": 1
            },
            {
              "name": "hopper",
              "inputs": { "chest": 1, "iron_ingot": 5 },
              "output": 1
            }
          ]
        }
      }
    }
    ```

## Contributing

Bug reports, feature requests, and suggestions are welcome! Please feel free to open an Issue on the GitHub repository. Pull requests are also considered.

Note: Sayori is the best
