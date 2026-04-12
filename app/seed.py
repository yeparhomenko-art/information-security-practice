"""
Скрипт початкового наповнення бази даних.
Створює ролі, дозволи та тестових користувачів.
"""

from app.database import SessionLocal
from app.models import Role, Permission, User, Group, Subject
from app.security import hash_password


def seed():
    db = SessionLocal()

    try:
        # якщо вже є дані — не пересоздаємо
        if db.query(Role).first():
            print("Database already seeded.")
            return

        # --------------------
        # РОЛІ
        # --------------------
        admin = Role(name="admin", description="Адміністратор деканату")
        teacher = Role(name="teacher", description="Викладач")
        student = Role(name="student", description="Студент")

        db.add_all([admin, teacher, student])
        db.flush()

        # --------------------
        # ДОЗВОЛИ
        # --------------------
        perms = [
            Permission(name="read_grades", description="Перегляд оцінок"),
            Permission(name="edit_grades", description="Редагування оцінок"),
            Permission(name="read_schedule", description="Перегляд розкладу"),
            Permission(name="manage_users", description="Управління користувачами"),
            Permission(name="manage_groups", description="Управління групами"),
            Permission(name="manage_subjects", description="Управління дисциплінами"),
            Permission(name="view_reports", description="Перегляд звітів"),
        ]

        db.add_all(perms)
        db.flush()

        # --------------------
        # РОЛІ → ДОЗВОЛИ
        # --------------------
        admin.permissions.extend(perms)

        teacher.permissions.extend([
            p for p in perms
            if p.name in ("read_grades", "edit_grades", "read_schedule", "view_reports")
        ])

        student.permissions.extend([
            p for p in perms
            if p.name in ("read_grades", "read_schedule")
        ])

        # --------------------
        # ГРУПА
        # --------------------
        group = Group(
            name="КН-31",
            department="Комп'ютерні науки",
            year=3
        )

        db.add(group)
        db.flush()

        # --------------------
        # ДИСЦИПЛІНА
        # --------------------
        subject = Subject(
            name="Безпека інформаційних систем",
            credits=4.0,
            semester=5
        )

        db.add(subject)

        # --------------------
        # КОРИСТУВАЧІ (ВАЖЛИВО: ВСЕ ХЕШУЄТЬСЯ)
        # --------------------

        admin_user = User(
            username="admin",
            email="admin@university.edu",
            full_name="Адміністратор Системи",
            password_hash=hash_password("Admin123!@#"),
            is_active=True
        )
        admin_user.roles.append(admin)

        teacher_user = User(
            username="petrov",
            email="petrov@university.edu",
            full_name="Петров Іван Сергійович",
            password_hash=hash_password("Teacher123!"),
            is_active=True
        )
        teacher_user.roles.append(teacher)

        student_user = User(
            username="ivanov",
            email="ivanov@university.edu",
            full_name="Іванов Олексій Петрович",
            password_hash=hash_password("Student123!"),
            is_active=True,
            group_id=group.id
        )
        student_user.roles.append(student)

        db.add_all([admin_user, teacher_user, student_user])

        # --------------------
        # SAVE
        # --------------------
        db.commit()

        print("✅ Seed completed successfully!")
        print(f"Roles: {db.query(Role).count()}")
        print(f"Permissions: {db.query(Permission).count()}")
        print(f"Users: {db.query(User).count()}")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()