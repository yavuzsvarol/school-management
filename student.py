import sqlite3, os

path = os.path.dirname(os.path.realpath(__file__))
con = sqlite3.connect(path + "\\db1.db")
cur = con.cursor()

def menu(current_id):
    print("Öğrenci paneline hoşgeldiniz.")
    match input("\n1 - Notları Listele\n2 - Çıkış\n\nSeçim Yapınız: "):
        case "1":
            list_own_grades(current_id)
        case "2":
            exit()
        case _:
            print("Hatalı girdi")
            menu()
    
def list_own_grades(current_id):
    grades = cur.execute("""SELECT name, credit, exam1, exam2, project FROM grades
                         LEFT JOIN subjects ON grades.subject_id = subjects.subject_id
                         WHERE grades.student_id=?""", (str(current_id),)).fetchall()
    ortalamalar = []
    toplam_kredi = 0
    if not grades:
        print("Şuanda hiçbir ders almıyorsunuz.")
        menu(current_id)
    for grade in grades:
        ortalama = (grade[2] + grade[3] + grade[4]) / 3
        print(
            f"Ders adı: {grade[0]} - "
            f"1. Sınav: {grade[2]} - "
            f"2. Sınav: {grade[3]} - "
            f"Proje: {grade[4]} - "
            f"Kredi: {grade[1]} - "
            f"Ortalama: {ortalama}"
        )
        ortalamalar.append(ortalama*grade[1])
        toplam_kredi += grade[1]
    ortalama = 0
    for ort in ortalamalar:
        ortalama += ort
    print("\nGenel Not Ortalaması: ", ortalama/toplam_kredi)
    