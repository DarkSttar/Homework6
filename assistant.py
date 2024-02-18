
import aiohttp
from datetime import datetime , timedelta
import websockets
import json
import logging
from aiofile import async_open
from main import CURRENCY,BOT_NAME,AUTH,HOST,PORT


logging.basicConfig(filename='log.txt',level=logging.INFO)



async def connect_to_server():
    uri = f'ws://{HOST}:{PORT}'   
    headers = {
        "Client-name":BOT_NAME,
        "AUTH": AUTH
    }
    async with websockets.connect(uri,extra_headers=headers) as ws:
        async for message in ws:
            client_request = json.loads(message) # Повідомлення від клієнта
            target_name = client_request['Name'] # ім'я клієнта
            arguments = client_request['Message'].split(' ') # Список переданних слів в повідомленні клієнта
            if arguments[0] in COMMAND: # якщо перше слово в списку комманд 
                result = await COMMAND[arguments[0]](arguments[1:]) # запуститься відовідна функція і поверне результат в  result
                
                # result список повідомлень для відправки клієнту який генерується в тілі команди 
                response_to_clinet = {
                        #Повідомлення для відправки серверу 
                        #Сервер відправить повідомлення клієнту з іменем яке в Target-Client
                        "Target-Client": target_name,
                        "Message": None
                        }
                for message in result: # Почерзі відправляє повідомлення із списку result
                    response_to_clinet['Message'] = message 
                    await ws.send(json.dumps(response_to_clinet))
                    

             
                
async def get_course(args,*kwargs):
    logging.info(f"{datetime.strftime(datetime.now(), '%d-%m-%Y:%H-%M-%S')}: Start Exchange")
    current_date = datetime.now().date() 
    answer = ['Exchange Complete!'] 
    days_ago = int()
    dates = list()
    currency = list()
    if len(args) >= 1:
        for arg in args:
            #Перевірка чи були передані числові данні якщо так запише їх в days_ago
            if arg.isdigit() and days_ago == 0: 
                days_ago = int(arg)
            else:
            #Перевірка чи були переданні валюти якщо такі є всписку бота запише їх в змінну currency
                if arg.upper() in CURRENCY:
                    currency.append(arg.upper())
                    
    if days_ago > 0 and days_ago <= 10:
        [dates.append(datetime.strftime(current_date - timedelta(days=days),"%d.%m.%Y")) for days in range(0,days_ago)]
    else:
        #Перевірка на макс задане число
        answer.append('Max Day:10!')
        answer.append('Please try Again.')
        return answer
    if currency == []:
        answer.append('bot does not handle any currency')
        return answer

        #В Exchange.json бот записує данні які получає при коннекті до API приватбанка
        #Якщо данні вже є він витягне їх з файла якщо ні буде коннектитись до API і збирати їх потім запише у файл
    logging.info(f"Exchange ARGS: [Days ago:{days_ago}, Dates:{dates}, Currency:{currency}]")
    async with async_open ('Exchange.json', 'r') as file:  # читає Exchange.json
        content = await file.read()
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = dict()
    #Словник з данними має наступну структуру {Key Дата(17.02.2024):Value List[{Валюта1},{Валюта2},{Валюта3},{Валюта4},]}
    for curr in currency: # Цикл Валют Приклад:['USD''EUR']
        answer.append(f'UAN TO {curr}') 
        for date in dates: # цикл Дат за які бот має видати результат
            if date in data: # Перевірка чи є ключ з такою датою
                for extract_data in data[date]: # Якщо ключ є запускається цикл який пройдеться по всіх валютах записаних в списку ключом до якого є дата
                    is_curr_in_ex_data = False # якщо данні для шуканої валюти були знайденні змінить значення на True
                    if curr == extract_data['currency']:  
                        
                        
                        answer.append(f"Date:{date}    Currency:{str(extract_data['baseCurrency'])}/{str(extract_data['currency'])}\
    Sell:{str(extract_data['saleRate'])}   Buy:{str(extract_data['purchaseRate'])}")        
                        is_curr_in_ex_data = True
                        break 
                if is_curr_in_ex_data == False:
                    answer,data = await connect_private(date=date,currency=currency,data=data,answer=answer,curr=curr)
            else:
                answer,data = await connect_private(date=date,currency=currency,data=data,answer=answer,curr=curr)
                 
    async with async_open('Exchange.json', 'w') as write_file:
        await write_file.write(json.dumps(data, indent=2))
    [logging.info(f'Result: {r}') for r in answer]
    logging.info(f'{datetime.strftime(datetime.now(), "%d-%m-%Y:%H-%M-%S")} Finish Exchange')
    return answer                                  




async def connect_private(currency,date,data,answer,curr):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}') as respone:
            print(f'Connect to PrivateBank API... {date}')
            result = await respone.json()
            ex_data = []
            for xdata in result['exchangeRate']:
                if xdata['currency'] in currency:
                   ex_data.append(xdata)
                   if len(ex_data) > len(currency):
                       break
        if ex_data != []:
            if date not in data:
                data.update({date:[]})
        
            [data[date].append(new_data) for new_data in ex_data]
            [answer.append(f"Date:{date}    Currency:{str(n_data['baseCurrency'])}/{str(n_data['currency'])}\
    Sell:{str(n_data['saleRate'])}   Buy:{str(n_data['purchaseRate'])}") if n_data['currency'] == curr else None  for n_data in ex_data] 
        else:
            [answer.append(f'Date:{date} Missing Data')]
    return answer,data

COMMAND = {
            'exchange': get_course,
            'help': help,
            'hello':'hello',
           }



    
                


   

