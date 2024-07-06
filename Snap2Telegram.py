# Snap2Telegram

# Added retry on error & most values from config.ini 
# import config ini file with configparser
# send once and close program
# define the specified screenshot areas to being blacked out before sending to telegram
# Set an image caption

## save your configuration within the config.ini 

## Thanks to GPT for assistance


import configparser
import ast
import pyautogui
from PIL import Image, ImageDraw
import io
from telegram import Bot
import time
import asyncio

# Path to config file
configini = configparser.ConfigParser()      
configini.read(r"config.ini")

# Telegram token and chat ID values from the config file 
bot_token = configini.get('Configuration', 'bot_token')
chat_id = configini.get('Configuration', 'chat_id')

# Screenshot position and size xy width height on desktop
ScreenshotArea =  ast.literal_eval(configini.get('Configuration', 'ScreenshotArea'))

# Optional image caption
caption = configini.get('Configuration', 'caption')

# Areas to be blacked out before sending xy width height OPTIONAL otherwise 0
Area1 = ast.literal_eval(configini.get('Configuration', 'Area1'))
Area2 = ast.literal_eval(configini.get('Configuration', 'Area2'))
Area3 = ast.literal_eval(configini.get('Configuration', 'Area3'))
Area4 = ast.literal_eval(configini.get('Configuration', 'Area4'))

# Errorhandling
max_attempts = int(configini.get('Configuration', 'max_attempts')) 
delay_between_attemps = int(configini.get('Configuration', 'delay_between_attemps'))

# Create, edit and send screenshot
async def send_screenshot():
    
    # Take the screenshot
    screenshot = pyautogui.screenshot(region = ScreenshotArea)
    
    # Define the areas to be blacked out [(x1, y1, x2, y2), (x3, y3, x4, y4)]
    areas_to_blackout = [(Area1), (Area2), (Area3), (Area4)]

    # Create a new image object with the same size as the screenshot
    blacked_out_image = screenshot.copy()

    # Create a drawing object to perform the blacking out
    draw = ImageDraw.Draw(blacked_out_image)

    # Black out the defined areas
    for area in areas_to_blackout:
        # Black out the area
        draw.rectangle(area, fill='black')

    # Create a byte stream to save the image as a file
    image_bytes = io.BytesIO()
    blacked_out_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    # Send the screenshot to the Telegram chat
    bot = Bot(token=bot_token)
    await bot.send_photo(chat_id=chat_id, photo=image_bytes, caption=caption)

    # Close the byte stream
    image_bytes.close()

    # Stop the event loop after sending the message
    loop = asyncio.get_event_loop()
    loop.stop()


# Manage attempts
async def main():
    attempts = 0
    while attempts < max_attempts:
        try:
            await send_screenshot()
            break
        except Exception as e:
            print(f"Error: {e}")
            attempts += 1
            if attempts < max_attempts:
                print(f"Retrying in {delay_between_attemps} seconds (attempt {attempts} of {max_attempts})...")
                await asyncio.sleep(delay_between_attemps)
            else:
                print(f"Failed after {attempts} attempts")
                
# Using an asynchronous event loop for sending message
def run_event_loop():
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

if __name__ == '__main__':
    
    run_event_loop()
