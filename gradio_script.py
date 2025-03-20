import gradio as gr
import os
import subprocess


# Get the names of folders in a directory
def get_folder_names(directory):
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

# Get the names of files in a directory
def get_file_names(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


# Function to write MVC
def writeMVC(character_folder, motion_file, target_file, export_radio, output_path, video_path):
    # Sets the video format to None, MP4 or Gif
    export_format = ""
    if export_radio == 1:
        export_format = """
controller:
  MODE: video_render
  OUTPUT_VIDEO_PATH: {output_video_path}/video.mp4
  OUTPUT_VIDEO_CODEC: avc1
""".format(
        output_video_path=video_path
    )
    elif export_radio == 2:
        export_format = """
controller:
  MODE: video_render
  OUTPUT_VIDEO_PATH: {output_video_path}/video.gif
""".format(
        output_video_path=video_path
    )

    updated_config = export_format + """
scene:
  ANIMATED_CHARACTERS:
    - character_cfg: examples/characters/{character_cfg}/char_cfg.yaml
      motion_cfg: examples/config/motion/{motion_cfg}
      retarget_cfg: examples/config/retarget/{retarget_cfg}
""".format(
        character_cfg=character_folder,
        motion_cfg=motion_file,
        retarget_cfg=target_file,
    )

    config_filename = os.path.join(output_path, "custom_config.yaml")
    with open(config_filename, "w") as f:
        f.write(updated_config)


    # Run the script to generate
    cmd = ['python', '-c', 
"""
from animated_drawings import render
render.start('{}')
""".format(config_filename)]

    subprocess.run(cmd)


    # If the video was generated, return it.
    if export_radio == 1:
        video_path = os.path.join(video_path, "video.mp4")
        if os.path.exists(video_path):
            return video_path

    return


# Function to refresh dropdown options
def refresh_options(directory):
    character_folder_path = os.path.join(directory, 'examples/characters')
    motion_file_path = os.path.join(directory, 'examples/config/motion')
    target_file_path = os.path.join(directory, 'examples/config/retarget')

    character_choices = get_folder_names(character_folder_path)
    motion_choices = get_file_names(motion_file_path)
    target_choices = get_file_names(target_file_path)

    # Debug
    # print(character_choices)
    # print(motion_choices)
    # print(target_choices)

    return character_dropdown.update(choices=character_choices), motion_dropdown.update(choices=motion_choices), target_dropdown.update(choices=target_choices), gr.update(visible=True)


# Variables for Gradio
character_choices = []
motion_choices = []
target_choices = []


# Gradio UI
with gr.Blocks() as iface:
    with gr.Row():
        output_video = gr.Video(label="Animation")

    with gr.Row():
        directory_path = gr.Textbox(label="Directory", info="/Users/.../AnimatedDrawings")
        output_path = gr.Textbox(label="Output Path Yaml", info="/Users/.../your_yaml_folder")


    with gr.Row():
        character_dropdown = gr.Dropdown(choices=character_choices, label="Character")
        motion_dropdown = gr.Dropdown(choices=motion_choices, label="Motion")
        target_dropdown = gr.Dropdown(choices=target_choices, label="Target")
        refresh_button = gr.Button("Refresh")
    
    with gr.Row():
        export_radio = gr.Radio(["None", "MP4", "GIF"], type="index", label="Export", info="Choose the export format")
        video_path = gr.Textbox(label="Output Path Video", info="/Users/.../your_video_folder")
        
    
    with gr.Row():
        submit = gr.Button("Export")

    # Gradio Actions
    submit.click(writeMVC, [character_dropdown, motion_dropdown, target_dropdown, export_radio, directory_path, video_path], [output_video])
    refresh_button.click(refresh_options, directory_path, [character_dropdown, motion_dropdown, target_dropdown]) #, [character_folder, motion_file, target_file]

# Launch Gradio as Web UI
iface.launch()




# Examples from the provided yaml files
"""
# Define the output format GIF or MP4
controller:
  MODE: video_render
  OUTPUT_VIDEO_PATH: ./video.mp4
  OUTPUT_VIDEO_CODEC: avc1

controller:
  MODE: video_render
  OUTPUT_VIDEO_PATH: ./video.gif

# Define the characters, motion and target
  scene:
  ANIMATED_CHARACTERS:
    - character_cfg: examples/characters/char1/char_cfg.yaml
      motion_cfg: examples/config/motion/dab.yaml
      retarget_cfg: examples/config/retarget/fair1_ppf_duo1.yaml

# Define View and Background
view:
  CAMERA_POS: [0.1, 1.3, 2.7]
  WINDOW_DIMENSIONS: [300, 400]
  BACKGROUND_IMAGE: examples/characters/char4/background.png

view:
  CAMERA_POS: [2.0, 0.7, 8.0]
  CAMERA_FWD: [0.0, 0.5, 8.0]
"""