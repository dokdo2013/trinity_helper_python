# ====================================== #
#            CUK.HAENU.COM               #
#  Developer : HAENU & CY7               #
#  Date : 2020.08.13.                    #
# ====================================== #
# ====================================== #
#           (1) 파이썬 기본 세팅         #
# ====================================== #
from bs4 import BeautifulSoup
import time
import requests
import uuid
import json
import timeit
import pymysql
from sqlalchemy import create_engine
import pandas as pd

# ====================================== #
#          (2) 기본 사용자 세팅          #
# ====================================== #
userId = 'trinity_id' # 사용자 입력
userPw = 'trinity_pw' # 사용자 입력
err = 0
server_name = 'server1';
limit_max_time = 15
limit_min_time = 5

# ====================================== #
#        (3) 트리니티 데이터 파싱        #
# ====================================== #
class catlog():
    def __init__(self):
        self.session = ''
        self.req_login = ''

    def login(self):
        sessid_1 = str(uuid.uuid4())
        sessid_2 = str(uuid.uuid4())

        sessid = sessid_1.replace('-', '') + sessid_2.replace('-', '')

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'}
        cookies = {'SESSION_SSO': sessid + '.c3R3X2RvbWFpbi9zc29fMg=='}

        re = requests.get('https://uportal.catholic.ac.kr/sso/jsp/sso/ip/login_form.jsp', headers=headers,
                          cookies=cookies)

        html = re.text
        soup = BeautifulSoup(html, 'lxml')
        samlRequest = soup.find('input', {'name': 'samlRequest'}).get('value')

        data1 = {'userId': 'dokdo2013', 'password': 'whgusdn00!', 'samlRequest': samlRequest}

        req = requests.post('https://uportal.catholic.ac.kr/sso/processAuthnResponse.do', headers=headers,
                            cookies=cookies, data=data1)

        html = req.text
        soup = BeautifulSoup(html, 'lxml')
        SAMLResponse = soup.find('input', {'name': 'SAMLResponse'}).get('value')

        data2 = {'SAMLResponse': SAMLResponse}

        self.session = requests.session()
        self.req_login = self.session.post('https://uportal.catholic.ac.kr/portal/login/login.ajax', headers=headers,
                                           data=data2)

    def find(self, id, no, json_data):
        try:
            for i in range(len(json_data["DS_CURR_OPSB010"])):
                if json_data["DS_CURR_OPSB010"][i]["sbjtNo"] == id and json_data["DS_CURR_OPSB010"][i]['clssNo'] == no:
                    cnt = json_data["DS_CURR_OPSB010"][i]['tlsnAplyRcnt']  # 신청인원
                    cnt2 = json_data["DS_CURR_OPSB010"][i]['tlsnLmtRcnt']  # 제한인원
                    cnt3 = json_data["DS_CURR_OPSB010"][i]['sbjtKorNm']  # 과목명

            return cnt, cnt2, cnt3
        except:
            return 'Error', 'Error', 'Error'

    def get_json(self):
        html = self.req_login.text
        soup = BeautifulSoup(html, 'lxml')
        csrf = soup.find('meta', {'id': '_csrf'}).get('content')

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'X-CSRF-TOKEN': csrf,
                   'Referer': 'https://uportal.catholic.ac.kr/stw/scsr/scoo/scooOpsbOpenSubjectInq.do'
                   }

        data = {'quatFg': 'INQ', 'posiFg': '10', 'openYyyy': '2020', 'openShtm': '20', 'campFg': 'M', 'sustCd': '%',
                'corsCd': '|', 'danFg': '', 'pobtFgCd': '%'}

        cookies = {'UCUPS_PT_SESSION': self.session.cookies.get_dict()['UCUPS_PT_SESSION']}

        return requests.post('https://uportal.catholic.ac.kr/stw/scsr/scoo/findOpsbOpenSubjectInq.json',
                             headers=headers, cookies=cookies, data=data).json()

    def hak(self):
        html = self.req_login.text
        soup = BeautifulSoup(html, 'lxml')
        csrf = soup.find('meta', {'id': '_csrf'}).get('content')

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'X-CSRF-TOKEN': csrf,
                   'Referer': 'https://uportal.catholic.ac.kr/portal/main.do',
                   'Content-Type': 'application/json'
                   }

        cookies = {'UCUPS_PT_SESSION': self.session.cookies.get_dict()['UCUPS_PT_SESSION']}

        data = {"sysDate": "2020.03.24(화)", "toDay": "20200324", "weekDay": 2, "yyyy": "2020", "MM": "03", "dd": "24"}

        return requests.post('https://uportal.catholic.ac.kr/portal/portlet/P018/listData.ajax',
                             headers=headers, cookies=cookies, data=json.dumps(data)).json()


# ====================================== #
#            (4) 여러 함수 세팅           #
# ====================================== #

def insert_time(name, time):
    global cursor, db
    q = "UPDATE cuk_server SET running_time = '" + str(time) + "' WHERE server_name = '" + str(name) + "'"
    cursor.execute(q)
    db.commit()

def send_message(phone, message):
    url = "https://api-sms.cloud.toast.com/sms/v2.3/appKeys/{API_KEY}/sender/sms" # API KEY 넣기
    data = {
        "body": message,
        "sendNo": '01012345678', # 폰 번호 입력
        "recipientList": [{
            "recipientNo": phone
        }]
    }
    headers = {'content-type': 'application/json' }
    res = requests.post(url, headers=headers, data=json.dumps(data))
    print(phone, message)

def finish_time():
    global start
    end = timeit.default_timer()
    total_time = '응답시간 : ' + str(end - start)[:6] + '초'
    print(total_time)
    res = str(end - start)[:6]
    return res

# ====================================== #
#                                        #
#               MAIN CODE                #
#                                        #
# ====================================== #
while True:
    try:
        start = timeit.default_timer()
        db = pymysql.connect(host='hostname', port=3306, user='dbuser', passwd='password', db='dbname', charset='utf8')
        cursor = db.cursor()
        catApi = catlog()
        catApi.login()
        pymysql.install_as_MySQLdb()
        engine = create_engine("mysql://dbuser:password@hostname:3306/dbname", encoding='utf-8', pool_size=20,
                               max_overflow=30)
        conn = engine.connect()
        df = pd.read_sql_table('cuk', conn)
        is_one = df['stat'] == 1
        df = df[is_one]
        subjList = df.iloc[:, 1:3]
        subjList = subjList.drop_duplicates()
        jsonData = catApi.get_json()
        for j in subjList.index:
            subj = subjList.loc[j, 'subj']
            no = subjList.loc[j, 'class']
            # print(subj, no)
            now, limit, className = catApi.find(subj, no, jsonData)
            if limit is None or limit == 'Error':
                pass
            else:
                available = int(limit) - int(now)
                if available > 0:
                    isAvailsubj = df['subj'] == subj
                    isAvailclass = df['class'] == no

                    phoneList = df[isAvailsubj & isAvailclass]
                    for phone in phoneList['phone']:
                        msg_temp = "[" + str(className) + "(" + str(no) + ")] 제한인원 : " + str(limit) + " / 현재인원 : " + str(now)
                        send_message(phone, msg_temp)

        time_set = finish_time()
        insert_time(server_name, time_set)
        db.close()
        if float(time_set) < limit_max_time and float(time_set) > limit_min_time:
            print('Delay', str(limit_max_time - float(time_set)), 'seconds')
            time.sleep(limit_max_time - float(time_set))
        elif float(time_set) < limit_min_time:
            print('Delay', str(limit_max_time - float(time_set)), 'seconds')
            time.sleep(limit_max_time - float(time_set))
    except:
        print("====ERROR OCCURED====")
        time.sleep(5)
