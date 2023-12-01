import pandas as pd
import requests

def SaveStock(message, data):
    try:
        data[str(message.chat.id)].append(message.text)
    except:
        data[str(message.chat.id)] = [message.text]
    df = pd.DataFrame(data)
    df.to_excel('/Users/khetag/Desktop/users_data.xlsx')
    

def GetStockInfo(message):
    APIs = ['4JN9ZD24ZTMKWX5R', 'BHM7WHDX7K66ET61', '8OKWRXIXB7VBMGAP', 'ZG7VF29SB1BSCTVF', 'D9SOYTBRK9ULOSNP']
    currency = message.text.strip()
    curr_api_id = 0
    try:
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}&to_currency=USD&apikey={APIs[curr_api_id]}'
        res = requests.get(url)
        data = res.json()
        try:
            test = data['Information']
            curr_api_id += 1
            url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}&to_currency=USD&apikey={APIs[curr_api_id]}'
            res = requests.get(url)
            data = res.json()
        except:
            pass
        curr_output = data["Realtime Currency Exchange Rate"]["4. To_Currency Name"]
        rate_output = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        return curr_output, rate_output
    except:
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={currency}&apikey={APIs[curr_api_id]}'
            res = requests.get(url)
            data = res.json()
            try:
                test = data['Information']
                curr_api_id += 1
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={currency}&apikey={APIs[curr_api_id]}'
                res = requests.get(url)
                data = res.json()
            except:
                pass
            curr_output = data["Global Quote"]["01. symbol"]
            rate_output = data["Global Quote"]["05. price"]
            return curr_output, rate_output
        except:
            return -1, -1
        