import numpy as np
import cv2
from typing import List
from matplotlib import pyplot as plt
from path import Path
from word_detector import detect, prepare_img, sort_multiline
# import tensorflow as tf
import os
import requests, json, time
# from gingerit.gingerit import GingerIt
# from HandWritingRecog import prediction_model, decode_batch_predictions, preprocess_image, distortion_free_resize, image_height, image_width
# import openai
# import keras_ocr
# from langchain import  LLMChain
from dotenv import load_dotenv
from serpapi import GoogleSearch
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_KEY")



from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import cloudinary
import cloudinary.uploader

cloudinary.config(
  cloud_name = "djvu7apub",
  api_key = "433374637814992",
  api_secret = os.getenv('CLOUDINARY_API'),
  secure = True
)



list_img_names_serial = []

def get_img_files(data_dir:Path)-> List[Path]:
    res  = []
    for ext in ['*.jpg', '*.png', '*.bmp']:
        res += Path(data_dir).files(ext)
        print(res)
    return res

# parser = GingerIt()



def save_image_names_to_text_files():
    for fn_img in get_img_files(r"C:\Users\ajayp\Animations\images"):
        print(f'Processing file {fn_img}')

        img = prepare_img(cv2.imread(fn_img), 1000)

        detections = detect(img, 
                            kernel_size = 25 ,
                            sigma = 11,
                            theta = 5,
                            min_area = 1000)
        
        lines = sort_multiline(detections)

        plt.imshow(img, cmap = 'gray')

        num_colors = 7
        colors = plt.cm.get_cmap('rainbow', num_colors)
        text = ""
        for line_idx, line in enumerate(lines):
            print("line index and line is printed", line_idx)
            for word_idx, det in enumerate(line):
                print("word index in line is printed", word_idx)

                xs = [det.bbox.x, det.bbox.x, det.bbox.x + det.bbox.w, det.bbox.x + det.bbox.w, det.bbox.x]
                ys = [det.bbox.y, det.bbox.y + det.bbox.h, det.bbox.y + det.bbox.h, det.bbox.y, det.bbox.y]

                plt.plot(xs, ys, c = colors(line_idx%num_colors))
                plt.text(det.bbox.x, det.bbox.y, f'{line_idx}/{word_idx}')
                # print(det.bbox.x, det.bbox.y, det.bbox.w, det.bbox.h)
                crop_img = img[det.bbox.y:det.bbox.y+det.bbox.h, det.bbox.x:det.bbox.x+det.bbox.w]
                image = np.expand_dims(crop_img, axis=-1)
                # print(image.shape)
                # cv2.imwrite("saved_images" + "/" + "line" + str(line_idx) + "word" + str(word_idx) + ".jpg", crop_img)
                image = tf.convert_to_tensor(image)
                image = distortion_free_resize(image, (image_width, image_height))
                image = tf.cast(image, tf.float32) / 255.0
                image = np.asarray(image)
                image = np.expand_dims(image, axis=0)
                image = tf.cast(image, tf.float32)

                preds = prediction_model.predict(image)
                pred_texts = decode_batch_predictions(preds)
                text += pred_texts[0] + " "
    
        plt.show()

    return parser.parse(text)["result"]

def pipeline_ocr():
    return keras_ocr.pipeline.Pipeline()

def templates():
    template_1 = """You are the helpful assistant which takes the {text} as a input and 
              Fix the grammer of the text and return the text as a output. 
              """
    template_2 = """Correct the grammer and spelling mistakes of input {text} if present and provide relevant answer. If you are not able to get correct answer just return same {text} as the output. Dont answer  Sorry, I am able able to undersatnd the meaning """
    
    template_3 = """You are the helpful assisant which creates the relevant answer from the provided {text}"""

    template_4 = "change the voice of the provided {text}"

    template_5 = "Generate meaningful input from provided {text}"

    return template_5

def get_chain():
    chat = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
    system_message_prompt_1 = SystemMessagePromptTemplate.from_template(templates())
    human_template_1="{text}"
    human_message_prompt_1 = HumanMessagePromptTemplate.from_template(human_template_1)
    chat_prompt_1 = ChatPromptTemplate.from_messages([system_message_prompt_1, human_message_prompt_1])
    chain_1 = LLMChain(llm=chat, prompt=chat_prompt_1)

    return chain_1

def audio_file(path):
    pipeline = pipeline_ocr()
    results = pipeline.recognize([path])
    text = " ".join([i[0] for i in results[0]])
    chain = get_chain()
    ans = chain.run(text)
    print(f"Extracted text is {ans}")

    apikey = os.getenv("rapid_api") # get your free API key from https://rapidapi.com/k_1/api/large-text-to-speech/
    filename = "test-file.wav"

    headers = {'content-type': "application/json", 'x-rapidapi-host': "large-text-to-speech.p.rapidapi.com", 'x-rapidapi-key': apikey}
    response = requests.request("POST", "https://large-text-to-speech.p.rapidapi.com/tts", data=json.dumps({"text": ans}), headers=headers)
    id = json.loads(response.text)['id']
    eta = json.loads(response.text)['eta']
    print(f'Waiting {eta} seconds for the job to finish...')
    time.sleep(eta)
    response = requests.request("GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
    while "url" not in json.loads(response.text):
        response = requests.request("GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
        print(f'Waiting some more...')
        time.sleep(3)
    url = json.loads(response.text)['url']
    response = requests.request("GET", url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f'File saved to {filename} ! \nOr download here: {url}')

    return url

# def audio_ocr(image_path):
    

#     apikey = os.getenv("rapid_api") # get your free API key from https://rapidapi.com/k_1/api/large-text-to-speech/
#     filename = "audio.wav"

#     headers = {'content-type': "application/json", 'x-rapidapi-host': "large-text-to-speech.p.rapidapi.com", 'x-rapidapi-key': apikey}
    

    


#     try:
#         response = cloudinary.uploader.upload(path)
#         params = {
#         "engine": "google_lens",
#         "url": response["secure_url"],
#         "api_key": os.getenv('SERP_API')
#         }

#         search = GoogleSearch(params)
#         results = search.get_dict()
#         text_results = results["text_results"]
    

#         sentence = ''
#         for i, data in enumerate(text_results):
#             dic = text_results[i]
#             sentence += dic['text'] + ' '
#         print(sentence)

#         response = requests.request("POST", "https://large-text-to-speech.p.rapidapi.com/tts", data=json.dumps({"text": sentence}), headers=headers)
#         id = json.loads(response.text)['id']
#         eta = json.loads(response.text)['eta']
#         print(f'Waiting {eta} seconds for the job to finish...')
#         time.sleep(eta)
#         response = requests.request("GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
#         while "url" not in json.loads(response.text):
#             response = requests.request("GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
#             print(f'Waiting some more...')
#             time.sleep(3)
#         url = json.loads(response.text)['url']
#         response = requests.request("GET", url)
#         with open(filename, 'wb') as f:
#             f.write(response.content)    
#         return url
    
#     except: 
#         print("Yes")
#         sentence = "No Text is Present in the image"
#         response = requests.request("POST", "https://large-text-to-speech.p.rapidapi.com/tts", data=json.dumps({"text": sentence}), headers=headers)
#         id = json.loads(response.text)['id']
#         eta = json.loads(response.text)['eta']
#         print(f'Waiting {eta} seconds for the job to finish...')
#         time.sleep(eta)
#         response = requests.request("GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
#         while "url" not in json.loads(response.text):
#             response = requests.request("GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
#             print(f'Waiting some more...')
#             time.sleep(3)
#         url = json.loads(response.text)['url']
#         response = requests.request("GET", url)
#         with open(filename, 'wb') as f:
#             f.write(response.content)
#         return url 
        
def audio_ocr(path):
    

    apikey = os.getenv("rapid_api") # get your free API key from https://rapidapi.com/k_1/api/large-text-to-speech/
    filename = "audio.wav"

    headers = {'content-type': "application/json", 'x-rapidapi-host': "large-text-to-speech.p.rapidapi.com", 'x-rapidapi-key': apikey}
    try:
        ans = cloudinary.uploader.upload(path)
        params = {
        "engine": "google_lens",
        "url": ans['secure_url'],
        "api_key": os.getenv('SERP_API')
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        text_results = results["text_results"]

        sentence = ''
        for i, data in enumerate(text_results):
            dic = text_results[i]
            sentence += dic['text'] + ' '
        print(sentence)

        url = "https://text-to-speech27.p.rapidapi.com/speech"

        querystring = {"text":sentence,"lang":"en-us"}

        headers = {
            "X-RapidAPI-Key": os.getenv('rapid_api'),
            "X-RapidAPI-Host": "text-to-speech27.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)     

        with open(filename, 'wb') as f:
            f.write(response.content)

        return url
    
    except: 
        
        sentence = "No Text is Present in the image"
        url = "https://text-to-speech27.p.rapidapi.com/speech"

        querystring = {"text":sentence,"lang":"en-us"}

        headers = {
            "X-RapidAPI-Key": os.getenv('rapid_api'),
            "X-RapidAPI-Host": "text-to-speech27.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)     

        with open(filename, 'wb') as f:
            f.write(response.content)
        return url 

if __name__ == "__main__":
    path = "/home/ajay/Animations/AnimatedDrawings/examples/drawings/garlic.png"
    print(audio_ocr(path))
