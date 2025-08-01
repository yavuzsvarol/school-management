import sqlite3, os

path = os.path.dirname(os.path.realpath(__file__))
con = sqlite3.connect(path + "\\db1.db")
cur = con.cursor()

def menu():
    print("\nMüdür paneline hoş geldiniz.")
    print("""1- Verileri Görüntüle\n2 - Kullanici ekle\n3 - Ders Oluştur
4 - Sınıf Oluştur\n5 - Derse Öğretmen Ata\n6 - Sınıfa Öğretmen Ata\n7 - Çıkış""")
    match input("\nSeçiminizi yapınız: "):
        case "1":
            list_data()
        case "2":
            add_user_menu()
        case "3":
            add_subject_menu()
        case "4":
            add_class_menu()
        case "5":
            assign_teacher_to_subject_menu()
        case "6":
            assign_teacher_to_class_menu()
        case "7":
            exit()
        case _:
            print("Geçersiz seçim, lütfen tekrar deneyin.")
            menu()

def list_data():
    print("""\nListelemek istediğiniz bilgileri seçiniz\n1 - Kullanicilari Listele
2 - Dersleri Listele\n3 - Sınıfları Listele\n4 - Notları Listele\n5 - Çıkış""")
    match input("\nSeçiminizi yapınız: "):
        case "1":
            list_users()
        case "2":
            list_subjects()
        case "3":
            list_classes()
        case "4":
            list_grades()
        case "5":
            menu()
        case _:
            print("Geçersiz seçim, lütfen tekrar deneyin.")
            list_data()

def list_users():
    print("\nKullanıcı Listesi:")
    users = cur.execute("SELECT id, username, role FROM users").fetchall()
    for user in users:
        print(f"ID: {user[0]} - Kullanıcı Adı: {user[1]} - Rol: {user[2]}")
    list_data()

def list_subjects():
    print("\nDers Listesi:")
    subjects = cur.execute("""
        SELECT subject_id, name, credit, username
        FROM subjects
        LEFT JOIN users ON subjects.teacher_id = users.id AND users.role='teacher'
    """).fetchall()
    for subject in subjects:
        if subject[3] is not None:
            teacher_name = subject[3]
        else: teacher_name = "Atanmamış"
        print(f"ID: {subject[0]} - Ders Adı: {subject[1]} - Kredi: {subject[2]} - Öğretmen: {teacher_name}")
    list_data()

def list_classes():
    print("\nSınıf Listesi:")
    classes = cur.execute("""
        SELECT class_id, name, username
        FROM classes
        LEFT JOIN users ON classes.teacher_id = users.id AND users.role='teacher'
    """).fetchall()
    for a_class in classes:
        if a_class[2] is not None:
            teacher_name = a_class[2]
        else: teacher_name = "Atanmamış"
        print(f"ID: {a_class[0]} - Sınıf Adı: {a_class[1]} - Öğretmen: {teacher_name}")
    list_data()

def list_grades():
    print("\nNot Listesi:")
    classes = cur.execute("SELECT class_id FROM classes").fetchall()
    for a_class in classes[0]:
        class_name = cur.execute("SELECT name FROM classes WHERE class_id=?", (a_class,)).fetchone()
        print(class_name[0], "Sınıfının Notları:")
        grades_of_class = cur.execute ("""SELECT student_id, username, subjects.name, exam1 ,exam2, project, average
                                       FROM grades
                                       LEFT JOIN users ON users.id = grades.student_id
                                       LEFT JOIN students ON students.user_id = grades.student_id
                                       LEFT JOIN subjects ON grades.subject_id = subjects.subject_id
                                       WHERE class_id=?""", (a_class,)).fetchall()
        for grade in grades_of_class:
            print(f"ID: {grade[0]} - Ad: {grade[1]} - Ders: {grade[2]} - Notlar: {grade[3]} - {grade[4]} - {grade[5]} - Ortalama: {grade[6]}")

def add_user_menu():
    print("\nKullanici ekleme menusu")
    new_username = input("Yeni kullanici adi: ")
    new_password = input("Yeni kullanici sifresi: ")
    new_role = input("Yeni kullanici rolü (admin, vice_admin, teacher, student): ")
    if new_role not in ["admin", "vice_admin", "teacher", "student"]:
        print("Geçersiz rol. Lütfen 'admin', 'vice_admin', 'teacher' veya 'student' olarak giriniz.")
        return add_user_menu()
    cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_username, new_password, new_role))
    con.commit()
    print("Kullanici başarıyla eklendi.")
    menu()

def add_subject_menu():
    print("\nDers ekleme menusu")
    new_subject = input("Yeni ders adi: ")
    new_subject_credits = input("Ders kredisi: ")
    cur.execute("INSERT INTO subjects (name, credit) VALUES (?, ?)", (new_subject, new_subject_credits))
    con.commit()
    print("Ders başarıyla eklendi.")
    menu()

def add_class_menu():
    print("\nSınıf ekleme menusu")
    new_class_name = input("Yeni sınıf adı: ")
    cur.execute("INSERT INTO classes (name) VALUES (?)", (new_class_name,))
    con.commit()
    print("Sınıf başarıyla eklendi.")
    menu()

def assign_teacher_to_subject_menu():
    subject_count = 0
    print("\nDerse öğretmen atama menusu")
    teacher_username = input("Öğretmen username giriniz: ")
    teacher_id = cur.execute("SELECT id FROM users WHERE username=? AND role='teacher'", (teacher_username,)).fetchone()[0]
    subject_count = cur.execute("SELECT COUNT(*) FROM subjects WHERE teacher_id=?", (teacher_id,)).fetchone()[0]
    if subject_count >= 2:
        print("Öğretmen zaten 2 derse atanmış.")
        menu()
    subject_name = input("Ders adı giriniz: ")
    cur.execute("UPDATE subjects SET teacher_id=? WHERE name=?", (teacher_id, subject_name))
    con.commit()
    print("Öğretmen başarıyla derse atandı.")
    menu()

def assign_teacher_to_class_menu():
    class_count = 0
    print("\nSınıf öğretmene atama menusu")
    teacher_username = input("Öğretmen kullanıcı adını giriniz: ")
    teacher_id = cur.execute("SELECT id FROM users WHERE username=? AND role='teacher'", (teacher_username,)).fetchone()[0]
    class_count = cur.execute("SELECT COUNT(*) FROM classes WHERE teacher_id=?", (teacher_id,)).fetchone()[0]
    if class_count >= 7:
        print("Öğretmen zaten 7 sınıfa atanmış.")
        menu()
    class_name = input("Sınıf adı giriniz: ")
    cur.execute("UPDATE classes SET teacher_id=? WHERE name=?", (teacher_id, class_name))
    con.commit()
    print("Öğretmen başarıyla sınıfa atandı.")
    menu()
