import os
from io import BytesIO

import requests
import tinify
import boto3

class UploadService:
    def __init__(self, compression_threshold_kb=250):
        self.region_name = os.environ.get('DO_SPACES_REGION_NAME')
        self.access_key = os.environ.get('DO_SPACES_ACCESS_KEY')
        self.secret_key = os.environ.get('DO_SPACES_SECRET_KEY')
        self.bucket_name = os.environ.get('DO_LOGO_BUCKET_NAME')
        self.cdn_endpoint = os.environ.get('DO_SPACES_CDN_ENDPOINT')
        self.compression_threshold_kb = compression_threshold_kb

        self.session = boto3.session.Session()
        self.client = self.session.client('s3',
                                          region_name=self.region_name,
                                          endpoint_url=f'https://{self.region_name}.digitaloceanspaces.com',
                                          aws_access_key_id=self.access_key,
                                          aws_secret_access_key=self.secret_key)

        tinify.key = os.environ.get('TINIFY_API_KEY')

    def upload_file(self, file, file_name):
        try:
            # Les filinnhold til minne
            original_data = file.read()
            file_size_kb = len(original_data) / 1024

            # Komprimer kun hvis filstørrelse overstiger terskel
            if file_size_kb > self.compression_threshold_kb:
                source = tinify.from_buffer(original_data)
                data_to_upload = source.to_buffer()
            else:
                data_to_upload = original_data

            # Last opp til CDN med 'public-read' permissions
            self.client.put_object(Body=data_to_upload,
                                   Bucket=self.bucket_name,
                                   Key=file_name,
                                   ACL='public-read',
                                   ContentType='image/png')

            cdn_url = f"{self.cdn_endpoint}/{file_name}"
            return {
                'imageUrl': f'{cdn_url}'
            }, 200

        except Exception as e:
            return {'error': f'Failed to upload. Error: {str(e)}'}, 500

    def download_image(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.exceptions.RequestException as e:
            return {'error': f'Failed to download image. Error: {str(e)}'}, 500