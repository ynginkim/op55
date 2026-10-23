### 새 cue 만들기

새 BGM, 또는 지켜야 할 기존 score·grid가 없는 요청이다. 형제 skill 경로는 이 mode 폴더 기준이다.

1. 길이, 영상 기준점, 나레이션 구간과 판정 기준을 확인한다.
2. cue sheet와 grid, 편곡을 정하고 악보를 작성한다.
3. 악보를 렌더하고 음악 파일과 분석·meta를 만든다.
4. 수치·그림·해당되는 mix를 검수하고 필요한 수정을 반복한다.
5. 파일과 credits, 검사 결과를 전달하고 사람의 청취를 요청한다.

**1.** Read ../resolve-op55-tools/SKILL.md. `$S`, 도구, bank를 확인한다. 브리프에서 길이 또는 timeline, 꼭 맞을 지점, 나레이션 여부와 줄별 시간, 분위기를 채운다. 직접 정할 수 없는 필수 정보만 한 번에 하나 묻는다. 이 cue에 해당하는 필수 검사와 N/A가 될 항목을 미리 적는다(나레이션이 없으면 mix margin, synth kick이 없으면 kick onset). 이미 있는 영상의 격자를 지켜야 하거나 기존 cue를 고치는 요청이면 `playbooks/revise-cue.md`로 바꾼다.

**2.** Read ../op55-compose/SKILL.md. 나레이션이 있으면 **principle-protect-the-voice**, palette와 강세에는 **principle-arrange-for-the-picture**를 적용한다. 반환된 cue.md, score.mjs, 정하지 못한 입력을 확인한다. 기준점이나 meter를 정하지 못했으면 3단계로 가지 않고 묻는다.

**3.** Read ../op55-render/SKILL.md. 음악 렌더 분기를 실행한다. bank가 없다는 반환이면 기본 bank는 resolve-op55-tools의 설치 명령으로 받고, grand는 용량과 크레딧 조건을 알린 뒤 받는다. 실패한 명령과 stderr가 score의 오류를 가리키면 2단계로 돌아간다.

**4.** Read ../op55-verify/SKILL.md. 반환된 상태표를 이렇게 다룬다.

- 미달: 원인 후보가 편곡이나 score 값(층 gain, `lead`, 시작 시각, `levels`)이면 2단계에서 고치고 3단계부터 다시 한다. 같은 score의 재렌더로 풀리는 문제(bank 설치 후 등)면 3단계로 돌아간다.
- 미측정: 경로나 옵션을 고쳐 op55-verify만 다시 부른다(`--spec` 시작점, `--mix-py` 경로).
- N/A: 이유와 대체 확인을 5단계 보고로 옮긴다. 다시 렌더하지 않는다.

필수 미달·미측정이 남으면 5단계로 가지 않는다. 수정을 거듭해도 같은 항목이 나아지지 않으면 멈추고 시도한 것과 수치를 보고해 사용자의 판단을 받는다. 끝내 고칠 수 없는 항목은 5단계 보고의 앞 문장에 적는다.

**5.** 파일 목록, 한 줄 선택(장르, palette, 템포·조성, 형식), verify 수치, N/A와 그 이유, `music.meta.json`의 credits 줄을 보고한다. 적용한 principle 이름과 그 때문에 바뀐 결정 하나를 남긴다. 마지막으로 mode의 납품 요청 문장으로 청취를 요청한다.

preview를 요청받았으면 5단계 전에 op55-render의 preview 분기로 MP4와 스틸을 만들고, op55-verify가 세 스틸을 확인한다. 기존 WAV만 받은 단독 preview 요청이면 2단계와 3단계를 `skip: 기존 WAV 사용`으로 두고, 1단계에서 WAV와 meta가 있는지 확인한 뒤 preview 분기로 간다. 외부 업로드는 별도 권한이다.
