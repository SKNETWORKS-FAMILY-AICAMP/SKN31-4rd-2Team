import os
import sys
import django

# 최상위 폴더(military_life)를 파이썬 경로에 추가하여 config.settings를 찾을 수 있게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from board.models import Category, Post

User = get_user_model()
# Get or create admin user for dummy data
admin_user = User.objects.first()

# Create categories if they don't exist
category_names = ["휴가", "징계", "급여", "전역", "병영생활"]
for name in category_names:
    Category.objects.get_or_create(name=name)

categories = Category.objects.all()

dummy_data = {
    "휴가": [
        ("연가 사용 거부 당했습니다", "정당한 사유 없이 연가를 반려당했습니다. 이럴 땐 어떻게 해야 하나요? 규정상 문제가 없는지 궁금합니다."),
        ("포상휴가 관련 질문", "이번 훈련 우수자로 포상휴가를 받게 되었는데, 언제까지 사용해야 하는지 아시는 분 계신가요?"),
    ],
    "징계": [
        ("징계위원회 회부되었습니다", "어제 일어난 일로 징계위원회에 회부된다고 들었습니다. 절차가 어떻게 진행되는지, 소명 기회는 있는지 알고 싶습니다."),
        ("군기교육대 며칠 가나요?", "보통 스마트폰 무단 반입으로 걸리면 군기교육대 며칠 정도 가는지 궁금합니다."),
    ],
    "급여": [
        ("병장 봉급 언제부터 오르나요?", "2025년 봉급 인상안이 통과됐다고 들었는데 실제 적용 시기를 알고 싶어요."),
        ("적금 만기 해지 방법", "전역이 다음 달인데 군 적금 만기 해지는 휴가 나가서 은행 가면 바로 할 수 있나요?"),
    ],
    "전역": [
        ("전역증 분실", "전역증을 잃어버렸는데 재발급이 가능한가요? 취업할 때 필요하다고 해서 급하게 문의합니다."),
        ("전역 전 휴가 계산", "말년 휴가를 모아서 한번에 나가려고 하는데 최대 며칠까지 붙여서 쓸 수 있나요? 부대마다 다른가요?"),
    ],
    "병영생활": [
        ("선임이 개인 물품을 자꾸 빌려갑니다", "명백히 제 물건인데 허락도 없이 쓰고 돌려주질 않네요. 직접 말하기엔 껄끄러운데 어떻게 대처해야 할까요?"),
        ("주말 종교활동 질문", "이번 주말에 처음으로 종교활동 가보려고 하는데 불교는 간식 뭐 주는지 아시는 분?"),
    ]
}

# Create posts if they don't exist
for cat in categories:
    if cat.name in dummy_data:
        for title, content in dummy_data[cat.name]:
            if not Post.objects.filter(title=title).exists():
                Post.objects.create(
                    author=admin_user,
                    category=cat,
                    title=title,
                    content=content
                )
                print(f"Created post: {title}")

print("Dummy data generation completed.")

