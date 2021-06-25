import os
from dotenv import load_dotenv

from google.cloud import speech_v1
from google.cloud import storage


load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
BUCKET_NAME = os.getenv('BUCKET_NAME')
GCLOUD_FILE_NAME = os.getenv('GCLOUD_FILE_NAME')

# Sample rate in Hertz of the audio data sent
SAMPLE_RATE_HERTZ = os.getenv('SAMPLE_RATE_HERTZ')

# The language of the supplied audio
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE')


def upload_audio_to_gcloud(file_name):
    """
    Upload audio file to Google Cloud Storage.
    :param file_name: Name of the file to upload.
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)

    # get file from the bucket by the file name
    blob = bucket.blob(GCLOUD_FILE_NAME)

    # uploading local file to the bucket
    blob.upload_from_filename(f'audio/{file_name}')
    print(f'File {file_name} uploaded to GCloud.')

    transcribe_long_audio_file(file_name)


def transcribe_long_audio_file(file_name):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech recognition.
    :param file_name: Name of the file to upload.
    """
    client = speech_v1.SpeechClient()

    # Encoding of audio data sent. This sample sets this explicitly.
    encoding = speech_v1.enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
    config = {
        "sample_rate_hertz": SAMPLE_RATE_HERTZ,
        "language_code": LANGUAGE_CODE,
        "encoding": encoding,
    }

    storage_uri = "gs://{}/{}".format(BUCKET_NAME, GCLOUD_FILE_NAME)
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(config, audio)

    print("Waiting for speech-to-text conversion to complete...")
    response = operation.result()
    save_text_to_file(response, file_name)


def save_text_to_file(response, file_name):
    """
    Saving transcribed text to file locally.
    :param response: Response from GCloud API with several transcriptions.
    :param file_name: Name of the file to upload.
    """
    txt_file_name = "text/{}.txt".format(file_name.split('.')[0])
    with open(txt_file_name, "w") as text_file:
        for result in response.results:
            # First alternative is the most probable result
            alternative = result.alternatives[0]
            text_file.write("{} ".format(alternative.transcript))


def run():
    all_files = os.listdir("audio")
    print("Total number of audio files: {}".format(len(all_files)))
    for index, file_name in enumerate(all_files):
        print(f'{index}. {file_name} - uploading to GCloud')
        upload_audio_to_gcloud(file_name)
    print("Processing finished!")


if __name__ == '__main__':
    run()
