### 기존 cue 고치기

기존 cue에 대한 피드백, 대사 공백 변경, 완성 영상의 음악 교체다. 형제 skill 경로는 이 mode 폴더 기준이다.

1. 기존 score, meta, analysis와 영상 소비값을 확인한다.
2. 피드백을 분류하고 변경·재사용 범위와 비용을 정한다.
3. 필요한 악보·편곡을 수정하고 영향을 받는 산출물을 다시 만든다.
4. 수치·그림·영상 경계와 mix를 다시 검수한다.
5. 바뀐 것과 재사용 근거를 전달하고 청취를 요청한다.

**1.** Read ../resolve-op55-tools/SKILL.md. 기존 score.mjs, music.meta.json, analysis.json, cue.md를 읽는다. 영상이 있으면 Read ../resolve-op55-tools/references/showreel-contract.md 다음에 영상이 실제로 소비하는 값을 찾는다. `barN`, `music.hitN`, `music.start`, 음악 envelope에 반응하는 장면, 화면에 나오는 credits다. meta가 없는 기존 음악이면 analysis.json이나 cue list에서 grid를 복구한다. meter가 자료에 없고 원본도 말하지 않으면 사용자에게 묻는다. 4/4를 가정하지 않는다.

**2.** **principle-freeze-the-grid**를 적용한다. 피드백을 다음으로 나눈다.

- 음색, 밀도, 균형처럼 표면만 바뀌는 수정. 같은 grid와 hit를 유지한다.
- 섹션이나 강세의 추가·이동. analysis의 hits가 다시 번호 매겨진다.
- VO 위치나 gap 변경. score의 gaps와 편곡이 바뀐다.
- BPM, beat, t0, meter, firstDownbeat 변경. 시간 계약이 바뀐다.
- credits가 바뀌는 bank 변경. 화면 credits가 달라질 수 있다.

분류마다 다시 만들 산출물, 재사용할 것, 비용(재렌더 시간, 영상 장면 재렌더, mix와 finish)을 적는다. 시간 계약을 바꾸거나 영상 장면을 다시 렌더해야 하면 실행 전에 범위와 비용을 알리고 승인을 받는다. 이 분류는 이번 cue의 수정 지시다. 이 skillset의 결함이 반복되면 그 일을 맡은 skill의 reference에 기록한다.

**3.** Read ../op55-compose/SKILL.md. 악보를 고친다. 나레이션이 바뀌었으면 **principle-protect-the-voice**, 화면 재질에 맞춘 변경이면 **principle-arrange-for-the-picture**를 적용한다. 이어서 Read ../op55-render/SKILL.md. 음악 파일을 다시 만든다. 유료 VO·SFX와 기존 영상 파일은 지우지 않는다.

**4.** Read ../op55-verify/SKILL.md. 미달·미측정·N/A는 `playbooks/create-cue.md` 4단계와 같은 방법으로 다룬다. 영상이 있으면 새 analysis의 beats와 downbeats가 기존 큐와 1 ms 안에서 맞는지 본다. 바뀐 `music.hitN` 번호와 그것을 쓰는 장면, 새 WAV의 envelope를 쓰는 장면을 대조한다. 나레이션이 있으면 `--mix`로 모든 줄을 다시 본다.

**5.** 바뀐 파일, 다시 만든 것과 이유, 재사용한 것과 근거(같은 grid, 같은 hit 번호, envelope를 소비하지 않는 장면 등), 영상 쪽에서 다시 할 일(장면 렌더, mix, finish), verify 수치와 credits를 보고한다. 적용한 principle과 바뀐 결정 하나를 남기고 mode의 납품 요청 문장으로 청취를 요청한다.

완성 영상의 음악 교체는 이 playbook의 분기다. 기존 영상이 쓰는 grid로 새 score를 쓰고, 렌더한 뒤 새 beats가 기존 큐와 1 ms 안인지 확인한다. grid만 같다는 이유로 영상 재사용을 보장하지 않는다. 실제로 소비되는 hit, cue, envelope가 같거나 그 값을 쓰지 않는 장면만 재사용한다.
