import Server
import assistant
import argparse
import logging
import platform
import asyncio
import websockets


parser = argparse.ArgumentParser(description='Аргументи хоста і порта для сервера')
parser.add_argument('--host',type=str,help='Назва Хоста.')
parser.add_argument('--port','-p',type=int,help='Номер Порта.')
parser.add_argument('--bot_name','-bn', type=str,help="Ім'я бота у чаті")
parser.add_argument('--bot_pass','-bp', type=str, help="Аутентифікатор для підключення")
parser.add_argument('--currency_usd','-usd', type=bool,help='Активує обробку USD (Доллар)')
parser.add_argument('--currency_eur','-eur', type=bool,help='Активує обробку EUR (Євро)')
parser.add_argument('--currency_pln','-pln', type=bool,help='Активує обробку PLN (Злотий)')
parser.add_argument('--currency_gbp','-gbp', type=bool,help='Активує обробку GBP (Фунт)')
args = parser.parse_args()
HOST = args.host if args.host != None else 'localhost'
PORT = args.port if args.port != None else 8080
BOT_NAME = args.bot_name if args.bot_name != None else 'Bot-Assistant'
AUTH = args.bot_pass if args.bot_pass != None else 'ASIS1234567890'
USD = 'USD' if args.currency_usd != None else None
EUR = 'EUR' if args.currency_eur != None else None
PLN = 'PLN' if args.currency_pln != None else None
GBP = 'GBP' if args.currency_gbp != None else None
CURRENCY = []
for currency in [USD,EUR,PLN,GBP]:
    if currency != None:
        CURRENCY.append(currency)
        print(CURRENCY)


async def main(host=HOST,port=PORT):
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        server = Server.Server()
        
    async with websockets.serve(server.ws_handler,host,port) as serv:
        print('Server started successfully')
        asyncio.create_task(server.connect_bot())       
        await asyncio.Future()
        

if __name__ == '__main__':
    asyncio.run(main(HOST,PORT))