import pickle
import os
import re
import sqlalchemy as db
import cx_Oracle
from sqlalchemy.sql import text


def load_cust(engine):
    with engine.begin() as conn:
        result = conn.execute("SELECT * FROM cust")
        cust_list = [dict(row)for row in result]
        # print(cust_list)
        page = len(cust_list)-1
        # print(page)

    return cust_list, page


def print_menu():
    return input("""
        다음 중 작업 하실 메뉴를 입력 하세요.
        I - 고객 정보 입력
        C - 현재 고객 정보 출력
        P - 이전 고객 정보 출력
        N - 다음 고객 정보 출력
        U - 고객 정보 수정
        D - 고객 정보 삭제
        S - 데이타 저장
        Q - 프로그램 종료
        """).strip().upper()


def input_cust(cust_list, page, engine):
    print("고객 정보 입력 로직")
    customer = {"name": "", "gender": "", "email": "", "birthyear": ""}
    while True:
        name = input("이름을 입력 하세요 : ")
        regex = re.compile("[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z]")
        if regex.search(name):
            break
        else:
            print("이름은 한글로만 입력하세요.")

    while True:
        gender = input("성별(M/F/O)을 입력 하세요 : ").upper()
        if gender in ("M", "F", "O"):
            break
        else:
            print("성별은 M/F/O 중에서만 입력하세요.")

    while True:
        email = input("이메일 주소를 입력 하세요 : ")
        regex = re.compile(
            "^[a-zA-Z][a-zA-Z0-9]{3,10}@[a-zA-Z]{2,6}[.][a-zA-Z]{2,4}$")
        if regex.search(email):  # True, False 0 == False, -2 == True
            break
        else:
            print("이메일은 example@example.com 형식으로 입력하세요. 아이디는 최소 4자 이상.")

    while True:
        birthyear = input("출생 년도를 입력 하세요 : ")
        regex = re.compile("^[0-9]{4}$")
        if regex.search(birthyear):
            break
        else:
            print("출생년도 4자리를 입력하세요.")

    customer["name"] = name
    customer["gender"] = gender
    customer["email"] = email
    customer["birthyear"] = birthyear
    cust_list.append(customer)

    with engine.begin() as conn:
        #conn = engine.begin()
        statement = text(
                """INSERT INTO cust(name, gender, email, birthyear)
                VALUES
                (:name, :gender, :email, :birthyear)
                """
            )
        conn.execute(statement,**customer)

    page = load_cust(engine)
    # page = len(cust_list)-1
    return page


def print_c(cust_list, page):
    print("현재 고객 정보 출력")
    if page >= 0:
        print(cust_list[page])
    else:
        print("입력된 정보가 없습니다.")


def print_p(cust_list, page):
    print("이전 고객 정보 출력")
    if page <= 0 or len(cust_list) == 0:
        print("첫 번째 페이지 입니다.")
    else:
        page = page - 1
        print(cust_list[page])
    return page


def print_n(cust_list, page):
    print("다음 고객 정보 출력")
    if page >= len(cust_list)-1:
        print("마지막 번째 페이지 입니다.")
    else:
        page = page + 1
        print(cust_list[page])
    return page


def update_cust(cust_list):
    while True:
        choice1 = input("수정하고 싶은 고객 정보의 이름을 입력하세요 : ")
        idx = -1
        for i, val in enumerate(cust_list):
            # if cust_list[i]["name"] == choice1.strip():
            if val["name"] == choice1.strip():
                idx = i
                break
        if idx == -1:
            print("등록되지 않은 이름입니다.")
            break

        choice1 = input("""수정하고싶은 항목을 입력하세요
        name, gender, email, birthyer, cancel
        """)
        if choice1 in ("name", "gender", "email", "birthyear"):
            cust_list[idx][choice1] = input(
                "수정할 {}을 입력 하세요. ".format(choice1))
            break
        elif choice1 == "cancel":
            break
        else:
            print("존재하지 않는 항목입니다.")
            break


def delete_cust(cust_list, page, engine):
    print("고객 정보 삭제")
    i = int(input("삭제할 회원의 페이지를 입력하세요"))
    with engine.begin() as conn:
        conn.execute("delete from cust where name = '%s' " %cust_list[i]['name'])
        # del cust_list[page]
    cust_list, page = load_cust(engine)
    return page


# def save_cust(cust_list):
#     with open("./data/cust_data.pkl", "wb") as f:
#         pickle.dump(cust_list, f)
#         print("저장 되었습니다.")


def main():

    engine = db.create_engine("oracle://hr:hr@oraxe11g/xe")
    page = 0
    cust_list = []
    cust_list, page = load_cust(engine)

    while True:
        choice = print_menu()
        if choice == "I":
            page = input_cust(cust_list, page, engine)
        elif choice == "C":
            print_c(cust_list, page)
        elif choice == "P":
            page = print_p(cust_list, page)
        elif choice == "N":
            page = print_n(cust_list, page)
        elif choice == "U":
            update_cust(cust_list)
        elif choice == "D":
            page = delete_cust(cust_list, page, engine)
        # elif choice == "S":
        #     save_cust(cust_list)
        # db 연동하면 save 기능 필요 X
        elif choice == "Q":
            break
        else:
            print("메뉴를 잘못입력했습니다.")




if __name__ == "__main__":
    main()
