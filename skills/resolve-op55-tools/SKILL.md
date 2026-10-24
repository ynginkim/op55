---
name: resolve-op55-tools
description: "op55 음악 작업의 실행 사실을 한 곳에서 확인한다. scripts 절대 경로, Node·Python·ffmpeg·Pillow, SoundFont bank 설치 상태, 그대로 쓸 명령, 비용·라이선스·오류 처리를 돌려준다. op55-compose, op55-render, op55-verify가 먼저 읽는다."
disable-model-invocation: true
---

# op55 도구 확인

입력은 프로젝트 폴더와 이번에 할 동작(작곡, 렌더, 검수, preview)이다. 결과는 확인한 `S` 절대 경로, 갖춘 도구와 빠진 도구, 설치된 bank, 그대로 실행할 명령이다. 음악을 고르거나 고치는 판단은 하지 않는다. 그 판단은 각 작업 skill과 그 skill을 부른 playbook이 맡는다.

## 경로

`S`는 이 skill 폴더 안의 `scripts/`를 가리키는 절대 경로다. 모든 명령은 프로젝트 폴더에서 실행한다. 실행 전에 경로를 확인하고, 확인한 절대 경로를 자식 명령과 다른 skill에 그대로 넘긴다. 설치 경로에 공백이 있을 수 있으니 항상 따옴표로 감싼다.

```bash
S="<이 skill의 base directory>/scripts"
test -f "$S/render.mjs" && test -f "$S/verify.py" && echo "$S"
```

설치본 안의 배치를 바꾸지 않는다. `scripts/render.mjs`, `scripts/verify.py`, `scripts/preview.py`, `scripts/setup.mjs`, `scripts/banks.mjs`, `scripts/lib/`, `scripts/vendor/`, `scripts/examples/`, 그리고 preview용 `assets/fonts/`가 한 벌이다. preview.py는 scripts 폴더 옆의 assets/fonts를 읽으므로 두 폴더는 형제로 남아야 한다. 이 자원을 다른 skill에 복사하지 않는다.

다른 skillset이 op55를 부를 때는 확인한 `$S`를 넘긴다(showreel은 `OP55_SCRIPTS`로 받는다). 부르는 쪽이 scripts를 따로 찾으면 다른 곳에 남은 이전 사본을 잡아 다른 버전의 엔진으로 렌더할 수 있다. op55가 쓰는 파일과 형식은 `references/output-contract.md`에 있다. 그 파일을 영상에서 어떻게 쓰는지는 부르는 skillset의 문서에 있다.

## 도구

| 동작 | 필요한 것 | 확인 |
| --- | --- | --- |
| 렌더 | Node 18 이상. 승인 hash의 기준 환경은 Node 22, macOS arm64 | `node --version`, `node "$S/setup.mjs" --check` |
| 검수 | python3와 numpy, ffmpeg | `python3 -c "import numpy"`, `ffmpeg -version` |
| preview | 검수 도구에 더해 Pillow. 한글·CJK 제목이면 시스템 CJK 폰트 또는 `OP55_CJK_FONT` | `python3 -c "import PIL"` |
| bank 대체 소스 | 시스템 `tar`(.7z, .tar.xz). Linux에서 .7z는 p7zip 필요 | setup.mjs 머리 주석 |

빠진 도구는 설치 명령과 함께 반환한다(`python3 -m pip install numpy pillow`, ffmpeg는 OS 패키지 관리자). 사용자 환경에 전역 설치하는 일은 사용자가 정한다.

## SoundFont bank

bank는 `$OP55_BANKS`, 없으면 `$XDG_CACHE_HOME/op55/banks`, 그것도 없으면 홈 폴더의 .cache/op55/banks에 둔다. 프로젝트에 복사하지 않는다. 목록과 hash의 정본은 `scripts/lib/banks.mjs`다.

| bank | 기본 | 크기 | 라이선스와 크레딧 |
| --- | --- | --- | --- |
| `gm` GeneralUser GS 2.0.3 | 예 | 32,319,396 bytes | GeneralUser GS License v2.0. 개인·상업 음악에 자유. 크레딧 없음 |
| `upright` Upright Piano KW | 예 | 57,377,848 bytes | CC0 1.0. 크레딧 없음 |
| `grand` Salamander Grand Piano V3 | 아니오 | 약 300 MB 다운로드, 디스크 1,266,462,334 bytes, 렌더 중 약 1.8 GB RAM | CC BY 3.0. 크레딧 필수: "Salamander Grand Piano by Alexander Holm (CC BY 3.0)" |

```bash
node "$S/setup.mjs" --check     # 보고만 하고 받지 않는다. 기본 bank가 없으면 exit 1
node "$S/setup.mjs"             # 기본 bank gm + upright, 약 88 MB
node "$S/setup.mjs" grand       # 선택. 받기 전에 용량과 크레딧 조건을 사용자에게 알린다
node "$S/banks.mjs" gm strings  # bank 안의 preset 찾기(bankMSB:program 이름). --drums는 drum kit 목록
```

setup은 새로 받은 파일의 SHA-256을 확인한다. 이미 있는 파일은 크기만 보고 건너뛴다. 매번 hash를 검사한다고 보고하지 않는다. 기본 bank는 무료이고 처음 쓸 때 받는 것이 원래 동작이다. 음악 생성 API 비용은 없지만 다운로드, 디스크, CPU 시간은 든다.

## 명령

명령은 이 표를 그대로 복사한다. 경로 부분만 실제 프로젝트에 맞춘다.

| 동작 | 명령 | 비용(소스 설명값, 현재 실측 아님) |
| --- | --- | --- |
| 악보 확인 | `node "$S/render.mjs" --score audio/music/score.mjs --describe` | 렌더 없음 |
| 렌더 | `node "$S/render.mjs" --score audio/music/score.mjs --out audio/music/music.wav --analysis audio/music/analysis.json` | 오케스트라 1분 약 5초, 촘촘한 synth 5분 약 35초. WAV는 초당 288,000 bytes(60초 17.28 MB) |
| 층 확인 | 렌더 명령 뒤에 `--stems a,b --stems-dir audio/music/stems` | stem마다 WAV 하나만큼 디스크 |
| 원인 층 진단 | `node "$S/render.mjs" --score audio/music/score.mjs --mute <name> --no-analysis --out dbg/<name>.wav` | 진단 렌더마다 WAV 하나. 납품 폴더에 쓰지 않는다 |
| 검수 | `python3 "$S/verify.py" audio/music/music.wav --analysis audio/music/analysis.json --waveform-png --spec 0,30` | 미측정. 실제 작업에서 시간을 기록 |
| showreel test mix | 검수 명령 뒤에 `--mix timeline.json --mix-py "<showreel scripts>/mix.py"` | verify/mix_test.wav 하나 |
| preview(요청 시만) | `python3 "$S/preview.py" audio/music/music.wav --check` | 1분 약 2.5 MB, 약 20초 |

render.mjs는 score 모듈을 import해서 실행한다. 이번 작업에서 쓰지 않았거나 사용자가 주지 않은 score는 코드로 보고 먼저 읽는다.

## 라이선스와 금지

- 음악 생성 서비스를 부르지 않는다. loop나 sample pack을 받지 않는다. 라이선스를 확인하지 않은 오디오를 쓰지 않는다. 쓸 수 있는 소리는 `scripts/lib/banks.mjs`의 bank와 synth voice뿐이다.
- 엔진 notices는 `scripts/vendor/spessasynth_core.LICENSE`, `scripts/vendor/stb-vorbis.LICENSE`, `scripts/vendor/README.md`에 있다. 폰트는 `assets/fonts/OFL-InstrumentSerif.txt`, `assets/fonts/OFL-JetBrainsMono.txt`(SIL OFL 1.1)다.
- bank 라이선스의 현재 원문과 배포 URL은 결과물을 외부에 배포하기 직전에 공식 출처에서 다시 확인한다.
- 설치본의 scripts를 고치지 않는다. 엔진을 바꾸는 일은 op55 저장소에서 승인 hash 회귀(tools/regress.sh)로 확인하는 별도 작업이다.

## 반환

- 확인한 `S` 절대 경로, 확인 날짜, 도구 버전.
- 빠진 도구와 설치 명령. 설치되지 않은 bank와 명령·용량·크레딧 조건.
- 경로를 찾지 못했으면 시도한 경로. 추정한 경로로 실행하지 않는다.
