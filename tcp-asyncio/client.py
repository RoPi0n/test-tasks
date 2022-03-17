import telnetlib

__CR__ = bytes([0xD])

with telnetlib.Telnet(host = 'localhost', port = 40000) as T:
    print('Обращаемся к нашему серверу по telnet, отправляем данные, которые вернут нам результат...')
    T.write('0002 C1 01:13:02.877 00'.encode('utf-8') + __CR__)
    print(T.read_all().decode('utf-8'))
    T.close()

with telnetlib.Telnet(host = 'localhost', port = 40000) as T:
    T.write('0007 D1 02:14:05.999 99'.encode('utf-8') + __CR__)
    print('Обращаемся к нашему серверу по telnet, отправляем данные, которые не вернут нам ничего кроме ok...')
    print(T.read_all().decode('utf-8'))
    T.close()

with telnetlib.Telnet(host = 'localhost', port = 40000) as T:
    print('Запрашиваем содержимое бд')
    T.write('showall'.encode('utf-8') + __CR__)
    print(T.read_all().decode('utf-8'))
    T.close()

    