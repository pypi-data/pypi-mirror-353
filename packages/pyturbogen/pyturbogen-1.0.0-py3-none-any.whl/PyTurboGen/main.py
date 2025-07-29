import requests

def Generate_Img(prompt:str, seed:int, file_name:str, width:int=1024, height:int=1024):
    """
    Generate an image based on the provided prompt.
    
    Parameters:
    - prompt: The text prompt for image generation.
    - seed: Random seed for image generation.
    - file_name: The name of the file to save the generated image (in .jpg format).
    - width: Width of the generated image (default is 1024).
    - height: Height of the generated image (default is 1024).
    """
    image_url = f"https://pollinations.ai/p/{prompt}?width={width}&height={height}&seed={seed}&model=turbo&nologo=True&enhance=True"
    response = requests.get(image_url)
    
    if response.status_code == 200:  
        with open(file_name, 'wb') as file:
            file.write(response.content)
            print("Image generated successfully!")
    else:
        raise TimeoutError("Try after sometime!")