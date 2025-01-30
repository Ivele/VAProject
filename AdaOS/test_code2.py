import os

name = "chicha"

with open(f'tests/{name}.yaml', 'w') as file:
    pass

def add_nlu_and_intent_to_yaml(directory, intent_name, new_examples):
    for filename in os.listdir(directory):
        if filename.endswith("chicha.yml") or filename.endswith("chicha.yaml"):
            filepath = os.path.join(directory, filename)
            
            # Read the file
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Check if `nlu:` already exists at the top
            if not content.startswith("nlu:"):
                # Add the `nlu:` block at the beginning if it's missing
                content = "nlu:\n" + content
            
            # Create the new intent and examples block
            new_intent_block = f"- intent: {intent_name}\n  examples: |\n"
            for example in new_examples:
                new_intent_block += f"      - {example}\n"
            
            # Add the new intent block right after `nlu:`
            content = content.replace("nlu:\n", f"nlu:\n{new_intent_block}", 1)

            # Write the updated content back to the file
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"Added new intent '{intent_name}' under 'nlu:' in: {filename}")

# Directory containing your YAML files
yaml_directory = "tests"  # Replace with your directory path

# New intent and the examples to add
new_intent = "greet_123"
new_training_examples = [
    "govno",
    "yzbek",
    "on?"
]

# Run the script
add_nlu_and_intent_to_yaml(yaml_directory, new_intent, new_training_examples)