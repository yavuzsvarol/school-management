import sqlite3, os

path = os.path.dirname(os.path.realpath(__file__))
con = sqlite3.connect(path + "\\db1.db")
cur = con.cursor()

def menu():
    tries = 3
    print("\nOkul BYS")
    while True:
        print("\nKalan deneme hakkınız:", tries)
        current_user = input("\nKullanici adi giriniz: ")
        current_passw = input("Şifreyi giriniz: ")
        data = [current_user, current_passw]
        users = cur.execute("SELECT username, password FROM users WHERE username=? AND password=?", data)
        if (users.fetchone() is None):
            print("Kullanici adi veya sifre hatali")
            tries -= 1
            continue
        if tries == 0:
            print("Çok fazla deneme yaptınız, program sonlandırılıyor.")
            con.close()
            exit()
        else:
            current_id = cur.execute("SELECT id FROM users WHERE username=?", (current_user,)).fetchone()[0]
            role = cur.execute("SELECT role FROM users WHERE id=?", (current_id,)).fetchone()[0]
            break
    if role == "admin":
        import principal
        principal.menu()
    elif role == "teacher":
        import teacher
        teacher.menu(current_id)
    elif role == "student":
        import student
        student.menu(current_id)

menu()
