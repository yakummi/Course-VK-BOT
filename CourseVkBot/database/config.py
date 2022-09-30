from dataclasses import dataclass

with open('C:\password\password.py', 'r', encoding='utf-8') as f:
    password = f.read()

@dataclass
class Settings:
    DATABASE = 'VkBase'
    USER = 'postgres'
    PASSWORD = password
