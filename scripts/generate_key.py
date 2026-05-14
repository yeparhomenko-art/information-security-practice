from cryptography.fernet import Fernet

key = Fernet.generate_key()

print("Згенерований ключ Fernet:")
print(f"ENCRYPTION_KEY={key.decode()}")
print()
print("Цей ключ потрібен для розшифрування даних.")
print("Не додавайте його в Git.")