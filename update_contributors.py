import pandas as pd
import json
import os
import re

# 1. 구글 시트 정보 (본인의 시트 ID로 교체하세요)
SHEET_ID = "여기에_복사한_시트_ID를_넣으세요"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1qfWSyzZ0ny2DZVRciA9dr_gYlp6UCierU5o6Mbo9UPU/export?format=csv"

# 2. 국가명 -> 파일명 매핑 (추가 가능)
COUNTRY_MAP = {
    "South Korea": "kr",
    "United States": "en",
    "Japan": "jp",
    "Global": "global"
}

def clean_category(val):
    # "religion - 종교..." 에서 "religion"만 추출
    if pd.isna(val): return ""
    return val.split(' - ')[0].strip()

def main():
    # 데이터 불러오기
    df = pd.read_csv(SHEET_URL)
    
    # 카테고리 정제
    df['Category'] = df['Category'].apply(clean_category)
    
    # 국가별로 그룹화하여 파일 저장
    for country_name, group in df.groupby('Country'):
        file_code = COUNTRY_MAP.get(country_name, country_name.lower().replace(" ", "_"))
        filename = f"contributors/{file_code}.json"
        
        # JSON 구조 생성
        json_data = []
        for _, row in group.iterrows():
            item = {
                "id": f"{file_code}_{index_to_id(row.name)}", # 간단한 ID 생성기
                "name": row['Organization Name'],
                "category": row['Category'],
                "country": file_code.upper(),
                "tags": [t.strip() for t in str(row['Search Tags']).split(',')] if pd.notna(row['Search Tags']) else [],
                "url": row['Official URL'],
                "desc": row['Description']
            }
            json_data.append(item)
        
        # 폴더가 없으면 생성
        os.makedirs('contributors', exist_ok=True)
        
        # 파일 쓰기
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"Saved {filename}")

def index_to_id(idx):
    return f"{idx+1:03d}"

if __name__ == "__main__":
    main()