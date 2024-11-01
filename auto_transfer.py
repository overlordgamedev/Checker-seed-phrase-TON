import aiohttp
from tonutils.client import TonapiClient
from tonutils.utils import to_amount
from tonutils.wallet import WalletV3R1
import asyncio

# Api ключ от tonconsole
api_key = ""
# Выбор сети
is_testnet = True
# Адрес получателя
destination_address = ""
# Путь к файлу с сид-фразами
file_path = "valid_seed.txt"


async def check_and_transfer(client, seed_phrase):
    retries = 3  # Количество попыток
    for attempt in range(retries):
        try:
            # Создание кошелька на основе мнемонической фразы
            wallet, public_key, private_key, mnemonic = WalletV3R1.from_mnemonic(client, seed_phrase)
            # Проверка баланса
            balance = await wallet.balance()
            balance_amount = to_amount(balance)

            # Проверка, если баланс больше 0, выполнить перевод
            if balance_amount > 0:
                transfer_amount = balance_amount * 0.9  # 90% от баланса
                # Создание транзакции и запись возвращенного хэша транзакции
                tx_hash = await wallet.transfer(destination=destination_address, amount=transfer_amount, body="test",)
                print(f"Переведено {transfer_amount} TON! Транзакция: {tx_hash}")
                await asyncio.sleep(10)
                # Проверка подтверждения транзакции
                confirmed = await check_transaction_confirmation()
                if confirmed:
                    print("Транзакция подтверждена.")
                else:
                    print("Транзакция не подтверждена.")
            else:
                print(f"Баланс на кошельке: {balance_amount} TON")
            break  # Завершение цикла при успешной транзакции

        except Exception as e:
            print(f"Ошибка для кошелька с сид-фразой {' '.join(seed_phrase)}: {e}")
            if attempt < retries - 1:
                print(f"Повторная попытка {attempt + 1} через 1 секунду...")
                await asyncio.sleep(1)  # Пауза перед следующей попыткой
            else:
                print("Все попытки исчерпаны. Переход к следующему кошельку.")


# Проверка транзакции на то что она подтверждена
async def check_transaction_confirmation():
    retries = 5
    url = f"https://testnet.tonapi.io/v2/blockchain/accounts/{destination_address}/transactions"

    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    first_transaction = data.get("transactions", [{}])[0]
                    # Проверка подтверждения первой транзакции
                    if first_transaction.get("success", False):
                        return True  # Транзакция подтверждена
                    else:
                        print(f"Попытка {attempt + 1}: транзакция не подтверждена, повтор через 1 секунду.")
                        await asyncio.sleep(1)  # Пауза перед повторной проверкой

    return False  # Если после пяти попыток транзакция не подтвердилась


async def main():
    client = TonapiClient(api_key=api_key, is_testnet=is_testnet)

    while True:
        # Чтение сид-фраз из файла
        with open(file_path, "r") as file:
            seed_phrases = [line.strip().split() for line in file]

        # Проверка и перевод для каждого кошелька
        for seed_phrase in seed_phrases:
            await check_and_transfer(client, seed_phrase)

        await asyncio.sleep(1)  # Пауза между проверками

if __name__ == "__main__":
    asyncio.run(main())
