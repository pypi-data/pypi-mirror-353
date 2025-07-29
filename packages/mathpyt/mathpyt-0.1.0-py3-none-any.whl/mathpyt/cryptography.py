"""
Шаблоны кода для криптографии
"""
import random
import math
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def caesar_cipher(text, shift, encrypt=True):
    """
    Шифр Цезаря
    
    Parameters:
    -----------
    text : str
        Исходный текст
    shift : int
        Сдвиг (ключ)
    encrypt : bool, optional
        True для шифрования, False для расшифрования
        
    Returns:
    --------
    str
        Зашифрованный или расшифрованный текст
    """
    if not encrypt:
        shift = -shift
    
    result = ""
    
    for char in text:
        # Обрабатываем только буквы
        if char.isalpha():
            # Определяем базовый код (ASCII)
            base = ord('A') if char.isupper() else ord('a')
            # Шифруем/расшифровываем
            shifted = (ord(char) - base + shift) % 26 + base
            result += chr(shifted)
        else:
            # Оставляем без изменений
            result += char
    
    return result


def vigenere_cipher(text, key, encrypt=True):
    """
    Шифр Виженера
    
    Parameters:
    -----------
    text : str
        Исходный текст
    key : str
        Ключ
    encrypt : bool, optional
        True для шифрования, False для расшифрования
        
    Returns:
    --------
    str
        Зашифрованный или расшифрованный текст
    """
    result = ""
    key = key.upper()
    key_length = len(key)
    key_as_int = [ord(k) - ord('A') for k in key]
    
    for i, char in enumerate(text):
        if char.isalpha():
            # Определяем базовый код (ASCII)
            base = ord('A') if char.isupper() else ord('a')
            # Определяем сдвиг на основе символа ключа
            key_index = i % key_length
            shift = key_as_int[key_index]
            
            # Шифруем/расшифровываем
            if encrypt:
                shifted = (ord(char) - base + shift) % 26 + base
            else:
                shifted = (ord(char) - base - shift) % 26 + base
                
            result += chr(shifted)
        else:
            # Оставляем без изменений
            result += char
    
    return result


def xor_cipher(text, key):
    """
    XOR-шифрование
    
    Parameters:
    -----------
    text : str или bytes
        Исходный текст
    key : str или bytes
        Ключ
        
    Returns:
    --------
    bytes
        Результат XOR-шифрования
    """
    # Преобразуем текст и ключ в байты, если они строки
    if isinstance(text, str):
        text = text.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    # Расширяем ключ до длины текста
    key_repeated = (key * (len(text) // len(key) + 1))[:len(text)]
    
    # Выполняем XOR
    result = bytes(a ^ b for a, b in zip(text, key_repeated))
    
    return result


def generate_rsa_keys(bits=1024):
    """
    Генерация пары ключей RSA
    
    Parameters:
    -----------
    bits : int, optional
        Размер ключа в битах
        
    Returns:
    --------
    tuple
        ((e, n), (d, n)) - открытый и закрытый ключи
    """
    try:
        from Crypto.PublicKey import RSA
        
        # Генерируем ключ RSA
        key = RSA.generate(bits)
        
        # Извлекаем компоненты
        e = key.e
        d = key.d
        n = key.n
        
        # Возвращаем пару ключей
        return ((e, n), (d, n))
    except ImportError:
        raise ImportError("Для генерации ключей RSA требуется библиотека pycryptodome")


def rsa_encrypt(message, public_key):
    """
    Шифрование сообщения с помощью RSA
    
    Parameters:
    -----------
    message : int
        Сообщение в виде числа (должно быть меньше n)
    public_key : tuple
        Открытый ключ (e, n)
        
    Returns:
    --------
    int
        Зашифрованное сообщение
    """
    e, n = public_key
    
    if message >= n:
        raise ValueError("Сообщение должно быть меньше n")
    
    # Шифрование: c = m^e mod n
    return pow(message, e, n)


def rsa_decrypt(ciphertext, private_key):
    """
    Расшифрование сообщения с помощью RSA
    
    Parameters:
    -----------
    ciphertext : int
        Зашифрованное сообщение
    private_key : tuple
        Закрытый ключ (d, n)
        
    Returns:
    --------
    int
        Расшифрованное сообщение
    """
    d, n = private_key
    
    # Расшифрование: m = c^d mod n
    return pow(ciphertext, d, n)


def diffie_hellman_key_exchange(p, g):
    """
    Реализация протокола обмена ключами Диффи-Хеллмана
    
    Parameters:
    -----------
    p : int
        Большое простое число
    g : int
        Примитивный корень по модулю p
        
    Returns:
    --------
    tuple
        (private_key_A, public_key_A, private_key_B, public_key_B, shared_secret_A, shared_secret_B)
    """
    # Генерируем приватные ключи
    private_key_A = random.randint(2, p - 2)
    private_key_B = random.randint(2, p - 2)
    
    # Вычисляем публичные ключи
    public_key_A = pow(g, private_key_A, p)
    public_key_B = pow(g, private_key_B, p)
    
    # Вычисляем общий секретный ключ
    shared_secret_A = pow(public_key_B, private_key_A, p)
    shared_secret_B = pow(public_key_A, private_key_B, p)
    
    return private_key_A, public_key_A, private_key_B, public_key_B, shared_secret_A, shared_secret_B


def sha256_hash(data):
    """
    Вычисление хеша SHA-256
    
    Parameters:
    -----------
    data : str или bytes
        Данные для хеширования
        
    Returns:
    --------
    str
        Хеш в виде шестнадцатеричной строки
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()


def md5_hash(data):
    """
    Вычисление хеша MD5
    
    Parameters:
    -----------
    data : str или bytes
        Данные для хеширования
        
    Returns:
    --------
    str
        Хеш в виде шестнадцатеричной строки
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.md5(data).hexdigest()


def aes_encrypt(data, key):
    """
    Шифрование данных с помощью AES
    
    Parameters:
    -----------
    data : str или bytes
        Данные для шифрования
    key : bytes
        Ключ шифрования (должен быть 16, 24 или 32 байта)
        
    Returns:
    --------
    bytes
        Зашифрованные данные (IV + шифртекст)
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Генерируем случайный IV
    iv = get_random_bytes(16)
    
    # Создаем шифр
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Шифруем данные
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    
    # Возвращаем IV + шифртекст
    return iv + ciphertext


def aes_decrypt(encrypted_data, key):
    """
    Расшифрование данных с помощью AES
    
    Parameters:
    -----------
    encrypted_data : bytes
        Зашифрованные данные (IV + шифртекст)
    key : bytes
        Ключ шифрования (должен быть 16, 24 или 32 байта)
        
    Returns:
    --------
    bytes
        Расшифрованные данные
    """
    # Извлекаем IV (первые 16 байт)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    
    # Создаем шифр
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Расшифровываем данные
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    return plaintext


def base64_encode(data):
    """
    Кодирование данных в Base64
    
    Parameters:
    -----------
    data : str или bytes
        Данные для кодирования
        
    Returns:
    --------
    str
        Данные, закодированные в Base64
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return base64.b64encode(data).decode('utf-8')


def base64_decode(data):
    """
    Декодирование данных из Base64
    
    Parameters:
    -----------
    data : str
        Данные в формате Base64
        
    Returns:
    --------
    bytes
        Декодированные данные
    """
    return base64.b64decode(data) 