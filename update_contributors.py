import pandas as pd
import json
import os
import pycountry
import urllib.parse

# 1. 환경 변수에서 시트 ID 가져오기 (공백 제거)
SHEET_ID = os.environ.get('GOOGLE_SHEET_ID', '').strip()

if not SHEET_ID:
    # 로컬 테스트용 (시트 ID가 없을 경우 대비)
    SHEET_ID = "1qfWSyzZ0ny2DZVRciA9dr_gYlp6UCierU5o6Mbo9UPU"

# 안전하게 URL 인코딩 처리
encoded_id = urllib.parse.quote(SHEET_ID)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{encoded_id}/export?format=csv"

def get_country_code(name):
    """국가 이름을 ISO 2자리 코드로 변환"""
    exceptions = {
        "South Korea": "kr",
        "United States": "us",
        "Global": "global"
    }
    if name in exceptions:
        return exceptions[name]
    
    try:
        return pycountry.countries.lookup(name).alpha_2.lower()
    except:
        return name.lower().replace(" ", "_")

def clean_category(val):
    """'category - 설명' 형식에서 key값만 추출"""
    if not val: return ""
    return str(val).split(' - ')[0].strip()

def index_to_id(file_code, idx):
    """고유 ID 생성 (예: kr_001)"""
    return f"{file_code}_{idx+1:03d}"

def main():
    # 데이터 로드 및 NaN 처리
    df = pd.read_csv(SHEET_URL)
    df = df.fillna("")
    
    os.makedirs('contributors', exist_ok=True)
    
    # [추가] index.json을 위한 데이터 수집 리스트
    index_data = []
    
    # 국가별 분류 및 JSON 생성
    for country_name, group in df.groupby('Country'):
        file_code = get_country_code(country_name)
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
            
        # 개별 국가 JSON 저장
        with open(relative_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # [추가] 인덱스 정보 수집
        index_data.append({
            "country": country_name,
            "code": file_code,
            "path": relative_path,
            "count": len(json_data)
        })
        print(f"✅ Saved {relative_path}")

    # [추가] 최종 index.json 생성
    index_filename = "contributors/index.json"
    with open(index_filename, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"🚀 All Done! Created index.json with {len(index_data)} countries.")

if __name__ == "__main__":
    main()