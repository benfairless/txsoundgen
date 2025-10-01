TXSoundGen
==========

![GitHub](https://img.shields.io/github/license/benfairless/txsoundgen?style=flat-square)
![GitHub release](https://img.shields.io/github/v/release/benfairless/txsoundgen?style=flat-square)

# WIP! This code is not yet fully functional. Low level components are relatively complete, but
# there is not a functional client for usage.

Sound pack generator for EdgeTX/OpenTX radios.

Unhappy with downloading sound packs for your radio only to find they are incomplete?
TXSoundgen uses self-hosted and cloud text-to-speech generation to create comprehensive
voice packs to suit your needs, giving you a consistent voice pack that covers default
sounds as well as any custom lines you would like to add.

## Technical details

All audio files are generated as 16kHz single-channel `.wav` files, ensuring
compatibility with all EdgeTX / OpenTX radios.

Currently supported speech engines:

- [Amazon Polly](https://aws.amazon.com/polly/)
- [Piper](https://github.com/OHF-Voice/piper1-gpl)


## Requirements

- Python 3.14
- Poetry
- ffmpeg

## Planned UX

Create a custom voicepack configuration:
``` bash
> txsoundgen init --provider piper

Voicepack config created from template at 'my-voicepack.yaml'
```

Build your custom voicepack:
``` bash
> txsoudgen build my-voicepack.yaml

Building voicepack 'my-voicepack' using Piper TTS.
[####################-------------------------------------] [57/236]

Completed building voicepacks.
my-voicepack: ./voicepacks/my-voicepack.zip
```

## Future capabilities

- CLI tool for building voicepacks.
- Packaging as docker container.
- Remove ffmpeg requirement and use native Python method for wave conversion.
- Proper webpage with audio examples.
- Web repository of existing sound packs.
- Generate default 'system' data from EdgeTX repository automatically.
- Cache provider responses, speeding up generation where sound data already exists locally.
- Multiprocessing.
- Support for more TTS services.
- Multilingual support.

## Notes

https://pypi.org/project/diff-cover/
https://docs.astral.sh/ruff/integrations/
https://github.com/EdgeTX/edgetx-sdcard-sounds
https://docs.astral.sh/uv/guides/integration/pre-commit/
