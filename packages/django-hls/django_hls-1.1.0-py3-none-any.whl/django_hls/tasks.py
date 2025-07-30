import os
import logging
import binascii
from celery import shared_task
from ffmpeg_progress_yield import FfmpegProgress

from django.core.files.base import ContentFile
from django.utils import timezone

from django_hls.models import DjangoHLSMedia, HLSMedia
from django_hls.conf import get_setting

M3U8_FILE_NAME = get_setting('M3U8_FILE_NAME')


@shared_task(bind=True)
def generate_hls(self, media_id: int, segment_duration: int):
    """
    Generate HLS segments and M3U8 file.

    Args:
        segment_duration (int): Duration of each segment in seconds

    Returns:
        None
    """
    
    media = DjangoHLSMedia.objects.get(id=media_id)
    hls_temp_dir = None
    try:
        # Create the temporary HLS directory if it doesn't exist
        media.generating_hls = True
        hls_temp_dir = os.path.abspath(
            os.path.join("hls_temp_dir", timezone.now().strftime("%Y-%m-%d_%H-%M-%S"))
        )
        os.makedirs(hls_temp_dir, exist_ok=True)

        # Specify absolute path for the output M3U8 file
        output_path = os.path.abspath(os.path.join(hls_temp_dir, M3U8_FILE_NAME))
        
        
        # Create AES key
        key_bytes = os.urandom(16)  # 128-bit AES key
        key_filename = f"{media.pk}.key"
        key_path = os.path.join(hls_temp_dir, key_filename)
        with open(key_path, 'wb') as key_file:
            key_file.write(key_bytes)
            
        # Save key file to model field
        media.key_file.save(key_filename, ContentFile(open(key_path, "rb").read()), save=True)
            
        # Create .keyinfo for ffmpeg
        key_uri = f"{media.pk}.key"
        print(key_uri)
        # Keyinfo file path
        keyinfo_path = os.path.join(hls_temp_dir, f"{media.pk}.keyinfo")
        # Generate IV as a random 16-byte number and convert to hex (32 characters)
        iv = binascii.hexlify(os.urandom(16)).decode()
        # Creating keyinfo file
        with open(keyinfo_path, 'w') as ki:
            ki.write(f"{key_uri}\n{key_path}\n{iv}\n")

        # Run ffmpeg to split the video into segments using FfmpegProgress
        cmd = [
            "ffmpeg",
            "-i", media.media.path,
            "-c:v", "libx264",
            "-hls_time", str(segment_duration),
            "-hls_list_size", "0",
            "-hls_key_info_file", keyinfo_path,
            "-f", "hls",
            output_path,
        ]
        
        ff = FfmpegProgress(cmd)


        logging.info("Progress: 0%")
        for progress in ff.run_command_with_progress():
            logging.info(f"Progress: {progress}%")

        # Create segments and upload to the Segment model
        ts_files = sorted(f for f in os.listdir(hls_temp_dir) if f.endswith('.ts'))

        for segment_number, filename in enumerate(ts_files):
            path = os.path.join(hls_temp_dir, filename)
            segment = HLSMedia(stream_media=media)
            segment.file.save(filename, ContentFile(open(path, "rb").read()), save=True)

        # Save M3U8 content to the hls_file field
        media.hls_file.save(
            M3U8_FILE_NAME,
            ContentFile(open(output_path, "rb").read()),
            save=True,
        )

    except Exception as e:
        # Handle exceptions if needed
        media.generating_hls = False
        logging.error(f"Error: {e}")

    finally:
        # Clean up temporary directory after ffmpeg has finished
        media.generating_hls = False
        if os.path.exists(hls_temp_dir):
            for file_name in os.listdir(hls_temp_dir):
                file_path = os.path.join(hls_temp_dir, file_name)
                try:
                    os.remove(file_path)
                except Exception as e:
                    logging.warning(f"Couldn't delete {file_path}: {e}")
            try:
                os.rmdir(hls_temp_dir)
            except Exception as e:
                logging.warning(f"Couldn't remove directory {hls_temp_dir}: {e}")