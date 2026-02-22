import pandas as pd
import json
import os
import sys
import pycountry
import urllib.parse
import urllib.request

# 1. 환경 변수 설정
SHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

if SHEET_ID:
    SHEET_ID = SHEET_ID.strip()

if not SHEET_ID:
    print("❌ GOOGLE_SHEET_ID environment variable is not set. Aborting.")
    sys.exit(1)

if SLACK_WEBHOOK_URL:
    SLACK_WEBHOOK_URL = SLACK_WEBHOOK_URL.strip()

# 안전하게 URL 인코딩 처리 (한글 등 방지)
encoded_id = urllib.parse.quote(SHEET_ID)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{encoded_id}/export?format=csv"

def get_country_info(name):
    """국가 이름으로 코드, 풀네임, 국기 이미지 URL을 반환"""
    # 특수 케이스 및 매핑 예외 처리
    exceptions = {
        "South Korea": ("kr", "South Korea"),
        "United States": ("us", "United States"),
        "Global": ("global", "Global"),
        "Russia": ("ru", "Russia"),
    }
    
    if name in exceptions:
        code, full_name = exceptions[name]
    else:
        try:
            # pycountry를 이용한 표준 국가 정보 탐색
            lookup = pycountry.countries.lookup(name)
            code = lookup.alpha_2.lower()
            full_name = lookup.name
        except:
            # 라이브러리가 찾지 못할 경우 기본 처리
            code = name.lower().replace(" ", "_")
            full_name = name
            
            # 슬랙으로 알림 전송
            warning_msg = f"⚠️ Country lookup failed for '{name}'. Using fallback code: '{code}'"
            print(warning_msg)
            send_slack_message(warning_msg)

    # 국기 이미지 서비스 (flagcdn) 활용
    if code == "global":
        flag_url = "https://flagcdn.com/w40/un.png"  # Global은 UN기로 대체
    else:
        flag_url = f"https://flagcdn.com/w40/{code}.png"
        
    return code, full_name, flag_url

def clean_category(val):
    """'category - 설명' 형식에서 key값만 추출"""
    if not val: return ""
    return str(val).split(' - ')[0].strip()

def index_to_id(file_code, idx):
    """고유 ID 생성 (예: kr_001)"""
    return f"{file_code}_{idx+1:03d}"

def send_slack_message(message):
    """Slack Webhook으로 메시지 전송"""
    if not SLACK_WEBHOOK_URL:
        print("⚠️ SLACK_WEBHOOK_URL not set. Skipping notification.")
        return

    payload = {
        "text": message
    }
    
    try:
        req = urllib.request.Request(
            SLACK_WEBHOOK_URL, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✅ Slack notification sent.")
            else:
                print(f"⚠️ Failed to send Slack notification: {response.status}")
    except Exception as e:
        print(f"⚠️ Error sending Slack notification: {e}")

def main():
    # 데이터 로드 및 NaN(결측치) 처리
    try:
        df = pd.read_csv(SHEET_URL)
        df = df.fillna("")
    except Exception as e:
        print(f"❌ Error loading sheet: {e}")
        return

    # 출력 폴더 생성
    os.makedirs('contributors', exist_ok=True)
    
    # index.json에 담을 국가 리스트
    index_data = []
    
    # 2. 국가별 그룹화 및 개별 JSON 파일 생성
    for country_name, group in df.groupby('Country'):
        # 국가 상세 정보 획득
        file_code, full_name, flag_url = get_country_info(country_name)
        
        file_name = f"{file_code}.json"
        relative_path = f"contributors/{file_name}"
        
        json_data = []
        for i, (index, row) in enumerate(group.iterrows()):
            item = {
                "id": index_to_id(file_code, i),
                "name": row['Organization Name'],
                "category": clean_category(row['Category']),
                "country": file_code.upper(),
                "tags": [t.strip() for t in str(row['Search Tags']).split(',')] if row['Search Tags'] else [],
                "url": row['Official URL'],
                "desc": row['Description']
            }
            json_data.append(item)
            
        # 각 국가별 JSON 저장
        with open(relative_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # 3. 인덱스 정보 수집 (풀네임 및 국기 포함)
        index_data.append({
            "country": full_name,      # 국가 전체 이름
            "code": file_code,      # kr, us 등 소문자 코드
            "flag": flag_url,       # 국기 이미지 URL
            "path": relative_path,  # 파일 경로
            "count": len(json_data) # 포함된 단체 수
        })
        print(f"✅ Saved {relative_path} ({len(json_data)} items)")

    # 4. 최종 index.json 파일 생성
    index_filename = "contributors/index.json"
    with open(index_filename, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🚀 All Done! Index file created at {index_filename}")

    # Slack 알림 전송
    total_countries = len(index_data)
    total_items = sum(item['count'] for item in index_data)
    message = (
        f"🚀 *HabitFund Data Update Complete*\n"
        f"• Countries: {total_countries}\n"
        f"• Total Contributors: {total_items}\n"
        f"• Index File: `{index_filename}` created successfully."
    )
    send_slack_message(message)

if __name__ == "__main__":
    main()
