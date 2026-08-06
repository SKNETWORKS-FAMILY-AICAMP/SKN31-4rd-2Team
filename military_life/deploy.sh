#!/bin/bash
set -e

cd ~/SKN31-4th-2Team/military_life

echo "1. 최신 코드 받는 중..."
git pull

echo "2. 패키지 설치 중..."
source ~/SKN31-4th-2Team/.venv/bin/activate
uv pip install -r requirements-linux.txt

echo "3. 마이그레이션 적용 중..."
python manage.py migrate

echo "4. 정적파일 모으는 중..."
python manage.py collectstatic --noinput

echo "5. gunicorn 재시작..."
sudo systemctl restart gunicorn

echo "배포 완료!"
