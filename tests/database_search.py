import sqlite3

def view_database(db_path):
    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 목록 조회
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])
    
    # 각 테이블의 데이터 조회
    for table in tables:
        print(f"\nData from {table[0]} table:")
        cursor.execute(f"SELECT * FROM {table[0]};")
        rows = cursor.fetchall()
        
        # 컬럼 이름 조회
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = [col[1] for col in cursor.fetchall()]
        print(columns)
        
        for row in rows:
            print(row)
    
    # 데이터베이스 연결 종료
    conn.close()

# 데이터베이스 파일 경로
db_path = 'app/food_database.db'

# 데이터베이스 조회 함수 호출
view_database(db_path)
