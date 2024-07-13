import sqlite3

def update_conversion_unit(db_path, food, old_unit, new_unit):
    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 데이터 업데이트
    cursor.execute("""
        UPDATE unit_conversion
        SET unit = ?
        WHERE food = ? AND unit = ?
    """, (new_unit, food, old_unit))
    
    # 변경사항 커밋
    conn.commit()
    
    # 업데이트 결과 확인
    cursor.execute("SELECT * FROM unit_conversion WHERE food = ? AND unit = ?", (food, new_unit))
    updated_rows = cursor.fetchall()
    print(f"Updated rows for food '{food}': {updated_rows}")
    
    # 데이터베이스 연결 종료
    conn.close()

# 데이터베이스 파일 경로
db_path = 'app/food_database.db'

# 업데이트 함수 호출
update_conversion_unit(db_path, '치킨', 'unit', '조각')
