"""Built-in voice presets for AstraFlow IndexTTS-2.

These are pre-uploaded reference audio IDs provided by AstraFlow.
Custom voices (uploaded via /v1/audio/voice/upload) are managed separately
through AstraFlowClient.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VoicePreset:
    id: str
    label: str
    description: str = ""


# All built-in voices available on AstraFlow IndexTTS-2.
# Verified via API: 2026-07-11
BUILTIN_VOICES: list[VoicePreset] = [
    VoicePreset(id="jack_cheng", label="Jack Cheng", description="标准男声"),
    VoicePreset(id="crystla_liu", label="Crystla Liu", description="温柔女声"),
    VoicePreset(id="stephen_chow", label="Stephen Chow", description="粤语男声"),
    VoicePreset(id="xiaoyueyue", label="小岳岳", description="相声风格"),
    VoicePreset(id="mkas", label="Mkas", description=""),
    VoicePreset(id="entertain", label="Entertain", description="娱乐风格"),
    VoicePreset(id="novel", label="Novel", description="小说朗读"),
    VoicePreset(id="movie", label="Movie", description="电影旁白"),
    VoicePreset(id="sales_voice", label="Sales Voice", description="营销语音"),
]

# Flat list of voice IDs for quick lookup
BUILTIN_VOICE_IDS: list[str] = [v.id for v in BUILTIN_VOICES]

# Mapping from voice ID to label
VOICE_LABEL_MAP: dict[str, str] = {v.id: v.label for v in BUILTIN_VOICES}
