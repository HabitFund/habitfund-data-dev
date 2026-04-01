# Google Sheets 자동 동기화 설정 가이드

이 가이드는 Google Sheets의 변경 사항을 자동으로 GitHub에 동기화하는 방법을 안내합니다.

## 📋 개요

Google Sheets에서 데이터를 수정하면:
1. Google Apps Script가 변경을 감지
2. 5-10분마다 변경 여부 확인
3. 변경이 있으면 GitHub Actions 트리거
4. Python 스크립트 실행 → JSON 파일 생성 → 자동 커밋

## 🔧 설정 단계

### 1. GitHub Personal Access Token 생성

1. GitHub 로그인 → [Settings](https://github.com/settings/tokens)
2. **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. **Generate new token (classic)** 클릭
4. 설정:
   - **Note**: `HabitFund-Dev Data Sync` (원하는 이름)
   - **Expiration**: `No expiration` 또는 적절한 기간
   - **Select scopes**: ✅ `repo` (전체 체크)
5. **Generate token** 클릭
6. 🔑 **토큰 복사** (한 번만 표시됨! 안전한 곳에 저장)

### 2. GitHub Repository에 토큰 등록

1. GitHub Repository → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. Secret 추가:
   - **Name**: `GH_PAT` (또는 원하는 이름)
   - **Secret**: 위에서 복사한 토큰
4. **Add secret** 클릭

> **참고**: 이미 설정된 `GOOGLE_SHEET_ID`, `SLACK_WEBHOOK_URL`도 동일한 위치에 있어야 합니다.

### 3. Google Sheets에 Apps Script 추가

1. **Google Sheets 열기** (동기화할 시트)
2. **확장 프로그램** → **Apps Script**
3. 기존 코드 삭제 후 `google-apps-script.js` 파일 내용 복사 & 붙여넣기
4. 💾 **저장** (Ctrl+S 또는 Command+S)
5. **setup() 함수 실행**:
   - 함수 목록에서 `setup` 선택
   - **실행** 버튼 클릭
   - 대화상자에 차례대로 입력:
     - GitHub Personal Access Token (ghp_로 시작하는 토큰)
     - GitHub 사용자명
     - Repository 이름 (habitfund-data-dev)
     - 브랜치 이름 (main 또는 master)
   - 권한 승인 (처음 1회만)

> **보안**: 토큰은 코드에 저장되지 않고 Google Script Properties에 암호화되어 저장됩니다.

### 4. 트리거 설정

Apps Script 편집기에서:

#### 트리거 1: 변경 감지 (onEdit)
1. 왼쪽 **시계 아이콘** (트리거) 클릭
2. **+ 트리거 추가** 클릭
3. 설정:
   - **실행할 함수 선택**: `onEdit`
   - **실행할 배포 선택**: `Head`
   - **이벤트 소스 선택**: `스프레드시트에서`
   - **이벤트 유형 선택**: `수정 시`
4. **저장** 클릭

#### 트리거 2: 주기적 확인 (checkAndTrigger)
1. **+ 트리거 추가** 클릭
2. 설정:
   - **실행할 함수 선택**: `checkAndTrigger`
   - **실행할 배포 선택**: `Head`
   - **이벤트 소스 선택**: `시간 기반`
   - **시간 기반 트리거 유형 선택**: `분 단위 타이머`
   - **시간 간격 선택(분)**: `5분마다` 또는 `10분마다`
3. **저장** 클릭

### 5. 권한 승인

처음 트리거를 저장하면 권한 요청이 나타납니다:
1. **권한 검토** 클릭
2. Google 계정 선택
3. **고급** → **{프로젝트 이름}(으)로 이동** 클릭
4. **허용** 클릭

## 🧪 테스트

### 설정 확인
1. Apps Script 편집기에서 `viewConfig` 함수 선택
2. **실행** 버튼 클릭
3. 현재 저장된 설정 확인 (토큰은 마스킹되어 표시됨)

### 방법 1: Apps Script에서 직접 테스트
1. Apps Script 편집기에서 `testTrigger` 함수 선택
2. **실행** 버튼 클릭
3. **실행 로그** 확인 (Ctrl+Enter)
4. GitHub Repository → **Actions** 탭에서 워크플로우 실행 확인

### 방법 2: Google Sheets에서 테스트
1. Google Sheets에서 아무 셀이나 수정
2. 5-10분 대기 (트리거 간격에 따라)
3. GitHub Repository → **Actions** 탭에서 자동 실행 확인

## 📊 상태 확인

Apps Script 편집기에서:
1. `checkStatus` 함수 선택 → **실행**
2. **실행 로그** 확인:
   ```
   Has Changes: true/false
   Last Edit: 2026-04-02 15:30:00
   Last Sync: 2026-04-02 15:35:00
   ```

## 🔍 문제 해결

### 설정이 저장되지 않음
- [ ] `setup()` 함수를 실행했는지 확인
- [ ] 권한을 승인했는지 확인
- [ ] `viewConfig()` 함수로 저장된 설정 확인

### GitHub Actions가 트리거되지 않음
- [ ] `viewConfig()`로 GitHub Token이 올바르게 저장되었는지 확인
- [ ] Token에 `repo` 권한이 있는지 확인
- [ ] Repository Owner/Name이 정확한지 확인
- [ ] Apps Script 실행 로그에서 에러 확인
- [ ] `testTrigger()` 함수로 수동 테스트

### 변경했는데 동기화 안 됨
- [ ] `onEdit` 트리거가 설정되었는지 확인
- [ ] `checkAndTrigger` 트리거가 5-10분마다 실행되도록 설정되었는지 확인
- [ ] `checkStatus()` 함수로 Has Changes 플래그 확인

### 권한 에러
- [ ] Apps Script에서 UrlFetchApp 권한이 승인되었는지 확인
- [ ] Google 계정 재인증 시도
- [ ] `setup()` 함수 재실행

## 🎯 장점

✅ **변경 시에만 실행** - GitHub Actions 무료 사용량 절약  
✅ **빠른 동기화** - 5-10분 이내에 반영  
✅ **Debouncing** - 여러 번 수정해도 한 번만 실행  
✅ **수동 실행 가능** - GitHub Actions 탭에서 언제든 실행 가능  

## 📝 참고

- Apps Script 로그: Apps Script 편집기 → **실행 로그** (Ctrl+Enter)
- GitHub Actions 로그: Repository → **Actions** 탭
- 수동 실행: Repository → **Actions** → **Sync Google Sheets to JSON** → **Run workflow**
