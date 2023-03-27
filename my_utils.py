import math
import pymysql
import cx_Oracle
import requests
from tqdm import tqdm
import pandas as pd
import time
import random

dsn = cx_Oracle.makedsn('localhost',1521,'xe')
seoul_api_key = '4378747841626c753937786d7a7a4e'
riot_api_key = ''

def db_open():
    global db
    global cursor
    db = cx_Oracle.connect(user = 'icia', password = '1234', dsn= dsn)
    cursor = db.cursor()
    print('oracle open!')


def oracle_execute(q):
    global db
    global cursor
    try:
        if 'select' in q:
            df = pd.read_sql(sql=q, con=db)
            return df
        cursor.execute(q)
        return 'oracle 쿼리 성공!'
    except Exception as e:
        print(e)


def oracle_close():
    global db
    global cursor
    try:
        db.commit()
        cursor.close()
        db.close()
        return '오라클 닫힘!'
    except Exception as e:
        print(e)


#mysql


def connect_mysql(db):
    conn = pymysql.connect(host = 'localhost', user='root',password='1234',db=db, charset='utf8')
    return conn


def mysql_execute(query, conn):
    cursor_mysql = conn.cursor()
    cursor_mysql.execute(query)
    result = cursor_mysql.fetchall()
    return result


def mysql_execute_dict(query, conn):
    cursor_mysql = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor_mysql.execute(query)
    result = cursor_mysql.fetchall()
    return result


def df_creater(url):
    url = url.replace('(인증키)',seoul_api_key).replace('xml','json').replace('/5/','/1000/')
    res = requests.get(url).json()
    key = list(res.keys())[0]
    data = res[key]['row']
    df = pd.DataFrame(data)
    return df


def get_puuid(user):
    url = f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}?api_key={riot_api_key}'
    res = requests.get(url).json()
    puuid = res['puuid']
    return puuid


def get_match_id(puuid, num):
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=100&api_key={riot_api_key}'
    id_list = requests.get(url).json()
    res = random.sample(id_list, num)
    return res


def get_match_id_master(puuid,num):
    start_list =[0,100,200,300,400,500]
    start = random.choice(start_list)
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start={start}&count=100&api_key={riot_api_key}'
    id_list = requests.get(url).json()
    res = random.sample(id_list, num)
    return res


def get_match_id_grandmaster(puuid,num):
    start_list = [0, 100, 200, 300, 400, 500]
    start = random.choice(start_list)
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start={start}&count=100&api_key={riot_api_key}'
    id_list = requests.get(url).json()
    res = random.sample(id_list, num)
    return res


def get_match_id_challenger(puuid,num):
    start_list = [0, 100, 200, 300, 400, 500]
    start = random.choice(start_list)
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start={start}&count=100&api_key={riot_api_key}'
    id_list = requests.get(url).json()
    res = random.sample(id_list, num)
    return res


def get_matches_timelines(match_id):
    url1 = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={riot_api_key}'
    res1 = requests.get(url1).json()
    url2 = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline?api_key={riot_api_key}'
    res2 = requests.get(url2).json()
    time.sleep(1.8)
    return res1,res2


# 티어별 원시 데이터 프레임 생성 함수
def get_rawdata(tier):
    lst = []
    summoner_lst = []
    key = riot_api_key
    page = random.randrange(1, 10)
    division_list = ['I', 'II', 'III', 'IV']
    url = ''

    if (
            tier == 'IRON' or tier == 'BRONZE' or tier == 'SILVER' or tier == 'GOLD' or tier == 'PLATINUM' or tier == 'DIAMOND'):
        for division in division_list:
            url = f'https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}?page={page}&api_key={key}'
            res = requests.get(url).json()
            lst += random.sample(res, 5)
    elif tier == 'MASTER':
        url = f'https://kr.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key={key}'
        res = requests.get(url).json()
        lst = random.sample(res['entries'], 10)
    elif tier == 'GRANDMASTER':
        url = f'https://kr.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key={key}'
        res = requests.get(url).json()
        lst = random.sample(res['entries'], 3)
    elif tier == 'CHALLENGER':
        url = f'https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={key}'
        res = requests.get(url).json()
        lst = random.sample(res['entries'], 1)
    else:
        print('티어를 잘못 입력하셨습니다')
        return

    summoner_lst = list(map(lambda x: x['summonerName'], lst))
    df_creates = []

    print('원시 데이터 생성중')
    for s in tqdm(summoner_lst):
        try:
            puuid = get_puuid(s)
            if (tier == 'IRON' or tier == 'BRONZE' or tier == 'SILVER' or tier == 'GOLD' or tier == 'PLATINUM' or tier == 'DIAMOND'):
                match_ids = get_match_id(puuid, 3)
            elif tier == 'MASTER':
                match_ids = get_match_id_master(puuid, 6)
            elif tier == 'GRANDMASTER':
                match_ids = get_match_id_grandmaster(puuid, 20)
            elif tier == 'CHALLENGER':
                match_ids = get_match_id_challenger(puuid, 60)
            for i in match_ids:
                matches, timeline = get_matches_timelines(i)
                df_creates.append([i, matches, timeline])
        except:
            continue

    df = pd.DataFrame(df_creates, columns=['match_id', 'matches', 'timeline'])
    return df


def get_match_timeline_df(raw_data):
    df_creater = []
    info = raw_data.iloc[0].matches['info']['participants']
    print('게임 데이터프레임 생성중...')
    for i in tqdm(range(len(raw_data))):
        try:
            for j in range(len(info)):
                lst = []
                tmp=[]
                a= int(raw_data.iloc[i].matches['info']['gameDuration']/60)
                if 15 <= a:  # 게임시간이 15분이상일때
                    lst.append(raw_data.iloc[i]['match_id'])
                    lst.append(raw_data.iloc[i].matches['info']['gameDuration'])
                    lst.append(raw_data.iloc[i].matches['info']['gameVersion'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['summonerName'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['summonerLevel'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['participantId'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['championName'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['champExperience'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['teamPosition'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['teamId'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['win'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['kills'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['deaths'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['assists'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['totalDamageDealtToChampions'])
                    lst.append(raw_data.iloc[i].matches['info']['participants'][j]['totalDamageTaken'])
                    for k in range(5,a+1):
                        if k<=25: #게임시간 25분까지만 데이터 삽입
                            lst.append(raw_data.iloc[i].timeline['info']['frames'][k]['participantFrames'][str(j+1)]['totalGold'])
                    df_creater.append(lst)
                else : continue

        except:continue

    df = pd.DataFrame(df_creater,columns =['gameId','gameDuration','gameVersion','summonerName','summonerLevel','participantId'
                                           ,'championName','champExperience','teamPosition','teamId','win','kills','deaths','assists'
                                           ,'totalDamageDealtToChampions','totalDamageTaken','g_5','g_6','g_7','g_8','g_9','g_10'
                                           ,'g_11','g_12','g_13','g_14','g_15','g_16','g_17','g_18','g_19','g_20','g_21','g_22'
                                           ,'g_23','g_24','g_25'])
    df = df.fillna(0) #NaN값을 0으로
    df=df.astype(dtype='int64',errors='ignore') #데이터 타입을 전부 int로 바꾸고 바꿀 수 없는 것들은 그대로
    df=df.astype({'win':'bool'})
    return df


# mysql 인서트 함수
def insert_my(x,conn):
    query = (
        f'insert into lol_datas (gameId, gameDuration, gameVersion, summonerName, summonerLevel,'
        f'participantId,championName,champExperience,teamPosition,teamId,win,kills,deaths,assists,'
        f'totalDamageDealtToChampions,totalDamageTaken,g_5,g_6,g_7,g_8,g_9,g_10,g_11,g_12,g_13,'
        f'g_14,g_15,g_16,g_17,g_18,g_19,g_20,g_21,g_22,g_23,g_24,g_25)'
        f'values({repr(x.gameId)},{x.gameDuration},{repr(x.gameVersion)},{repr(x.summonerName)},{x.summonerLevel},{x.participantId}'
        f',{repr(x.championName)},{x.champExperience},{repr(x.teamPosition)},{x.teamId},{repr(str(x.win))},{x.kills},{x.deaths},{x.assists},{x.totalDamageDealtToChampions},{x.totalDamageTaken}'
        f',{x.g_5},{x.g_6},{x.g_7},{x.g_8},{x.g_9},{x.g_10},{x.g_11},{x.g_12},{x.g_13},{x.g_14},{x.g_15},{x.g_16},{x.g_17},{x.g_18},{x.g_19},{x.g_20},{x.g_21},{x.g_22},{x.g_23},{x.g_24},{x.g_25})'
    )
    try:
        mysql_execute(query,conn)
    except Exception as e:
        print(e)
    return


# oracle 인서트 함수
def insert_o(x):
    query = (
        f'insert into lol_datas (gameId, gameDuration, gameVersion, summonerName, summonerLevel,'
        f'participantId,championName,champExperience,teamPosition,teamId,win,kills,deaths,assists,'
        f'totalDamageDealtToChampions,totalDamageTaken,g_5,g_6,g_7,g_8,g_9,g_10,g_11,g_12,g_13,'
        f'g_14,g_15,g_16,g_17,g_18,g_19,g_20,g_21,g_22,g_23,g_24,g_25)'
        f'values({repr(x.gameId)},{x.gameDuration},{repr(x.gameVersion)},{repr(x.summonerName)},{x.summonerLevel},{x.participantId}'
        f',{repr(x.championName)},{x.champExperience},{repr(x.teamPosition)},{x.teamId},{repr(str(x.win))},{x.kills},{x.deaths},{x.assists},{x.totalDamageDealtToChampions},{x.totalDamageTaken}'
        f',{x.g_5},{x.g_6},{x.g_7},{x.g_8},{x.g_9},{x.g_10},{x.g_11},{x.g_12},{x.g_13},{x.g_14},{x.g_15},{x.g_16},{x.g_17},{x.g_18},{x.g_19},{x.g_20},{x.g_21},{x.g_22},{x.g_23},{x.g_24},{x.g_25})'
    )
    try:
        oracle_execute(query)
    except Exception as e:
        print(e)
        pass
    return


# mysql 자동 삽입
def auto_insert_my(num):
    tier_lst = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND','MASTER','GRANDMASTER','CHALLENGER']
    for i in range(num):
        try:
            tier = random.choices(tier_lst,weights = [0.0209,0.1516, 0.3255, 0.3186, 0.1468, 0.03, 0.0005, 0.0004, 0.0002])[0]
            print('티어:',tier)
            df=get_rawdata(tier)
            tmp=get_match_timeline_df(df)
            conn = connect_mysql('icia')
            print('DB에 데이터 저장중...')
            tmp.progress_apply(lambda x: insert_my(x,conn),axis =1)
            print('인서트 완료')
            conn.commit()
            conn.close()
            print('커밋 완료')
            print('=====================================================')
        except Exception as e:
            print('인서트 실패: ',e)
            continue



# 오라클 자동 삽입
def auto_insert_o(num):
    tier_lst = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND','MASTER','GRANDMASTER','CHALLENGER']
    for i in range(num):
        try:
            tier = random.choices(tier_lst,weights = [0.0209,0.1516, 0.3255, 0.3186, 0.1468, 0.03, 0.0005, 0.0004, 0.0002])[0]
            print('티어:',tier)
            df=get_rawdata(tier)
            tmp=get_match_timeline_df(df)
            db_open()
            print('DB에 데이터 저장중...')
            tmp.progress_apply(lambda x: insert_o(x),axis =1)
            print('인서트 완료')
            oracle_close()
            print('커밋 완료')
            print('=====================================================')
        except Exception as e:
            print('인서트 실패: ',e)
            continue



# mysql 인서트 중복업데이트
def insert_matches_timeline_mysql(row,conn):
    # lambda를 이용해서 progress_apply를 통해 insert할 구문 만들기
    query = (
             f'insert into lol_datas(gameId, gameDuration, gameVersion, summonerName, summonerLevel, participantId,'
             f'championName, champExperience, teamPosition, teamId, win, kills, deaths, assists,'
             f'totalDamageDealtToChampions, totalDamageTaken, g_5, g_6, g_7, g_8, g_9, g_10, g_11, g_12 ,g_13,g_14,'
             f'g_15, g_16, g_17, g_18, g_19, g_20, g_21, g_22, g_23, g_24, g_25)'
             f'values(\'{row.gameId}\',{row.gameDuration}, \'{row.gameVersion}\', \'{row.summonerName}\','
             f'{row.summonerLevel}, {row.participantId},\'{row.championName}\',{row.champExperience},'
             f'\'{row.teamPosition}\', {row.teamId}, \'{row.win}\', {row. kills}, {row.deaths}, {row.assists},'
             f'{row.totalDamageDealtToChampions},{row.totalDamageTaken},{row.g_5},{row.g_6},{row.g_7},{row.g_8},'
             f'{row.g_9},{row.g_10},{row.g_11},{row.g_12},{row.g_13},{row.g_14},{row.g_15},{row.g_16},{row.g_17},'
             f'{row.g_18},{row.g_19},{row.g_20},{row.g_21},{row.g_22},{row.g_23},{row.g_24},{row.g_25})'
             f'ON DUPLICATE KEY UPDATE '
             f'gameId = \'{row.gameId}\', gameDuration = {row.gameDuration}, gameVersion = \'{row.gameVersion}\', summonerName= \'{row.summonerName}\','
             f'summonerLevel = {row.summonerLevel},participantId = {row.participantId},championName = \'{row.championName}\','
             f'champExperience = {row.champExperience}, teamPosition = \'{row.teamPosition}\', teamId = {row.teamId},win = \'{row.win}\','
             f'kills = {row. kills}, deaths = {row.deaths}, assists = {row.assists}, totalDamageDealtToChampions = {row.totalDamageDealtToChampions},'
             f'totalDamageTaken = {row.totalDamageTaken},g_5 = {row.g_5},g_6 = {row.g_6},g_7 = {row.g_7},g_8 = {row.g_8},g_9 = {row.g_9},'
             f'g_10 = {row.g_10},g_11 = {row.g_11},g_12 = {row.g_12},g_13 = {row.g_13},g_14 = {row.g_14},g_15 = {row.g_15},g_16 = {row.g_16},g_17 = {row.g_17},'
             f'g_18 = {row.g_18},g_19 = {row.g_19},g_20 = {row.g_20},g_21 = {row.g_21},g_22 = {row.g_22},g_23 = {row.g_23},g_24 = {row.g_24},g_25 = {row.g_25}'
            )
    mysql_execute(query,conn)
    return query


# 오라클 인서트 중복업데이트
def insert_matches_timeline_oracle(row):
    #데이터프레임에서 apply 한줄씩 넣는다는 전제에서 중복값을 업데이트
    query = (
             f'MERGE INTO lol_datas USING DUAL ON(gameId=\'{row.gameId}\' and participantId={row.participantId}) '
             f'WHEN NOT MATCHED THEN '
             f'insert (gameId, gameDuration, gameVersion, summonerName, summonerLevel, participantId,'
             f'championName, champExperience, teamPosition, teamId, win, kills, deaths, assists,'
             f'totalDamageDealtToChampions, totalDamageTaken, g_5, g_6, g_7, g_8, g_9, g_10, g_11, g_12 ,g_13,g_14,'
             f'g_15, g_16, g_17, g_18, g_19, g_20, g_21, g_22, g_23, g_24, g_25)'
             f'values(\'{row.gameId}\',{row.gameDuration}, \'{row.gameVersion}\', \'{row.summonerName}\','
             f'{row.summonerLevel}, {row.participantId},\'{row.championName}\',{row.champExperience},'
             f'\'{row.teamPosition}\', {row.teamId}, \'{row.win}\', {row. kills}, {row.deaths}, {row.assists},'
             f'{row.totalDamageDealtToChampions},{row.totalDamageTaken},{row.g_5},{row.g_6},{row.g_7},{row.g_8},'
             f'{row.g_9},{row.g_10},{row.g_11},{row.g_12},{row.g_13},{row.g_14},{row.g_15},{row.g_16},{row.g_17},'
             f'{row.g_18},{row.g_19},{row.g_20},{row.g_21},{row.g_22},{row.g_23},{row.g_24},{row.g_25})'
            )
    oracle_execute(query)
    return query


def assi_calc(x):
    try:
        return ','.join(list(map(lambda y : str(y),x['assistingParticipantIds'])))
    except:
        return ''


def get_kill_log_df(raw_data):
    all_lst = []
    for i, game in enumerate(raw_data['matches']):
        game_id = raw_data.iloc[i]['match_id']
        game_duration = game['info']['gameDuration']
        game_version = game['info']['gameVersion']

        bans = '|'.join(str(ban['championId']) for team in game['info']['teams'] for ban in team['bans'])

        k_log, v_log, a_log = [], [], []
        for frame in raw_data.iloc[i]['timeline']['info']['frames']:
            for event in frame['events']:
                try:
                    event_type = event['type']
                    if event_type == 'CHAMPION_KILL':
                        k_log.append(str(event['killerId']))
                        v_log.append(str(event['victimId']))
                        a_log.append(assi_calc(event))
                except KeyError:
                    continue

        k_log, v_log, a_log = '|'.join(k_log), '|'.join(v_log), '|'.join(a_log)
        all_lst.append([game_id, game_duration, game_version, bans, k_log, v_log, a_log])

    df = pd.DataFrame(all_lst,columns=['gameId','gameDuration','gameVersion','ban','killerId','victimId','assistId'])
    return df