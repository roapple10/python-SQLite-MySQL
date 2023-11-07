#台北市串接Youbike網址
#https://tcgbusfs.blob.core.windows.net/blobyoubike/YouBikeTP.json
'''
sno(站點代號)、sna(場站中文名稱)、tot(場站總停車格)、sbi(場站目前車輛數量)、sarea(場站區域)、mday(資料更新時間)、lat(緯度)、lng(經度)、ar(地點)、sareaen(場站區域英文)、snaen(場站名稱英文)、aren(地址英文)、bemp(空位數量)、act(全站禁用狀態)
'''
import requests
import psycopg2
from psycopg2 import Error


def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(host='dpg-cl3jvnhnovjs73bitii0-a.singapore-postgres.render.com',
                                     user='roberthsu',
                                     password='0IKBERnnSpOtM4SbqyVIWjtKIuqY4BSZ',
                                     database='testdb_ct3o',
                                     port="5432"
                                     )
    except Error as e:
        print(e)
    return connection

def create_table(conn):
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS youbike (
	id SERIAL,
	sno VARCHAR(6) NOT NULL,
	sna VARCHAR(50),
	tot SMALLINT ,
	sbi SMALLINT ,
	sarea VARCHAR(10) ,
	mday time,
	lat REAL,
	lng REAL,
	ar VARCHAR(100),
	bemp SMALLINT,
	act SMALLINT,
	PRIMARY KEY(id),
	UNIQUE (sno));
    '''

    with conn.cursor() as cursor:
        try:
            cursor.execute(create_table_sql)
        except Error as e:
            print(e)

from datetime import datetime
def update_data(downloadData):
    def change_datetime_format(d):
        datetime_object = datetime.strptime(d,'%Y%m%d%H%M%S')
        return datetime_object.strftime('%Y-%m-%d %H:%M:%S')

    conn = create_connection()
    with conn:
        create_table(conn)
        replace_into_sql = '''
        REPLACE INTO youbike(sno,sna,tot,sbi,sarea,mday,lat,lng,ar,bemp,act)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        '''
        with conn.cursor() as cursor:
            for item in downloadData:
                sno = item['sno']
                sna = item['sna']
                tot = int(item['tot'])
                sbi = int(item['sbi'])
                sarea = item['sarea']
                mday = change_datetime_format(item['mday'])
                lat = float(item['lat'])
                lng = float(item['lng'])
                ar = item['ar']
                bemp = int(item['bemp'])
                act = int(item['act'])
                cursor.execute(replace_into_sql,(sno,sna,tot,sbi,sarea,mday,lat,lng,ar,bemp,act))
            conn.commit()




def loadDataFraomYouBikeTP():
    response = requests.get('https://tcgbusfs.blob.core.windows.net/blobyoubike/YouBikeTP.json')
    response.encoding = 'utf-8'
    downloadData = response.json()
    downloadData = downloadData['retVal']
    # 取出value值，轉為list
    # youbikeData取得過濾解析完的資料,list內存dictionary
    youbikeData = list(downloadData.values())
    return youbikeData