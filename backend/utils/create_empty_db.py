import sqlite3
import shutil
import os
from pathlib import Path

def create_empty_database():

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    source_db = DATA_DIR / "Chinook.db"
    target_db = DATA_DIR / "empty_chinook.db"

    # 1. 기존 DB 파일이 있는지 확인
    if not os.path.exists(source_db):
        print(f"오류: {source_db} 파일이 같은 폴더에 없습니다.")
        return

    # 2. 파일 복사 (뼈대를 가져오기 위해)
    shutil.copyfile(source_db, target_db)
    print(f"1단계: {target_db} 파일이 복사되었습니다.")

    # 3. 복사본에 연결하여 모든 데이터 삭제
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    try:
        # 삭제 중 외래키 제약조건(Foreign Key) 에러를 막기 위해 잠시 기능 끄기
        cursor.execute("PRAGMA foreign_keys = OFF;")

        # DB 안의 모든 테이블 이름 가져오기
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # 각 테이블을 돌면서 데이터(행) 싹 다 지우기
        for table in tables:
            table_name = table[0]
            # sqlite_sequence는 자동 증가 번호를 관리하는 시스템 테이블이므로 제외
            if table_name != "sqlite_sequence": 
                cursor.execute(f"DELETE FROM {table_name};")
                print(f" - {table_name} 테이블 데이터 비우기 완료")

        conn.commit()
        print("\n성공: 모든 테이블이 비워진 깨끗한 empty_chinook.db 가 준비되었습니다!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 외래키 제약조건 다시 켜기
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.close()

if __name__ == "__main__":
    create_empty_database()