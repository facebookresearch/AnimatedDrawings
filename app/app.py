import sys
import yaml
import os
sys.path.insert(0,'./AnimatedDrawings')
sys.path.insert(1,'./examples')
sys.path.insert(2,'./TextExtraction-to-voice')
from examples.image_to_animation import image_to_animation
from fastapi.middleware.cors import CORSMiddleware
from animated_drawings import render
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from moviepy.editor import *
import urllib.request
import uvicorn

load_dotenv()
import cloudinary
from get_image import  audio_ocr
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

@app.post("/Animation")
async def create_image(request : Request):
    
    data = await request.json()
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
                raise e
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
        elif motion == 'Motion':
            try:
                print("Motion")
            
                print(f"{os.getenv('MOTION')}/{motion}.yaml")
                print(os.getenv('FOUR_LEGS'))
                image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion}.yaml", os.getenv('FOUR_LEGS'))
                print(f"{os.getenv('MOTION')}/{motion}.yaml")
                print(os.getenv('FOUR_LEGS'))
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
            data['scene']['ANIMATED_CHARACTERS'][0]['retarget_cfg'] = os.getenv('FOUR_LEGS')


            try :
                with open('example.yaml', 'w') as file:
                    yaml.dump(data, file)
                render.start("./example.yaml")
                # audio_url = audio_ocr(image_path)
                # audio_path = "./audio.wav"
                # if audio.duration < 10:
                #     audio.duration = 10
                # gif_path = "./vedio.gif"
                # audio = AudioFileClip(audio_path)
                # gif = VideoFileClip(gif_path).set_duration(audio.duration)
                # final_clip = CompositeVideoClip([gif.set_audio(audio)])
                # output_path = "./file.mp4"
                # final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            except Exception as e:
                raise e
            finally:
                # upload_result = cloudinary.uploader.upload("./file.mp4", resource_type="auto")
                # os.remove("./example.yaml")
                pass
                
                # os.remove("./vedio.gif")
                # os.remove("./audio.wav")
                # os.remove("./file.mp4")
                # os.remove("./image.jpg")

        return {
                "status": "success",
                "url": upload_result["secure_url"], 
                "message" : "Successfully created gif"
            }
    
    else:
        # print("We are getting error ")
        Animated_Characters = []
        urllib.request.urlretrieve(image, "image_path.jpg")
        image = "image_path.jpg"
   

        for i, url in enumerate(data['image_url']):
            # path = os.path.join('./output' , str(i))
            # char_anno_dir = os.mkdir(path)
            char_anno_dir = os.path.join('./output' , str(i))
            urllib.request.urlretrieve(url, "image.jpg")
            image_path = "image.jpg"

            if motion[i] == 'dab' or motion[i] == 'jumping' or motion[i] == 'wave_hello':
                try:
                    image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.getenv('RETARGET'))
                except Exception as e:
                    return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
                Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.getenv('RETARGET')})

            elif motion[i] == 'jesse_dance':
                try:
                    image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.getenv('RETARGET_JESSE'))
                except Exception as e:
                    return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
                Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.getenv('RETARGET_JESSE')})
                

            elif motion[i] == 'zombie':
                try:
                    image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.getenv('RETARGET_ZOMBIE'))
                except Exception as e:
                    return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
                Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.getenv('RETARGET_ZOMBIE')})

            elif motion[i] == 'jumping_jacks':
                try:
                    image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.getenv('RETARGET_JACKS'))
                except Exception as e:
                    return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
                Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.getenv('RETARGET_JACKS')})

            elif motion[i] == 'Running_Motion':
                try:
                    image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.getenv('RETARGET_RUNNING'))
                except Exception as e:
                    return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
                Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.getenv('RETARGET_RUNNING')})

            elif motion[i] == 'Running_L_t_R_Motion':
                try:
                    image_to_animation(image_path, char_anno_dir, f"{os.getenv('MOTION')}/{motion[i]}.yaml", os.getenv('RUNNING_ABC'))
                except Exception as e:
                    return {
                    "status": "error",
                    "message": str(e),
                    "url": None
                }
                Animated_Characters.append({'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'), 'motion_cfg': f"{os.getenv('MOTION')}/{motion[i]}.yaml", 'retarget_cfg': os.getenv('RUNNING_ABC')})
        data = {
        'scene': {
            'ANIMATED_CHARACTERS': Animated_Characters,
        },
        'controller': {
            'MODE': 'video_render',
            'OUTPUT_VIDEO_PATH': './video.gif'
        }
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
        

        return {
            'status' : 'success',
            "url": upload_result["secure_url"],
            "message" : "Successfully created gif"
        }





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
    print("Setup Complete")

    