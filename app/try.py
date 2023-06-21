import yaml

# Load the YAML file
with open('/home/ajay/Animations/AnimatedDrawings/config/retarget/fair1_ppf_duo1.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

# Update the char_starting_location
DIM = [0.6, 0, -0.6]  # New values for char_starting_location
data['char_starting_location'] = DIM

# Save the updated YAML file
with open('updated_yaml_file.yaml', 'w') as file:
    yaml.dump(data, file)