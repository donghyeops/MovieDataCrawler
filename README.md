# Movie Data Crawler
네이버 영화 웹사이트에서 영화 메타 데이터를 크롤링합니다.

크롤링 구간 및 메타 데이터 범위는 config.ini에서 설정 가능합니다.

대상 웹사이트 예시 : [URL(date=20100101)](https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&tg=0&date=20100101)

[로그인 기능은 선택사항이며 [NaverCaptcha 오픈소스](https://github.com/lumyjuwon/NaverCaptcha)를 활용하였습니다.]



## How to Run
```
pip install -r requirements.txt
python data_crawling.py # python version <= 3.7
```
## Dataset Example
```
"180372": {  
		"title": "극장판 공룡메카드: 타이니소어의 섬",  
		"mv_code": "180372",  
		"image": "180372.jpg", 
		"categories": [  
			"애니메이션"  
		],  
		"countries": [  
			"한국"  
		],  
		"showtime(m)": 70,  
		"summary": "타이니소어로 가득한 환상의 섬에서 펼쳐지는 뜨거운 우정 이야기가 시작된다!",  
		"contents": "머나먼 옛날, 소행성 충돌로 인해 지구의 공룡들이 모두 사라지고\n사람들에게 알려지지 않은 어느 작은 섬에서 공룡들은 아주 작은 모습의 타이니소어로 탄생한다. \n씩씩한 트리케라, 장난꾸러기 티라노, 잠꾸러기 스테고 등 타이니소어 친구들이\n도토리 축구를 하며 즐거운 나날을 보내고 있던 중,\n수상한 악당들이 나타나 평화로운 ‘타이니소어의 섬’을 위협하기 시작하는데… \n타이니소어들을 노리는 수상한 눈빛의 정체는? \n과연 이들은 위기에 처한 지상 낙원 ‘타이니소어의 섬’을 지켜낼 수 있을까?",  
		"netizen_score": 9.17,  
		"audience_score": 9.14,  
		"reple": "와 예매율 2위 실화냐 공룡 떡상 가자  "  
	},  
```

## Dependency
 - selenium
 - beautifulsoup4
 - pyperclip
 - pywin32
 
## Crawling Target
 - 영화제목
 - 포스터 이미지 (config.ini에서 설정)
 - 영화 카테고리 (ex: 멜로, 액션, SF, ...)
 - 국가 (한국, 영국, 미국, ...)
 - 관객 평점
 - 네티즌 평점
 - 줄거리 요약문
 - 줄거리 본문
 - 인기 리뷰 (추천 수가 제일 높은 댓글)
