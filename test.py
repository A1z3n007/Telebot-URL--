from tel_bot1 import bool_1, process_article
from types import SimpleNamespace

def test_start_authorized():
    message = SimpleNamespace(chat=SimpleNamespace(id=1795671737))
    return bool_1(message) == True

def test_start_unauthorized():
    message = SimpleNamespace(chat=SimpleNamespace(id=1234567890))
    return bool_1(message) == True

def test_art_find_valid():
    message = SimpleNamespace(chat=SimpleNamespace(id=1795671737), text="272181996")
    try:
        process_article(message)
        return True
    except Exception as e:
        print("Ошибка в test_art_find_valid:", e)
        return False

def test_art_find_valid_2():
    message = SimpleNamespace(chat=SimpleNamespace(id=1795671737), text="31372372")
    try:
        process_article(message)
        return True
    except Exception as e:
        print("Ошибка в test_art_find_valid_2:", e)
        return False

print(test_start_authorized())
print(test_start_unauthorized())
print(test_art_find_valid())
print(test_art_find_valid_2())
