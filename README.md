# HabitFund Data (Dev)
HabitFund 앱 개발 및 테스트를 위한 후원처 및 습관 프리셋 데이터 저장소입니다.

## 폴더 구조
- `/contributors`: 국가별 JSON 데이터 (KR, US, JP 등)
- `/tags`: 습관 태그 프리셋 데이터 (예정)

## 자동 동기화

Google Sheets의 데이터가 변경되면 자동으로 JSON 파일로 변환됩니다.

### 동작 방식
1. Google Sheets에서 데이터 수정
2. Google Apps Script가 변경 감지
3. 5-10분 이내에 GitHub Actions 자동 실행
4. JSON 파일 생성 및 자동 커밋

### 설정 방법
자세한 설정 가이드는 [SETUP.md](SETUP.md)를 참고하세요.

### 수동 실행
필요 시 [GitHub Actions](../../actions) 탭에서 수동으로 실행할 수 있습니다.

