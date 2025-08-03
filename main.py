import zipfile
import tkinter as tk
from tkinter import filedialog
import itertools
import os
import sys
import time
import pyzipper

def welcome():
    print("Welcome./.")

def select_zip_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="ZIPファイルを選択してください", filetypes=[("ZIP files", "*.zip")])
    return file_path

def select_mode():
    print("[1] Num（数字のみ）")
    print("[2] Word（a-zA-Z 総当たり）")
    while True:
        choice = input("モードを数字で選んでください (1 or 2): ")
        if choice in {"1", "2"}:
            return int(choice)
        else:
            print("無効な入力です。1か2を入力してください。")

def nummm():
    while True:
        try:
            min_digits = int(input("最小桁数を入力（例: 1）: "))
            max_digits = int(input("最大桁数を入力（例: 6）: "))
            if 1 <= min_digits <= max_digits:
                return min_digits, max_digits
            else:
                print("最小桁数は1以上、最大桁数は最小桁数以上で入力してください。")
        except ValueError:
            print("数字で入力してください。")

def get_word_length_range():
    while True:
        try:
            min_len = int(input("最小文字数を入力（例: 1）: "))
            max_len = int(input("最大文字数を入力（例: 4）: "))
            if 1 <= min_len <= max_len:
                return min_len, max_len
            else:
                print("最小文字数は1以上、最大文字数は最小文字数以上で入力してください。")
        except ValueError:
            print("数字で入力してください。")

def load_word_list():
    return [chr(c) for c in range(ord('a'), ord('z')+1)] + [chr(c) for c in range(ord('A'), ord('Z')+1)]

def generate_passwords(mode, digit_range=None):
    if mode == 1:
        min_d, max_d = digit_range
        for length in range(min_d, max_d + 1):
            for pwd in itertools.product("0123456789", repeat=length):
                yield ''.join(pwd)

    elif mode == 2:
        chars = load_word_list()
        min_len, max_len = digit_range
        for length in range(min_len, max_len + 1):
            for pwd in itertools.product(chars, repeat=length):
                yield ''.join(pwd)

def count_total_combinations(mode, digit_range=None):
    if mode == 1:
        total = 0
        min_d, max_d = digit_range
        for d in range(min_d, max_d + 1):
            total += 10 ** d
        return total
    elif mode == 2:
        min_len, max_len = digit_range
        return sum([52 ** i for i in range(min_len, max_len + 1)])

def print_progress(current, total, bar_length=30):
    percent = current / total if total else 0
    filled_length = int(bar_length * percent)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r進捗: |{bar}| {percent:.2%} ({current}/{total})')
    sys.stdout.flush()

def try_extract(zip_path, mode, digit_range=None):
    total = count_total_combinations(mode, digit_range)
    count = 0

    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zf:
            for pwd in generate_passwords(mode, digit_range):
                count += 1
                try:
                    zf.extractall(pwd=pwd.encode('utf-8'))
                    print_progress(count, total)
                    print(f"\n[+] 成功")
                    return pwd
                except RuntimeError:
                    print_progress(count, total)
                except Exception as e:
                    print_progress(count, total)
            else:
                print()
    except FileNotFoundError:
        print("[-] 指定されたZIPファイルが見つかりません。")
        return None
    except Exception as e:
        print(f"[-] エラーが発生しました: {e}")
        return None

    print("\n[-] 全パターンを試しましたが、パスワードは見つかりませんでした。")
    return None


def main():
    welcome()
    zip_path = select_zip_file()
    if not zip_path:
        print("ZIPファイルが選択されませんでした。終了します。")
        input("終了するにはEnterを押してください。")
        return

    mode = select_mode()
    digit_range = None

    if mode == 1:
        digit_range = nummm()
    elif mode == 2:
        digit_range = get_word_length_range()

    print("\n解析を開始します。しばらくお待ちください...\n")
    start_time = time.time()
    found = try_extract(zip_path, mode, digit_range)
    end_time = time.time()

    if found:
        print(f"[+] パスワード発見: {found}")
    else:
        print("[-] パスワードは見つかりませんでした。")

    print(f"[+] 経過時間: {end_time - start_time:.2f}秒")
    input("終了するにはEnterを押してください。")

if __name__ == "__main__":
    main()
