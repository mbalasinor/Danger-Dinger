import openai
import imgbbpy
import os
import re
import imageio as iio
import matplotlib.pyplot as plt
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

B = "\033[1m"  # universal bold style
D = "\033[0m"  # universal default style

openai.api_key = os.getenv('open_ai_key')

params = {
    "api_key": "c21d01d2714ceaab64d56cc1f7b9f4ab78689307ee6106810e9b85993765a9ed",
    "engine": "google_lens",
    "url": None
}


def getPhoto():
    camera = iio.get_reader("<video0>")
    screenshot = camera.get_data(0)
    camera.close()

    plt.imshow(screenshot)
    plt.axis('off')
    plt.savefig('screenshot.jpg', bbox_inches='tight', pad_inches=0)


def uploadImage(image):
    client = imgbbpy.SyncClient('a5669be3aac43d7e3818bf97c4de183a')
    image = client.upload(file=image)
    return image.url


def imgInfo():
    input(f"{B}Press enter to take the photo...")
    getPhoto()
    print(f"Photo successfully taken!{D}\n")
    print("-" * 163)
    img_input = uploadImage('screenshot.jpg')
    params["url"] = img_input
    search = GoogleSearch(params)
    results = search.get_dict()
    return results


def getList():
    results = imgInfo()
    list_of_img_titles = []
    for i in range(int(len(results["visual_matches"]))):
        list_of_img_titles.append(results["visual_matches"][i]["title"])
    return list_of_img_titles


def genObjName():
    title_list = getList()
    model_engine = "text-davinci-003"
    prompt = f"Out of this list, return the most likely general (no specific brands) name for the object being talked about: :{title_list}, with a new line at the end."

    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message.strip()


def generate_response():
    model_engine = "text-davinci-003"
    user_input = genObjName()
    prompt = f"On a scale from 0 to 100, provide the objective danger-levels of the following item and include any theoretical potiental risks of the object on the user in the format Objective Danger level = and then in a new line, add a succinct list of any theoretical Potential Risks: :{user_input}"

    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=3,
        stop=None,
        temperature=1,
    )

    message = completions.choices[0].text
    output_list = message.strip().split('\n')
    output_list.insert(0, user_input)
    return output_list


def print_response():
    output_list = generate_response()
    text = '\n'.join(output_list)
    if re.search(r'Objective Danger Level =\s*(\d+)', text):
        danger_level = int(
            re.search(r'Objective Danger Level = (\d+)', text).group(1))
        if danger_level < 25:
            text = '\033[32m' + text + '\033[0m'  # Green
        elif danger_level <= 75:
            text = '\033[33m' + text + '\033[0m'  # Yellow
        else:
            text = '\033[31m' + text + '\033[0m'  # Red
    return text


def main():
    os.system('clear')
    print(f"\n{B}{print_response()}{D}\n")


main()
