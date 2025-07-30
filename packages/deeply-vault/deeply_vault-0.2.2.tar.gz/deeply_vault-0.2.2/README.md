# Deeply CLI

`dotenv-vault`와 유사한 환경 변수 관리 CLI 도구입니다. 프로젝트의 `.env` 파일들을 중앙 서버에 안전하게 관리하고 팀원들과 공유할 수 있습니다.

## 소개

Deeply CLI는 프로젝트의 환경 변수를 안전하게 관리하고 팀원들과 공유할 수 있는 도구입니다. `.env` 파일을 중앙 서버에 저장하고, 필요할 때 로컬 환경으로 동기화할 수 있습니다. 여러 개발 환경(개발, 테스트, 스테이징, 프로덕션)에 대한 환경 변수를 관리하고, 팀원들이 최신 환경 설정을 유지할 수 있도록 도와줍니다.

## 주요 기능

- **환경 변수 중앙 관리**: 프로젝트의 환경 변수를 중앙 서버에 안전하게 저장
- **팀 협업**: 팀원들과 환경 변수를 쉽게 공유
- **버전 관리**: 환경 변수의 변경 사항을 추적하고 관리
- **보안**: 민감한 정보를 안전하게 관리
- **다중 환경 지원**: 개발, 테스트, 스테이징, 프로덕션 등 다양한 환경에 대한 설정 관리
- **CI/CD 통합**: CI/CD 파이프라인에서 API 키를 통한 인증 지원

## 시스템 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- 인터넷 연결 (중앙 서버 통신용)

## 설치 방법

### Unix/Linux/Mac

```bash
# 저장소 클론
git clone [repository-url]
cd deeply-env-vault/cli

# 설치 스크립트 실행
bash scripts/install.sh
```

### Windows

```powershell
# 저장소 클론
git clone [repository-url]
cd deeply-env-vault/cli

# 설치 스크립트 실행
.\scripts\install.ps1
```

설치가 완료되면 `uv run deeply-vault` 명령을 사용할 수 있습니다. 설치 확인을 위해 다음 명령어를 실행해보세요:

```bash
uv run deeply-vault --version
```

## 시작하기

### 1. 로그인

서버에 로그인하여 인증 토큰을 발급받습니다. 로그인 시 사용자명/비밀번호 또는 API 키를 사용할 수 있습니다.

```bash
# 서버 URL 지정하여 로그인
uv run deeply-vault login -s https://your-server-url

# 사용자명으로 로그인 (비밀번호는 프롬프트로 입력)
uv run deeply-vault login -s https://your-server-url -u your-username

# API 키로 로그인 (CI/CD 환경 등에서 사용)
uv run deeply-vault login -s https://your-server-url -k your-api-key
```

로그인하면 인증 토큰이 `~/.deeply/vault/token.json` 파일에 저장됩니다.

로그인 과정 상세 설명:

1. 서버 URL을 지정하지 않으면 대화형으로 서버 URL을 입력받습니다.
2. 사용자명을 지정하면 비밀번호만 입력받습니다.
3. 사용자명과 API 키 모두 지정하지 않으면 로그인 방식을 선택할 수 있는 메뉴가 표시됩니다.
4. 인증에 성공하면 발급받은 토큰이 로컬에 저장되고, 이후 명령어에서 자동으로 사용됩니다.

### 2. 프로젝트 초기화

현재 프로젝트 디렉토리에서 Deeply CLI를 초기화합니다. 이 명령은 `.env.vault.yml` 설정 파일을 생성합니다.

```bash
# 기본 초기화 (현재 디렉토리 이름을 볼트 이름으로 사용)
uv run deeply-vault init

# 볼트 이름 지정
uv run deeply-vault init -v my-project

# 기존 설정 덮어쓰기
uv run deeply-vault init -v my-project -f
```

초기화 과정 상세 설명:

1. 볼트 이름을 지정하지 않으면 현재 디렉토리 이름을 기본값으로 사용합니다.
2. 이미 초기화된 프로젝트에서 다시 init 명령을 실행하면 오류가 발생합니다. 이때 `--force` 옵션을 사용하여 덮어쓸 수 있습니다.
3. 초기화하면 `.env.vault.yml` 파일이 생성되며, 이 파일에는 볼트 이름과 서버 URL이 포함됩니다.

`.env.vault.yml` 파일 예시:

```yaml
vault: my-project
server: https://your-server-url
```

### 3. 볼트 관리

볼트는 환경 변수 파일들을 저장하는 논리적인 단위입니다. 각 프로젝트마다 별도의 볼트를 사용할 수 있습니다.

```bash
# 볼트 목록 조회
uv run deeply-vault vault list

# 상세 정보 포함하여 조회
uv run deeply-vault vault list --detail

# 볼트 생성
uv run deeply-vault vault create my-new-vault

# 볼트 선택
uv run deeply-vault vault select my-project

# 볼트 삭제
uv run deeply-vault vault delete my-old-vault
```

볼트 관리 상세 설명:

#### 볼트 목록 조회

볼트 목록을 조회하면 다음 정보가 표시됩니다:

- 볼트 이름
- 상태 (현재 선택된 볼트는 "선택됨"으로 표시)
- 설명 (있는 경우)

상세 정보를 표시하면 생성일, 마지막 수정일, 파일 수, 소유자 등의 추가 정보를 볼 수 있습니다.

#### 볼트 생성

볼트를 생성할 때 다음 정보를 지정할 수 있습니다:

- 볼트 이름 (필수)
- 설명 (선택, `--description` 옵션으로 지정)

#### 볼트 선택

볼트를 선택하면 이후의 명령어(push, pull, sync 등)에서 해당 볼트를 대상으로 작업합니다.

#### 볼트 삭제

볼트를 삭제하면 해당 볼트에 저장된 모든 환경 변수 파일이 함께 삭제됩니다. 이 작업은 되돌릴 수 없으므로 주의해야 합니다.

### 4. 환경 변수 파일 목록 확인

프로젝트에서 관리 중인 환경 변수 파일 목록을 확인합니다.

```bash
# 로컬 파일 목록 확인
uv run deeply-vault list --local

# 서버 파일 목록 확인
uv run deeply-vault list --remote

# 로컬 및 서버 파일 모두 확인
uv run deeply-vault list
```

파일 목록 확인 상세 설명:

#### 로컬 파일 목록

로컬 파일 목록을 확인하면 다음 정보가 표시됩니다:

- 파일 경로 (현재 디렉토리 기준 상대 경로)
- 파일 크기

만약 `.vaultignore` 파일에 의해 무시되는 파일이 있다면, 해당 파일 목록도 함께 표시됩니다.

#### 서버 파일 목록

서버 파일 목록을 확인하면 다음 정보가 표시됩니다:

- 파일 경로
- 마지막 수정일
- 파일 크기

### 5. 환경 변수 파일 업로드

로컬의 `.env` 파일들을 서버에 업로드합니다.

```bash
# 모든 환경 파일 업로드
uv run deeply-vault push

# 서버의 기존 파일을 삭제하고 현재 파일만 유지
uv run deeply-vault push --force
```

업로드 과정 상세 설명:

1. `push` 명령은 현재 디렉토리와 하위 디렉토리에서 `.env` 파일과 `.env.*` 패턴의 파일을 찾아 서버에 업로드합니다.
2. `.vaultignore` 파일에 지정된 변수나 파일은 업로드하지 않습니다.
3. `--force` 옵션을 사용하면 서버의 기존 파일을 모두 삭제하고 현재 로컬 파일만 업로드합니다. 이 작업은 되돌릴 수 없으므로 주의해야 합니다.

업로드되는 파일 예시:

- `.env`
- `.env.development`
- `.env.production`
- `.env.staging`
- `.env.test`

### 6. 환경 변수 파일 다운로드

서버에 저장된 환경 변수 파일을 로컬로 다운로드합니다.

```bash
uv run deeply-vault pull
```

다운로드 과정 상세 설명:

1. `pull` 명령은 서버에 저장된 모든 환경 변수 파일을 로컬로 다운로드합니다.
2. 이미 로컬에 있는 파일은 덮어씁니다.
3. `.vaultignore` 파일에 지정된 변수는 로컬 파일에서 유지됩니다.

### 7. 동기화

서버와 로컬의 환경 변수 파일을 비교하고 동기화합니다.

```bash
# 서버와 로컬 파일 비교 및 동기화
uv run deeply-vault sync

# 서버의 파일을 강제로 로컬과 동기화
uv run deeply-vault sync --force
```

동기화 과정 상세 설명:

1. **파일 목록 비교**:

   - 서버에만 있는 파일: 로컬로 다운로드
   - 로컬에만 있는 파일: 서버에 업로드
   - 양쪽에 있는 파일: 해시값 비교하여 내용이 다른 파일 확인

2. **내용 비교**:
   양쪽에 있으나 내용이 다른 파일에 대해:

   - 차이점(diff)을 화면에 표시
   - 사용자에게 동기화 방향 확인 (로컬 → 서버 또는 서버 → 로컬)

3. **동기화 실행**:
   - 사용자 확인 후 선택된 방향으로 파일 동기화
   - `--force` 옵션을 사용하면 모든 파일을 서버에서 로컬로 강제 동기화

동기화 중 표시되는 정보:

- 동기화할 파일 목록
- 각 파일의 차이점
- 동기화 진행 상황 및 결과

### 8. 환경 변수 비교

두 환경 변수 파일의 차이점을 비교합니다.

```bash
uv run deeply-vault diff .env .env.production
```

비교 결과는 다음과 같이 표시됩니다:

- **추가**: 두 번째 파일에만 있는 변수
- **삭제**: 첫 번째 파일에만 있는 변수
- **수정**: 양쪽에 있지만 값이 다른 변수

비교 상세 설명:

1. `diff` 명령은 두 환경 변수 파일을 파싱하여 변수 단위로 비교합니다.
2. 결과는 테이블 형태로 표시되며, 변경 유형, 변수 이름, 값(수정된 경우 변경 전후 값) 정보를 보여줍니다.
3. 두 파일이 완전히 동일한 경우 "두 파일이 동일합니다." 메시지가 표시됩니다.

### 9. 환경 변수 검색

환경 변수 파일에서 특정 키워드를 검색합니다.

```bash
# 기본 검색
uv run deeply-vault search API_KEY

# 정규식 사용
uv run deeply-vault search --regex "API_.*"

# 파일명에서만 검색
uv run deeply-vault search --files-only production

# 내용에서만 검색
uv run deeply-vault search --content-only SECRET
```

검색 상세 설명:

1. `search` 명령은 현재 디렉토리와 하위 디렉토리의 환경 변수 파일에서 키워드를 검색합니다.
2. 검색 결과는 파일명, 라인 번호, 내용을 포함하는 테이블 형태로 표시됩니다.
3. `--regex` 옵션을 사용하면 정규식 패턴으로 검색할 수 있습니다.
4. `--files-only` 옵션을 사용하면 파일명에서만 검색합니다.
5. `--content-only` 옵션을 사용하면 파일 내용에서만 검색합니다.

검색 결과 예시:

```
┌──────────────┬──────┬───────────────────────────┐
│ 파일         │ 라인 │ 내용                      │
├──────────────┼──────┼───────────────────────────┤
│ .env         │ 5    │ API_KEY=abcdef123456      │
│ .env.staging │ 8    │ API_KEY=staging123456     │
└──────────────┴──────┴───────────────────────────┘
```

### 10. 상태 확인

서버 연결 상태, 버전 정보, 로그인 상태, 현재 선택된 볼트 정보를 표시합니다.

```bash
uv run deeply-vault status
```

상태 확인 상세 설명:

1. `status` 명령은 다음 정보를 표시합니다:

   - 서버 상태 (연결됨/연결 실패)
   - 서버 버전
   - 로그인 상태 (로그인됨/로그아웃됨)
   - 현재 선택된 볼트

2. 서버 연결에 실패한 경우, 서버 상태는 "연결 실패"로 표시되고, 버전은 "알 수 없음"으로 표시됩니다.

3. 로그인되지 않은 경우, 로그인 상태는 "로그아웃됨"으로 표시됩니다.

4. 볼트가 선택되지 않은 경우, 현재 볼트는 "선택되지 않음"으로 표시됩니다.

상태 확인 결과 예시:

```
┌────────────┬─────────────────────────────┐
│ 항목       │ 상태                        │
├────────────┼─────────────────────────────┤
│ 서버 상태  │ 연결됨                      │
│ 서버 버전  │ 1.0.0                       │
│ 로그인 상태│ 로그인됨                    │
│ 현재 볼트  │ my-project                  │
└────────────┴─────────────────────────────┘
```

## 환경 변수 무시하기

`.vaultignore` 파일을 생성하여 서버에 업로드하지 않을 환경 변수나 파일을 지정할 수 있습니다. 각 줄에 무시할 변수 이름이나 파일 패턴을 작성합니다.

`.vaultignore` 파일 예시:

```
# 특정 변수 무시
SECRET_KEY
API_TOKEN

# 패턴으로 무시
*.local
.env.test*
```

무시 기능 상세 설명:

1. `.vaultignore` 파일은 프로젝트 루트 디렉토리에 위치해야 합니다.
2. 파일 패턴은 glob 패턴을 지원합니다 (예: `*.local`, `.env.test*`).
3. 변수 이름을 지정하면 해당 변수는 서버에 업로드되지 않습니다.
4. 변수 무시는 파일 내의 특정 변수만 무시하는 기능입니다. 파일 자체는 업로드되지만, 무시된 변수는 제외됩니다.
5. 파일 패턴을 지정하면 해당 패턴과 일치하는 파일 자체가 업로드되지 않습니다.

## 사용 예시

### 프로젝트 설정

```bash
# 로그인
uv run deeply-vault login -s https://your-server-url

# 프로젝트 초기화
uv run deeply-vault init -v my-project

# 볼트 선택
uv run deeply-vault vault select my-project

# 상태 확인
uv run deeply-vault status
```

### 환경 변수 파일 관리

```bash
# 로컬 파일 목록 확인
uv run deeply-vault list --local

# 파일 업로드
uv run deeply-vault push

# 서버 파일 목록 확인
uv run deeply-vault list --remote

# 파일 동기화
uv run deeply-vault sync
```

### 여러 환경 관리

```bash
# 개발 환경 설정
echo "DEBUG=true\nAPI_URL=https://dev-api.example.com" > .env.development

# 프로덕션 환경 설정
echo "DEBUG=false\nAPI_URL=https://api.example.com" > .env.production

# 스테이징 환경 설정
echo "DEBUG=true\nAPI_URL=https://staging-api.example.com" > .env.staging

# 모든 환경 설정 업로드
uv run deeply-vault push

# 환경 간 차이점 확인
uv run deeply-vault diff .env.development .env.production
```

### CI/CD 파이프라인에서 사용

```bash
# API 키로 로그인
uv run deeply-vault login -s https://your-server-url -k $API_KEY

# 프로덕션 환경 변수 다운로드
uv run deeply-vault pull

# 서버 상태 확인
uv run deeply-vault status
```

## 명령어 참조

### `login`: 서버에 로그인

```bash
uv run deeply-vault login -s [서버URL] -u [사용자명]
uv run deeply-vault login -s [서버URL] -k [API키]
```

- `-s, --server`: 서버 URL 지정
- `-u, --username`: 사용자명 지정 (비밀번호는 프롬프트로 입력)
- `-k, --api-key`: API 키로 로그인 (CI/CD 환경용)

로그인 후 인증 토큰은 `~/.deeply/vault/token.json` 파일에 저장됩니다.

### `logout`: 로그아웃

```bash
uv run deeply-vault logout
```

저장된 인증 토큰을 삭제합니다.

### `init`: 프로젝트 초기화

```bash
uv run deeply-vault init -v [볼트이름] -f
```

- `-v, --vault`: 볼트 이름 지정
- `-f, --force`: 기존 설정 덮어쓰기

현재 디렉토리에 `.env.vault.yml` 설정 파일을 생성합니다. 이 파일에는 볼트 이름과 서버 URL 정보가 포함됩니다.

### `vault`: 볼트 관리

볼트 목록 조회:

```bash
uv run deeply-vault vault list
uv run deeply-vault vault list --detail  # 상세 정보 표시
```

볼트 선택:

```bash
uv run deeply-vault vault select [볼트이름]
```

볼트 생성:

```bash
uv run deeply-vault vault create [볼트이름] --description "볼트 설명"
```

볼트 삭제:

```bash
uv run deeply-vault vault delete [볼트이름]
```

볼트 정보 업데이트:

```bash
uv run deeply-vault vault update [볼트이름] --description "새로운 설명"
```

### `list`: 환경 변수 파일 목록 조회

```bash
uv run deeply-vault list           # 로컬 및 서버 파일 모두 표시
uv run deeply-vault list --local   # 로컬 파일만 표시
uv run deeply-vault list --remote  # 서버 파일만 표시
```

### `push`: 로컬 파일 업로드

```bash
uv run deeply-vault push
uv run deeply-vault push --force   # 서버의 기존 파일을 모두 삭제하고 현재 파일만 업로드
```

### `pull`: 서버 파일 다운로드

```bash
uv run deeply-vault pull
```

### `sync`: 서버와 로컬 파일 동기화

```bash
uv run deeply-vault sync
uv run deeply-vault sync --force   # 서버의 파일을 강제로 로컬과 동기화
```

### `diff`: 환경 변수 파일 비교

```bash
uv run deeply-vault diff [파일1] [파일2]
```

### `search`: 환경 변수 검색

```bash
uv run deeply-vault search [검색어]
uv run deeply-vault search --regex [정규식패턴]   # 정규식 사용
uv run deeply-vault search --files-only [검색어]  # 파일명에서만 검색
uv run deeply-vault search --content-only [검색어] # 내용에서만 검색
```

### `status`: 상태 확인

```bash
uv run deeply-vault status
```

## 환경 변수 파일 형식

Deeply CLI는 다음과 같은 형식의 환경 변수 파일을 지원합니다:

```
# 주석
KEY1=value1
KEY2=value2
KEY_WITH_SPACES="value with spaces"
```

## 문제 해결

### 로그인 문제

로그인에 실패한 경우:

- 서버 URL이 올바른지 확인하세요.
- 사용자 인증 정보가 올바른지 확인하세요.
- 네트워크 연결을 확인하세요.

서버 URL 변경이 필요한 경우:

```bash
uv run deeply-vault login -s https://new-server-url
```

### 파일 동기화 문제

파일 동기화에 실패한 경우:

- 볼트가 선택되어 있는지 확인하세요: `uv run deeply-vault status`
- 로그인 상태를 확인하세요: `uv run deeply-vault status`
- 권한 문제가 있는지 확인하세요.
- 서버 연결 상태를 확인하세요: `uv run deeply-vault status`

동기화 충돌이 발생한 경우:

1. `uv run deeply-vault diff` 명령으로 차이점을 확인하세요.
2. 필요한 경우 로컬 파일을 수정하세요.
3. `uv run deeply-vault push` 또는 `uv run deeply-vault pull`로 동기화를 완료하세요.

### 서버 연결 문제

서버 연결에 실패한 경우:

- 인터넷 연결을 확인하세요.
- 서버 URL이 올바른지 확인하세요: `cat ~/.deeply/vault/config.json`
- 서버가 실행 중인지 확인하세요.
- 방화벽 설정을 확인하세요.

### 권한 문제

권한 오류가 발생한 경우:

- 올바른 볼트를 선택했는지 확인하세요.
- 해당 볼트에 대한 권한이 있는지 확인하세요.
- 로그아웃 후 다시 로그인해보세요: `uv run deeply-vault logout` 후 `uv run deeply-vault login`
