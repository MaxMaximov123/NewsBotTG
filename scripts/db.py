import psycopg2
import asyncio
from decouple import config


class BotDB:
	def __init__(self):
		self.conn = psycopg2.connect(
			user=config('DB_USER'),
			password=config('DB_PASSWORD'),
			host=config('DB_HOST'),
			port=config('DB_PORT'),
			database=config('DB_DATABASE'))

		self.cursor = self.conn.cursor()

		query = '''SELECT EXISTS (SELECT relname FROM pg_class WHERE relname = 'trackers');'''
		resp = self.cursor.execute(query)
		rows = self.cursor.fetchone()
		if not rows[0]:
			self.create_table()

	def create_table(self):
		try:
			create_table_query1 = '''CREATE TABLE trackers(
USER_ID	BIGINT,
STATUS	TEXT,
ZNAK	TEXT,
NAME	TEXT,
USERNAME	TEXT,
TOPIC	TEXT,
ARTICLE	INT,
MODES	TEXT,
BIRTHDAY	TEXT,
CURR	TEXT,
STOCKS	TEXT);'''
			self.cursor.execute(create_table_query1)
			self.conn.commit()
			print('БД успешно создана')
		except (Exception, psycopg2.Error) as error:
			print("Ошибка при работе с PostgreSQL", error)

	async def user_exists(self, user_id):
		self.cursor.execute("SELECT * FROM trackers WHERE user_id = %s", (user_id,))
		return bool(len(self.cursor.fetchall()))

	async def add_user(self, user_id, status, name, username, znak, modes, curr, stocks):
		self.cursor.execute(
			"""INSERT INTO trackers (user_id, name, status, username, znak, modes, curr, stocks) VALUES
			(%s, %s, %s, %s, %s, %s, %s, %s)""", (user_id, name, status, username, znak, modes, curr, stocks))
		return self.conn.commit()

	async def update_status(self, user_id, new_status):
		self.cursor.execute("UPDATE trackers SET status = %s WHERE user_id = %s", (new_status, user_id))
		return self.conn.commit()

	async def update_znak(self, user_id, new_znak):
		self.cursor.execute("UPDATE trackers SET znak = %s WHERE user_id = %s", (new_znak, user_id))
		return self.conn.commit()

	async def get_status(self, user_id):
		self.cursor.execute("SELECT status FROM trackers WHERE user_id = %s", (user_id,))
		return self.cursor.fetchone()[0]

	async def get_curr(self, user_id):
		self.cursor.execute("SELECT curr FROM trackers WHERE user_id = %s", (user_id,))
		return self.cursor.fetchone()[0]

	async def update_curr(self, user_id, new_curr):
		self.cursor.execute("UPDATE trackers SET curr = %s WHERE user_id = %s", (new_curr, user_id))
		return self.conn.commit()

	async def get_id(self):
		self.cursor.execute("SELECT user_id FROM trackers")
		return self.cursor.fetchall()

	async def get_znak(self, user_id):
		self.cursor.execute("SELECT znak FROM trackers WHERE user_id = %s", (user_id,))
		return self.cursor.fetchone()[0]

	async def update_topic(self, user_id, topic):
		self.cursor.execute("UPDATE trackers SET topic = %s WHERE user_id = %s", (topic, user_id))
		return self.conn.commit()

	async def update_article(self, user_id, article):
		self.cursor.execute("UPDATE trackers SET article = %s WHERE user_id = %s", (article, user_id))
		return self.conn.commit()

	async def get_article(self, user_id):
		self.cursor.execute("SELECT article FROM trackers WHERE user_id = %s", (user_id,))
		return self.cursor.fetchone()[0]

	async def get_topic(self, user_id):
		self.cursor.execute("SELECT topic FROM trackers WHERE user_id = %s", (user_id,))
		return self.cursor.fetchone()[0]

	async def update_modes(self, user_id, modes):
		self.cursor.execute("UPDATE trackers SET modes = %s WHERE user_id = %s", (modes, user_id))
		return self.conn.commit()

	async def get_modes(self, user_id):
		self.cursor.execute("SELECT modes FROM trackers WHERE user_id = %s", (user_id,))
		return self.cursor.fetchone()[0]

	async def add_birth(self, user_id, data):
		data = '.'.join(list(map(str, list(map(int, data.split('.'))))))
		self.cursor.execute("UPDATE trackers SET birthday = %s WHERE user_id = %s", (data, user_id))
		return self.conn.commit()

	async def get_birth(self, user_id):
		self.cursor.execute("SELECT birthday FROM trackers WHERE user_id = %s", (user_id,))
		return self.cursor.fetchone()[0]

	async def update_stocks(self, user_id, stocks):
		self.cursor.execute("UPDATE trackers SET stocks = %s WHERE user_id = %s", (stocks, user_id))
		return self.conn.commit()

	async def get_stocks(self, user_id):
		self.cursor.execute("SELECT stocks FROM trackers WHERE user_id = %s", (user_id,))
		return self.cursor.fetchone()[0]


if __name__ == '__main__':
	print(BotDB().get_id())
