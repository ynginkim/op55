---
name: op55-verify
description: "op55 렌더 결과를 verify.py의 수치와 파형·스펙트로그램 그림으로 검수하고, 항목마다 통과·미달·미측정·N/A와 원인 후보를 돌려준다. preview를 요청받았으면 세 스틸도 확인한다. 사람의 청취를 대신하지 않는다."
disable-model-invocation: true
---

# op55 검수

Read ../resolve-op55-tools/SKILL.md. 아래 `$S`와 명령은 그 skill이 확인한 값을 쓴다.

소리를 들을 수 없으니 숫자와 그림으로 증명한다. `verify.py`는 WAV를 그 악보(`music.meta.json`)와 비교한다.

## 입력과 결과

입력은 `music.wav`, `analysis.json`, 옆의 `music.meta.json`이다. showreel 프로젝트면 `timeline.json`과 showreel의 mix.py 경로, preview를 요청받았으면 세 JPG가 더해진다. 결과는 항목별 상태표, 근거 수치, 읽은 그림 목록, 원인 후보 층, 다음 수정 후보다. 납품 파일을 바꾸지 않는다.

```bash
python3 "$S/verify.py" audio/music/music.wav --analysis audio/music/analysis.json --waveform-png --spec 0,30
```

- `--spec` 시작점은 cue 안에 있어야 한다. 30초 미만 cue는 `--spec 0`을 쓴다. 넓은 범위가 필요하면 `--bars 36-44`, 출력 폴더는 `--out-dir`.
- showreel 프로젝트면 `--mix timeline.json --mix-py "<showreel scripts>/mix.py"`를 붙인다. 계약은 `../resolve-op55-tools/references/showreel-contract.md`에 있다.
- 출력한 PNG(`hits_waveform.png`, `spec_*.png`)는 Read 도구로 직접 연다. 열지 않은 그림은 검사하지 않은 것이다.
- verify 출력, 로그, 진단 렌더(dbg/)는 프로젝트 안에 쓰고 /tmp 같은 프로젝트 밖에 쓰지 않는다. 진단 폴더는 보고한 뒤 사용자에게 지울지 묻고, 묻기 전에 지우지 않는다.

## 판정

통과 기준의 정본은 `references/verify.md`의 Pass criteria 표다. 여기에 숫자를 다시 적지 않는다. verify.py는 품질이 나빠도 exit code를 바꾸지 않는다. exit 0만으로 통과라고 쓰지 않고 줄마다 읽는다.

필수 항목은 loudness(목표 ±0.5 LUFS, true peak), clipping, DC, fade 뒤 무음, limiter, grid, kick onset, 각 accent onset, 섹션 순위 상관, 가장 강한 강세 마디, 스펙트로그램, 그리고 showreel이면 mix의 모든 나레이션 줄이다. 각 항목을 아래 넷 중 하나로 적는다.

| 상태 | 언제 |
| --- | --- |
| 통과 | 그 줄이 ✓이고 그림에서도 문제가 없음. 숫자만 나오는 항목(clipping, DC, fade 뒤, 강세 마디)은 verify.md 기준과 비교해 맞음 |
| 미달 | ✗. 순위 상관의 △. accent의 `△ late attack`. mix 줄의 △ 또는 ✗. 스펙트로그램의 세로 줄무늬, 클릭, 구멍, 나레이션 아래 1.3-4 kHz가 밝음. accent의 `soft`는 의도한 swell이라는 근거가 score에 없으면 미달 |
| 미측정 | 실행할 수 있었던 필수 검사가 빠짐. `music.meta.json` 없음(loudness와 analysis grid만 검사됨), `[mix] showreel mix.py not found`, `[mix] no narration table`, `[mix] ! timeline music.file is ...`, `[spec] ... skipped`, onset 줄이 없는 accent, 열지 않은 PNG |
| N/A | 해당 없는 검사. 이유와 대체 확인을 함께 적음 |

N/A로 두는 경우는 정해져 있다.

- kick onset: synth `kick`이 없거나 4개 미만이면 verify가 그 줄을 출력하지 않는다. sampled drum kit의 kick은 측정 대상이 아니다. 대체 확인은 파형과 accent onset이다.
- 순위 상관: 유효 섹션이 3개 미만이면 출력되지 않는다. 대체 확인은 섹션별 LUFS 표다.
- mix margin: 나레이션이 없는 곡.

N/A를 없애려고 다시 렌더하지 않는다. 미측정은 원인을 고쳐 다시 검사한다(예: `--spec`을 cue 안의 시작점으로, `--mix-py` 경로 전달). meta가 없는 기존 WAV는 meta를 복구할지 다시 렌더할지 playbook이 정하도록 반환한다.

## 원인 찾기

- 늦은 accent: resolve-op55-tools 명령 표의 원인 층 진단 렌더(`--mute <name>`)를 층마다 dbg/에 만들고 각 WAV를 verify한다. 음량 균형이 바뀌므로 offset만 읽는다. 같은 다운비트의 synth bass나 sampled 화음이 원인인 경우가 많다.
- limiter가 hit를 누름: `--stems`로 뾰족한 층을 찾는다. 증상별 원인과 수정 후보는 `references/verify.md`의 Common problems 표를 읽는다.
- 같은 문제가 두 번 생기면 `references/verify.md`의 Common problems에 기록한다. 공개 저장소이므로 프로젝트 자료를 넣지 않는다.

## Preview 스틸(요청받았을 때만)

`../op55-render/references/preview.md`의 확인 항목으로 25·50·75% JPG 세 장을 직접 연다. 색이 playhead에서 정확히 멈추는지, NOW 라벨이 그 순간의 섹션인지, 라벨이 겹치거나 화면 밖으로 나가지 않는지, 제목(한글 포함)이 그려졌는지 본다. 스틸 확인은 사람이 동영상을 보고 듣는 일을 대신하지 않는다.

## 반환

- 항목별 상태(통과, 미달, 미측정, N/A)와 근거 수치, 연 그림 목록.
- 미달·미측정의 원인 후보 층과 다음 수정 후보(악보 수정, 재렌더, 경로 전달).
- `music.meta.json`의 credits 줄.
- 사람 청취는 아직 하지 않았다는 사실.

다시 고칠지, 어느 단계로 돌아갈지, 언제 멈출지는 이 skill을 부른 playbook이 정한다.
