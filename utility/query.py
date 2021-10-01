import sqlite3
from utility.setting import db_stg, db_tick


class Query:
    def __init__(self, windowQ, queryQ):
        self.windowQ = windowQ
        self.queryQ = queryQ
        self.con1 = sqlite3.connect(db_stg)
        self.cur1 = self.con1.cursor()
        self.con2 = sqlite3.connect(db_tick)
        self.Start()

    def __del__(self):
        self.con1.close()
        self.con2.close()

    def Start(self):
        while True:
            query = self.queryQ.get()
            if query[0] == 1:
                if len(query) == 2:
                    try:
                        self.cur1.execute(query[1])
                    except Exception as e:
                        self.windowQ.put([1, f'시스템 명령 오류 알림 - 입력값이 잘못되었습니다. {e}'])
                    else:
                        self.con1.commit()
                elif len(query) == 4:
                    try:
                        query[1].to_sql(query[2], self.con1, if_exists=query[3], chunksize=1000)
                    except Exception as e:
                        self.windowQ.put([1, f'시스템 명령 오류 알림 - {e}'])
            elif query[0] == 2:
                if len(query) == 2:
                    count = len(query[1])
                    for i, code in enumerate(list(query[1].keys())):
                        query[1][code].to_sql(code, self.con2, if_exists='append', chunksize=1000)
                        text = f'시스템 명령 실행 알림 - 틱데이터 저장 중 ... [{i+1}/{count}]'
                        self.windowQ.put([1, text])
                elif len(query) == 4:
                    try:
                        query[1].to_sql(query[2], self.con2, if_exists=query[3], chunksize=1000)
                    except Exception as e:
                        self.windowQ.put([1, f'시스템 명령 오류 알림 - {e}'])
