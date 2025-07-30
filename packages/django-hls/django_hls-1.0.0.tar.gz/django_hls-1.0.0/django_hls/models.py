import ffmpeg  
import os
import logging
import binascii

from django.db import models
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.db import transaction

from django_hls.conf import get_setting
from django_hls.utils import is_celery_running, is_queue_available


SEGMENT_DURATION = get_setting('SEGMENT_DURATION')
M3U8_FILE_NAME = get_setting('M3U8_FILE_NAME')
USE_CELERY = get_setting('USE_CELERY')
CELERY_QUEUE = get_setting('CELERY_QUEUE')


class HLSMedia(models.Model):
    """
        A model for storing the segments of each media(audio or video)
    """
    stream_media = models.ForeignKey(
        "DjangoHLSMedia", on_delete=models.CASCADE, related_name="segments"
    )

    def upload_to_path(instance, filename):
        return os.path.join(
            "django_hls/hls",
            os.path.basename(instance.stream_media.media.name),
            filename,
        )

    file = models.FileField(upload_to=upload_to_path)


class DjangoHLSMedia(models.Model):
    media = models.FileField(
        upload_to="django_hls/uploads/",
        validators=[FileExtensionValidator(allowed_extensions=["mp4", "mp3", "m4a"])],
    )
    
    def upload_to_path(instance, filename):
        return os.path.join(
            "django_hls/hls",
            os.path.basename(instance.media.name),
            filename,
        )

    hls_file = models.FileField(upload_to=upload_to_path, blank=True, null=True)
    key_file = models.FileField(upload_to=upload_to_path, blank=True, null=True)
    generating_hls = False

    def save(self, *args, **kwargs):
        """
            Save method to trigger HLS generation
        """
        
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            if USE_CELERY and is_celery_running():
                from django_hls.tasks import generate_hls
                if is_queue_available(CELERY_QUEUE):
                    generate_hls.apply_async(args=[self.id, SEGMENT_DURATION], queue=CELERY_QUEUE)
                else:
                    generate_hls.apply_async(args=[self.id, SEGMENT_DURATION])  # default queue
            else:
                self.generate_hls()

    def generate_keyinfo_file(self, hls_temp_dir, key_path):
            """
            Creating a .keyinfo file for ffmpeg for AES-128 HLS encryption
            
            Args:
                hls_temp_dir: hls temporary directory
                key_path: AES key file path
            Returns:
                keyinfo_path: keyinfo file path
            """
            # Key access path for player
            
            key_uri = f"{self.pk}.key"

            # Keyinfo file path
            keyinfo_path = os.path.join(hls_temp_dir, f"{self.pk}.keyinfo")

            # Generate IV as a random 16-byte number and convert to hex (32 characters)
            iv = binascii.hexlify(os.urandom(16)).decode()

            # Creating keyinfo file
            with open(keyinfo_path, 'w') as ki:
                ki.write(f"{key_uri}\n{key_path}\n{iv}\n")

            return keyinfo_path

    @transaction.atomic
    def generate_hls(self, segment_duration=SEGMENT_DURATION):
        """
        Generate HLS segments and M3U8 file.

        Args:
            segment_duration (int): Duration of each segment in seconds

        Returns:
            None
        """
        try:
            # Create the temporary HLS directory if it doesn't exist
            self.generating_hls = True
            hls_temp_dir = os.path.abspath(
                os.path.join("hls_temp_dir", timezone.now().strftime("%Y-%m-%d_%H-%M-%S"))
            )
            os.makedirs(hls_temp_dir, exist_ok=True)

            # Specify absolute path for the output M3U8 file
            output_path = os.path.abspath(os.path.join(hls_temp_dir, M3U8_FILE_NAME))
            
            # Create AES key
            key_bytes = os.urandom(16)  # 128-bit AES key
            key_filename = f"{self.pk}.key"
            key_path = os.path.join(hls_temp_dir, key_filename)
            with open(key_path, 'wb') as key_file:
                key_file.write(key_bytes)
                
            # Save key file to model field
            self.key_file.save(key_filename, ContentFile(open(key_path, "rb").read()), save=True)
                
            # Create .keyinfo for ffmpeg
            keyinfo_path = self.generate_keyinfo_file(hls_temp_dir, key_path)

            # Run ffmpeg to split the video into segments
            ffmpeg.input(self.media.path).output(
                output_path,
                format='hls',
                hls_time=segment_duration,
                hls_key_info_file=keyinfo_path,
                hls_list_size=0
            ).run()
            
            # Save M3U8 content to the hls_file field
            self.hls_file.save(
                M3U8_FILE_NAME,
                ContentFile(open(output_path, "rb").read()),
                save=True,
            )
            
            
            # Create segments and upload to the Segment model
            ts_files = sorted(f for f in os.listdir(hls_temp_dir) if f.endswith('.ts'))

            for segment_number, filename in enumerate(ts_files):
                path = os.path.join(hls_temp_dir, filename)
                segment = HLSMedia(stream_media=self)
                segment.file.save(filename, ContentFile(open(path, "rb").read()), save=True)
        except Exception as e:
            # Handle exceptions if needed
            self.generating_hls = False
            logging.exception(f"Error: {e}")

        finally:
            # Clean up temporary directory after ffmpeg has finished
            self.generating_hls = False
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
                    