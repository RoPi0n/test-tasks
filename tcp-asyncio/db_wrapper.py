import sqlite3
import os
import types


"""
  
   Как можно догадаться из названия файла - тут у нас обертка над sqlite3.
   По заданию мы должны писать данные в файл.
   sqlite тут подходит как самое надежное/простое решение, так и +- показательное, т.к. тут демонстрируются базовые sql запросы.

"""


class DataRecord:
	def __init__(self, bbbb: int, nn: str, time: str, gg: int) -> None:
		self.bbbb = bbbb
		self.nn   = nn
		self.time = time
		self.gg   = gg


class DataBaseWrapper:
	def __init__(self, db_name: str = 'data.db') -> None:
		self.db_name = os.path.join(os.path.dirname(__file__), db_name)
		self.first_launch_check()


	"""
		Инициализация бд, создание отсутствующих таблиц.
		Код должен делать это сам, отправить решение задачи с уже созданной бд в комплекте - жульничество.
	"""
	def first_launch_check(self) -> None:
		with sqlite3.connect(self.db_name) as conn:
			cur = conn.cursor()
			r = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DATA_TABLE';").fetchall()
			if len(r) == 0:
				cur.execute(
					"""
					CREATE TABLE DATA_TABLE(
						BBBB INTEGER NOT NULL, 
						NN   VARCHAR(2) NOT NULL, 
						TIME VARCHAR(12) NOT NULL,
						GG   INTEGER NOT NULL
					);
					"""
				)

				conn.commit()


	"""
		push_record:
		добавляем запись в бд
	"""
	def push_record(self, rec: DataRecord) -> None:
		with sqlite3.connect(self.db_name) as conn:
			cur = conn.cursor()

			cur.execute(
				"""
				INSERT INTO DATA_TABLE (BBBB,NN,TIME,GG) VALUES (?,?,?,?);
				""",
				(rec.bbbb, rec.nn, rec.time, rec.gg)
			)
			conn.commit()


	"""
		read_records:
		читаем все записи из бд
	"""
	def read_records(self) -> list[DataRecord]:
		with sqlite3.connect(self.db_name) as conn:
			cur = conn.cursor()

			return [
				DataRecord(rec[0], rec[1], rec[2], rec[3]) 
				for rec in cur.execute('SELECT BBBB,NN,TIME,GG FROM DATA_TABLE;').fetchall()
			]
				
