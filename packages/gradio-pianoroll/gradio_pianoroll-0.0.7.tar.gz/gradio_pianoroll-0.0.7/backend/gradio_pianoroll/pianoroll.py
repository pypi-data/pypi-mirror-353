from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

from .timing_utils import (
    generate_note_id,
    pixels_to_flicks,
    pixels_to_seconds,
    pixels_to_beats,
    pixels_to_ticks,
    pixels_to_samples,
    calculate_all_timing_data,
    create_note_with_timing,
)

if TYPE_CHECKING:
    from gradio.components import Timer

class PianoRoll(Component):
    """
    PianoRoll custom Gradio component for MIDI note editing and playback.

    This class manages the state and data for the piano roll, including note timing, audio data,
    and backend/ frontend synchronization. It provides methods for preprocessing and postprocessing
    data, as well as updating backend audio/curve/segment data.

    Attributes:
        width (int): Width of the piano roll component in pixels.
        height (int): Height of the piano roll component in pixels.
        value (dict): Current piano roll data (notes, settings, etc.).
        audio_data (str|None): Backend audio data (base64 or URL).
        curve_data (dict): Backend curve data (pitch, loudness, etc.).
        segment_data (list): Backend segment data (timing, etc.).
        use_backend_audio (bool): Whether to use backend audio engine.
    """

    EVENTS = [
        Events.change,
        Events.input,
        Events.play,
        Events.pause,
        Events.stop,
        Events.clear,
    ]

    def __init__(
        self,
        value: dict | None = None,
        *,
        audio_data: str | None = None,
        curve_data: dict | None = None,
        segment_data: list | None = None,
        use_backend_audio: bool = False,
        label: str | I18nData | None = None,
        every: "Timer | float | None" = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        width: int | None = 1000,
        height: int | None = 600,
    ):
        """
        Parameters:
            value: default MIDI notes data to provide in piano roll. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            audio_data: 백엔드에서 전달받은 오디오 데이터 (base64 인코딩된 오디오 또는 URL)
            curve_data: 백엔드에서 전달받은 선형 데이터 (피치 곡선, loudness 곡선 등)
            segment_data: 백엔드에서 전달받은 구간 데이터 (발음 타이밍 등)
            use_backend_audio: 백엔드 오디오를 사용할지 여부 (True시 프론트엔드 오디오 엔진 비활성화)
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will be rendered as an editable piano roll; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            width: width of the piano roll component in pixels.
            height: height of the piano roll component in pixels.
        """
        self.width = width
        self.height = height

        # Default settings for flicks calculation
        default_pixels_per_beat = 80
        default_tempo = 120
        default_sample_rate = 44100
        default_ppqn = 480

        default_notes = [
            create_note_with_timing(generate_note_id(), 80, 80, 60, 100, "안녕",
                                  default_pixels_per_beat, default_tempo, default_sample_rate, default_ppqn),      # 1st beat of measure 1
            create_note_with_timing(generate_note_id(), 160, 160, 64, 90, "하세요",
                                  default_pixels_per_beat, default_tempo, default_sample_rate, default_ppqn),    # 1st beat of measure 2
            create_note_with_timing(generate_note_id(), 320, 80, 67, 95, "반가워요",
                                  default_pixels_per_beat, default_tempo, default_sample_rate, default_ppqn)    # 1st beat of measure 3
        ]

        if value is None:
            self.value = {
                "notes": default_notes,
                "tempo": default_tempo,
                "timeSignature": { "numerator": 4, "denominator": 4 },
                "editMode": "select",
                "snapSetting": "1/4",
                "pixelsPerBeat": default_pixels_per_beat,
                "sampleRate": default_sample_rate,
                "ppqn": default_ppqn
            }
        else:
            # Ensure all notes have IDs and flicks values, generate them if missing
            if "notes" in value and value["notes"]:
                pixels_per_beat = value.get("pixelsPerBeat", default_pixels_per_beat)
                tempo = value.get("tempo", default_tempo)

                for note in value["notes"]:
                    if "id" not in note or not note["id"]:
                        note["id"] = generate_note_id()

                    # Add flicks values if missing
                    if "startFlicks" not in note:
                        note["startFlicks"] = pixels_to_flicks(note["start"], pixels_per_beat, tempo)
                    if "durationFlicks" not in note:
                        note["durationFlicks"] = pixels_to_flicks(note["duration"], pixels_per_beat, tempo)

            self.value = value

        # 백엔드 데이터 속성들
        self.audio_data = audio_data
        self.curve_data = curve_data or {}
        self.segment_data = segment_data or []
        self.use_backend_audio = use_backend_audio

        self._attrs = {
            "width": width,
            "height": height,
            "value": self.value,
            "audio_data": self.audio_data,
            "curve_data": self.curve_data,
            "segment_data": self.segment_data,
            "use_backend_audio": self.use_backend_audio,
        }

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            value=value,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )

    def preprocess(self, payload):
        """
        Preprocess incoming MIDI notes data from the frontend before passing to user function.
        Args:
            payload: The MIDI notes data to preprocess.
        Returns:
            The preprocessed data (passed through).
        """
        return payload

    def postprocess(self, value):
        """
        Postprocess outgoing MIDI notes data from the user function before sending to the frontend.
        Ensures all notes have IDs and timing values, and attaches backend data if needed.
        Args:
            value: The MIDI notes data to postprocess.
        Returns:
            The postprocessed data (with all required fields).
        """
        # Ensure all notes have IDs and all timing values when sending to frontend
        if value and "notes" in value and value["notes"]:
            pixels_per_beat = value.get("pixelsPerBeat", 80)
            tempo = value.get("tempo", 120)
            sample_rate = value.get("sampleRate", 44100)
            ppqn = value.get("ppqn", 480)

            for note in value["notes"]:
                if "id" not in note or not note["id"]:
                    note["id"] = generate_note_id()

                # Add all timing values if missing
                if "startFlicks" not in note or "startSeconds" not in note:
                    start_timing = calculate_all_timing_data(note["start"], pixels_per_beat, tempo, sample_rate, ppqn)
                    note.update({
                        "startFlicks": start_timing['flicks'],
                        "startSeconds": start_timing['seconds'],
                        "startBeats": start_timing['beats'],
                        "startTicks": start_timing['ticks'],
                        "startSample": start_timing['samples']
                    })

                if "durationFlicks" not in note or "durationSeconds" not in note:
                    duration_timing = calculate_all_timing_data(note["duration"], pixels_per_beat, tempo, sample_rate, ppqn)
                    note.update({
                        "durationFlicks": duration_timing['flicks'],
                        "durationSeconds": duration_timing['seconds'],
                        "durationBeats": duration_timing['beats'],
                        "durationTicks": duration_timing['ticks'],
                        "durationSamples": duration_timing['samples']
                    })

                # Calculate end time if missing
                if "endSeconds" not in note:
                    note["endSeconds"] = note.get("startSeconds", 0) + note.get("durationSeconds", 0)

        # 백엔드 데이터 속성들도 함께 전달
        if value and isinstance(value, dict):
            # value에 이미 있는 백엔드 데이터를 우선하고, 없으면 컴포넌트 속성에서 가져옴
            # 이렇게 하면 컴포넌트 인스턴스별로 독립적인 백엔드 설정이 가능함

            if "audio_data" not in value or value["audio_data"] is None:
                if hasattr(self, 'audio_data') and self.audio_data:
                    value["audio_data"] = self.audio_data

            if "curve_data" not in value or value["curve_data"] is None:
                if hasattr(self, 'curve_data') and self.curve_data:
                    value["curve_data"] = self.curve_data

            if "segment_data" not in value or value["segment_data"] is None:
                if hasattr(self, 'segment_data') and self.segment_data:
                    value["segment_data"] = self.segment_data

            if "use_backend_audio" not in value:
                if hasattr(self, 'use_backend_audio'):
                    value["use_backend_audio"] = self.use_backend_audio
                else:
                    value["use_backend_audio"] = False

            # 디버깅용 로그 추가
            print(f"🔊 [postprocess] Backend audio data processed:")
            print(f"   - audio_data present: {bool(value.get('audio_data'))}")
            print(f"   - use_backend_audio: {value.get('use_backend_audio', False)}")
            print(f"   - curve_data present: {bool(value.get('curve_data'))}")
            print(f"   - segment_data present: {bool(value.get('segment_data'))}")

        return value

    def example_payload(self):
        """
        Example payload for the piano roll component (for documentation/testing).
        Returns:
            dict: Example piano roll data.
        """
        pixels_per_beat = 80
        tempo = 120
        sample_rate = 44100
        ppqn = 480

        return {
            "notes": [
                create_note_with_timing(generate_note_id(), 80, 80, 60, 100, "안녕",
                                      pixels_per_beat, tempo, sample_rate, ppqn)
            ],
            "tempo": tempo,
            "timeSignature": { "numerator": 4, "denominator": 4 },
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": pixels_per_beat,
            "sampleRate": sample_rate,
            "ppqn": ppqn
        }

    def example_value(self):
        """
        Example value for the piano roll component (for documentation/testing).
        Returns:
            dict: Example piano roll data.
        """
        pixels_per_beat = 80
        tempo = 120
        sample_rate = 44100
        ppqn = 480

        return {
            "notes": [
                create_note_with_timing(generate_note_id(), 80, 80, 60, 100, "안녕",
                                      pixels_per_beat, tempo, sample_rate, ppqn),
                create_note_with_timing(generate_note_id(), 160, 160, 64, 90, "하세요",
                                      pixels_per_beat, tempo, sample_rate, ppqn)
            ],
            "tempo": tempo,
            "timeSignature": { "numerator": 4, "denominator": 4 },
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": pixels_per_beat,
            "sampleRate": sample_rate,
            "ppqn": ppqn
        }

    def api_info(self):
        """
        Returns OpenAPI-style schema for the piano roll data object.
        Returns:
            dict: API schema for the piano roll component.
        """
        return {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "start": {"type": "number", "description": "Start position in pixels"},
                            "duration": {"type": "number", "description": "Duration in pixels"},
                            "startFlicks": {"type": "number", "description": "Start position in flicks (precise timing)"},
                            "durationFlicks": {"type": "number", "description": "Duration in flicks (precise timing)"},
                            "startSeconds": {"type": "number", "description": "Start time in seconds (for audio processing)"},
                            "durationSeconds": {"type": "number", "description": "Duration in seconds (for audio processing)"},
                            "endSeconds": {"type": "number", "description": "End time in seconds (startSeconds + durationSeconds)"},
                            "startBeats": {"type": "number", "description": "Start position in musical beats"},
                            "durationBeats": {"type": "number", "description": "Duration in musical beats"},
                            "startTicks": {"type": "integer", "description": "Start position in MIDI ticks"},
                            "durationTicks": {"type": "integer", "description": "Duration in MIDI ticks"},
                            "startSample": {"type": "integer", "description": "Start position in audio samples"},
                            "durationSamples": {"type": "integer", "description": "Duration in audio samples"},
                            "pitch": {"type": "number", "description": "MIDI pitch (0-127)"},
                            "velocity": {"type": "number", "description": "MIDI velocity (0-127)"},
                            "lyric": {"type": "string", "description": "Optional lyric text"}
                        },
                        "required": ["id", "start", "duration", "startFlicks", "durationFlicks",
                                   "startSeconds", "durationSeconds", "endSeconds", "startBeats", "durationBeats",
                                   "startTicks", "durationTicks", "startSample", "durationSamples", "pitch", "velocity"]
                    }
                },
                "tempo": {
                    "type": "number",
                    "description": "BPM tempo"
                },
                "timeSignature": {
                    "type": "object",
                    "properties": {
                        "numerator": {"type": "number"},
                        "denominator": {"type": "number"}
                    },
                    "required": ["numerator", "denominator"]
                },
                "editMode": {
                    "type": "string",
                    "description": "Current edit mode"
                },
                "snapSetting": {
                    "type": "string",
                    "description": "Note snap setting"
                },
                "pixelsPerBeat": {
                    "type": "number",
                    "description": "Zoom level in pixels per beat"
                },
                "sampleRate": {
                    "type": "integer",
                    "description": "Audio sample rate (Hz) for sample-based timing calculations",
                    "default": 44100
                },
                "ppqn": {
                    "type": "integer",
                    "description": "Pulses Per Quarter Note for MIDI tick calculations",
                    "default": 480
                },
                # 백엔드 데이터 전달용 속성들
                "audio_data": {
                    "type": "string",
                    "description": "Backend audio data (base64 encoded audio or URL)",
                    "nullable": True
                },
                "curve_data": {
                    "type": "object",
                    "description": "Linear curve data (pitch curves, loudness curves, etc.)",
                    "properties": {
                        "pitch_curve": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Pitch curve data points"
                        },
                        "loudness_curve": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Loudness curve data points"
                        },
                        "formant_curves": {
                            "type": "object",
                            "description": "Formant frequency curves",
                            "additionalProperties": {
                                "type": "array",
                                "items": {"type": "number"}
                            }
                        }
                    },
                    "additionalProperties": True,
                    "nullable": True
                },
                "segment_data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "number", "description": "Segment start time (seconds)"},
                            "end": {"type": "number", "description": "Segment end time (seconds)"},
                            "type": {"type": "string", "description": "Segment type (phoneme, syllable, word, etc.)"},
                            "value": {"type": "string", "description": "Segment value/text"},
                            "confidence": {"type": "number", "description": "Confidence score (0-1)", "minimum": 0, "maximum": 1}
                        },
                        "required": ["start", "end", "type", "value"]
                    },
                    "description": "Segmentation data (pronunciation timing, etc.)",
                    "nullable": True
                },
                "use_backend_audio": {
                    "type": "boolean",
                    "description": "Whether to use backend audio (disables frontend audio engine when true)",
                    "default": False
                }
            },
            "required": ["notes", "tempo", "timeSignature", "editMode", "snapSetting"],
            "description": "Piano roll data object containing notes array, settings, and optional backend data"
        }

    def update_backend_data(self, audio_data=None, curve_data=None, segment_data=None, use_backend_audio=None):
        """
        Update backend audio, curve, and segment data for this component instance.
        Args:
            audio_data (str|None): New audio data.
            curve_data (dict|None): New curve data.
            segment_data (list|None): New segment data.
            use_backend_audio (bool|None): Whether to use backend audio.
        """
        if audio_data is not None:
            self.audio_data = audio_data
        if curve_data is not None:
            self.curve_data = curve_data
        if segment_data is not None:
            self.segment_data = segment_data
        if use_backend_audio is not None:
            self.use_backend_audio = use_backend_audio

        # _attrs도 업데이트
        self._attrs.update({
            "audio_data": self.audio_data,
            "curve_data": self.curve_data,
            "segment_data": self.segment_data,
            "use_backend_audio": self.use_backend_audio,
        })

    def set_audio_data(self, audio_data: str):
        """
        Set the backend audio data for this component.
        Args:
            audio_data (str): New audio data (base64 or URL).
        """
        self.audio_data = audio_data
        self._attrs["audio_data"] = audio_data

    def set_curve_data(self, curve_data: dict):
        """
        Set the backend curve data for this component.
        Args:
            curve_data (dict): New curve data.
        """
        self.curve_data = curve_data
        self._attrs["curve_data"] = curve_data

    def set_segment_data(self, segment_data: list):
        """
        Set the backend segment data for this component.
        Args:
            segment_data (list): New segment data.
        """
        self.segment_data = segment_data
        self._attrs["segment_data"] = segment_data

    def enable_backend_audio(self, enable: bool = True):
        """
        Enable or disable backend audio for this component.
        Args:
            enable (bool): True to enable backend audio, False to disable.
        """
        self.use_backend_audio = enable
        self._attrs["use_backend_audio"] = enable
