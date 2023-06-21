import sys
import yaml
import os
sys.path.insert(0,'./AnimatedDrawings')
sys.path.insert(1,'./examples')
sys.path.insert(2,'./TextExtraction-to-voice')
from examples.image_to_animation import image_to_animation
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from animated_drawings import render
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from moviepy.editor import *
import urllib.request
import uvicorn
from typing import Dict
import json
load_dotenv()
import cloudinary
from get_image import  audio_ocr
from schemas import APIPARAMTERS
cloudinary.config(
  cloud_name = "djvu7apub",
  api_key = "433374637814992",
  api_secret = "cyuhetMn3-yrGgOjJthC9FBy9FY",
  secure = True
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"response": "Service is ready to run"}

async def create_image(api_params : Dict):
    
    data = api_params
    motion = data['motion']
    image = data['image']


    if len(data['image_url']) == 1:
        motion = data['motion'][0]
        image_url = data['image_url'][0]
        char_anno_dir = os.getenv("OUTPUT")
        urllib.request.urlretrieve(image_url, "image.jpg")
        image_path = "image.jpg"
        # img = cv2.imread(image_path)

        if motion == 'dab' or motion == 'jumping' or motion == 'wave_hello':
            print("started")
            try:
                image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion}.yaml", os.getenv('RETARGET'))
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            with open(os.getenv("EXPORT_GIF"), "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            data['scene']['ANIMATED_CHARACTERS'][0]['character_cfg'] = os.getenv("OUTPUT_CHAR_CFG")
            data["scene"]["ANIMATED_CHARACTERS"][0]["motion_cfg"] = f"{os.getenv('MOTION')}/{motion}.yaml"
            data['scene']['ANIMATED_CHARACTERS'][0]['retarget_cfg'] = os.getenv('RETARGET')

            try :
                with open('example.yaml', 'w') as file:
                    yaml.dump(data, file)
                render.start("./example.yaml")
                audio_url = audio_ocr(image_path)

                audio_path = "./audio.wav"
                gif_path = "./vedio.gif"
                audio = AudioFileClip(audio_path)
                if audio.duration < 10:
                    audio.duration = 10
                gif = VideoFileClip(gif_path).set_duration(audio.duration)
                final_clip = CompositeVideoClip([gif.set_audio(audio)])
                output_path = "./file.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            finally:
                upload_result = cloudinary.uploader.upload("./file.mp4", resource_type="auto")
                os.remove("./example.yaml")
                
                os.remove("./vedio.gif")
                os.remove("./audio.wav")
                os.remove("./file.mp4")
        elif motion == 'jesse_dance':
            try:
                image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion}.yaml", os.getenv('RETARGET_JESSE'))
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            with open(os.getenv("EXPORT_GIF"), "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            data['scene']['ANIMATED_CHARACTERS'][0]['character_cfg'] = os.getenv("OUTPUT_CHAR_CFG")
            data["scene"]["ANIMATED_CHARACTERS"][0]["motion_cfg"] = f"{os.getenv('MOTION')}/{motion}.yaml"
            data['scene']['ANIMATED_CHARACTERS'][0]['retarget_cfg'] = os.getenv('RETARGET_JESSE')

            try :
                with open('example.yaml', 'w') as file:
                    yaml.dump(data, file)
                render.start("./example.yaml")

                audio_url = audio_ocr(image_path)
                audio_path = "./audio.wav"
                gif_path = "./vedio.gif"
                audio = AudioFileClip(audio_path)
                if audio.duration < 10:
                    audio.duration = 10
                gif = VideoFileClip(gif_path).set_duration(audio.duration)
                final_clip = CompositeVideoClip([gif.set_audio(audio)])
                output_path = "./file.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            except Exception as e:
                raise e
            finally:
                upload_result = cloudinary.uploader.upload("./file.mp4", resource_type="auto")
                os.remove("./example.yaml")
                
                os.remove("./vedio.gif")
                os.remove("./audio.wav")
                os.remove("./file.mp4")
        elif motion == 'zombie':
            try:
                image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion}.yaml", os.getenv('RETARGET_ZOMBIE'))
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            with open(os.getenv("EXPORT_GIF"), "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            data['scene']['ANIMATED_CHARACTERS'][0]['character_cfg'] = os.getenv("OUTPUT_CHAR_CFG")
            data["scene"]["ANIMATED_CHARACTERS"][0]["motion_cfg"] = f"{os.getenv('MOTION')}/{motion}.yaml"
            data['scene']['ANIMATED_CHARACTERS'][0]['retarget_cfg'] = os.getenv('RETARGET_ZOMBIE')

            try :
                with open('example.yaml', 'w') as file:
                    yaml.dump(data, file)
                render.start("./example.yaml")
                audio_url = audio_ocr(image_path)
                audio_path = "./audio.wav"
                gif_path = "./vedio.gif"
                audio = AudioFileClip(audio_path)
                if audio.duration < 10:
                    audio.duration = 10
                gif = VideoFileClip(gif_path).set_duration(audio.duration)
                final_clip = CompositeVideoClip([gif.set_audio(audio)])
                output_path = "./file.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            except Exception as e:
                raise e
            finally:
                upload_result = cloudinary.uploader.upload("./file.mp4", resource_type="auto")
                os.remove("./example.yaml")
                
                os.remove("./vedio.gif")
                os.remove("./audio.wav")
                os.remove("./file.mp4")
        elif motion == 'jumping_jacks':
            try:
                image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion}.yaml", os.getenv('RETARGET_JACKS'))
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            with open(os.getenv("EXPORT_GIF"), "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            print("start here")

            data['scene']['ANIMATED_CHARACTERS'][0]['character_cfg'] = os.getenv("OUTPUT_CHAR_CFG")
            data["scene"]["ANIMATED_CHARACTERS"][0]["motion_cfg"] = f"{os.getenv('MOTION')}/{motion}.yaml"
            data['scene']['ANIMATED_CHARACTERS'][0]['retarget_cfg'] = os.getenv('RETARGET_JACKS')

            print("End here")

            try :
                with open('example.yaml', 'w') as file:
                    yaml.dump(data, file)
                render.start("./example.yaml")
                audio_url = audio_ocr(image_path)
                audio_path = "./audio.wav"
                gif_path = "./vedio.gif"
                audio = AudioFileClip(audio_path)
                if audio.duration < 10:
                    audio.duration = 10
                gif = VideoFileClip(gif_path).set_duration(audio.duration)
                final_clip = CompositeVideoClip([gif.set_audio(audio)])
                output_path = "./file.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            finally:
                upload_result = cloudinary.uploader.upload("./file.mp4", resource_type="auto")
                os.remove("./example.yaml")
                
                os.remove("./vedio.gif")
                os.remove("./audio.wav")
                os.remove("./file.mp4")
        elif motion == 'Running_Motion':
            try:
                image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion}.yaml", os.getenv('RETARGET_RUNNING'))
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            with open(os.getenv("EXPORT_GIF"), "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            data['scene']['ANIMATED_CHARACTERS'][0]['character_cfg'] = os.getenv("OUTPUT_CHAR_CFG")
            data["scene"]["ANIMATED_CHARACTERS"][0]["motion_cfg"] = f"{os.getenv('MOTION')}/{motion}.yaml"
            data['scene']['ANIMATED_CHARACTERS'][0]['retarget_cfg'] = os.getenv('RETARGET_RUNNING')


            try :
                with open('example.yaml', 'w') as file:
                    yaml.dump(data, file)
                render.start("./example.yaml")
                audio_url = audio_ocr(image_path)
                audio_path = "./audio.wav"
                gif_path = "./vedio.gif"
                audio = AudioFileClip(audio_path)
                if audio.duration < 10:
                    audio.duration = 10
                gif = VideoFileClip(gif_path).set_duration(audio.duration)
                final_clip = CompositeVideoClip([gif.set_audio(audio)])
                output_path = "./file.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            finally:
                upload_result = cloudinary.uploader.upload("./file.mp4", resource_type="auto")
                os.remove("./example.yaml")
                
                os.remove("./vedio.gif")
                os.remove("./audio.wav")
                os.remove("./file.mp4")
        elif motion == 'Running_L_t_R_Motion':
            try:
                print("Running_L_t_R_Motion new wala")
                image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion}.yaml", os.getenv('RUNNING_ABC'))
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            with open(os.getenv("EXPORT_GIF"), "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            data['scene']['ANIMATED_CHARACTERS'][0]['character_cfg'] = os.getenv("OUTPUT_CHAR_CFG")
            data["scene"]["ANIMATED_CHARACTERS"][0]["motion_cfg"] = f"{os.getenv('MOTION')}/{motion}.yaml"
            data['scene']['ANIMATED_CHARACTERS'][0]['retarget_cfg'] = os.getenv('RUNNING_ABC')


            try :
                with open('example.yaml', 'w') as file:
                    yaml.dump(data, file)
                render.start("./example.yaml")
                audio_url = audio_ocr(image_path)
                audio_path = "./audio.wav"
                if audio.duration < 10:
                    audio.duration = 10
                gif_path = "./vedio.gif"
                audio = AudioFileClip(audio_path)
                gif = VideoFileClip(gif_path).set_duration(audio.duration)
                final_clip = CompositeVideoClip([gif.set_audio(audio)])
                output_path = "./file.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
            finally:
                upload_result = cloudinary.uploader.upload("./file.mp4", resource_type="auto")
                os.remove("./example.yaml")
                
                os.remove("./vedio.gif")
                os.remove("./audio.wav")
                os.remove("./file.mp4")
                os.remove("./image.jpg")

        return {
                "status": "success",
                "url": upload_result["secure_url"], 
                "message" : "Successfully created gif"
            }
    
    else:
        # print("We are getting error ")

        try:
            Animated_Characters = []
            urllib.request.urlretrieve(image, "image_path.jpg")
            image = "image_path.jpg"


            if len(data['image_url']) == 2:
                DIM = [-0.5, 0.5, 0.0]
                window = [600, 600]

            else:
                DIM = [-1.0, 1.0, 0.0]
                window = [1500, 800]

            for i, url in enumerate(data['image_url']):
                # path = os.path.join('./output' , str(i))
                # char_anno_dir = os.mkdir(path)
                char_anno_dir = os.path.join('./output' , str(i))
                urllib.request.urlretrieve(url, "image.jpg")
                image_path = "image.jpg"

                if motion[i] == 'dab' or motion[i] == 'jumping' or motion[i] == 'wave_hello':
                    try:
                        with open(os.getenv('RETARGET')) as f:
                            data = yaml.load(f, Loader=yaml.FullLoader)

                        data['char_starting_location'][0] = DIM[0]
                        DIM.remove(data['char_starting_location'][0])
                        with open(os.path.join(f'./newretarget_{str(i)}.yaml'), 'w') as f:
                            yaml.dump(data, f)
                        # print(data['char_starting_location'][0])
                        image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.path.join(f'./newretarget_{str(i)}.yaml'))
                    except Exception as e:
                        return {
                        "status": "error",
                        "message": str(e),
                        "url": None
                    }
                    Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.path.join(f'./newretarget_{str(i)}.yaml')})

                elif motion[i] == 'jesse_dance':
                    try:
                        with open(os.getenv('RETARGET_JESSE')) as f:
                            data = yaml.load(f, Loader=yaml.FullLoader)
                        
                        data['char_starting_location'][0] = DIM[0]
                        DIM.remove(data['char_starting_location'][0])
                        with open(os.path.join(f'./newretarget_{str(i)}.yaml'), 'w') as f:
                            yaml.dump(data, f)
                        image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.path.join(f'./newretarget_{str(i)}.yaml'))
                    except Exception as e:
                        return {
                        "status": "error",
                        "message": str(e),
                        "url": None
                    }
                    Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.path.join(f'./newretarget_{str(i)}.yaml')})
                    

                elif motion[i] == 'zombie':
                    try:
                        with open(os.getenv('RETARGET_ZOMBIE')) as f:
                            data = yaml.load(f, Loader=yaml.FullLoader)
                        data['char_starting_location'][0] = DIM[0]
                        DIM.remove(data['char_starting_location'][0])
                        with open(os.path.join(f'./newretarget_{str(i)}.yaml'), 'w') as f:
                            yaml.dump(data, f)
                        image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.path.join(f'./newretarget_{str(i)}.yaml'))
                    except Exception as e:
                        return {
                        "status": "error",
                        "message": str(e),
                        "url": None
                    }
                    Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.path.join(f'./newretarget_{str(i)}.yaml')})

                elif motion[i] == 'jumping_jacks':
                    try:
                        with open(os.getenv('RETARGET_JACKS')) as f:
                            data = yaml.load(f, Loader=yaml.FullLoader)
                        data['char_starting_location'][0] = DIM[0]
                        DIM.remove(data['char_starting_location'][0])
                        with open(os.path.join(f'./newretarget_{str(i)}.yaml'), 'w') as f:
                            yaml.dump(data, f)
                        image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.path.join(f'./newretarget_{str(i)}.yaml'))
                    except Exception as e:
                        return {
                        "status": "error",
                        "message": str(e),
                        "url": None
                    }
                    Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.path.join(f'./newretarget_{str(i)}.yaml')})

                elif motion[i] == 'Running_Motion':
                    try:
                        with open(os.getenv('RETARGET_RUNNING')) as f:
                            data = yaml.load(f, Loader=yaml.FullLoader)
                        data['char_starting_location'][0] = DIM[0]
                        DIM.remove(data['char_starting_location'][0])
                        with open(os.path.join(f'./newretarget_{str(i)}.yaml'), 'w') as f:
                            yaml.dump(data, f)
                        image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.path.join(f'./newretarget_{str(i)}.yaml'))
                    except Exception as e:
                        return {
                        "status": "error",
                        "message": str(e),
                        "url": None
                    }
                    Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.path.join(f'./newretarget_{str(i)}.yaml')})

                elif motion[i] == 'Running_L_t_R_Motion':
                    try:
                        with open(os.getenv('RETARGET_RUNNING_L_T_R')) as f:
                            data = yaml.load(f, Loader=yaml.FullLoader)
                        data['char_starting_location'][0] = DIM[0]
                        DIM.remove(data['char_starting_location'][0])
                        with open(os.path.join(f'./newretarget_{str(i)}.yaml'), 'w') as f:
                            yaml.dump(data, f)
                        image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.path.join(f'./newretarget_{str(i)}.yaml'))
                    except Exception as e:
                        return {
                        "status": "error",
                        "message": str(e),
                        "url": None
                    }
                    Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.path.join(f'./newretarget_{str(i)}.yaml')})
            data = {
            'scene': {
                'ANIMATED_CHARACTERS': Animated_Characters,
            },
            'controller': {
                'MODE': 'video_render',
                'OUTPUT_VIDEO_PATH': './video.gif'
            },
            'view':
              {'WINDOW_DIMENSIONS': window}
            }
            

            try:
                with open('config.yaml', 'w') as file:
                    yaml.dump(data, file)
                render.start("./config.yaml")
                audio_url = audio_ocr("image_path.jpg")
                audio_path = "./audio.wav"
                gif_path = "./video.gif"
                audio = AudioFileClip(audio_path)

                if audio.duration < 10:
                    audio.duration = 10
                gif = VideoFileClip(gif_path).set_duration(audio.duration)
                final_clip = CompositeVideoClip([gif.set_audio(audio)])
                output_path = "./file.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            except Exception as e:
                raise e
            finally:
                upload_result = cloudinary.uploader.upload("./file.mp4", resource_type="auto")
                os.remove("./config.yaml")
                os.remove("./video.gif")
                os.remove("./audio.wav")
                os.remove("./file.mp4")
                os.remove("./image_path.jpg")
                os.remove("./image.jpg")
                os.remove('./newretarget_0.yaml')
                os.remove('./newretarget_1.yaml')
            

            return {
                'status' : 'success',
                "url": upload_result["secure_url"],
                "message" : "Successfully created gif"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "url": None
            }

@app.post("/Animation")
async def Animation(request: Request, payload : APIPARAMTERS):
    api_params = json.loads(payload.json())
    response = await create_image(api_params=api_params)

    status , message, url = response["status"], response["message"], response["url"]

    if status == "error":
        response_body = {"message" : message }
        response = JSONResponse(status_code = 400, content = response_body)
        return response
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
    print("Setup Complete")

    