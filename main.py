import os
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "credentials.json"
bucket_name = "podcast_to_text"
gcloud_file_name = "podcast.mp3"


def upload_audio_to_gcloud(bucket_name, file_name, gcloud_file_name):
    """
    Upload audio file to Google Cloud Storage.
    :param bucket_name: str, name of the bucket in Google Cloud Storage, where the file will be stored
    :param file_name: str, name of the file to upload
    :return: URI of that audio file, stored in Google Cloud Storage
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(gcloud_file_name)
    blob.upload_from_filename("audio/{}".format(file_name))
    print('File {} uploaded to GCloud.'.format(file_name))

    storage_uri = "gs://{}/{}".format(bucket_name, gcloud_file_name)
    sample_long_running_recognize(storage_uri)


def sample_long_running_recognize(storage_uri):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech
    recognition

    Args:
      storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
    """

    client = speech_v1.SpeechClient()

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 16000

    # The language of the supplied audio
    language_code = "en-US"

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
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

    print("Done!\n")


if __name__ == '__main__':
    all_files = os.listdir("audio")
    print("Total number of audio files: {}".format(len(all_files)))
    for file_name in all_files:
        print("{}. {} - uploading to GCloud".format(all_files.index(file_name)+1, file_name))
        upload_audio_to_gcloud(bucket_name, file_name, gcloud_file_name)
