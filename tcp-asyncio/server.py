import asyncio
from   asyncio.streams import StreamReader, StreamWriter
import sys, os, platform, logging
import re, datetime
from   db_wrapper import DataRecord, DataBaseWrapper


"""
	Настраиваем и создаем экземпляр логгера.
	Не думаю что в текущем проекте он сильно полезен, но в более крупных это позволяет обнаружить причину падения
	спустя время, а не в те секунды когда оно падает.
"""
logging.basicConfig(
    level=logging.ERROR, 
    format='%(levelname)s - %(message)s',
    handlers=[
		logging.FileHandler(filename=os.path.join(os.path.dirname(__file__), 'server_log.log')),
		logging.StreamHandler(sys.stdout)
	]
)

logger = logging.getLogger('Srv_Logger')


"""
	Определяем символ [CR] из задания. Взял 0xD, потому что в задании четко значение не прописано и я захотел 0xD...
"""
__CR__ = bytes([0xD])


"""
	Экземпляр wrapper'a
"""
data_base = DataBaseWrapper(db_name = 'data.db')		


"""
	Выбрал реализацию asyncio -> handler(reader, writer), т.к. она показалась мне удобной из-за наличия readuntil() у StreamReader'a
"""
async def handle_connection(reader: StreamReader, writer: StreamWriter) -> None:
	try:
		req = (await reader.readuntil(separator = __CR__))[:-1].decode('utf-8', 'ignore')

		# Проводим валидацию того что к нам пришло извне. Иногда это делать полезно :)
		if re.match(r'[0-9]{4}.[A-Z0-9]{2}.[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{3}.[0-9]{2}', req):
			dt = DataRecord(int(req[:4]), req[5:7], req[8:20], int(req[21:]))
			data_base.push_record(dt)

			time = datetime.datetime.strptime(dt.time, '%H:%M:%S.%f')
			resp = f'Спортсмен с нагрудным номером %04d прошёл отсечку %s за «%s»!'%(dt.bbbb, dt.nn, time.strftime('%H:%M:%S.%f')[:-5])
			
			print(resp)
			
			if dt.gg == 00:
				writer.write(resp.encode('utf-8'))
				await writer.drain()
			else:
				writer.write('Ok!'.encode('utf-8'))
				await writer.drain()

		# showall - выводит все содержимое бд. В задании это не прописано, но функционал не лишний.
		elif req.lower() == 'showall':
			for r in data_base.read_records():
				time = datetime.datetime.strptime(r.time, '%H:%M:%S.%f')
				resp = f'Спортсмен с нагрудным номером %04d прошёл отсечку %s за «%s»!'%(r.bbbb, r.nn, time.strftime('%H:%M:%S.%f')[:-3])
				writer.write((resp + '\n').encode('utf-8'))
			await writer.drain()

		# на случай если пришло что то совсем не то
		else:
			writer.write('Invalid request!'.encode('utf-8'))
			print('"', req, '"')
			await writer.drain()
		
	except:
		logger.exception('At handle_connection')

	finally:
		if not writer.is_closing():
			writer.close()
			await writer.wait_closed()


"""
	Стандартная запускалка asyncio сервера.
"""
async def run_server(port: int) -> None:
	server = await asyncio.start_server(handle_connection, '0.0.0.0', port)
	async with server:
		await server.serve_forever()


if __name__ == '__main__':
	if platform.system() == 'Windows':
		"""
			В некоторых случаях asyncio может некорректно работать на Windows Server, если не выставить этот селектор на главный цикл
			На unix системах это лишнее.
		"""
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	
	asyncio.run(run_server(port = 40000))