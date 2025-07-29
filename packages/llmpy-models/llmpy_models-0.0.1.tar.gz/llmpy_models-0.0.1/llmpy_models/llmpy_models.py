from enum import Enum, auto

class Provider(Enum):
    ANTHROPIC = auto()
    GOOGLE = auto()
    GROQ = auto()
    OPENAI = auto()

class Model(Enum):
    CLAUDE_3_5_HAIKU_20241022 = 'claude-3-5-haiku-20241022'
    CLAUDE_3_5_SONNET_20240620 = 'claude-3-5-sonnet-20240620'
    CLAUDE_3_5_SONNET_20241022 = 'claude-3-5-sonnet-20241022'
    CLAUDE_3_7_SONNET_20250219 = 'claude-3-7-sonnet-20250219'
    CLAUDE_3_HAIKU_20240307 = 'claude-3-haiku-20240307'
    CLAUDE_3_OPUS_20240229 = 'claude-3-opus-20240229'
    CLAUDE_OPUS_4_20250514 = 'claude-opus-4-20250514'
    CLAUDE_SONNET_4_20250514 = 'claude-sonnet-4-20250514'
    MODELS_GEMINI_1_0_PRO_VISION_LATEST = 'models/gemini-1.0-pro-vision-latest'
    MODELS_GEMINI_1_5_FLASH = 'models/gemini-1.5-flash'
    MODELS_GEMINI_1_5_FLASH_001 = 'models/gemini-1.5-flash-001'
    MODELS_GEMINI_1_5_FLASH_001_TUNING = 'models/gemini-1.5-flash-001-tuning'
    MODELS_GEMINI_1_5_FLASH_002 = 'models/gemini-1.5-flash-002'
    MODELS_GEMINI_1_5_FLASH_8B = 'models/gemini-1.5-flash-8b'
    MODELS_GEMINI_1_5_FLASH_8B_001 = 'models/gemini-1.5-flash-8b-001'
    MODELS_GEMINI_1_5_FLASH_8B_EXP_0827 = 'models/gemini-1.5-flash-8b-exp-0827'
    MODELS_GEMINI_1_5_FLASH_8B_EXP_0924 = 'models/gemini-1.5-flash-8b-exp-0924'
    MODELS_GEMINI_1_5_FLASH_8B_LATEST = 'models/gemini-1.5-flash-8b-latest'
    MODELS_GEMINI_1_5_FLASH_LATEST = 'models/gemini-1.5-flash-latest'
    MODELS_GEMINI_1_5_PRO = 'models/gemini-1.5-pro'
    MODELS_GEMINI_1_5_PRO_001 = 'models/gemini-1.5-pro-001'
    MODELS_GEMINI_1_5_PRO_002 = 'models/gemini-1.5-pro-002'
    MODELS_GEMINI_1_5_PRO_LATEST = 'models/gemini-1.5-pro-latest'
    MODELS_GEMINI_2_0_FLASH = 'models/gemini-2.0-flash'
    MODELS_GEMINI_2_0_FLASH_001 = 'models/gemini-2.0-flash-001'
    MODELS_GEMINI_2_0_FLASH_EXP = 'models/gemini-2.0-flash-exp'
    MODELS_GEMINI_2_0_FLASH_EXP_IMAGE_GENERATION = 'models/gemini-2.0-flash-exp-image-generation'
    MODELS_GEMINI_2_0_FLASH_LITE = 'models/gemini-2.0-flash-lite'
    MODELS_GEMINI_2_0_FLASH_LITE_001 = 'models/gemini-2.0-flash-lite-001'
    MODELS_GEMINI_2_0_FLASH_LITE_PREVIEW = 'models/gemini-2.0-flash-lite-preview'
    MODELS_GEMINI_2_0_FLASH_LITE_PREVIEW_02_05 = 'models/gemini-2.0-flash-lite-preview-02-05'
    MODELS_GEMINI_2_0_FLASH_PREVIEW_IMAGE_GENERATION = 'models/gemini-2.0-flash-preview-image-generation'
    MODELS_GEMINI_2_0_FLASH_THINKING_EXP = 'models/gemini-2.0-flash-thinking-exp'
    MODELS_GEMINI_2_0_FLASH_THINKING_EXP_01_21 = 'models/gemini-2.0-flash-thinking-exp-01-21'
    MODELS_GEMINI_2_0_FLASH_THINKING_EXP_1219 = 'models/gemini-2.0-flash-thinking-exp-1219'
    MODELS_GEMINI_2_0_PRO_EXP = 'models/gemini-2.0-pro-exp'
    MODELS_GEMINI_2_0_PRO_EXP_02_05 = 'models/gemini-2.0-pro-exp-02-05'
    MODELS_GEMINI_2_5_FLASH_PREVIEW_04_17 = 'models/gemini-2.5-flash-preview-04-17'
    MODELS_GEMINI_2_5_FLASH_PREVIEW_04_17_THINKING = 'models/gemini-2.5-flash-preview-04-17-thinking'
    MODELS_GEMINI_2_5_FLASH_PREVIEW_05_20 = 'models/gemini-2.5-flash-preview-05-20'
    MODELS_GEMINI_2_5_FLASH_PREVIEW_TTS = 'models/gemini-2.5-flash-preview-tts'
    MODELS_GEMINI_2_5_PRO_EXP_03_25 = 'models/gemini-2.5-pro-exp-03-25'
    MODELS_GEMINI_2_5_PRO_PREVIEW_03_25 = 'models/gemini-2.5-pro-preview-03-25'
    MODELS_GEMINI_2_5_PRO_PREVIEW_05_06 = 'models/gemini-2.5-pro-preview-05-06'
    MODELS_GEMINI_2_5_PRO_PREVIEW_TTS = 'models/gemini-2.5-pro-preview-tts'
    MODELS_GEMINI_EXP_1206 = 'models/gemini-exp-1206'
    MODELS_GEMINI_PRO_VISION = 'models/gemini-pro-vision'
    MODELS_GEMMA_3_12B_IT = 'models/gemma-3-12b-it'
    MODELS_GEMMA_3_1B_IT = 'models/gemma-3-1b-it'
    MODELS_GEMMA_3_27B_IT = 'models/gemma-3-27b-it'
    MODELS_GEMMA_3_4B_IT = 'models/gemma-3-4b-it'
    MODELS_GEMMA_3N_E4B_IT = 'models/gemma-3n-e4b-it'
    MODELS_LEARNLM_2_0_FLASH_EXPERIMENTAL = 'models/learnlm-2.0-flash-experimental'
    ALLAM_2_7B = 'allam-2-7b'
    COMPOUND_BETA = 'compound-beta'
    COMPOUND_BETA_MINI = 'compound-beta-mini'
    DEEPSEEK_R1_DISTILL_LLAMA_70B = 'deepseek-r1-distill-llama-70b'
    DISTIL_WHISPER_LARGE_V3_EN = 'distil-whisper-large-v3-en'
    GEMMA2_9B_IT = 'gemma2-9b-it'
    LLAMA_3_1_8B_INSTANT = 'llama-3.1-8b-instant'
    LLAMA_3_3_70B_VERSATILE = 'llama-3.3-70b-versatile'
    LLAMA_GUARD_3_8B = 'llama-guard-3-8b'
    LLAMA3_70B_8192 = 'llama3-70b-8192'
    LLAMA3_8B_8192 = 'llama3-8b-8192'
    META_LLAMA_LLAMA_4_MAVERICK_17B_128E_INSTRUCT = 'meta-llama/llama-4-maverick-17b-128e-instruct'
    META_LLAMA_LLAMA_4_SCOUT_17B_16E_INSTRUCT = 'meta-llama/llama-4-scout-17b-16e-instruct'
    META_LLAMA_LLAMA_GUARD_4_12B = 'meta-llama/llama-guard-4-12b'
    META_LLAMA_LLAMA_PROMPT_GUARD_2_22M = 'meta-llama/llama-prompt-guard-2-22m'
    META_LLAMA_LLAMA_PROMPT_GUARD_2_86M = 'meta-llama/llama-prompt-guard-2-86m'
    MISTRAL_SABA_24B = 'mistral-saba-24b'
    PLAYAI_TTS = 'playai-tts'
    PLAYAI_TTS_ARABIC = 'playai-tts-arabic'
    QWEN_QWQ_32B = 'qwen-qwq-32b'
    WHISPER_LARGE_V3 = 'whisper-large-v3'
    WHISPER_LARGE_V3_TURBO = 'whisper-large-v3-turbo'
    BABBAGE_002 = 'babbage-002'
    CHATGPT_4O_LATEST = 'chatgpt-4o-latest'
    CODEX_MINI_LATEST = 'codex-mini-latest'
    COMPUTER_USE_PREVIEW = 'computer-use-preview'
    COMPUTER_USE_PREVIEW_2025_03_11 = 'computer-use-preview-2025-03-11'
    DALL_E_2 = 'dall-e-2'
    DALL_E_3 = 'dall-e-3'
    DAVINCI_002 = 'davinci-002'
    GPT_3_5_TURBO = 'gpt-3.5-turbo'
    GPT_3_5_TURBO_0125 = 'gpt-3.5-turbo-0125'
    GPT_3_5_TURBO_1106 = 'gpt-3.5-turbo-1106'
    GPT_3_5_TURBO_16K = 'gpt-3.5-turbo-16k'
    GPT_3_5_TURBO_INSTRUCT = 'gpt-3.5-turbo-instruct'
    GPT_3_5_TURBO_INSTRUCT_0914 = 'gpt-3.5-turbo-instruct-0914'
    GPT_4 = 'gpt-4'
    GPT_4_0125_PREVIEW = 'gpt-4-0125-preview'
    GPT_4_0613 = 'gpt-4-0613'
    GPT_4_1106_PREVIEW = 'gpt-4-1106-preview'
    GPT_4_TURBO = 'gpt-4-turbo'
    GPT_4_TURBO_2024_04_09 = 'gpt-4-turbo-2024-04-09'
    GPT_4_TURBO_PREVIEW = 'gpt-4-turbo-preview'
    GPT_4_1 = 'gpt-4.1'
    GPT_4_1_2025_04_14 = 'gpt-4.1-2025-04-14'
    GPT_4_1_MINI = 'gpt-4.1-mini'
    GPT_4_1_MINI_2025_04_14 = 'gpt-4.1-mini-2025-04-14'
    GPT_4_1_NANO = 'gpt-4.1-nano'
    GPT_4_1_NANO_2025_04_14 = 'gpt-4.1-nano-2025-04-14'
    GPT_4_5_PREVIEW = 'gpt-4.5-preview'
    GPT_4_5_PREVIEW_2025_02_27 = 'gpt-4.5-preview-2025-02-27'
    GPT_4O = 'gpt-4o'
    GPT_4O_2024_05_13 = 'gpt-4o-2024-05-13'
    GPT_4O_2024_08_06 = 'gpt-4o-2024-08-06'
    GPT_4O_2024_11_20 = 'gpt-4o-2024-11-20'
    GPT_4O_AUDIO_PREVIEW = 'gpt-4o-audio-preview'
    GPT_4O_AUDIO_PREVIEW_2024_10_01 = 'gpt-4o-audio-preview-2024-10-01'
    GPT_4O_AUDIO_PREVIEW_2024_12_17 = 'gpt-4o-audio-preview-2024-12-17'
    GPT_4O_AUDIO_PREVIEW_2025_06_03 = 'gpt-4o-audio-preview-2025-06-03'
    GPT_4O_MINI = 'gpt-4o-mini'
    GPT_4O_MINI_2024_07_18 = 'gpt-4o-mini-2024-07-18'
    GPT_4O_MINI_AUDIO_PREVIEW = 'gpt-4o-mini-audio-preview'
    GPT_4O_MINI_AUDIO_PREVIEW_2024_12_17 = 'gpt-4o-mini-audio-preview-2024-12-17'
    GPT_4O_MINI_REALTIME_PREVIEW = 'gpt-4o-mini-realtime-preview'
    GPT_4O_MINI_REALTIME_PREVIEW_2024_12_17 = 'gpt-4o-mini-realtime-preview-2024-12-17'
    GPT_4O_MINI_SEARCH_PREVIEW = 'gpt-4o-mini-search-preview'
    GPT_4O_MINI_SEARCH_PREVIEW_2025_03_11 = 'gpt-4o-mini-search-preview-2025-03-11'
    GPT_4O_MINI_TRANSCRIBE = 'gpt-4o-mini-transcribe'
    GPT_4O_MINI_TTS = 'gpt-4o-mini-tts'
    GPT_4O_REALTIME_PREVIEW = 'gpt-4o-realtime-preview'
    GPT_4O_REALTIME_PREVIEW_2024_10_01 = 'gpt-4o-realtime-preview-2024-10-01'
    GPT_4O_REALTIME_PREVIEW_2024_12_17 = 'gpt-4o-realtime-preview-2024-12-17'
    GPT_4O_REALTIME_PREVIEW_2025_06_03 = 'gpt-4o-realtime-preview-2025-06-03'
    GPT_4O_SEARCH_PREVIEW = 'gpt-4o-search-preview'
    GPT_4O_SEARCH_PREVIEW_2025_03_11 = 'gpt-4o-search-preview-2025-03-11'
    GPT_4O_TRANSCRIBE = 'gpt-4o-transcribe'
    GPT_IMAGE_1 = 'gpt-image-1'
    O1 = 'o1'
    O1_2024_12_17 = 'o1-2024-12-17'
    O1_MINI = 'o1-mini'
    O1_MINI_2024_09_12 = 'o1-mini-2024-09-12'
    O1_PREVIEW = 'o1-preview'
    O1_PREVIEW_2024_09_12 = 'o1-preview-2024-09-12'
    O1_PRO = 'o1-pro'
    O1_PRO_2025_03_19 = 'o1-pro-2025-03-19'
    O3 = 'o3'
    O3_2025_04_16 = 'o3-2025-04-16'
    O3_MINI = 'o3-mini'
    O3_MINI_2025_01_31 = 'o3-mini-2025-01-31'
    O4_MINI = 'o4-mini'
    O4_MINI_2025_04_16 = 'o4-mini-2025-04-16'
    OMNI_MODERATION_2024_09_26 = 'omni-moderation-2024-09-26'
    OMNI_MODERATION_LATEST = 'omni-moderation-latest'
    TEXT_EMBEDDING_3_LARGE = 'text-embedding-3-large'
    TEXT_EMBEDDING_3_SMALL = 'text-embedding-3-small'
    TEXT_EMBEDDING_ADA_002 = 'text-embedding-ada-002'
    TTS_1 = 'tts-1'
    TTS_1_1106 = 'tts-1-1106'
    TTS_1_HD = 'tts-1-hd'
    TTS_1_HD_1106 = 'tts-1-hd-1106'
    WHISPER_1 = 'whisper-1'

model_to_provider = {
    Model.CLAUDE_3_5_HAIKU_20241022: Provider.ANTHROPIC,
    Model.CLAUDE_3_5_SONNET_20240620: Provider.ANTHROPIC,
    Model.CLAUDE_3_5_SONNET_20241022: Provider.ANTHROPIC,
    Model.CLAUDE_3_7_SONNET_20250219: Provider.ANTHROPIC,
    Model.CLAUDE_3_HAIKU_20240307: Provider.ANTHROPIC,
    Model.CLAUDE_3_OPUS_20240229: Provider.ANTHROPIC,
    Model.CLAUDE_OPUS_4_20250514: Provider.ANTHROPIC,
    Model.CLAUDE_SONNET_4_20250514: Provider.ANTHROPIC,
    Model.MODELS_GEMINI_1_0_PRO_VISION_LATEST: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_001: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_001_TUNING: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_002: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_8B: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_8B_001: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_8B_EXP_0827: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_8B_EXP_0924: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_8B_LATEST: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_FLASH_LATEST: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_PRO: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_PRO_001: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_PRO_002: Provider.GOOGLE,
    Model.MODELS_GEMINI_1_5_PRO_LATEST: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_001: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_EXP: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_EXP_IMAGE_GENERATION: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_LITE: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_LITE_001: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_LITE_PREVIEW: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_LITE_PREVIEW_02_05: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_PREVIEW_IMAGE_GENERATION: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_THINKING_EXP: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_THINKING_EXP_01_21: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_FLASH_THINKING_EXP_1219: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_PRO_EXP: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_0_PRO_EXP_02_05: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_5_FLASH_PREVIEW_04_17: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_5_FLASH_PREVIEW_04_17_THINKING: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_5_FLASH_PREVIEW_05_20: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_5_FLASH_PREVIEW_TTS: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_5_PRO_EXP_03_25: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_5_PRO_PREVIEW_03_25: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_5_PRO_PREVIEW_05_06: Provider.GOOGLE,
    Model.MODELS_GEMINI_2_5_PRO_PREVIEW_TTS: Provider.GOOGLE,
    Model.MODELS_GEMINI_EXP_1206: Provider.GOOGLE,
    Model.MODELS_GEMINI_PRO_VISION: Provider.GOOGLE,
    Model.MODELS_GEMMA_3_12B_IT: Provider.GOOGLE,
    Model.MODELS_GEMMA_3_1B_IT: Provider.GOOGLE,
    Model.MODELS_GEMMA_3_27B_IT: Provider.GOOGLE,
    Model.MODELS_GEMMA_3_4B_IT: Provider.GOOGLE,
    Model.MODELS_GEMMA_3N_E4B_IT: Provider.GOOGLE,
    Model.MODELS_LEARNLM_2_0_FLASH_EXPERIMENTAL: Provider.GOOGLE,
    Model.ALLAM_2_7B: Provider.GROQ,
    Model.COMPOUND_BETA: Provider.GROQ,
    Model.COMPOUND_BETA_MINI: Provider.GROQ,
    Model.DEEPSEEK_R1_DISTILL_LLAMA_70B: Provider.GROQ,
    Model.DISTIL_WHISPER_LARGE_V3_EN: Provider.GROQ,
    Model.GEMMA2_9B_IT: Provider.GROQ,
    Model.LLAMA_3_1_8B_INSTANT: Provider.GROQ,
    Model.LLAMA_3_3_70B_VERSATILE: Provider.GROQ,
    Model.LLAMA_GUARD_3_8B: Provider.GROQ,
    Model.LLAMA3_70B_8192: Provider.GROQ,
    Model.LLAMA3_8B_8192: Provider.GROQ,
    Model.META_LLAMA_LLAMA_4_MAVERICK_17B_128E_INSTRUCT: Provider.GROQ,
    Model.META_LLAMA_LLAMA_4_SCOUT_17B_16E_INSTRUCT: Provider.GROQ,
    Model.META_LLAMA_LLAMA_GUARD_4_12B: Provider.GROQ,
    Model.META_LLAMA_LLAMA_PROMPT_GUARD_2_22M: Provider.GROQ,
    Model.META_LLAMA_LLAMA_PROMPT_GUARD_2_86M: Provider.GROQ,
    Model.MISTRAL_SABA_24B: Provider.GROQ,
    Model.PLAYAI_TTS: Provider.GROQ,
    Model.PLAYAI_TTS_ARABIC: Provider.GROQ,
    Model.QWEN_QWQ_32B: Provider.GROQ,
    Model.WHISPER_LARGE_V3: Provider.GROQ,
    Model.WHISPER_LARGE_V3_TURBO: Provider.GROQ,
    Model.BABBAGE_002: Provider.OPENAI,
    Model.CHATGPT_4O_LATEST: Provider.OPENAI,
    Model.CODEX_MINI_LATEST: Provider.OPENAI,
    Model.COMPUTER_USE_PREVIEW: Provider.OPENAI,
    Model.COMPUTER_USE_PREVIEW_2025_03_11: Provider.OPENAI,
    Model.DALL_E_2: Provider.OPENAI,
    Model.DALL_E_3: Provider.OPENAI,
    Model.DAVINCI_002: Provider.OPENAI,
    Model.GPT_3_5_TURBO: Provider.OPENAI,
    Model.GPT_3_5_TURBO_0125: Provider.OPENAI,
    Model.GPT_3_5_TURBO_1106: Provider.OPENAI,
    Model.GPT_3_5_TURBO_16K: Provider.OPENAI,
    Model.GPT_3_5_TURBO_INSTRUCT: Provider.OPENAI,
    Model.GPT_3_5_TURBO_INSTRUCT_0914: Provider.OPENAI,
    Model.GPT_4: Provider.OPENAI,
    Model.GPT_4_0125_PREVIEW: Provider.OPENAI,
    Model.GPT_4_0613: Provider.OPENAI,
    Model.GPT_4_1106_PREVIEW: Provider.OPENAI,
    Model.GPT_4_TURBO: Provider.OPENAI,
    Model.GPT_4_TURBO_2024_04_09: Provider.OPENAI,
    Model.GPT_4_TURBO_PREVIEW: Provider.OPENAI,
    Model.GPT_4_1: Provider.OPENAI,
    Model.GPT_4_1_2025_04_14: Provider.OPENAI,
    Model.GPT_4_1_MINI: Provider.OPENAI,
    Model.GPT_4_1_MINI_2025_04_14: Provider.OPENAI,
    Model.GPT_4_1_NANO: Provider.OPENAI,
    Model.GPT_4_1_NANO_2025_04_14: Provider.OPENAI,
    Model.GPT_4_5_PREVIEW: Provider.OPENAI,
    Model.GPT_4_5_PREVIEW_2025_02_27: Provider.OPENAI,
    Model.GPT_4O: Provider.OPENAI,
    Model.GPT_4O_2024_05_13: Provider.OPENAI,
    Model.GPT_4O_2024_08_06: Provider.OPENAI,
    Model.GPT_4O_2024_11_20: Provider.OPENAI,
    Model.GPT_4O_AUDIO_PREVIEW: Provider.OPENAI,
    Model.GPT_4O_AUDIO_PREVIEW_2024_10_01: Provider.OPENAI,
    Model.GPT_4O_AUDIO_PREVIEW_2024_12_17: Provider.OPENAI,
    Model.GPT_4O_AUDIO_PREVIEW_2025_06_03: Provider.OPENAI,
    Model.GPT_4O_MINI: Provider.OPENAI,
    Model.GPT_4O_MINI_2024_07_18: Provider.OPENAI,
    Model.GPT_4O_MINI_AUDIO_PREVIEW: Provider.OPENAI,
    Model.GPT_4O_MINI_AUDIO_PREVIEW_2024_12_17: Provider.OPENAI,
    Model.GPT_4O_MINI_REALTIME_PREVIEW: Provider.OPENAI,
    Model.GPT_4O_MINI_REALTIME_PREVIEW_2024_12_17: Provider.OPENAI,
    Model.GPT_4O_MINI_SEARCH_PREVIEW: Provider.OPENAI,
    Model.GPT_4O_MINI_SEARCH_PREVIEW_2025_03_11: Provider.OPENAI,
    Model.GPT_4O_MINI_TRANSCRIBE: Provider.OPENAI,
    Model.GPT_4O_MINI_TTS: Provider.OPENAI,
    Model.GPT_4O_REALTIME_PREVIEW: Provider.OPENAI,
    Model.GPT_4O_REALTIME_PREVIEW_2024_10_01: Provider.OPENAI,
    Model.GPT_4O_REALTIME_PREVIEW_2024_12_17: Provider.OPENAI,
    Model.GPT_4O_REALTIME_PREVIEW_2025_06_03: Provider.OPENAI,
    Model.GPT_4O_SEARCH_PREVIEW: Provider.OPENAI,
    Model.GPT_4O_SEARCH_PREVIEW_2025_03_11: Provider.OPENAI,
    Model.GPT_4O_TRANSCRIBE: Provider.OPENAI,
    Model.GPT_IMAGE_1: Provider.OPENAI,
    Model.O1: Provider.OPENAI,
    Model.O1_2024_12_17: Provider.OPENAI,
    Model.O1_MINI: Provider.OPENAI,
    Model.O1_MINI_2024_09_12: Provider.OPENAI,
    Model.O1_PREVIEW: Provider.OPENAI,
    Model.O1_PREVIEW_2024_09_12: Provider.OPENAI,
    Model.O1_PRO: Provider.OPENAI,
    Model.O1_PRO_2025_03_19: Provider.OPENAI,
    Model.O3: Provider.OPENAI,
    Model.O3_2025_04_16: Provider.OPENAI,
    Model.O3_MINI: Provider.OPENAI,
    Model.O3_MINI_2025_01_31: Provider.OPENAI,
    Model.O4_MINI: Provider.OPENAI,
    Model.O4_MINI_2025_04_16: Provider.OPENAI,
    Model.OMNI_MODERATION_2024_09_26: Provider.OPENAI,
    Model.OMNI_MODERATION_LATEST: Provider.OPENAI,
    Model.TEXT_EMBEDDING_3_LARGE: Provider.OPENAI,
    Model.TEXT_EMBEDDING_3_SMALL: Provider.OPENAI,
    Model.TEXT_EMBEDDING_ADA_002: Provider.OPENAI,
    Model.TTS_1: Provider.OPENAI,
    Model.TTS_1_1106: Provider.OPENAI,
    Model.TTS_1_HD: Provider.OPENAI,
    Model.TTS_1_HD_1106: Provider.OPENAI,
    Model.WHISPER_1: Provider.OPENAI,
}
