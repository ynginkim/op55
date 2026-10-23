---
name: op55-compose
description: "영상 BGM의 cue sheet와 격자, 편곡을 정하고 op55 score.mjs를 작성한다. 길이·영상 기준점·나레이션 구간·기존 격자를 받아 audio/music/cue.md와 score.mjs를 돌려준다."
disable-model-invocation: true
---

# op55 작곡

Read ../resolve-op55-tools/SKILL.md. 아래 `$S`는 그 skill이 확인한 scripts 절대 경로다.

당신은 작곡가이자 편곡자이고 소리를 들을 수 없다. 그래서 음악을 코드로 쓰고, 렌더와 검수가 숫자와 그림으로 확인할 수 있게 계획을 남긴다.

## 입력과 결과

| 입력(정할 수 없는 것만 묻는다) | 결과(프로젝트 안, 기본 audio/music/) |
| --- | --- |
| 길이 또는 영상의 timeline. 꼭 맞아야 할 지점(컷, 로고, 마지막 프레임) | `cue.md`: 섹션별 시작 마디, energy(0-1), 소리에서 바뀌는 것, 강세(마디와 이유), 나레이션 공백 |
| 나레이션 여부와, 있으면 줄별 시간 | `score.mjs`: 격자, 섹션, 강세, gaps, ensemble, compose. 다시 렌더하면 같은 WAV가 바이트까지 다시 나온다 |
| 분위기나 참고 곡(있으면) | 한 줄씩의 선택 보고: 장르, palette, 템포·조성, 형식 |
| 기존 영상이 있으면 그 analysis.json, music.meta.json, cue 목록 | 지키지 못한 입력이 있으면 그 목록 |

장르, palette, 템포, 조성, 형식, 섹션 길이는 직접 정한다. 정한 것은 보고에 한 줄씩 적는다.

## 순서

1. **Cue sheet.** `audio/music/cue.md`를 쓴다. energy에는 대비가 필요하다. 정점(0.85 이상)은 cue의 4분의 1 이하, 중간 근처에 숨 돌리는 구간(0.3-0.45) 하나, 모든 섹션 경계에서 들리는 악기 변화가 있어야 한다.
2. **격자부터.** 영상의 기준점이 다운비트에 오도록 `bpm`, `beatsPerBar`, `t0`를 정한다. 영상이 이미 있으면 그 격자를 그대로 가져온다(`references/score.md`의 grid 절). 모든 음은 `bar(k, beat)`로 놓고 초 단위를 직접 쓰지 않는다.
3. **score.mjs 작성.** 예제 하나를 복사해 시작한다. `../resolve-op55-tools/scripts/examples/starter.score.mjs`(32초, synth), `../resolve-op55-tools/scripts/examples/eroica.score.mjs`(55초, sampled 오케스트라와 synth 층), `../resolve-op55-tools/scripts/examples/pstack-harness.score.mjs`(300초 나레이션 설명 영상, synth). 명령에서는 같은 파일을 `$S/examples/` 아래로 부른다. API는 `references/score.md`, 편곡 기술은 `references/arranging.md`를 읽는다.
4. `node "$S/render.mjs" --score audio/music/score.mjs --describe`로 격자·섹션·강세·ensemble이 의도대로 읽히는지 확인한다. 렌더와 검수는 이 skill의 일이 아니다.

## Palette: synth, sampled, 둘 다

| cue의 성격 | 쓸 것 |
| --- | --- |
| 기술, 설명, 모션 그래픽, 미니멀, 전자음, 째깍거리는 기계적 질감 | synth voice(`pad bass kick tick pluck arp glass bell piano fx`). 정밀하고 가볍고 bank가 필요 없다 |
| 오케스트라, 시네마틱, 감정, 피아노 중심, 어쿠스틱, 재즈, 듣는 사람이 실제 악기를 아는 모든 것 | sampled part(`ensemble`): 현, 금관, 목관, 팀파니, 피아노, drum kit |
| 대부분의 영상 | 둘 다. 따뜻함과 실감은 sampled lead·bed, 무게와 싱크는 synth sub, kick, tick, riser, boom |

General MIDI 샘플은 정직하지만 화려하지 않다. 중간 음역, 중간 velocity, 솔로보다 합주, expression swell과 약간의 공간에서 가장 좋게 들린다. 관용구는 `references/arranging.md`에 있다.

## 지켜야 할 것

직접 불려도 아래는 그대로 지킨다.

- 음악 생성 서비스를 부르지 않는다. loop나 sample pack을 받지 않는다. 라이선스를 확인하지 않은 오디오를 쓰지 않는다. `ensemble`에는 resolve-op55-tools의 bank 표에 있는 bank만 쓴다.
- **결정성.** `Math.random`이나 시계를 쓰지 않는다. 모든 무작위 선택은 `makeRng('<name>')`로 한다. 같은 score, seed, bank면 같은 바이트다.
- **큰 hit는 다운비트에** 화성 해결과 함께 온다. 직전에 짧게 내려가고(`automation`), 뾰족한 층은 작게 두어 limiter가 hit를 누르지 않게 한다.
- **sampled 싱크 지점.** sampled attack은 note-on 뒤 2-8 ms에 절반 크기에 닿는다. 싱크 음은 약 5 ms 일찍 치거나 part에 `lead`를 준다. 확인은 op55-verify의 onset 줄이 한다.
- **크레딧.** `grand` 같은 크레딧 필수 bank를 쓰면 그 사실을 보고에 남긴다. render가 `music.meta.json`의 credits에 기록한다.
- 기존 영상이 쓰는 시간 계약을 바꿔야 하면 바꾸기 전에 그 이유와 영향을 반환한다. 사용자가 승인하지 않은 계약 변경을 하지 않는다.

판단에는 세 principle을 적용한다. 나레이션이 있으면 Read ../principle-protect-the-voice/SKILL.md, 기존 영상이나 cue가 있으면 Read ../principle-freeze-the-grid/SKILL.md, palette와 강세를 고를 때 Read ../principle-arrange-for-the-picture/SKILL.md. 적용한 원칙 이름과 그 때문에 바뀐 선택 하나를 보고에 남긴다.

같은 편곡 문제가 두 번 생기면 `references/arranging.md`에 기록한다. 공개 저장소이므로 프로젝트 자료나 고객 정보를 넣지 않는다.

## 반환

- `cue.md`, `score.mjs` 경로와 한 줄씩의 선택.
- 정하지 못한 입력(길이, 기준점, meter)과 묻지 않고 쓴 기본값.
- 지키지 못한 시간 계약이나 나레이션 구간, 그 이유.

렌더할지, 다시 고칠지는 이 skill을 부른 playbook이 정한다.
