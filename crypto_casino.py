import asyncio
import random
from tonutils.client import TonapiClient
from tonutils.utils import to_amount
from tonutils.wallet import WalletV3R1

# Api ключ от tonconsole
api_key = ""
# Выбор сети
is_testnet = True
file_path = "bip39.txt"
output_file = "results.txt"

async def check_balance_from_random_seed():
    client = TonapiClient(api_key=api_key, is_testnet=is_testnet)

    # Чтение всех слов из текстового файла
    with open(file_path, 'r') as file:
        word_list = file.read().split()

    while True:
        try:
            # Генерация сид-фразы из 24 слов
            seed_phrase = ' '.join(random.sample(word_list, 24))

            # Создание кошелька на основе сид-фразы
            wallet, public_key, private_key, mnemonic = WalletV3R1.from_mnemonic(client, seed_phrase)

            # Попытка проверки баланса
            balance = await wallet.balance()
            balance_amount = to_amount(balance)
            print(f"Баланс для сид-фразы '{seed_phrase}': {balance_amount} TON")

        except Exception as e:
            # В случае ошибки баланс = None
            balance_amount = None
            print(f"Ошибка: {e}. Пропуск и продолжение.")

        # Запись данных в файл
        with open(output_file, 'a') as f:
            f.write(f"Сид-фраза: {seed_phrase}\n")
            f.write(f"Адрес кошелька: {wallet.address}\n")
            f.write(f"Баланс: {balance_amount if balance_amount is not None else 'не удалось проверить'}\n\n")

        await asyncio.sleep(1)

asyncio.run(check_balance_from_random_seed())
