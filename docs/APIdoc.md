# IndexTTS-2

## AstraFlow API

### Request Body

model
`IndexTeamIndexTTSExtendModel` `required`
提交语音合成请求。请求中传入文本、音色和输出格式，响应返回音频内容。

input
`string` `required`
Text to synthesize.

voice
`string` `required`
Voice to use for synthesis. The source examples show the built-in `jack_cheng` voice and custom voice IDs shaped like `uspeech:xxxx`.

response_format
`string`
OpenAI-compatible base TTS field mentioned by the source document. Concrete response-format values are not enumerated in this source.

speed
`number<double>`
Speech playback speed. The documented range is 0.25 to 4.

instructions
`string`
OpenAI-compatible base TTS field mentioned by the source document. This source does not define additional IndexTTS-specific semantics.

sample_rate
`integer`
Target audio sample rate. Supported concrete values are defined by the provider; the source lists examples such as 16000, 22050, and 24000.

gain
`number<double>`
Output volume gain coefficient. The source recommends the range (0, 10] and notes that 0 mutes output.

emo_control_method
`integer`
Emotion-control method identifier. `0` disables emotion control, `1` uses emotion audio, `2` uses an emotion vector, and `3` uses emotion text.
`0` `1` `2` `3`

emo_weight
`number<double>`
Weight applied to the emotion reference audio, vector, or text. The documented valid range is 0.0 to 1.0. The source recommends about 0.6 or lower for text emotion mode to produce more natural speech.

emo_vec
`number<double>[]`
Emotion vector ordered as happiness, anger, sadness, fear, disgust, melancholy, surprise, and calm. Each dimension is documented as 0 to 1.2, and the sum of all dimensions must not exceed 1.5.

emo_text
`string`
Natural-language emotion prompt, such as happy, calm, or excited.

emo_random
`boolean`
Whether to introduce randomness into emotion control for more variety or to avoid identical emotion expression between sentences.

interval_silence
`integer`
Controls interval silence between sentences. The field table and curl examples use a millisecond integer with a recommended value of 200.

max_text_tokens_per_sentence
`integer`
Maximum token count or length threshold for internal sentence splitting in long-text synthesis. The source recommends 120.

### Responses

`200` Synthesized speech audio.
`string<binary>`
提交语音合成请求。请求中传入文本、音色和输出格式，响应返回音频内容。

`400` 请求参数无效。

`default` 错误响应。
