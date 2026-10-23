# op55 skillset 설계

Status: implemented, verification in progress. 이 문서는 단일 `op55` skill을 mode·playbook·skill·principle 구조로 옮긴 결과와 그 이유, 검증 기록을 담는다. 변환 계획은 meta-harness 저장소의 examples/op55/plan.md(기준점 op55 828990b)이며, 이 저장소에는 복사하지 않았다.

## 목표와 범위

영상 BGM을 코드로 작곡하고 렌더·마스터링·검수까지 끝내는 기존 기능을 그대로 두고, 흐름(playbook), 수행(skill), 판단(principle), 이를 운용하는 mode로 나눈다. 공개 설치 명령 `npx skills add ynginkim/op55`는 바뀌지 않으며 여덟 skill이 한 벌로 설치된다.

바꾸지 않은 것: 렌더 엔진(scripts/lib, scripts/vendor, DSP)의 바이트, score module API, 세 예제와 승인 hash(tools/regress.sha256), verify.py와 preview.py의 동작과 출력 형식. 파일은 위치만 옮겼다.

이 저장소 밖의 소비자(video-creator의 SessionStart 훅과 CLAUDE.md, showreel의 preflight와 문서)는 이번 변경에 포함하지 않는다. 아래 이전 장부에 후속 작업으로 남긴다.

## 판정 기준

| 기준 | 확인 방법 | 통과 기준 |
| --- | --- | --- |
| 기존 기능 보존 | 원본 SKILL.md 줄별 대응표, 옮긴 파일의 SHA-256 대조 | 기능을 근거 없이 지우지 않음. 옮긴 scripts·assets·references의 바이트가 원본과 같음(문서 경로 수정 세 곳 제외) |
| 같은 소리 | `tools/regress.sh` | 세 예제 WAV가 승인 hash와 바이트까지 같음(Node 22, macOS arm64) |
| 구조 | `python3 scripts/check.py .`, `python3 scripts/selftest.py` | 오류 0. 오류 주입이 실패로 잡힘 |
| 설치 | 빈 Git 프로젝트에 이 저장소 경로로 `npx skills add <path> -a claude-code -a codex -y` | 여덟 skill만 설치되고 형제 참조가 열림 |
| 동작 | 합성·sampled·odd meter 예제 렌더, verify.py 출력과 PNG 판독, preview `--check` | 각 필수 항목을 통과·미달·미측정·N/A로 판정. exit 0만으로 통과라 쓰지 않음 |
| 사람 판정 | 사람이 직접 청취 | 이 저장소의 검증으로 대신하지 않음 |

## 구성과 선택 이유

| 역할 | 요소 | 원본 출처 | 남긴 이유 |
| --- | --- | --- | --- |
| mode | `op55-mode` | SKILL.md:1-8, 23-32, 49 | 요청을 보고 playbook을 고르고, skill이 돌려준 결과로 다음 단계를 정한다. 유일한 자연어 진입점 |
| playbook | `create-cue` | SKILL.md:34-49 | 새 cue는 그래프 전체를 지난다. 시작 파일이 브리프다 |
| playbook | `revise-cue` | references/showreel.md:24-30, verify.md:27-43 | 기존 score·meta·영상 소비값에서 시작하고 재사용 범위를 먼저 정한다. 시작 파일과 무효화 범위가 create-cue와 다르다 |
| skill | `resolve-op55-tools` | SKILL.md:10-21, scripts/, assets/, lib/banks.mjs | 경로·도구·bank·명령·비용·라이선스의 한 곳. scripts와 fonts를 원래 상대 배치로 한 벌 둔다 |
| skill | `op55-compose` | SKILL.md:23-38, 51-69, references/score.md, arranging.md | cue sheet·격자·편곡·score 작성. showreel이 직접 읽는다 |
| skill | `op55-render` | SKILL.md:39-43, 49, render.mjs, preview.py, references/preview.md | WAV·analysis·meta와 요청 시 preview. showreel이 직접 읽는다 |
| skill | `op55-verify` | SKILL.md:44-48, references/verify.md, verify.py | 출력 판독과 통과·미달·미측정·N/A 분류. 반복 결정은 playbook에 넘긴다 |
| principle | `principle-protect-the-voice` | SKILL.md:65, arranging.md:33-40 | 나레이션 아래 음역·선율·밀도의 판단 |
| principle | `principle-freeze-the-grid` | SKILL.md:37, score.md:43, showreel.md:25-30 | 기존 영상의 시간 계약을 바꿀지의 판단 |
| principle | `principle-arrange-for-the-picture` | SKILL.md:53-59, arranging.md:14-17, 42-48 | palette·섹션 경계·강세를 화면에 맞추는 판단 |

### 고려했다가 뺀 후보

| 후보 | 처리와 이유 |
| --- | --- |
| bank 설치, score API, 편곡 기준, showreel 계약을 각각 별도 skill | resolve-op55-tools와 각 skill의 references로 충분. 따로 부를 일이 없다 |
| 장르별 playbook | 장르는 편곡 기준이다. 단계가 같다 |
| 검수용 두 번째 mode | 사람의 역할이 바뀌지 않는다. 사람은 마지막에 듣는 사람 한 역할이다 |
| 음량·라이선스·결정성 규칙을 principle로 | 강제력이 낮아진다. 수행 skill의 필수 제약과 스크립트에 둔다 |
| 운영 adapter(subagent, session lookup 등) | 필요한 운영 어휘가 셋 미만이다. render/verify/bank는 도메인 동작이라 세지 않는다 |
| scripts를 skill마다 복사 | 정본이 갈라진다. resolve-op55-tools 한 곳에 두고 형제 경로로 읽는다 |
| 이름을 `op55`로 유지(Q8 A안) | 사용자가 B안(`op55-mode`, `resolve-op55-tools/scripts`)을 골랐다 |

## 원본 SKILL.md 대응표

원본은 828990b의 skills/op55/SKILL.md(83줄)다. 줄마다 새 위치가 하나 이상 있다.

| 원본 줄 | 내용 | 새 위치 |
| --- | --- | --- |
| 1-4 | name, description, 트리거 문구 | op55-mode description. 영어·한국어 트리거를 그대로 두고, showreel 음악 단계 트리거는 뺐다(showreel은 작업 skill을 직접 읽는다) |
| 6-8 | 들을 수 없는 작곡가라는 역할 | op55-mode 첫 문단, op55-compose 첫 문단 |
| 10 | `S` 정의 | resolve-op55-tools 경로 절 |
| 12-21 | setup, bank, cache | resolve-op55-tools 도구·bank 절 |
| 23-32 | 입력·출력 계약 | op55-mode 결과와 완료, op55-compose 입력과 결과, op55-render 입력과 결과 |
| 34-38 | cue sheet, 격자, score 작성 | op55-compose 순서, create-cue 2단계 |
| 39-43 | 렌더 명령과 시간 | resolve-op55-tools 명령 표, op55-render 음악 렌더, create-cue 3단계 |
| 44-48 | verify 명령과 필수 항목 | op55-verify, create-cue 4단계 |
| 49 | 납품 보고와 청취 요청, 요청 시만 preview | op55-mode 납품 문장, create-cue 5단계, op55-render preview 분기 |
| 51-59 | palette 표 | op55-compose palette, principle-arrange-for-the-picture |
| 63 | 음악 API·loop·미확인 오디오 금지 | op55-compose 지켜야 할 것, resolve-op55-tools 라이선스와 금지 |
| 64 | 결정성 | op55-compose 지켜야 할 것, op55-render |
| 65 | 나레이션 대역 | principle-protect-the-voice |
| 66 | 큰 hit는 다운비트에 | op55-compose 지켜야 할 것, principle-arrange-for-the-picture |
| 67 | sampled 싱크 지점 | op55-compose 지켜야 할 것, op55-verify onset |
| 68 | credits | op55-compose, op55-render·op55-verify 반환, op55-mode 완료 |
| 69 | 같은 문제가 두 번이면 기록 | op55-mode 경험 남기기, op55-compose와 op55-verify의 기록 문장 |
| 71-73 | showreel 연결 | resolve-op55-tools/references/showreel-contract.md, op55-mode 경계 |
| 75-83 | references 색인 | 각 reference를 소유한 skill의 본문 |

## 옮긴 파일과 바뀐 문서

| 원본(828990b) | 새 위치 | 바이트 |
| --- | --- | --- |
| skills/op55/scripts/ (lib, vendor, examples 포함 19개) | skills/resolve-op55-tools/scripts/ | 같음 |
| skills/op55/assets/fonts/ (4개) | skills/resolve-op55-tools/assets/fonts/ | 같음 |
| references/score.md, arranging.md | skills/op55-compose/references/ | arranging.md 같음. score.md는 43줄의 그림 재사용 문장만 고침 |
| references/preview.md | skills/op55-render/references/ | 폰트 경로 한 곳만 고침 |
| references/verify.md | skills/op55-verify/references/ | 같음 |
| references/showreel.md | skills/resolve-op55-tools/references/showreel-contract.md | 다시 씀: 경로 전달(OP55_SCRIPTS, --mix-py), 필드 표, 소비 hit·envelope 확인, meta 없는 교체 |
| skills/op55/SKILL.md | 위 대응표의 여러 SKILL.md | 지움 |

score.md:43은 "격자가 1 ms 안에서 같으면 그림을 다시 렌더할 필요가 없다"고 했다. showreel의 timeline.py는 WAV에서 envelope를 다시 계산하고, hit가 추가되면 `music.hitN` 번호가 바뀐다. 그래서 격자 일치는 필요조건으로만 남기고 계약 문서를 가리키게 했다.

## 보존 목록

- synth 10종, GM/GS·drum kit·upright/grand, odd meter·pickup·sampled lead·CC ramp·VO gaps·master/space·stems·mute·describe.
- 요청 전용 preview(폭 1920, 높이는 내용에 따라 약 800 px, label 세 줄이면 약 860 px, `--size`로 고정, meta 없으면 초 눈금, `--check` 스틸 세 장).
- verify.py 출력 계약(limiter ✓/✗, `--spec` 건너뜀 표시, meta 없을 때 경고). op55-verify가 이 문구를 판독하므로 출력을 바꾸면 판독 기준도 함께 바꾼다.
- OP55_BANKS와 XDG cache 처리, bank registry의 credit, MIT·Apache-2.0·OFL 파일.
- 음악 생성 API 비용 0. 다운로드·디스크·CPU 비용은 resolve-op55-tools 표에 남겼다.
- 저장소 루트의 README, assets/demo, tools/는 설치되지 않는 저장소 자료로 남긴다.

## 진입 정책과 언어

name은 영어 kebab-case, SKILL.md 본문·description·default_prompt는 한국어다(변환 계획 §2). 옮긴 references는 원문 영어를 유지한다. op55-mode의 description에는 영어 사용자도 자연어로 진입할 수 있게 원래의 영어 트리거 문구를 남겼다. op55-mode만 자연어 자동 진입이고(Q1) 나머지는 명시 호출이다. Claude Code는 `disable-model-invocation`, Codex는 `policy.allow_implicit_invocation`으로 표시한다.

<!-- skillset:policy:start -->
| mode | 자연어 자동 호출 |
| --- | --- |
| `op55-mode` | `true` |

leaf skill과 principle의 자동 호출은 `false`다.
<!-- skillset:policy:end -->

## 이전 장부

예전 경로 skills/op55/와 진입 이름 `op55`를 가정하던 소비자다. 이 저장소 안의 것은 이번에 고쳤고 `skillset.json`의 migration.rewritten에 올렸다. 저장소 밖 소비자는 checker가 경로로 다룰 수 없어 이 표가 정본이다.

| 소비자 | 가정하던 것 | 상태 |
| --- | --- | --- |
| tools/regress.sh, tools/art/demo-video.sh | skills/op55/scripts | 고침 |
| README.md, README.ko.md | skill 하나, 예전 링크와 트리, `/op55` | 고침: 여덟 skill 설치, `/op55-mode`, 예전 사본 제거 명령 |
| THIRD_PARTY.md | vendor와 fonts의 예전 경로 | 고침 |
| skills/resolve-op55-tools/scripts/vendor/README.md | 재빌드 예시의 출력 경로 | 그대로 둠. vendor 바이트 보존 지시. portability transition에 등록, 다음 vendor 갱신 때 고침 |
| video-creator tools/session-start.sh | skills/op55 한 폴더만 .claude/skills/op55로 링크, setup 경로 고정 | 후속 작업: op55/skills/* 각각 링크, setup 경로를 resolve-op55-tools/scripts로, 끊어진 .claude/skills/op55 링크 정리 |
| video-creator CLAUDE.md | O=.claude/skills/op55/scripts, 예제 경로 | 후속 작업: O를 .claude/skills/resolve-op55-tools/scripts로 |
| showreel scripts/preflight.py | 예전 이름의 scripts 후보 | 후속 작업(showreel 정렬). 그 전까지 op55를 부를 때 OP55_SCRIPTS 전달 |
| showreel SKILL.md, references/audio.md, CUSTOM.md | "op55 스킬을 불러" | 후속 작업(showreel 정렬) |
| 공개 설치자 | `npx skills add ynginkim/op55`로 skill 하나 | 같은 명령으로 여덟 개. 예전 사본은 `npx skills remove op55`(전역이면 `-g`) |

video-creator의 SessionStart 훅은 op55 checkout이 깨끗하고 main이면 자동으로 pull한다. 훅과 CLAUDE.md 변경이 준비되기 전에 이 변경이 main에 들어가면, 다음 세션부터 .claude/skills/op55 링크가 끊어지고 showreel preflight가 사용자 전역의 예전 사본을 잡을 수 있다. 그래서 merge는 훅 변경 뒤에 한다.

## 구조 검사 적용

검사 코드는 meta-harness check-skillset의 사본이다(출처와 hash는 scripts/CHECKER-SOURCE.md).

| 검사 | 적용 |
| --- | --- |
| S1 참조·frontmatter·색인·언어·오류 주입 | 적용 |
| S2 설치 경계·등록된 사본 diff | 설치 경계 적용. 등록 사본 없음(copies 빔). checker 사본은 외부 원본이라 CHECKER-SOURCE.md의 hash로 관리 |
| S3 adapter 소비 leaf의 제목 직후 포인터 | 적용: op55-compose, op55-render, op55-verify → resolve-op55-tools |
| S4 제품명 lint·경로별 예외·transition | 적용: 예전 경로 skills/op55/를 skills, README 두 개, THIRD_PARTY, tools에서 금지. transition 3건 |
| S5 이전 장부 prune 검사 | 적용: rewritten 8건, pending 0건. 저장소 밖 소비자는 위 표 |
| S6 CLI 스냅샷 대조 | 쓰지 않음. 명령은 resolve-op55-tools 표가 정본이고 실제 실행으로 확인 |
| S7 install smoke | 적용 |
| S8 진입 정책 | 적용 |
| S9 색인 밖 principle 사용 | 적용(경고 0이 목표) |
| S10 미확인 닫을 조건 | 적용 |
| S11 생성 문서·링크 드리프트 | 적용 |
| S12 push·PR CI | .github/workflows/check.yml |

구조 검사 통과는 음악 품질이나 사람의 청취 판단을 포함하지 않는다.

## 검증 기록

검증은 진행 중이다. 결과는 같은 커밋 범위에서 이 절에 채운다.

## 확인하지 못한 것

| 항목 | 상태 | 닫을 조건 |
| --- | --- | --- |
| 실제 음악 품질 | unverified | 사용자가 렌더된 WAV를 전체 청취하고 질감·흐름·영상/대사 적합성을 판정 |
| 새 세션의 자연어·명시 진입 | unverified | 설치본을 새 Claude Code와 Codex 세션에서 열어 op55-mode 진입, playbook Read, 원문 todo를 확인. 실행 횟수는 사용자 승인 |
| GitHub 원격 설치 형식 | unverified | main 반영 뒤 `npx skills add ynginkim/op55`로 빈 프로젝트에 설치해 여덟 skill과 형제 참조 확인 |
| 원격 CI | unverified | push한 커밋에서 GitHub Actions check 워크플로 결과 확인 |
| SessionStart 훅 링크 | unverified | video-creator 훅 변경 뒤 사본에서 훅을 실행해 모든 skill 링크와 setup 안내 확인 |
| showreel 경계 end-to-end | unverified | showreel 정렬 뒤 신규 제작과 기존 오디오 교체를 hit·envelope 소비 장면까지 확인 |
| 다른 환경의 회귀 hash | unverified | Node 22, macOS arm64 밖의 환경에서 tools/regress.sh를 돌려 같은지 기록 |
| bank 라이선스 최신성 | unverified | 결과물 배포 직전 공식 원문과 배포 hash 재확인 |
