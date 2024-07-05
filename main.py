import tkinter as tk
from tkinter import ttk
import json
import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
from time import sleep

class CurrencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Курси валют")
        self.root.geometry("400x400")
        self.root.configure(bg='light yellow')

        self.create_widgets()

    def create_widgets(self):
        self.path_label = tk.Label(self.root, text="Вкажіть шлях для збереження файлу з даними", bg='light blue', anchor='w')
        self.path_label.pack(fill='x', padx=10, pady=5)
        self.path_entry = tk.Entry(self.root, width=50)
        self.path_entry.pack(fill='x', padx=10, pady=5)
        self.default_path_label = tk.Label(self.root, text="*Файл буде створено на робочому столі, якщо шлях не вказано", bg='light yellow', anchor='w')
        self.default_path_label.pack(fill='x', padx=10, pady=5)

        self.currency_label = tk.Label(self.root, text="Оберіть валюту", bg='light blue', anchor='w')
        self.currency_label.pack(fill='x', padx=10, pady=5)
        self.currency_var = tk.StringVar(value="EUR")
        self.currency_combobox = ttk.Combobox(self.root, textvariable=self.currency_var)
        self.currency_combobox['values'] = ("USD", "EUR", "CHF", "GBP", "PLZ", "SEK", "XAU", "CAD")
        self.currency_combobox.pack(fill='x', padx=10, pady=5)

        self.days_label = tk.Label(self.root, text="Оберіть кількість днів", bg='light blue', anchor='w')
        self.days_label.pack(fill='x', padx=10, pady=5)
        self.days_var = tk.IntVar(value=1)
        self.days_combobox = ttk.Combobox(self.root, textvariable=self.days_var)
        self.days_combobox['values'] = [i for i in range(1, 11)]
        self.days_combobox.pack(fill='x', padx=10, pady=5)

        self.get_rate_button = tk.Button(self.root, text="Дізнатися курс валют", command=self.get_exchange_rate)
        self.get_rate_button.pack(fill='x', padx=10, pady=20)

        self.status_label = tk.Label(self.root, text="", bg='light yellow', anchor='w')
        self.status_label.pack(fill='x', padx=10, pady=5)

    async def fetch_exchange_rate(self, date):
        async with aiohttp.ClientSession() as session:
            url = f"https://api.privatbank.ua/p24api/exchange_rates?date={date}"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to fetch data: {response.status} {response.reason}")

    def save_to_json(self, data, path):
        if not path:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            path = desktop

        filename = f"exchange_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        full_path = os.path.join(path, filename)

        # Форматування даних у потрібну структуру
        formatted_data = []
        for date, rates in data.items():
            if 'exchangeRate' in rates:
                for rate in rates['exchangeRate']:
                    if rate.get('currency') == self.currency_var.get():
                        formatted_data.append({date: {self.currency_var.get(): {'sale': rate.get('saleRateNB', rate.get('saleRate')), 'purchase': rate.get('purchaseRateNB', rate.get('purchaseRate'))}}})

        with open(full_path, 'w') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=4)

    def get_exchange_rate(self):
        currency = self.currency_var.get()
        days = self.days_var.get()
        path = self.path_entry.get()

        try:
            asyncio.run(self.get_exchange_rate_async(currency, days, path))
        except Exception as e:
            self.status_label.config(text="Щось пішло не так", bg='red')
            print(f"Error: {e}")

    async def get_exchange_rate_async(self, currency, days, path):
        try:
            start_date = datetime.now()
            date_list = [(start_date - timedelta(days=i)).strftime('%d.%m.%Y') for i in range(days)]
            all_data = {}

            for date in date_list:
                data = await self.fetch_exchange_rate(date)
                all_data[date] = data

            self.save_to_json(all_data, path)
            sleep(2)
            self.status_label.config(text="Дані успішно завантажені", bg='green')
        except Exception as e:
            self.status_label.config(text=f"Помилка: {str(e)}", bg='red')
            print(f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyApp(root)
    root.mainloop()
