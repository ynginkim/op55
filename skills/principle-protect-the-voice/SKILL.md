---
name: principle-protect-the-voice
description: "나레이션이 있는 영상 음악에서 대사 구간의 음역·선율·밀도를 비우고 공백과 음악만 나오는 구간에서 풀어 주는 판단 원칙."
disable-model-invocation: true
---

# 대사 먼저

**Why:** 나레이션은 300-4000 Hz를 쓴다. 음악이 그 대역을 바쁜 선율로 채우면 말이 묻힌다. 영상의 mix 단계가 음악을 낮추고 덕킹해도, 줄마다 목소리가 배경보다 9 dB 이상 크다는 보장은 악보에서 대역을 비울 때만 생긴다.

**Pattern:** 목소리 아래에서는 300-4000 Hz의 바쁜 lead를 빼고 bass, sub, kick, 4 kHz 위의 tick으로 움직임을 나른다. pad는 500-1200 Hz로 low-pass하고 bell과 glass는 드물고 작게 둔다. sampled 현은 낮은 음역에서 expression 0.3-0.5로 쓴다. 공백(`gaps`, 1.2초 이상)에서는 pad를 열고 +1.6 dB, bell이나 피아노 악구로 숨을 쉰다. 음악만 나오는 구간은 선율, 밝기, 층을 자유롭게 쓴다. 결과는 op55-verify의 mix 줄이 모두 통과하는지로 확인한다.

**Stop:** 나레이션이 없는 cue와 음악만 나오는 구간(콜드 오픈, 피날레, 엔드 카드)에는 적용하지 않는다. 그 구간에서 이 원칙을 이유로 선율을 막지 않는다.
