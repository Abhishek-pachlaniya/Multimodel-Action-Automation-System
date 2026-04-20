import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep


def open_images(prompt):
    folder_path = os.path.join(os.path.dirname(__file__), "..", "data")
    prompt      = prompt.replace(" ", "_")
    files = os.listdir(folder_path)
    files = [f for f in files if f.startswith(prompt)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")


API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}


async def query(payload):
    response = await asyncio.to_thread(
        requests.post,
        API_URL,
        headers=headers,
        json=payload
    )
    return response.content


async def generate_images(prompt: str):
    folder_path = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(folder_path, exist_ok=True)
    tasks = []

    for _ in range(1):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes.startswith(b"{") or image_bytes.startswith(b"<"):
            print("API ERROR:", image_bytes[:200].decode(errors="ignore"))
            continue

        import io
        try:
            img = Image.open(io.BytesIO(image_bytes))
            save_path = os.path.join(
                folder_path,
                f"{prompt.replace(' ', '_')}{i+1}.png"
            )
            img.save(save_path)
            print("Saved:", save_path)
        except Exception as e:
            print(f"Could not save image {i+1}: {e}")


def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)


# -------------------------------------------------------
# FIX: Proper loop with max retries and graceful exit
# -------------------------------------------------------
DATA_FILE = r"frontend\files\ImageGeneration.data"
MAX_WAIT_SECONDS = 300   # 5 minutes max wait
POLL_INTERVAL    = 1     # seconds between checks

def main():
    waited = 0

    while waited < MAX_WAIT_SECONDS:
        try:
            if not os.path.exists(DATA_FILE):
                sleep(POLL_INTERVAL)
                waited += POLL_INTERVAL
                continue

            with open(DATA_FILE, "r") as f:
                Data = f.read().strip()

            if not Data or "," not in Data:
                sleep(POLL_INTERVAL)
                waited += POLL_INTERVAL
                continue

            Prompt, Status = Data.split(",", 1)
            Prompt = Prompt.replace("generate image ", "").strip()

            if Status.strip() == "True":
                print(f"Generating image for: {Prompt}")

                GenerateImages(prompt=Prompt)

                # Reset the data file after generation
                with open(DATA_FILE, "w") as f:
                    f.write("None,False")

                print("Image generation complete.")
                break   # Exit after successful generation

            else:
                sleep(POLL_INTERVAL)
                waited += POLL_INTERVAL

        except KeyboardInterrupt:
            print("Image generation cancelled.")
            break

        except Exception as e:
            print(f"ImageGeneration Error: {e}")
            sleep(POLL_INTERVAL)
            waited += POLL_INTERVAL

    else:
        print(f"ImageGeneration: Timed out after {MAX_WAIT_SECONDS} seconds.")


if __name__ == "__main__":
    main()
