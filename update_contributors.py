import pandas as pd
import json
import os

# 1. 구글 시트 정보 (Secrets 사용 권장)
import os as env_os
SHEET_ID = env_os.environ.get('GOOGLE_SHEET_ID', '여기에_시트_ID_직접입력(테스트용)')
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1qfWSyzZ0ny2DZVRciA9dr_gYlp6UCierU5o6Mbo9UPU/export?format=csv"

def get_country_code(name):
    # 특수 케이스 예외 처리
    exceptions = {
        "South Korea": "kr",
        "United States": "us",
        "Global": "global"
    }
    if name in exceptions:
        return exceptions[name]
    
    try:
        # 국가명 검색 -> 2자리 코드(ISO 3166-1 alpha_2) 반환
        return pycountry.countries.lookup(name).alpha_2.lower()
    except:
        # 라이브러리가 못 찾으면 공백을 언더바로 바꿔 파일명 생성
        return name.lower().replace(" ", "_")

def clean_category(val):
    if not val: return ""
    return str(val).split(' - ')[0].strip()

def index_to_id(file_code, idx):
    return f"{file_code}_{idx+1:03d}"

def main():
    # 데이터 로드
    df = pd.read_csv(SHEET_URL)
    
    # NaN 결측치를 빈 문자열로 처리 (JSON 깨짐 방지)
    df = df.fillna("")
    
    # 폴더 생성
    os.makedirs('contributors', exist_ok=True)
    
    # 국가별 분류
    for country_name, group in df.groupby('Country'):
        file_code = get_country_code(country_name)
        filename = f"contributors/{file_code}.json"
        
        json_data = []
        for i, (index, row) in enumerate(group.iterrows()):
            item = {
                "id": index_to_id(file_code, i),
                "name": row['Organization Name'],
                "category": clean_category(row['Category']),
                "country": file_code.upper(),
                "tags": [t.strip() for t in str(row['Search Tags']).split(',')] if row['Search Tags'] else [],
                "url": row['Official URL'], # 이제 NaN 대신 "" 가 들어갑니다.
                "desc": row['Description']
            }
            json_data.append(item)
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved {filename}")

if __name__ == "__main__":
    main()