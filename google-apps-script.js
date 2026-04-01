/**
 * HabitFund Data - Google Sheets 자동 동기화
 * 
 * 이 스크립트를 Google Sheets의 Apps Script에 추가하세요.
 * 변경 사항이 있을 때만 GitHub Actions를 트리거합니다.
 * 
 * 설정 방법:
 * 1. Google Sheets 열기
 * 2. 확장 프로그램 → Apps Script
 * 3. 이 코드 복사 & 붙여넣기
 * 4. setup() 함수 실행하여 설정값 입력
 * 5. 트리거 설정 (시계 아이콘)
 */

const PROPERTIES = PropertiesService.getScriptProperties();

/**
 * 초기 설정 함수
 * Apps Script 편집기에서 이 함수를 선택하고 실행하세요.
 * GitHub 토큰과 Repository 정보를 입력받습니다.
 */
function setup() {
  const ui = SpreadsheetApp.getUi();
  
  // GitHub Token 입력
  const tokenResponse = ui.prompt(
    '설정: GitHub Personal Access Token',
    'GitHub Personal Access Token을 입력하세요 (ghp_로 시작):',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (tokenResponse.getSelectedButton() !== ui.Button.OK) {
    ui.alert('설정이 취소되었습니다.');
    return;
  }
  
  const token = tokenResponse.getResponseText().trim();
  if (!token || !token.startsWith('ghp_')) {
    ui.alert('올바른 GitHub Token이 아닙니다. ghp_로 시작해야 합니다.');
    return;
  }
  
  // Repository Owner 입력
  const ownerResponse = ui.prompt(
    '설정: GitHub Username',
    'GitHub 사용자명을 입력하세요:',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (ownerResponse.getSelectedButton() !== ui.Button.OK) {
    ui.alert('설정이 취소되었습니다.');
    return;
  }
  
  const owner = ownerResponse.getResponseText().trim();
  
  // Repository Name 입력
  const repoResponse = ui.prompt(
    '설정: Repository Name',
    'Repository 이름을 입력하세요:',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (repoResponse.getSelectedButton() !== ui.Button.OK) {
    ui.alert('설정이 취소되었습니다.');
    return;
  }
  
  const repo = repoResponse.getResponseText().trim();
  
  // Branch 입력 (기본값: main)
  const branchResponse = ui.prompt(
    '설정: Branch Name',
    '브랜치 이름을 입력하세요 (기본값: main):',
    ui.ButtonSet.OK_CANCEL
  );
  
  let branch = 'main';
  if (branchResponse.getSelectedButton() === ui.Button.OK) {
    const inputBranch = branchResponse.getResponseText().trim();
    if (inputBranch) {
      branch = inputBranch;
    }
  }
  
  // 설정 저장
  PROPERTIES.setProperty('GITHUB_TOKEN', token);
  PROPERTIES.setProperty('REPO_OWNER', owner);
  PROPERTIES.setProperty('REPO_NAME', repo);
  PROPERTIES.setProperty('BRANCH', branch);
  
  ui.alert(
    '설정 완료',
    `GitHub: ${owner}/${repo} (${branch})\n\n이제 트리거를 설정하세요:\n1. onEdit - 수정 시\n2. checkAndTrigger - 5-10분마다`,
    ui.ButtonSet.OK
  );
  
  Logger.log('Configuration saved successfully');
}

/**
 * 수동 설정 함수 (대화상자 없이 직접 입력)
 * 타임아웃 에러가 발생하면 이 함수를 사용하세요.
 * 
 * 사용법:
 * 1. 아래 값을 수정
 * 2. 이 함수 실행
 */
function manualSetup() {
  // ========== 여기에 값을 직접 입력하세요 ==========
  const token = 'ghp_YOUR_TOKEN_HERE';
  const owner = 'YOUR_GITHUB_USERNAME';
  const repo = 'habitfund-data';
  const branch = 'main';
  // =================================================
  
  // 검증
  if (token === 'ghp_YOUR_TOKEN_HERE' || !token.startsWith('ghp_')) {
    Logger.log('❌ GitHub Token을 설정하세요');
    return;
  }
  
  if (owner === 'YOUR_GITHUB_USERNAME') {
    Logger.log('❌ GitHub Username을 설정하세요');
    return;
  }
  
  // 저장
  PROPERTIES.setProperty('GITHUB_TOKEN', token);
  PROPERTIES.setProperty('REPO_OWNER', owner);
  PROPERTIES.setProperty('REPO_NAME', repo);
  PROPERTIES.setProperty('BRANCH', branch);
  
  Logger.log('✅ 설정이 저장되었습니다.');
  Logger.log(`GitHub: ${owner}/${repo} (${branch})`);
  
  const ui = SpreadsheetApp.getUi();
  ui.alert('설정 완료', `GitHub: ${owner}/${repo} (${branch})`, ui.ButtonSet.OK);
}

/**
 * 설정 확인 함수
 */
function viewConfig() {
  const token = PROPERTIES.getProperty('GITHUB_TOKEN');
  const owner = PROPERTIES.getProperty('REPO_OWNER');
  const repo = PROPERTIES.getProperty('REPO_NAME');
  const branch = PROPERTIES.getProperty('BRANCH');
  
  const ui = SpreadsheetApp.getUi();
  
  if (!token || !owner || !repo) {
    ui.alert('설정이 없습니다. setup() 함수를 먼저 실행하세요.');
    return;
  }
  
  const maskedToken = token.substring(0, 8) + '...' + token.substring(token.length - 4);
  
  ui.alert(
    '현재 설정',
    `Token: ${maskedToken}\nOwner: ${owner}\nRepo: ${repo}\nBranch: ${branch || 'main'}`,
    ui.ButtonSet.OK
  );
}

/**
 * 설정 값 가져오기
 */
function getConfig() {
  return {
    GITHUB_TOKEN: PROPERTIES.getProperty('GITHUB_TOKEN'),
    REPO_OWNER: PROPERTIES.getProperty('REPO_OWNER'),
    REPO_NAME: PROPERTIES.getProperty('REPO_NAME'),
    BRANCH: PROPERTIES.getProperty('BRANCH') || 'main'
  };
}

/**
 * 스프레드시트 편집 시 자동 실행
 * 변경 플래그만 설정 (즉시 실행하지 않음)
 */
function onEdit(e) {
  const now = new Date().getTime();
  PROPERTIES.setProperty('LAST_EDIT_TIME', now.toString());
  PROPERTIES.setProperty('HAS_CHANGES', 'true');
  
  Logger.log('Change detected at: ' + new Date(now));
}

/**
 * 시간 기반 트리거로 주기적 실행 (5-10분마다)
 * 변경 플래그가 true일 때만 GitHub Actions 트리거
 */
function checkAndTrigger() {
  const hasChanges = PROPERTIES.getProperty('HAS_CHANGES');
  const lastEditTime = PROPERTIES.getProperty('LAST_EDIT_TIME');
  
  if (hasChanges === 'true') {
    Logger.log('Changes detected. Triggering GitHub Actions...');
    const result = triggerGitHubAction();
    
    if (result.success) {
      // 성공 시 플래그 초기화
      PROPERTIES.setProperty('HAS_CHANGES', 'false');
      PROPERTIES.setProperty('LAST_SYNC_TIME', new Date().getTime().toString());
      Logger.log('✅ GitHub Actions triggered successfully');
    } else {
      Logger.log('❌ Failed to trigger GitHub Actions: ' + result.error);
    }
  } else {
    Logger.log('No changes detected. Skipping sync.');
  }
}

/**
 * GitHub Actions workflow를 트리거
 */
function triggerGitHubAction() {
  const config = getConfig();
  
  // 설정 확인
  if (!config.GITHUB_TOKEN || !config.REPO_OWNER || !config.REPO_NAME) {
    return {
      success: false,
      error: 'Configuration not set. Run setup() first.'
    };
  }
  
  const url = `https://api.github.com/repos/${config.REPO_OWNER}/${config.REPO_NAME}/dispatches`;
  
  const payload = {
    event_type: 'sheets-updated',
    client_payload: {
      timestamp: new Date().toISOString(),
      source: 'google-apps-script'
    }
  };
  
  const options = {
    method: 'post',
    headers: {
      'Authorization': 'Bearer ' + config.GITHUB_TOKEN,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
      'User-Agent': 'Google-Apps-Script'
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode === 204) {
      return { success: true };
    } else {
      return { 
        success: false, 
        error: `HTTP ${statusCode}: ${response.getContentText()}` 
      };
    }
  } catch (error) {
    return { 
      success: false, 
      error: error.toString() 
    };
  }
}

/**
 * 수동 테스트용 함수
 * Apps Script 편집기에서 직접 실행 가능
 */
function testTrigger() {
  Logger.log('=== Manual Test Trigger ===');
  const result = triggerGitHubAction();
  
  if (result.success) {
    Logger.log('✅ Test successful! Check GitHub Actions tab.');
  } else {
    Logger.log('❌ Test failed: ' + result.error);
  }
}

/**
 * 디버깅용: 현재 상태 확인
 */
function checkStatus() {
  const hasChanges = PROPERTIES.getProperty('HAS_CHANGES');
  const lastEditTime = PROPERTIES.getProperty('LAST_EDIT_TIME');
  const lastSyncTime = PROPERTIES.getProperty('LAST_SYNC_TIME');
  
  Logger.log('=== Current Status ===');
  Logger.log('Has Changes: ' + hasChanges);
  Logger.log('Last Edit: ' + (lastEditTime ? new Date(parseInt(lastEditTime)) : 'Never'));
  Logger.log('Last Sync: ' + (lastSyncTime ? new Date(parseInt(lastSyncTime)) : 'Never'));
}

/**
 * 초기화 함수 (필요시 사용)
 */
function resetFlags() {
  PROPERTIES.deleteProperty('HAS_CHANGES');
  PROPERTIES.deleteProperty('LAST_EDIT_TIME');
  Logger.log('Flags reset.');
}
