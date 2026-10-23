---
name: op55-render
description: "op55 score.mjs를 오프라인으로 렌더해 48kHz 24bit WAV, analysis.json, music.meta.json을 만든다. 요청이 있을 때만 기존 WAV로 스펙트로그램 preview MP4와 확인용 스틸을 만든다."
disable-model-invocation: true
---

# op55 렌더

Read ../resolve-op55-tools/SKILL.md. 아래 `$S`, 명령, bank 조건은 그 skill이 확인한 값을 쓴다.

## 입력과 결과

| 분기 | 입력 | 결과 |
| --- | --- | --- |
| 음악 렌더 | `score.mjs`, 설치된 bank | `music.wav`(48 kHz, 24-bit, stereo, 기본 -13 LUFS integrated, 렌더 기준 -1.3 dBTP 이하), `analysis.json`(`bpm, beats, downbeats, hits, energy`를 정확한 격자에서 계산), `music.meta.json`(grid, sections, accents, gaps, onsets, master 보고, **credits**) |
| 선택 stem | 위와 같고 `--stems a,b --stems-dir DIR` | 이름을 준 층의 dry stem(glue·limiter 전, 최종 gain 적용) |
| preview(요청 시만) | 기존 WAV, 옆의 `music.meta.json`(없어도 됨), 제목 | `music.preview.mp4`와 `--check`의 25·50·75% JPG 세 장 |

master 목표는 score의 `master.lufs`다. 기본 -13이고 다이내믹한 오케스트라 cue는 -14~-15를 고를 수 있다. 엔진 ceiling은 -1.35 dBTP다.

## 음악 렌더

1. resolve-op55-tools로 `$S`, Node, 필요한 bank를 확인한다. score가 쓰는 bank가 없으면 렌더하지 않고 설치 명령과 용량을 반환한다.
2. score 출처를 확인한다. render.mjs는 score 모듈을 실행한다. 이번 작업에서 쓰지 않았거나 사용자가 주지 않은 score는 먼저 읽는다.
3. resolve-op55-tools 명령 표의 렌더 명령을 실행한다. 층을 확인해야 하면 `--stems`, 원인 층을 찾아야 하면 `--mute`를 붙이되 진단 출력은 dbg/ 같은 납품 밖 폴더에 쓴다.
4. 세 파일이 생겼는지, WAV 길이가 score의 `duration`과 맞는지 확인한다. 품질 판정은 op55-verify가 한다.

결정성은 바꾸지 않는다. 같은 score, seed, bank, Node면 같은 바이트다. 설치본의 `../resolve-op55-tools/scripts/lib/`와 `../resolve-op55-tools/scripts/vendor/`를 고치지 않는다.

## Preview 분기

사용자가 preview, 공유용 음악 영상, 구간을 보며 검토할 영상을 요청했을 때만 만든다. 일반 음악 납품에 자동으로 붙이지 않는다. 기존 WAV만 받은 단독 preview 요청이면 작곡과 음악 렌더를 하지 않는다.

```bash
python3 "$S/preview.py" audio/music/music.wav --check [--title "Product launch BGM"] [--out audio/music/music.preview.mp4]
```

- Pillow와 ffmpeg가 필요하다. 폰트는 `../resolve-op55-tools/assets/fonts`에 들어 있다(OFL). 한글 제목은 시스템 CJK 폰트나 `OP55_CJK_FONT`가 필요하다.
- `music.meta.json`이 없으면 섹션·강세·마디 대신 초 눈금이 나온다. 그 사실을 반환한다.
- 화면 구성, 크기 옵션, 용량, 공유 방법은 `references/preview.md`를 읽는다.
- 외부 업로드와 게시는 별도 권한이다. 이 skill은 파일만 만든다.

세 스틸의 판정은 op55-verify가 `references/preview.md`의 확인 항목으로 한다.

## 반환

- 만든 파일 경로와 크기, 걸린 시간.
- 실패하면 실패한 명령, stderr 요약, 설치되지 않은 bank, 만들지 못한 파일.
- `music.meta.json`의 credits 줄(있으면).

다시 렌더할지는 이 skill을 부른 playbook이 op55-verify의 결과로 정한다.
