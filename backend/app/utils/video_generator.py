import os
import shutil
import uuid
from gradio_client import Client
from PIL import Image
import numpy as np
from app.utils.image_generator import image_gen

class VideoGenerator:
    def __init__(self):
        # Try to init client, but don't crash if it fails
        self.client = None
        try:
            self.client = Client("damo-vilab/modelscope-text-to-video-synthesis")
        except:
            print("Video: ModelScope Client Init Failed. Using Fallback.")

    def generate(self, prompt: str, output_path: str):
        # 1. Try Real AI Video (if client exists)
        if self.client:
            try:
                result = self.client.predict(prompt, -1, 16, 25, api_name="/predict")
                if os.path.exists(result):
                    shutil.move(result, output_path)
                    return output_path
            except Exception as e:
                print(f"Real Video Gen Failed: {e}")

        # 2. FALLBACK: Generate Image -> Video (Slideshow)
        print("Video: Using Image-to-Video Fallback.")
        try:
            # Compatibility for MoviePy v2
            try:
                from moviepy import ImageClip
            except ImportError:
                try:
                    from moviepy.editor import ImageClip
                except ImportError:
                     from moviepy.video.VideoClip import ImageClip
            
            # Generate a frame using our ImageGenerator
            temp_img = output_path.replace(".mp4", ".png")
            image_gen.generate(prompt, temp_img)
            
            
            if os.path.exists(temp_img):
                # Create 4 sec video from image
                # MoviePy v2 uses with_duration, v1 uses set_duration. Try both.
                try:
                    clip = ImageClip(temp_img)
                    if hasattr(clip, "with_duration"):
                        clip = clip.with_duration(4).with_fps(24)
                    else:
                        clip = clip.set_duration(4).set_fps(24)
                        
                    clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
                except Exception as e:
                    print(f"MoviePy Clip Error: {e}")
                    raise e
                
                # Cleanup
                if os.path.exists(temp_img):
                    os.remove(temp_img)
                    
                return output_path
        except Exception as e:
            print(f"Fallback Video Failed: {e}")
            return None

video_gen = VideoGenerator()
