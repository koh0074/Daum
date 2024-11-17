import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from apps.places.models import Festival

def parse_date(date_text):
    """
    날짜 텍스트를 파싱하여 시작 날짜와 종료 날짜를 반환합니다.
    """
    # 날짜와 시간 정보 분리
    date_pattern = r'(\d{4}\. \d{1,2}\. \d{1,2})'
    dates = re.findall(date_pattern, date_text)

    if len(dates) == 1:
        # 단일 날짜만 있는 경우
        start_date = datetime.strptime(dates[0], "%Y. %m. %d").date()
        end_date = start_date
    elif len(dates) == 2:
        # 시작 날짜와 종료 날짜가 있는 경우
        start_date = datetime.strptime(dates[0], "%Y. %m. %d").date()
        end_date = datetime.strptime(dates[1], "%Y. %m. %d").date()
    else:
        return None, None

    return start_date, end_date

def fetch_festival_data():
    url = "https://www.mcst.go.kr/kor/s_culture/festival/festivalList.jsp"  # 실제 URL로 변경하세요
    response = requests.get(url)
    if response.status_code != 200:
        print(f"HTTP 요청 실패: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    festival_list = soup.find('ul', class_='mediaWrap color01')
    if not festival_list:
        print("축제 목록을 찾지 못했습니다.")
        return

    festivals = festival_list.find_all('li')
    for festival in festivals:
        try:
            # 축제 제목 추출
            title_element = festival.find('p', class_='title')
            name = title_element.text.strip() if title_element else None

            if not name:
                print("제목을 찾지 못했습니다.")
                continue

            # 축제 이미지 추출
            image_element = festival.find('div', class_='img').find('img')
            image_url = image_element['src'] if image_element else None

            # 축제 기간 추출
            detail_info = festival.find('ul', class_='detail_info')
            if detail_info:
                date_li = detail_info.find_all('li')
                date_text = date_li[0].text.split('기간:')[1].strip() if len(date_li) > 0 else None

                # 날짜 파싱
                start_date, end_date = parse_date(date_text)
                if not start_date or not end_date:
                    print(f"날짜 형식이 맞지 않음: {date_text}")
                    continue

                # 장소 추출
                location = date_li[1].text.split('장소:')[1].strip() if len(date_li) > 1 else "장소 미정"
            else:
                start_date = end_date = None
                location = "장소 미정"

            # 데이터베이스에 저장 (중복 방지)
            Festival.objects.get_or_create(
                name=name,
                location=location,
                start_date=start_date,
                end_date=end_date,
                image=image_url
            )
            print(f"축제 저장: {name}")

        except Exception as e:
            print(f"오류 발생: {e}")

    print("크롤링 완료")
