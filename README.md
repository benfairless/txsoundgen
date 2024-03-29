TXSoundGen
==========

![GitHub](https://img.shields.io/github/license/benfairless/txsoundgen?style=flat-square)
![GitHub release](https://img.shields.io/github/v/release/benfairless/txsoundgen?style=flat-square)

Sound pack generator for EdgeTX/OpenTX radios.

Unhappy with finding sound packs for your radio only to find they are incomplete?
TXSoundgen uses cloud text-to-speech generation to create comprehensive voice packs to
suit your needs, giving you a consistent voice pack that covers default sounds as well
as any custom lines you would like to add.

## Technical details

All audio files are generated as 16kHz single-channel `.wav` files, ensuring
compatibility with all EdgeTX / OpenTX radios.

Currently supported speech engines:

- Amazon Polly.
