---
name: principle-freeze-the-grid
description: "기존 영상이나 cue에 붙은 음악의 시간 계약(beat, t0, meter, 첫 다운비트, hit 번호)을 지키고, 바꿔야 할 때는 다시 만들 범위와 비용을 먼저 밝히는 판단 원칙."
disable-model-invocation: true
---

# 격자 고정

**Why:** 영상은 음악의 시간 계약을 소비한다. 컷은 다운비트에, 장면 큐는 hit 번호에, 음악에 반응하는 장면은 WAV envelope에 붙는다. 격자가 바뀌면 소리만 고친 요청이어도 장면 렌더, mix, finish를 다시 해야 한다.

**Pattern:** 영상이나 기존 cue가 있으면 그 grid를 그대로 쓴다. `music.meta.json`의 beat, t0, beatsPerBar, firstDownbeat를 먼저 쓰고, 없으면 analysis.json이나 cue list에서 복구한다. meter가 자료에 없으면 원본에서 확인하고 그래도 모를 때만 묻는다. 계약을 바꿔야 하면 바꾸기 전에 영향받는 산출물과 비용을 밝히고 승인을 받는다. grid가 같아도 섹션·강세 추가로 hit 번호가 바뀌거나 envelope를 쓰는 장면의 소리가 바뀌면 그 장면을 재사용한다고 말하지 않는다.

**Stop:** 아직 영상이 없는 새 cue, 또는 사용자가 시간 계약 변경을 승인한 경우에는 적용하지 않는다. 그때는 새 격자를 영상 기준점에 맞춰 정한다.
