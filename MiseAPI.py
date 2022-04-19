import requests
from pyproj import Transformer

import service_key

service_key = service_key.ServiceKey.mise_key


# 위도, 경도 >>> TM 좌표, 리턴 값(도,근처 측정소)
def get_nearby_station(lat, lng):
    # pyproj를 이용한 좌표 변환
    transformer = Transformer.from_crs("epsg:4326", "epsg:2097")

    x, y = lat, lng
    tmy, tmx = transformer.transform(x, y)

    url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList'
    params = {'serviceKey': service_key, 'returnType': 'json', 'tmX': tmx, 'tmY': tmy,
              }

    response = requests.get(url, params=params)
    stations = response.json().get('response').get('body').get('items')
    # json 거리 순으로 정렬
    stations = sorted(stations, key=lambda pos: pos['tm'], reverse=False)
    target_station = stations[0]
    sido_name = target_station['addr'][0:2]
    station_name = target_station['stationName']
    print(station_name)
    return sido_name, station_name


def get_mise_info(lat=37.29650670336803, lng=126.9850504453901):
    sido_name, station_name = get_nearby_station(lat, lng)

    url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
    params = {'serviceKey': service_key, 'returnType': 'json', 'pageNo': '1',
              'stationName': station_name, 'dataTerm': 'DAILY', 'ver': '1.3'}

    response = requests.get(url, params=params)
    mise_data = response.json().get('response').get('body').get('items')
    target_data = sorted(mise_data, key=lambda date: date['dataTime'], reverse=True)  # dataTime을 기준 으로 내림 차순 정렬
    target_data = target_data[0]
    result = dict()

    try:
        pm10_grade = target_data['pm10Grade']
        pm25_grade = target_data['pm25Grade']
    except KeyError:
        pm10_grade = target_data['pm10Grade1h']
        pm25_grade = target_data['pm25Grade1h']

    if pm10_grade == '1':
        pm10_state = "좋음"
    elif pm10_grade == '2':
        pm10_state = "보통"
    elif pm10_grade == '3':
        pm10_state = "나쁨"
    elif pm10_grade == '4':
        pm10_state = "매우나쁨"
    else:
        pm10_state = "_"

    pm10 = dict()
    pm10['value'] = target_data['pm10Value']
    pm10['grade'] = pm10_state
    result['pm10'] = pm10

    if pm25_grade == '1':
        pm25_state = "좋음"
    elif pm25_grade == '2':
        pm25_state = "보통"
    elif pm25_grade == '3':
        pm25_state = "나쁨"
    elif pm25_grade == '4':
        pm25_state = "매우나쁨"
    else:
        pm25_state = "_"

    pm25 = dict()
    pm25['value'] = target_data['pm25Value']
    pm25['grade'] = pm25_state
    result['pm25'] = pm25
    result['do'] = sido_name

    return result


if __name__ == '__main__':
    print(get_mise_info())
