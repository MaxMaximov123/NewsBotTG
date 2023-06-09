from pprint import pprint

import requests
from scripts import config
from bs4 import BeautifulSoup as BS
import json
from threading import Thread
import asyncio
import logging

path_ = ''
LOG_LEVEL = logging.INFO
LOGFORMAT = "%(asctime)-4s | %(levelname)-4s | %(message)s"
logging.basicConfig(
	level=logging.INFO,
	format=LOGFORMAT,
)

data = {}


async def search(text):
	exp_data = []
	try:
		res_data = requests.get(
			f'https://dzen.ru/news/search?issue_tld=ru&p=1&text={text}'
			f'&ajax=10000&neo_parent_id=1681220433567864-7112010267673059742-'
			f'vwm4cd6b67joezqu-BAL-1570-NEWS-NEWS_NEWS_SEARCH', headers=config.HEADERS_TO_NEWS).json()['data']['stories']
		for i in res_data:
			i = i['docs'][0]
			exp_data.append(
				{
					'title': "".join([j['text'] for j in i['title']]),
					'img': i['image'],
					'url': i['url']
				}
			)
	except Exception as e:
		logging.warning(f'Не удалось найти "{text}" | {e}')
	return exp_data


def save_img(url, num):
	try:
		img_data = requests.get(url).content
		path = url.split('/')[-2]
		with open(f'{path_}data/news_images/{path}.jpg', 'wb') as handler:
			handler.write(img_data)
	except Exception as e:
		print(e)


def get_news(url):
	all_news_data = []
	r = requests.get(url + '?issue_tld=ru&utm_referrer=dzen.ru', headers=config.HEADERS_TO_NEWS)
	html = BS(r.text, "html.parser")
	html = html.find_all(class_="mg-card")
	for i, block in enumerate(html):
		try:
			news_data = {
				'title': block.find(class_='mg-card__title').text,
				'url': block.find(class_='mg-card__link')['href']
			}
			img = block.find(class_='mg-card__media-block')
			if 'src' in str(img):
				news_data['img'] = img.find('img')['src']
			elif 'style' in str(img) and 'url' in str(img):
				news_data['img'] = str(img['style']).split('url')[1].replace('(', '').replace(')', '')
			elif 'neo-image' in str(img):
				news_data['img'] = img.find(class_='neo-image').find('img')['src']
			else:
				news_data['img'] = ''
			all_news_data.append(news_data)
			# if news_data['img']:
			# t = Thread(target=save_img, args=(news_data['img'], i))
			# t.start()
		except Exception as e:
			print(e)
	data[url] = all_news_data
	return [url, all_news_data]


def save_all_news():
	logging.info('start saving news')
	with open(f'{path_}data/news_data.json', encoding='utf-8') as json_file:
		data1 = json.load(json_file)

	tasks = []
	for text, url in config.NEWS_URLS.items():
		t1 = Thread(target=get_news, args=(url, ))
		tasks.append(t1)
	[i.start() for i in tasks]
	[i.join() for i in tasks]

	with open(f'{path_}data/news_data.json', 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=4)
	logging.info('download completed')
	return data


async def main():
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s %(levelname)s %(name)s %(message)s'
	)
	tr = Thread(target=save_all_news)
	tr.start()


if __name__ == '__main__':
	path_ = '../'
	asyncio.run(search('смерть'))
