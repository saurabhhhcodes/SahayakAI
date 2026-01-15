
import os
from huggingface_hub import InferenceClient
from PIL import Image
import io

# Using a default free token or expecting env var. 
# For this demo, we can use a highly rated open model.
# StabilityAI/stable-diffusion-xl-base-1.0 is SOTA open source.

class ImageGenerator:
    def __init__(self):
        # In a real deployed app, user should provide HF_TOKEN.
        # We will try to use reliable public inference or fallback to a hardcoded demo token if needed.
        # For now, we instantiate client without token (rate limited but works for public models often)
        # or better, use a specific public space wrapper. 
        self.client = InferenceClient(model="stabilityai/stable-diffusion-xl-base-1.0")

    def generate(self, prompt, output_path):
        try:
            image = self.client.text_to_image(prompt)
            image.save(output_path)
            return output_path
        except Exception as e:
            print(f"HF Generation Error: {e}")
            # Fallback to simple placeholder if API fails (rate limit)
            img = Image.new('RGB', (1024, 1024), color = (73, 109, 137))
            img.save(output_path)
            return output_path

# Singleton
image_gen = ImageGenerator()
