import os
from dotenv import load_dotenv

from google.cloud import speech_v1
from google.cloud import storage


load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
BUCKET_NAME = os.getenv('BUCKET_NAME')
GCLOUD_FILE_NAME = os.getenv('GCLOUD_FILE_NAME')


def upload_audio_to_gcloud(file_name):
    """
    Upload audio file to Google Cloud Storage.
    :param file_name: Name of the file to upload.
    :return: URI of that audio file, stored in Google Cloud Storage.
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(GCLOUD_FILE_NAME)
    blob.upload_from_filename("audio/{}".format(file_name))
    print('File {} uploaded to GCloud.'.format(file_name))

    storage_uri = "gs://{}/{}".format(BUCKET_NAME, GCLOUD_FILE_NAME)
    transcribe_long_audio_file(storage_uri, file_name)


def transcribe_long_audio_file(storage_uri, file_name):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech recognition.
    :param storage_uri: URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE].
    :param file_name: Name of the file to upload.
    """
    client = speech_v1.SpeechClient()

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 16000

    # The language of the supplied audio
    language_code = "en-US"

    # Encoding of audio data sent. This sample sets this explicitly.
    encoding = speech_v1.enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
    config = {
        "sample_rate_hertz": sample_rate_hertz,
        "language_code": language_code,
        "encoding": encoding,
    }
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(config, audio)

    print("Waiting for speech-to-text conversion to complete...")
    response = operation.result()

    txt_file_name = "text/{}.txt".format(file_name.split('.')[0])
    with open(txt_file_name, "w") as text_file:
        for result in response.results:
            # First alternative is the most probable result
            alternative = result.alternatives[0]
            text_file.write("{} ".format(alternative.transcript))


def run():
    all_files = os.listdir("audio")
    print("Total number of audio files: {}".format(len(all_files)))
    for file_name in all_files:
        print("{}. {} - uploading to GCloud".format(all_files.index(file_name), file_name))
        upload_audio_to_gcloud(file_name)
    print("Processing finished!")


if __name__ == '__main__':
    run()
