from tonutils.client import TonapiClient
from tonutils.utils import to_amount
from tonutils.wallet import WalletV3R1
import asyncio

# Api ключ от tonconsole
api_key = ""
# Выбор сети
is_testnet = True
# Файл с фразами
file_path = "seed_phrases.txt"
# Файл для сохранения результатов
output_file = "balance_results.txt"
# Файл для валидных кошельков
valid_seeds_file = "valid_seed.txt"

async def main() -> None:
    client = TonapiClient(api_key=api_key, is_testnet=is_testnet)
    # Начальные значения переменных
    total_balance = 0  # Общий баланс
    wallets_with_balance = 0  # Кошельки с балансом больше нуля
    wallets_with_zero_balance = 0 # Кошельки с нулевым балансом
    failed_wallets = 0  # Кошельки с ошибками

    # Чтение сид-фраз из файла
    with open(file_path, "r") as file:
        # Запись сид-фраз, по одной в строку
        seed_phrases = [line.strip().split() for line in file]

    total_wallets = len(seed_phrases)  # Общее количество кошельков

    # Открытие файлов для записи результатов
    with open(output_file, "w") as outfile, open(valid_seeds_file, "w") as valid_file:
        # Обработка каждой сид-фразы
        for seed in seed_phrases:
            try:
                # Создание кошелька на основе сид-фразы
                wallet, public_key, private_key, mnemonic = WalletV3R1.from_mnemonic(client, seed)
                # Проверка баланса
                balance = await wallet.balance()
                balance_amount = to_amount(balance)

                # Запись валидной сид-фразы в файл
                valid_file.write(" ".join(seed) + "\n")

                # Подсчет статистики
                total_balance += balance_amount
                if balance_amount > 0:
                    wallets_with_balance += 1
                else:
                    wallets_with_zero_balance += 1

                # Запись результата в файл
                outfile.write("======================\n")
                outfile.write(f"Сид-фраза: {' '.join(seed)}\n")
                outfile.write(f"Баланс: {balance_amount}\n")

                print(f"Баланс для сид-фразы {' '.join(seed)}: {balance_amount}")
            except KeyError as e:
                failed_wallets += 1
                print(f"Ошибка при получении баланса для сид-фразы {' '.join(seed)}: {e}")
            except Exception as e:
                failed_wallets += 1
                print(f"Неизвестная ошибка для сид-фразы {' '.join(seed)}: {e}")

    # Вывод общей статистики
    print("\n======== Общая статистика ========")
    print(f"Общее количество кошельков: {total_wallets}")
    print(f"Общий баланс: {total_balance}")
    print(f"Кошельков с балансом > 0: {wallets_with_balance}")
    print(f"Кошельков с балансом 0: {wallets_with_zero_balance}")
    print(f"Не удалось проверить: {failed_wallets}")

if __name__ == "__main__":
    asyncio.run(main())
