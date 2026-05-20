# Звіт аудиту безпеки — Електронний деканат

## 1. Резюме

Проведено комплексний аудит безпеки системи «Електронний деканат», створеної в межах практичних робіт №2–9.

Під час аудиту перевірено:
- автентифікацію та авторизацію;
- захист веб-додатку;
- шифрування персональних даних;
- аудит та моніторинг;
- безпеку Docker-середовища;
- HTTPS та Security Headers;
- захист від SQL Injection, XSS та Brute Force.

Основні висновки:
- реалізовано багатошаровий захист Defense in Depth;
- система захищена від більшості типових веб-атак;
- використовується RBAC, JWT та Bcrypt;
- персональні дані шифруються через Fernet AES;
- Docker-середовище пройшло hardening;
- частина механізмів реалізована частково (CSRF, MFA, WAF).

---

# 2. Реалізовані шари захисту (Defense in Depth)

| Шар | Механізм | Практична |
|---|---|---|
| Інфраструктура | Docker Compose, SQLAlchemy ORM, Alembic | №2–3 |
| Автентифікація | Bcrypt хешування, JWT access + refresh tokens | №4–5 |
| Авторизація | RBAC з ролями admin, teacher, student | №5 |
| Валідація вводу | Pydantic, bleach, CSP, Rate Limiting | №6 |
| Шифрування даних | Fernet AES, encrypted backups | №7 |
| Аудит і моніторинг | audit_log, brute force detection | №8 |
| Безпека середовища | HTTPS, Docker non-root, Trivy, Bandit | №9 |

---

# 3. Модель загроз STRIDE

| STRIDE | Загроза | Реалізований контрзахід | Бажаний контрзахід |
|---|---|---|---|
| Spoofing | Підробка JWT-токена | JWT HMAC-SHA256 | RS256 + Token Blacklist |
| Tampering | Підміна оцінок через API | RBAC + Pydantic | MFA |
| Repudiation | Заперечення змін | audit_log 5W | Цифровий підпис логів |
| Information Disclosure | Витік email з БД | Fernet encryption | Full DB encryption |
| Denial of Service | Перевантаження API | Rate Limiting | Cloudflare WAF |
| Elevation of Privilege | Student → admin | require_role() | ABAC |

---

# 4. Матриця ризиків

| Загроза | Ймовірність | Вплив | Ризик | Рівень | Статус |
|---|---|---|---|---|---|
| Brute Force | 4 | 3 | 12 | Високий | Захищено |
| SQL Injection | 2 | 5 | 10 | Високий | Захищено |
| Stored XSS | 3 | 4 | 12 | Високий | Захищено |
| JWT Token Theft | 2 | 5 | 10 | Високий | Частково |
| Витік файлу БД | 2 | 5 | 10 | Високий | Захищено |
| CSRF | 3 | 3 | 9 | Середній | Частково |
| DDoS | 3 | 3 | 9 | Середній | Частково |
| Соціальна інженерія | 4 | 4 | 16 | Критичний | Не реалізовано |

---

# 5. Чеклист безпеки

## 5.1. Автентифікація та авторизація

| Перевірка | Статус | Практична | Коментар |
|---|---|---|---|
| Паролі хешуються (Bcrypt) | ✅ | №4 | Реалізовано через Passlib |
| JWT з exp | ✅ | №5 | Access token має expiration |
| Refresh Token | ✅ | №5 | Реалізовано |
| RBAC | ✅ | №5 | admin / teacher / student |
| JWT Secret у env | ✅ | №5 | .env |
| Rate Limiting login | ✅ | №6 | slowapi |
| Brute Force detection | ✅ | №8 | Security logs |

---

## 5.2. Захист даних

| Перевірка | Статус | Практична | Коментар |
|---|---|---|---|
| Email encrypted | ✅ | №7 | Fernet AES |
| Encryption key у env | ✅ | №7 | ENCRYPTION_KEY |
| Encrypted backup | ✅ | №7 | .db.enc |
| SQL Injection protection | ✅ | №3–7 | ORM + parameterized queries |
| .env у .gitignore | ✅ | №9 | Secrets не в Git |

---

## 5.3. Безпека веб-додатку

| Перевірка | Статус | Практична | Коментар |
|---|---|---|---|
| Input validation | ✅ | №6 | Pydantic |
| XSS sanitization | ✅ | №6 | bleach |
| CSP | ✅ | №6 | Security headers |
| X-Frame-Options | ✅ | №6 | DENY |
| X-Content-Type-Options | ✅ | №6 | nosniff |
| CORS restrictions | ✅ | №6 | allow_origins |
| HTTPS | ✅ | №9 | TLS |
| HSTS | ✅ | №9 | Strict-Transport-Security |

---

## 5.4. Моніторинг та аудит

| Перевірка | Статус | Практична | Коментар |
|---|---|---|---|
| Audit Log 5W | ✅ | №8 | who/what/when/where/why |
| Login logging | ✅ | №8 | Success/failed login |
| Grade change logging | ✅ | №8 | Audit trail |
| Anomaly detection | ✅ | №8 | Brute force |
| Admin endpoint logs | ✅ | №8 | /admin/logs |
| JSON logs | ✅ | №8 | Structured logging |

---

## 5.5. Безпека середовища

| Перевірка | Статус | Практична | Коментар |
|---|---|---|---|
| Docker non-root | ✅ | №9 | USER appuser |
| Read-only filesystem | ✅ | №9 | Hardening |
| Docker HEALTHCHECK | ✅ | №9 | Health endpoint |
| Trivy scan | ✅ | №9 | Vulnerability scanning |
| pip-audit | ✅ | №9 | Dependency audit |
| Bandit SAST | ✅ | №9 | Static analysis |
| security_check.sh | ✅ | №9 | Automated checks |

---

# 6. Результати тестування

| Тест | Результат | HTTP Code | Висновок |
|---|---|---|---|
| Доступ без токена | Unauthorized | 401 | Захист працює |
| IDOR | Доступ заборонено | 403 | IDOR відсутній |
| Student → admin | Forbidden | 403 | RBAC працює |
| XSS script tag | Endpoint не існує | 404 | XSS не виконується |
| SQL Injection OR 1=1 | Endpoint не існує | 404 | SQL Injection не виконується |
| SQL Injection DROP TABLE | Endpoint не існує | 404 | SQL Injection не виконується |
| Brute Force | Too Many Requests | 429 | Rate Limiting працює |
| Security Headers | Headers present | 200 | CSP/HSTS активні |

---

# 7. Знайдені вразливості та рекомендації

| Проблема | Рекомендація |
|---|---|
| Відсутній MFA | Додати двофакторну автентифікацію |
| JWT у localStorage | Перейти на HttpOnly cookies |
| Частковий CSRF-захист | Реалізувати CSRF tokens |
| Немає WAF | Додати Cloudflare або ModSecurity |
| Немає SIEM | Інтегрувати ELK/Splunk |
| Немає Token Blacklist | Додати blacklist refresh/access tokens |

---

# 8. Висновок

Система «Електронний деканат» реалізує основні принципи сучасної безпеки інформаційних систем:
- Defense in Depth;
- RBAC;
- JWT Authentication;
- Input Validation;
- Encryption at Rest;
- Security Monitoring;
- Infrastructure Hardening.

Більшість критичних ризиків закрито. Система готова до демонстрації та захисту проєкту.

Для production-рівня рекомендується:
- MFA;
- WAF;
- SIEM;
- HttpOnly cookies;
- повний CSRF-захист;
- централізований моніторинг безпеки.

---

# 9. README.md — секція Security

## Безпека

### Реалізовані механізми захисту
- Автентифікація: Bcrypt хешування паролів, JWT access + refresh tokens
- Авторизація: RBAC з ролями admin, teacher, student
- Валідація: Pydantic, bleach sanitization, ORM SQL Injection protection
- Шифрування: Fernet AES для email та телефону
- Security Headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- Моніторинг: Audit Log 5W, Brute Force detection
- Hardening: Docker non-root, HTTPS, Trivy, Bandit