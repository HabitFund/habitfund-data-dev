import os
import sys
from update_contributors import get_country_info, send_slack_message

# 테스트를 위한 환경 변수 확인
webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
if not webhook_url:
    print("❌ SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
    sys.exit(1)

print(f"✅ Webhook URL found: {webhook_url[:10]}...") 

print("\n--- Testing Unknown Country ---")
# 존재하지 않는 국가 이름으로 테스트 (Slack 알림이 와야 함)
trial1 = "wonderland"
code, name, flag = get_country_info(trial1)

print(f"\nResult:")
print(f"Code: {code}")
print(f"Name: {name}")
print(f"Flag: {flag}")

if code == "wonderland":
    print("\n✅ Fallback logic worked (code is lowercase name). Check your Slack for a warning message!")
else:
    print("\n❌ Something unexpected happened.")


trial2 = "USA"
code, name, flag = get_country_info(trial2)

print(f"\nResult:")
print(f"Code: {code}")
print(f"Name: {name}")
print(f"Flag: {flag}")

if code == "us":
    print("\n✅ Fallback logic worked (code is lowercase name). Check your Slack for a warning message!")
else:
    print("\n❌ Something unexpected happened.")