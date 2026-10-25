# op55 skillset 설계

Status: implemented. 구조·설치·회귀·동작 검증은 아래에 따로 기록했다. 새 세션 진입은 세 조합(경로 2회, 제작 1회)만 확인했고 사람 청취는 미확인이다. 이 문서는 단일 `op55` skill을 mode·playbook·skill·principle 구조로 옮긴 결과와 그 이유, 검증 기록을 담는다. 변환 계획은 meta-harness 저장소의 examples/op55/plan.md(기준점 op55 828990b)이며, 이 저장소에는 복사하지 않았다. 기준점 828990b는 history 재작성 전 hash이고 지금 main의 1aece78과 트리가 같다. 이 문서의 다른 커밋 hash는 재작성 뒤 값이다. 2026-10-24에 main에 들어온 PR #3(공개 준비 문서, CI, 회귀 테스트)을 이 브랜치에 merge했다(5ccd582). 2026-10-25에 op55를 특정 소비자를 모르는 독립 skillset으로 정리했다(아래 "공개 인터페이스와 소비자").

## 목표와 범위

영상 BGM을 코드로 작곡하고 렌더·마스터링·검수까지 끝내는 기존 기능을 그대로 두고, 흐름(playbook), 수행(skill), 판단(principle), 이를 운용하는 mode로 나눈다. 공개 설치 명령 `npx skills add ynginkim/op55`는 바뀌지 않으며 여덟 skill이 한 벌로 설치된다.

바꾸지 않은 것: 렌더 엔진(scripts/lib, scripts/vendor, DSP)의 바이트, score module API, 세 예제와 승인 hash(tools/regress.sha256), verify.py와 preview.py의 동작과 출력 형식. 파일은 위치만 옮겼다. 그 뒤 2026-10-25에 verify.py의 `--mix`를 뺐다(아래 "공개 인터페이스와 소비자").

이 저장소 밖의 소비자는 이 저장소의 변경에 들어 있지 않다. 각 소비자가 자기 저장소에서 맞춘다.

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
| skill | `op55-compose` | SKILL.md:23-38, 51-69, references/score.md, arranging.md | cue sheet·격자·편곡·score 작성. 다른 skillset이 직접 읽는다 |
| skill | `op55-render` | SKILL.md:39-43, 49, render.mjs, preview.py, references/preview.md | WAV·analysis·meta와 요청 시 preview. 다른 skillset이 직접 읽는다 |
| skill | `op55-verify` | SKILL.md:44-48, references/verify.md, verify.py | 출력 판독과 통과·미달·미측정·N/A 분류. 반복 결정은 playbook에 넘긴다 |
| principle | `principle-protect-the-voice` | SKILL.md:65, arranging.md:33-40 | 나레이션 아래 음역·선율·밀도의 판단 |
| principle | `principle-freeze-the-grid` | SKILL.md:37, score.md:43, showreel.md:25-30 | 기존 영상의 시간 계약을 바꿀지의 판단 |
| principle | `principle-arrange-for-the-picture` | SKILL.md:53-59, arranging.md:14-17, 42-48 | palette·섹션 경계·강세를 화면에 맞추는 판단 |

### 고려했다가 뺀 후보

| 후보 | 처리와 이유 |
| --- | --- |
| bank 설치, score API, 편곡 기준, 출력 계약을 각각 별도 skill | resolve-op55-tools와 각 skill의 references로 충분. 따로 부를 일이 없다 |
| 장르별 playbook | 장르는 편곡 기준이다. 단계가 같다 |
| 검수용 두 번째 mode | 사람의 역할이 바뀌지 않는다. 사람은 마지막에 듣는 사람 한 역할이다 |
| 음량·라이선스·결정성 규칙을 principle로 | 강제력이 낮아진다. 수행 skill의 필수 제약과 스크립트에 둔다 |
| 운영 adapter(subagent, session lookup 등) | 필요한 운영 어휘가 셋 미만이다. render/verify/bank는 도메인 동작이라 세지 않는다 |
| scripts를 skill마다 복사 | 정본이 갈라진다. resolve-op55-tools 한 곳에 두고 형제 경로로 읽는다 |
| 이름을 `op55`로 유지(Q8 A안) | 사용자가 B안(`op55-mode`, `resolve-op55-tools/scripts`)을 골랐다 |

### 공개 인터페이스와 소비자

op55는 누가 자기를 쓰는지 모르는 공개 skillset이다. 약속하는 것은 `resolve-op55-tools/references/output-contract.md`의 공개 인터페이스뿐이다. 스킬 이름, 도구 경로와 `OP55_SCRIPTS`라는 이름, 명령 인자, 출력 파일, 버전이다. 소비자가 op55를 어떻게 쓰는지는 그 소비자의 저장소가 정한다.

처음 옮길 때는 showreel-contract.md에 한 소비자의 내부 동작과 제작 순서를 같이 두었다. 그 소비자의 코드가 바뀌자 설명이 곧바로 틀렸고, 제작 순서는 두 저장소에 같이 적혀 있었다. 그래서 2026-10-25에 다음처럼 바꿨다.

| 결정 | 이유 |
| --- | --- |
| output-contract.md에는 op55 쪽 약속만 둔다 | 제공하는 쪽이 소비자 내부를 설명하면 소비자가 바뀔 때마다 틀린다 |
| `verify.py --mix`와 `--mix-py`를 뺐다 | 외부 영상 믹서를 실행해 그 줄별 표를 다시 요약했을 뿐이다. 믹서가 같은 표를 이미 출력한다. op55 코드가 특정 소비자를 아는 유일한 곳이었다 |
| `metadata.version`과 `render.mjs --version`을 더했다 | 저장소의 VERSION은 설치본에 들어가지 않는다. 소비자가 실행할 때 쓴 버전을 기록할 수 있어야 한다. `tools/test_version.mjs`가 세 값이 같은지 본다 |
| 기본 seed 문자열 `'showreel'`과 lib 주석은 그대로 둔다 | seed를 바꾸면 모든 렌더의 바이트가 달라져 승인 hash와 청취를 다시 해야 한다. lib 파일은 엔진 바이트를 건드리지 않으려고 주석도 그대로 둔다 |
| README에서 showreel은 크레딧의 출처 설명에만 둔다 | op55가 시작된 계기라서 원본 저장소를 링크한다 |

## 원본 SKILL.md 대응표

원본은 828990b의 skills/op55/SKILL.md(83줄)다. 줄마다 새 위치가 하나 이상 있다.

| 원본 줄 | 내용 | 새 위치 |
| --- | --- | --- |
| 1-4 | name, description, 트리거 문구 | op55-mode description. 영어·한국어 트리거를 그대로 두고, 영상 skillset의 음악 단계 트리거는 뺐다(그쪽은 작업 skill을 직접 읽는다) |
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
| 71-73 | 영상 skillset 연결 | resolve-op55-tools/references/output-contract.md, op55-mode 경계 |
| 75-83 | references 색인 | 각 reference를 소유한 skill의 본문 |

## 옮긴 파일과 바뀐 문서

| 원본(828990b) | 새 위치 | 바이트 |
| --- | --- | --- |
| skills/op55/scripts/ (lib, vendor, examples 포함 19개) | skills/resolve-op55-tools/scripts/ | 같음 |
| skills/op55/assets/fonts/ (4개) | skills/resolve-op55-tools/assets/fonts/ | 같음 |
| references/score.md, arranging.md | skills/op55-compose/references/ | arranging.md 같음. score.md는 43줄의 그림 재사용 문장만 고침 |
| references/preview.md | skills/op55-render/references/ | 폰트 경로 한 곳만 고침 |
| references/verify.md | skills/op55-verify/references/ | 같음 |
| references/showreel.md | skills/resolve-op55-tools/references/output-contract.md | 다시 씀: 공개 인터페이스, op55가 쓰는 파일과 형식, 경로 전달, meta 없는 격자 복구. 처음에는 showreel-contract.md로 옮겼다가 2026-10-25에 소비자 내부 설명을 빼고 이름을 바꿨다 |
| skills/op55/SKILL.md | 위 대응표의 여러 SKILL.md | 지움 |

score.md:43은 "격자가 1 ms 안에서 같으면 그림을 다시 렌더할 필요가 없다"고 했다. 영상 쪽은 WAV에서 envelope를 다시 계산하거나 hit 번호에 장면을 걸 수 있고, hit가 추가되면 번호가 밀린다. 그래서 격자 일치는 필요조건으로만 남기고 출력 계약 문서를 가리키게 했다. 화면이 무엇을 소비하는지는 영상 skillset이 확인한다.

## 보존 목록

- synth 10종, GM/GS·drum kit·upright/grand, odd meter·pickup·sampled lead·CC ramp·VO gaps·master/space·stems·mute·describe.
- 요청 전용 preview(폭 1920, 높이는 내용에 따라 약 800 px, label 세 줄이면 약 860 px, `--size`로 고정, meta 없으면 초 눈금, `--check` 스틸 세 장).
- verify.py 출력 계약(limiter ✓/✗, `--spec` 건너뜀 표시, meta 없을 때 경고). op55-verify가 이 문구를 판독하므로 출력을 바꾸면 판독 기준도 함께 바꾼다.
- OP55_BANKS와 XDG cache 처리, bank registry의 credit, MIT·Apache-2.0·OFL 파일.
- 음악 생성 API 비용 0. 다운로드·디스크·CPU 비용은 resolve-op55-tools 표에 남겼다.
- 저장소 루트의 README, assets/demo, tools/는 설치되지 않는 저장소 자료로 남긴다.

## 진입 정책과 언어

name은 영어 kebab-case, SKILL.md 본문·description·default_prompt는 한국어다(변환 계획 §2). 옮긴 references는 원문 영어를 유지한다. op55-mode의 description에는 영어 사용자도 자연어로 진입할 수 있게 원래의 영어 트리거 문구를 남겼다. 사용자가 2026-10-24에 이 언어 배치를 유지하기로 했다. op55-mode만 자연어 자동 진입이고(Q1) 나머지는 명시 호출이다. Claude Code는 `disable-model-invocation`, Codex는 `policy.allow_implicit_invocation`으로 표시한다.

<!-- skillset:policy:start -->
| mode | 자연어 자동 호출 |
| --- | --- |
| `op55-mode` | `true` |

leaf skill과 principle의 자동 호출은 `false`다.
<!-- skillset:policy:end -->

## 이전 장부

예전 경로 skills/op55/와 진입 이름 `op55`를 가정하던 소비자다. 이 저장소 안의 것은 이번에 고쳤고 `skillset.json`의 migration.rewritten에 올렸다. 저장소 밖 소비자는 각자 자기 저장소에서 맞추므로, 이 표에는 공개 설치자만 적는다.

| 소비자 | 가정하던 것 | 상태 |
| --- | --- | --- |
| tools/regress.sh, tools/art/demo-video.sh | skills/op55/scripts | 고침 |
| README.md, README.ko.md | skill 하나, 예전 링크와 트리, `/op55` | 고침: 여덟 skill 설치, `/op55-mode`, 예전 사본 제거 명령 |
| THIRD_PARTY.md | vendor와 fonts의 예전 경로 | 고침 |
| skills/resolve-op55-tools/scripts/vendor/README.md | 재빌드 예시의 출력 경로 | 고침. 문서만 바꾸고 vendor 바이트는 그대로다. PR #3도 이 파일에 fflate 문장을 더했다 |
| PR #3이 더한 CONTRIBUTING.md, tools/test_regress.py, .github/workflows/check.yml | skills/op55/scripts | 고침. check.yml은 main의 문법 검사·macOS 음질 회귀 job에 skillset job을 더한 한 파일이다. CONTRIBUTING.md에 skillset 검사 두 줄을 더했다 |
| CHANGELOG.md | 없음(main에서 새로 생김) | Unreleased에 breaking 변경과 이전 방법을 적음. VERSION과 릴리스는 바꾸지 않음 |
| `verify.py --mix`를 쓰던 호출 | 외부 믹서 실행과 줄별 요약 | 2026-10-25에 뺌. 호출하던 쪽은 자기 믹서의 줄별 표를 읽는다(CHANGELOG의 이전 방법) |
| 공개 설치자 | `npx skills add ynginkim/op55`로 skill 하나 | 같은 명령으로 여덟 개. 예전 사본은 `npx skills remove op55`(전역이면 `-g`) |

## 구조 검사 적용

검사 코드는 meta-harness check-skillset의 사본이다(출처와 hash는 scripts/CHECKER-SOURCE.md).

| 검사 | 적용 |
| --- | --- |
| S1 참조·frontmatter·색인·언어·오류 주입 | 적용 |
| S2 설치 경계·등록된 사본 diff | 설치 경계 적용. 등록 사본 없음(copies 빔). checker 사본은 외부 원본이라 CHECKER-SOURCE.md의 hash로 관리 |
| S3 adapter 소비 leaf의 제목 직후 포인터 | 적용: op55-compose, op55-render, op55-verify → resolve-op55-tools |
| S4 제품명 lint·경로별 예외·transition | 적용: 예전 경로 skills/op55/를 skills, README 두 개, THIRD_PARTY, CONTRIBUTING, tools의 sh·py, workflow에서 금지. transition 0건. 처음에는 한 소비자의 preflight를 설명하던 문장 2건이 있었고, 2026-10-25에 그 설명을 빼면서 닫았다 |
| S5 이전 장부 prune 검사 | 적용: rewritten 12건, pending 0건. 저장소 밖 소비자는 위 표 |
| S6 CLI 스냅샷 대조 | 쓰지 않음. 명령은 resolve-op55-tools 표가 정본이고 실제 실행으로 확인 |
| S7 install smoke | 적용 |
| S8 진입 정책 | 적용 |
| S9 색인 밖 principle 사용 | 적용(경고 0이 목표) |
| S10 미확인 닫을 조건 | 적용 |
| S11 생성 문서·링크 드리프트 | 적용 |
| S12 push·PR CI | .github/workflows/check.yml의 skillset job. 같은 파일에 main의 structural, audio-regression job이 있다 |

구조 검사 통과는 음악 품질이나 사람의 청취 판단을 포함하지 않는다.

## 검증 기록

2026-10-23, macOS (Darwin arm64), Node v22.22.2, Python 3.15.0, ffmpeg 8.1, numpy 2.5.4, Pillow 13.0.0, npx 10.9.7, skills CLI 1.7.4. skill 파일은 커밋 f405457 이후 op55-verify의 위생 문장 한 줄(6574f20)과 vendor/README.md의 경로 한 줄 말고는 바뀌지 않았다. main merge 뒤 재검증은 아래 'main merge 뒤 재검증'에 따로 적는다. 증거 파일은 작업 세션의 임시 폴더에 있고 저장소에 넣지 않았다.

### 구조

| 명령 | 결과 |
| --- | --- |
| `python3 scripts/check.py .` | exit 0. 8 skills, 1 mode, 2 playbooks, 4 leaves, 3 principles, 경고 0 |
| `python3 scripts/selftest.py` | exit 0. 49 tests OK(일반 오류 주입) |
| op55 전용 오류 주입 5건(HEAD를 git archive로 뽑은 사본마다 하나씩) | 모두 exit 1. README에 예전 경로 → PORTABILITY, REF_MISSING. preview.md의 형제 폰트 경로 오타 → REF_MISSING. op55-verify의 adapter 포인터 제거 → ADAPTER_POINTER. op55-verify 자동 호출 켬 → POLICY. mode 색인의 principle 이름 오타 → UNKNOWN_PRINCIPLE, PRINCIPLE_INDEX. 바꾸지 않은 사본은 exit 0 |

### 설치

| 확인 | 결과 |
| --- | --- |
| `npx skills add <worktree> -l` | 8개만 나열. worktree 디스크에 git 제외 meta-harness 설치본(.agents/skills)이 있어도 섞이지 않음 |
| `python3 scripts/install_smoke.py <worktree> --dest <새 빈 폴더>` | exit 0. `npx --yes skills add <worktree> -a claude-code -a codex -y` 성공. .agents/skills에 8개 복사, .claude/skills에 8개 링크. 두 경로에서 playbook 4건, 참조 114건 열림. 원본 바이트 불변 |
| `diff -r skills/ <설치본>/.agents/skills/` | 같음 |
| 형제 경로 실행 | `.claude/skills/op55-render/../resolve-op55-tools/scripts/setup.mjs --check`와 `.agents/skills/op55-verify/../resolve-op55-tools/scripts/setup.mjs --check` 모두 exit 0(gm, upright 설치됨). 설치본 preview.py가 형제 assets/fonts(4개 파일)를 찾음 |

GitHub 원격 형식(`ynginkim/op55`)은 main 반영 전이라 확인하지 않았다.

### 회귀

| 시점 | 결과 |
| --- | --- |
| 이동 직후(4b62721) | `tools/regress.sh` exit 0. eroica, pstack-harness, starter 모두 ✓ |
| 문서·검사 추가 후(d52f2b7) | exit 0. 세 예제 모두 ✓. SHA-256이 tools/regress.sha256과 같음 |
| 설치본 scripts로 `--analysis`까지 렌더 | starter, eroica WAV가 승인 hash와 같음 |

### 동작

설치본의 scripts 경로로 세 사례를 렌더하고 verify.py 출력과 PNG를 직접 읽었다. 합성은 starter, sampled와 3/4는 eroica다. 홀수 박자는 starter를 7/8(eighth 210 BPM, kick 2+2+3)로 바꾼 임시 fixture로 확인했다. fixture는 저장소에 넣지 않았다.

| 항목 | 합성(starter, 33 s) | sampled·3/4(eroica, 57 s) | 7/8 fixture(33 s) |
| --- | --- | --- | --- |
| 렌더 | 5.1 s, 9,504,044 bytes | 10.6 s, 16,416,044 bytes | 4.1 s, 9,504,044 bytes |
| loudness, true peak | -13.0(목표 -13) ✓, -1.3 dBTP ✓ | -14.5(목표 -14.5) ✓, -1.3 ✓ | -13.0 ✓, -1.3 ✓ |
| clipping, DC, fade 뒤 | 0, 2.0e-05 이하, 0 → 통과 | 0, 4.4e-05 이하, 0 → 통과 | 0, 1.0e-05 이하, 0 → 통과 |
| limiter | 최대 4.20 dB ✗ → **미달** | 3.70 dB ✓ | 3.60 dB ✓ |
| grid | 0.00 / 0.00 ms ✓ | 0.33 / 0.00 ms ✓ | 0.43 / 0.00 ms ✓ |
| kick onset | 31개, 최대 1.84 ms ✓ | 52개, 최대 1.17 ms ✓ | 23개, 최대 1.62 ms ✓ |
| accent onset | Main hit +3.27 ms ✓. Final chord는 soft. score가 작은 bell과 피아노로 쓴 끝 화음이라 의도로 판정 | 6개 모두 ✓, 최대 +3.40 ms | Main hit +1.23 ms ✓. Final chord soft, starter와 같은 근거 |
| 섹션 순위 상관 | +1.00 ✓ | +0.96 ✓ | +1.00 ✓ |
| 가장 강한 강세 마디 | bar 8이 곡에서 가장 큼(-10.0), 직전보다 +3.4 dB → 통과 | bar 38(-11.6)이 직전보다 +2.4 dB지만 bar 41과 49(-10.9)가 더 큼 → **미달** | bar 8이 가장 큼, +3.4 dB → 통과 |
| 파형 PNG | 두 패널, 빨강·초록 일치 | 여섯 패널 모두 일치 | 두 패널 일치 |
| 스펙트로그램 | spec_0: 구멍·앨리어싱 줄무늬 없음. 세로선은 악보의 clock tick과 hat 위치(0.5 s, 0.25 s 간격) | spec_0, spec_30: 구멍·줄무늬 없음. 세로선은 강세와 Finale의 kick | spec_0: 같음, kick 2+2+3 보임 |
| mix margin | N/A(나레이션 없음, 대체 확인 없음) | N/A | N/A |
| 나레이션 아래 1.3-4 kHz | N/A | N/A | N/A |
| credits | 없음 | gm, upright. credit 줄 없음 | 없음 |

미측정 분기도 실제 출력으로 확인했다. meta 없이 WAV만 검사하면 "! ... music.meta.json not found ... only loudness and the analysis grid are checked"가 나오고 onset·energy 줄이 빠진다. 33초 cue에 `--spec 40`을 주면 "[spec] 40 s: skipped"가 나온다. 둘 다 verify.py는 exit 0이었다. exit code로 통과를 판정하지 않는 이유다.

preview는 설치본 경로로 starter WAV에 `--check`를 한 번 돌렸다. 1920×802, 33.0 s, 1.4 MB, 32.5 s 걸림. 세 스틸을 열어 확인한 것: 색이 playhead에서 멈춤, NOW 라벨이 01 INTRO·03 MAIN·04 RESOLVE로 그 순간의 섹션과 맞음, 라벨 겹침과 화면 밖 넘침 없음, 한글 제목이 그려짐. 동영상 재생과 소리는 확인하지 않았다.

### 재구성 전부터 있던 미달

위 두 미달은 이번 변경이 만든 것이 아니다. 세 예제의 WAV가 828990b의 승인 hash와 바이트까지 같고 verify.py도 같으므로, 기준점에서도 같은 출력이 나온다. verify.py가 limiter 4 dB 초과를 ✗로 표시하기 시작한 것은 bdb958b(재작성 뒤 f151990)다(그 전에는 SKILL.md의 문장 기준만 있었다). 예제를 고치면 승인 hash가 바뀌므로 이번 범위에서 고치지 않았고, 사용자가 2026-10-24에 고치지 않기로 했다.

| 예제 | 미달 | 고칠 때 |
| --- | --- | --- |
| starter | limiter 최대 4.20 dB(16 s, Main hit) | references/verify.md의 처방대로 boom·stab 같은 뾰족한 층을 낮추고, 소리 변경으로 승인 hash를 갱신 |
| eroica | 가장 강한 강세 bar 38이 곡에서 가장 큰 마디가 아님(bar 41·49보다 0.7 dB 작음) | Finale 진입을 키우거나 뒤 마디의 `levels`를 낮추고 hash 갱신. 또는 강세 strength 설계를 다시 정함 |

### 새 세션 경로

사용자가 경로 시험 2회와 실제 제작 1회를 승인했다. 세 세션 모두 install smoke로 만든 설치 프로젝트의 복사본에서 새로 시작했다. 프롬프트에는 skill 이름(명시 호출 시험 제외)이나 기대 playbook을 넣지 않았다. 사용자 전역과 프로필 skill 폴더에 예전 `op55` 사본은 없었다. 프로필에는 다른 skill 81개가 있었다.

| 시험 | 요청 | 결과 |
| --- | --- | --- |
| Claude Code 자연어(`claude -p`, Claude Code 2.1.309, 요청 effort low, 실제 모델 claude-opus-5-5, 실제 effort는 기록에 없음) | 30초 제품 소개 BGM, 0:15 히트, 나레이션 없음. 단계 목록만 적고 멈추고 파일을 바꾸지 말 것 | 통과. Skill 도구로 `op55-mode`에 자동 진입했고 `playbooks/create-cue.md`를 도구(cat)로 읽었다. 원문 5단계를 그대로 적고 멈췄다. 파일 변경 없음. 4 turns, 24 s, 0.22 USD. todo 도구(TaskCreate)가 있었지만 쓰지 않고 텍스트 fallback(`단계 0/5:`)을 썼다. 도구 todo와 fallback은 같은 증거가 아니다 |
| Codex 명시(`codex exec -s read-only`, CLI 0.160.1, 실제 모델 gpt-6.1-sol, effort low) | `$op55-mode` 완성된 홍보 영상의 음악 교체, 컷과 장면 유지. 단계 목록만 적고 멈추고 파일을 바꾸지 말 것 | 통과. mode 본문이 주입됐고 `playbooks/revise-cue.md`를 골라 cat으로 읽었다. 원문 5단계를 그대로 적고 시간 계약·장면 재렌더 승인 조건을 덧붙인 뒤 멈췄다. 파일 변경 없음. todo 도구는 쓰지 않고 텍스트 fallback |
| Claude Code 실제 제작(`claude -p --permission-mode acceptEdits`, 실제 모델 claude-opus-5-5, effort 지정 없음) | 20초 앱 소개 BGM, 밝고 가벼운 전자음, 0:10 로고 히트, 나레이션 없음, 결과는 audio/music/ | 통과(에이전트 단계). 자연어로 `op55-mode` 진입, create-cue.md를 Read, TaskCreate에 원문 5단계를 그대로 넣었다. resolve-op55-tools → op55-compose(+principle-arrange-for-the-picture) → op55-render → op55-verify 순서로 SKILL.md를 읽었다. 1차 검수에서 Logo hit onset +20.38 ms ✗를 찾고 `--mute` 진단 렌더(dbg/)로 pad를 원인으로 지목해 score를 고친 뒤 재렌더했다. preview는 요청이 없어 `skip`. 최종 보고에 파일, 선택, 수치, N/A, credits, principle과 바뀐 결정, 납품 요청 문장이 있다. 59 turns, 11분 55초, 3.02 USD, 출력 59,137 tokens, cache read 3,070,512 tokens(사전 견적 0.5~1M보다 많음) |

제작 결과는 세션의 보고를 그대로 쓰지 않고 따로 확인했다. 같은 score를 다시 렌더하면 SHA-256이 같다(313887e7…). verify.py를 다시 돌린 결과: -13.0 LUFS ✓, -1.3 dBTP ✓, clipping 0, DC 1e-6 미만, fade 뒤 무음, limiter 최대 2.00 dB ✓, grid 0.00 ms ✓, kick 20개 최대 1.31 ms ✓, Logo hit +2.21 ms ✓, Final chord +0.08 ms ✓, 순위 상관 +1.00 ✓, Logo 마디(bar 4)가 곡에서 가장 크고 직전보다 +8.6 dB. 파형과 스펙트로그램도 직접 열어 문제를 찾지 못했다. score에는 `Math.random`과 시계가 없고 `makeRng`를 쓴다. bank는 gm(drum kit 25)뿐이라 credit 줄이 없다. mix margin은 N/A다.

제작 세션에서 본 위생 문제 두 가지가 있다. verify 출력을 프로젝트 밖 /tmp에 tee했다가 verify/로 복사했다. 끝에 자기가 만든 dbg/ 진단 폴더를 지웠다. 사용자 자산은 건드리지 않았다. 사용자 결정(2026-10-24)으로 op55-verify의 입력과 결과 절에 "verify 출력, 로그, 진단 렌더는 프로젝트 안에 쓰고, 진단 폴더는 보고 뒤 사용자에게 묻기 전에 지우지 않는다"는 문장을 넣었다(6574f20). 사람 청취는 하지 않았다.

### main merge 뒤 재검증

2026-10-24, 같은 기기와 도구 버전. 5ccd582(main merge)에 6574f20, 7f504dc를 더한 작업 트리에서 돌렸다.

| 확인 | 결과 |
| --- | --- |
| 충돌 | 6건 해결: tools/regress.sh(main의 인자 검사 + 새 경로), THIRD_PARTY.md(fflate 줄 + 새 경로), fflate.LICENSE(vendor/ 새 위치, 바이트는 main과 같음), README 두 개(여덟 skill 설치 문단 + main의 skills@1.7.4 고정, banks/ 경로, regress.sha256), check.yml(job 합침) |
| `python3 scripts/check.py .` | exit 0. 8 skills, 경고 0 |
| `python3 scripts/selftest.py` | 49 tests OK |
| `python3 tools/test_regress.py` | 7 tests OK(가짜 renderer로 실패 의미만 확인) |
| CI structural 단계의 명령 | `node --check`(scripts의 모든 .mjs), `bash -n` 두 개, Python AST 검사 모두 통과 |
| `tools/regress.sh` | exit 0. eroica, pstack-harness, starter 모두 ✓(Node v22.22.2, 69 s) |
| `python3 scripts/install_smoke.py . --dest <새 폴더>` | exit 0. 8개 설치, playbook 4건과 참조 114건 열림. `diff -r skills/ <설치본>/.agents/skills/` 같음(fflate.LICENSE 포함) |

### 공개 인터페이스 정리 뒤 재검증

2026-10-25, 같은 기기, Node v22.22.2. main의 62ebdb8(#10, levels 검증)을 merge한 작업 트리에서 돌렸다.

| 확인 | 결과 |
| --- | --- |
| `python3 scripts/check.py .` | 8 skills, 경고 0, transition 0 |
| `python3 scripts/selftest.py`, `python3 tools/test_regress.py` | 모두 OK |
| `node --test tools/test_engine.mjs tools/test_version.mjs` | 10 pass, 0 fail. VERSION, `metadata.version`, `render.mjs --version`이 같음 |
| CI structural 단계의 문법 검사 | `node --check`(모든 .mjs), Python AST 모두 통과 |
| `tools/regress.sh` | eroica, pstack-harness, starter 모두 ✓(44 s) |
| `python3 scripts/install_smoke.py . --dest <새 폴더>` | 8개 설치, playbook 4건과 참조 114건 열림. 두 설치 경로 모두 `render.mjs --version`이 `op55 0.2.0` |
| starter 렌더 뒤 verify.py | loudness, grid, onset, energy 줄이 전과 같이 나옴. `--mix`는 알 수 없는 인자로 거부됨 |
| skills/ 안 소비자 이름 | 문서에는 없음. 남은 곳은 lib 주석과 기본 seed 문자열 |

## 확인하지 못한 것

| 항목 | 상태 | 닫을 조건 |
| --- | --- | --- |
| 실제 음악 품질 | unverified | 사용자가 렌더된 WAV를 전체 청취하고 질감·흐름·영상/대사 적합성을 판정 |
| 새 세션 진입의 나머지 조합 | 일부 확인(사용자 결정으로 추가 시험 안 함) | Claude 자연어(경로·제작)와 Codex 명시는 통과. Claude 명시(`/op55-mode`)와 Codex 자연어는 미확인. 진입 문제가 보고되면 같은 설치본으로 각 1회 시험 |
| op55-verify 위생 문장의 효과 | 문장만 넣음 | 다음 실제 제작 세션에서 verify 로그와 dbg/가 프로젝트 안에 남고 삭제 전에 묻는지 확인 |
| GitHub 원격 설치 형식 | 확인함(cd7f370) | 빈 Git 프로젝트에 `npx skills@1.7.4 add ynginkim/op55 -a claude-code -a codex -y`: 여덟 skill과 링크 여덟 개, 형제 경로의 setup --check 통과, 설치본이 main의 skills/와 같고 meta-harness skill이 섞이지 않음. 기록은 PR #2 코멘트 |
| 원격 CI | 확인함 | PR #2의 push·pull_request 실행 모두 통과. main merge 뒤(aa54639)에는 세 job을 로그로 확인했다. skillset(ubuntu): check 경고 0, selftest 49 tests, install smoke 8개·참조 114건. structural: 문법 검사와 test_regress. audio-regression(macos-15-arm64, Node 22.23.2, bank cache 복원 뒤 크기·SHA-256 확인): eroica, pstack-harness, starter 모두 ✓ |
| 소비자 경계 end-to-end | unverified(이 저장소 밖) | 소비자 skillset이 자기 쪽에서 신규 제작과 기존 음악 교체를 화면이 소비하는 값까지 확인 |
| starter limiter, eroica 강세 마디 미달 | 확인함(기존 상태, 사용자 결정으로 고치지 않음) | 예제를 고치기로 하면 소리를 바꾸고 승인 hash를 갱신한 뒤 사람이 청취 |
| 다른 환경의 회귀 hash | unverified | Node 22, macOS arm64 밖의 환경에서 tools/regress.sh를 돌려 같은지 기록 |
| bank 라이선스 최신성 | unverified | 결과물 배포 직전 공식 원문과 배포 hash 재확인 |
