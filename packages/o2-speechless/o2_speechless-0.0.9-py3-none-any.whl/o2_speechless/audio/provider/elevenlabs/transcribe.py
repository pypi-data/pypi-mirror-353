"""ElevenLabs Transcriber Class"""

import os
import json
from io import BytesIO
from elevenlabs.client import ElevenLabs
from elevenlabs.types.speech_to_text_chunk_response_model import (
    SpeechToTextChunkResponseModel,
)
from dotenv import load_dotenv


class ElevenLabsTranscriber:
    """
    A client for transcribing audio using the ElevenLabs Speech-to-Text API.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the ElevenLabsTranscriber with an API key.

        Parameters
        ----------
        api_key : str
            ElevenLabs API key. If not provided, will attempt to load from the
            'ELEVENLABS_API_KEY' environment variable.

        Raises
        ------
        ValueError
            If the API key is not provided or found in environment variables.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as a parameter or in the 'ELEVENLABS_API_KEY' environment variable."
            )
        self.client = ElevenLabs(api_key=self.api_key)

    def transcribe(
        self,
        audio_path: str,
        model_id: str = "scribe_v1",
        language_code: str = None,
        tag_audio_events: bool = True,
        diarize: bool = False,
        num_speakers: int = None,
        timestamps_granularity: str = "word",
        file_format: str = "other",
    ) -> dict:
        """
        Transcribe an audio file using the ElevenLabs Speech-to-Text API.

        Parameters
        ----------
        audio_path : str
            Path to the local audio file.
        model_id : str
            Model ID to use for transcription. Default is 'scribe_v1'.
        language_code : str
            ISO-639-1 or ISO-639-3 code for the spoken language in the audio.
            If None, the language will be auto-detected.
        tag_audio_events : bool
            Whether to annotate non-verbal audio events (e.g., laughter, applause).
        diarize : bool
            Whether to include speaker diarization in the output.
        num_speakers : int
            Number of speakers in the audio. Helpful for diarization.
        timestamps_granularity : str
            Level of timestamp detail: 'none', 'word', or 'character'.
        file_format : str
            Format of the input file. Options include 'pcm_s16le_16' or 'other'.

        Returns
        -------
        dict
            A dictionary containing transcription results, including the text and metadata.

        Raises
        ------
        FileNotFoundError
            If the audio file does not exist.
        """
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"The audio file '{audio_path}' does not exist.")

        with open(audio_path, "rb") as audio_file:
            audio_data = BytesIO(audio_file.read())

        additional_formats = json.dumps([{"format": "segmented_json"}])

        transcription = self.client.speech_to_text.convert(
            file=audio_data,
            model_id=model_id,
            language_code=language_code,
            tag_audio_events=tag_audio_events,
            diarize=diarize,
            num_speakers=num_speakers,
            timestamps_granularity=timestamps_granularity,
            file_format=file_format,
            additional_formats=additional_formats,
        )

        return transcription

    @staticmethod
    def save(
        transcription: SpeechToTextChunkResponseModel,
        file_path: str,
        file_type: str = "json",
    ) -> None:
        """
        Save the transcript to a file:

        - If file_type='json', saves a JSON file with word-level metadata.
        - If file_type='stt', saves plain text.

        Parameters
        ----------
        transcription : SpeechToTextChunkResponseModel
            The transcription object returned by the ElevenLabs API.
        file_path : str
            Destination file path. Must end in '.json' if file_type='json', otherwise '.stt'.
        file_type : str
            Output format: 'json' (default) or 'stt' (plain text).

        Raises
        ------
        ValueError
            If the file extension does not match the expected output format.
        """
        ext = os.path.splitext(file_path)[-1].lower()

        if file_type == "json":
            if ext != ".json":
                raise ValueError("JSON transcript must be saved as a '.json' file.")
            # Extract and parse the segmented JSON content
            segmented_content = transcription.additional_formats[0].content
            if isinstance(segmented_content, str):
                data = json.loads(segmented_content)
            else:
                data = segmented_content
            with open(file_path, "w", encoding="utf-8") as f:  # noqa: WPS440
                json.dump(data, f, ensure_ascii=False, indent=2)

        elif file_type == "stt":
            if ext != ".stt":
                raise ValueError("Plain transcript must be saved as a '.stt' file.")
            # Extract plain text from the transcription object
            text = getattr(transcription, "text", None)
            if text is None:
                # fallback for dict-like access
                text = transcription.get("text", "")
            with open(file_path, "w", encoding="utf-8") as f:  # noqa: WPS440
                f.write(text)
        else:
            raise ValueError("Invalid file_type. Use 'json' or 'stt'.")
