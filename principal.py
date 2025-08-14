import sqlite3, os

path = os.path.dirname(os.path.realpath(__file__))
con = sqlite3.connect(path + "\\db1.db")
cur = con.cursor()

def menu():
    while True:
        print("\nMüdür paneline hoş geldiniz.")
        print("""1 - Verileri Görüntüle\n2 - Kullanici ekle\n3 - Ders Oluştur
4 - Sınıf Oluştur\n5 - Derse Öğretmen Ata\n6 - Sınıf Öğretmeni Belirle\n7 - Sınıfa Ders Ata\n8 - Çıkış""")
        match input("\nSeçiminizi yapınız: "):
            case "1":
                list_data_menu()
            case "2":
                add_user()
            case "3":
                add_subject()
            case "4":
                add_class()
            case "5":
                assign_teacher_to_subject()
            case "6":
                assign_teacher_to_class()
            case "7":
                assign_subject_to_class()
            case "8":
                return
            case _:
                print("Geçersiz seçim, lütfen tekrar deneyin.")

def list_data_menu():
    while True:
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
                    return
                case _:
                    print("Geçersiz seçim, lütfen tekrar deneyin.")

def list_users():
    print("\nKullanıcı Listesi:")
    users = cur.execute("SELECT id, username, role FROM users").fetchall()
    for user in users:
        print(f"ID: {user[0]} - Kullanıcı Adı: {user[1]} - Rol: {user[2]}")

def list_subjects():
    print("\nDers Listesi:")
    subjects = cur.execute("""SELECT subjects.id, name, credit FROM subjects""").fetchall()
    for subject in subjects:
        print(f"ID: {subject[0]} - Ders Adı: {subject[1]} - Kredi: {subject[2]}")

def list_classes():
    print("\nSınıf Listesi:")
    classes = cur.execute("""
        SELECT classes.id, name, username
        FROM classes
        LEFT JOIN users ON classes.teacher_id = users.id AND users.role='teacher'
    """).fetchall()
    for a_class in classes:
        if a_class[2] is not None:
            teacher_name = a_class[2]
        else: teacher_name = "Atanmamış"
        print(f"ID: {a_class[0]} - Sınıf Adı: {a_class[1]} - Öğretmen: {teacher_name}")

def list_grades():
    print("\nNot Listesi:")
    classes = cur.execute("SELECT id FROM classes").fetchall()
    for a_class in classes:
        class_name = cur.execute("SELECT name FROM classes WHERE id=?", (a_class[0],)).fetchone()
        print("\n", class_name[0], "Sınıfının Notları:")
        grades_of_class = cur.execute ("""SELECT student_id, username, subjects.name, exam1 ,exam2, project, average
                                       FROM grades
                                       LEFT JOIN users ON users.id = grades.student_id
                                       LEFT JOIN students ON students.user_id = grades.student_id
                                       LEFT JOIN subjects ON grades.subject_id = subjects.id
                                       WHERE class_id=?""", (a_class[0],)).fetchall()
        for grade in grades_of_class:
            print(f"ID: {grade[0]} - Ad: {grade[1]} - Ders: {grade[2]} - Notlar: {grade[3]} - {grade[4]} - {grade[5]} - Ortalama: {grade[6]}")

def add_user():
    print("\nKullanici ekleme menusu")
    new_username = input("Yeni kullanici adi: ")
    new_password = input("Yeni kullanici sifresi: ")
    new_role = input("Yeni kullanici rolü (admin, vice_admin, teacher, student): ")
    if new_role not in ["admin", "teacher", "student"]:
        print("Geçersiz rol. Lütfen 'admin', 'teacher' veya 'student' olarak giriniz.")
        return
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_username, new_password, new_role))
        con.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            print("Bu kullanici adi zaten bulunmakta.")
            return
        else:
            print("Database integrity hatası:", e)
            return
    if new_role == 'student':
        list_classes()
        stu_id = cur.execute("SELECT id FROM users WHERE username=? AND password=?", (new_username, new_password)).fetchone()[0]
        new_class = input("Öğrenciyi eklemek istediğiniz sınıfı seçiniz: ")
        cur.execute(
            "INSERT INTO students (user_id, class_id) VALUES (?, (SELECT id FROM classes WHERE name=?))",
            (stu_id, new_class)
        )
        class_subjects = cur.execute("""SELECT subject_id FROM class_subjects
                                     LEFT JOIN classes ON classes.id = class_subjects.class_id
                                     WHERE classes.name=?""", (new_class,)).fetchall()
        if not class_subjects:
            print("Bu sınıf hiçbir dersi almıyor.")
        else:
            for subject in class_subjects:
                cur.execute("INSERT INTO grades (student_id, subject_id) VALUES (?, ?)", (stu_id, subject[0]))
    con.commit()
    print("Kullanici başarıyla eklendi.")

def add_subject():
    print("\nDers ekleme menusu")
    new_subject = input("Yeni ders adi: ")
    new_subject_credits = input("Ders kredisi: ")
    try: 
        cur.execute("INSERT INTO subjects (name, credit) VALUES (?, ?)", (new_subject, new_subject_credits))
        con.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            print("Bu isme sahip bir ders zaten var.")
            return
        else:
            print("Database integrity hatası:", e)
            return
    print("Ders başarıyla eklendi.")

def add_class():
    print("\nSınıf ekleme menusu")
    new_class_name = input("Yeni sınıf adı: ")
    try:
        cur.execute("INSERT INTO classes (name) VALUES (?)", (new_class_name,))
        con.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            print("Bu isme sahip bir sınıf zaten var.")
            return
        else:
            print("Database integrity hatası:", e)
            return
    print("Sınıf başarıyla eklendi.")

def assign_subject_to_class():      #class_subjects tablosu row ekleme
    print("\nSınıfa ders atama menüsü")
    list_subjects()
    selected_subject = input("Ders adını girin: ")
    selected_subject_id = cur.execute("SELECT id FROM subjects WHERE name=?", (selected_subject,)).fetchone()[0]
    if not selected_subject_id:
        print("Girdiğiniz isimle bir ders bulunamadı.")
        return
    subject_teachers = cur.execute("""SELECT teacher_id, username FROM teachers
                                   LEFT JOIN users ON teacher_id = users.id
                                   WHERE subject_id=?""", (selected_subject_id,)).fetchall()
    if not subject_teachers:
        print("Bu dersi hiçbir öğretmen vermiyor.")
        return
    print("\nDersi veren öğretmenler: ")
    for teacher in subject_teachers:
        print(f"ID: {teacher[0]} - Kullanıcı Adı: {teacher[1]}")
    selected_teacher = input("Dersi verecek öğretmenin IDsini giriniz: ")
    if selected_teacher not in subject_teachers:
        print("Hatalı seçim.")
        return
    list_classes()
    selected_class = input("Sınıf adını girin: ")
    selected_class_id = cur.execute("SELECT id FROM classes WHERE name=?", (selected_class,)).fetchone()[0]
    if not selected_class_id:
        print("Girdiğiniz isimle bir sınıf bulunamadı.")
        return
    try:
        cur.execute("""INSERT INTO class_subjects (class_id, subject_id, teacher_id) 
                    VALUES (?,?,?)""", (selected_class_id, selected_subject_id, selected_teacher,))
        con.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            print("Bu sınıfa bu ders zaten atanmış")
            return
        else:
            print("Database integrity hatası:", e)
            return
    class_student_ids = cur.execute("SELECT user_id FROM students WHERE class_id=?", (selected_class_id,)).fetchall()
    for student in class_student_ids:
        cur.execute("INSERT INTO grades (student_id, subject_id) VALUES (?, ?)", (student[0], selected_subject_id))
    con.commit()
    print("Sınıfa ders başarıyla eklendi.")

def assign_teacher_to_subject():    #teachers tablosu row ekleme
    print("\nDerse öğretmen atama menüsü")
    teacher_name = input("Öğretmen adını giriniz: ")
    teacher_id = cur.execute("SELECT id FROM users WHERE username=? AND role='teacher'", (teacher_name,)).fetchone()[0]
    if not teacher_id:
        print("Bu adla bir öğretmen bulunamadı.")
        return
    list_subjects()
    subject_name = input("Ders adını giriniz: ")
    subject_id = cur.execute("SELECT id FROM subjects WHERE name=?", (subject_name,)).fetchone()[0]
    if not subject_id:
        print("Böyle bir ders bulunamadı.")
        return
    try:
        cur.execute("INSERT INTO teachers (teacher_id, subject_id) VALUES (?,?)", (teacher_id, subject_id,))
        con.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            print("Bu hocaya bu ders zaten atanmış")
            return
        else:
            print("Database integrity hatası:", e)
            return
    print("Öğretmen derse başarıyla atandı.")

def assign_teacher_to_class():  #Sınıf öğretmeni
    class_count = 0
    print("\nSınıf öğretmeni belirleme menüsü")
    teacher_username = input("Öğretmen kullanıcı adını giriniz: ")
    teacher_id = cur.execute("SELECT id FROM users WHERE username=? AND role='teacher'", (teacher_username,)).fetchone()[0]
    class_count = cur.execute("SELECT COUNT(*) FROM classes WHERE teacher_id=?", (teacher_id,)).fetchone()[0]
    if class_count >= 1:
        print("Öğretmen zaten bir sınıfa atanmış.")
        return
    list_classes()
    class_name = input("Sınıf adı giriniz: ")
    cur.execute("UPDATE classes SET teacher_id=? WHERE name=?", (teacher_id, class_name))
    con.commit()
    print("Öğretmen başarıyla sınıfa atandı.")
