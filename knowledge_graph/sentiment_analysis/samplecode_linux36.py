# -*- coding: utf-8 -*-
from dataapi_linux36 import Client
if __name__ == "__main__":
    try:
        client = Client()
        client.init(
            '6b43638d6764d9eba9fe803d5c46e9be126be3b192a6cb3fcd75074bd96d221c')
        url1 = '/api/equity/getEqu.json?field=&listStatusCD=&secID=&ticker=&equTypeCD=A'
        code, result = client.getData(url1)
        if code == 200:
            print(result.decode('utf-8'))
        else:
            print(code)
            print(result)
        url2 = '/api/equity/getSecST.csv?field=&secID=&ticker=000521&beginDate=20020101&endDate=20150828'
        code, result = client.getData(url2)
        if (code == 200):
            file_object = open('thefile.csv', 'w')
            file_object.write(result.decode('GBK'))
            file_object.close()
        else:
            print(code)
            print(result)
    except Exception as e:
        #traceback.print_exc()
        raise e
