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
        self.root.title("Currency Rates")
        self.root.geometry("400x400")
        self.root.configure(bg='light yellow')

        # Трансляції для кожної мови / Übersetzungen für jede Sprache / Translations for each language
        self.translations = {
            'EN': {
                'path_label': "Specify the path to save the data file",
                'default_path_label': "*The file will be created on the desktop if the path is not specified",
                'currency_label': "Select Currency",
                'days_label': "Select Number of Days",
                'get_rate_button': "Get Exchange Rates",
                'status_success': "Data successfully loaded",
                'status_error': "Something went wrong"
            },
            'UK': {
                'path_label': "Вкажіть шлях для збереження файлу з даними",
                'default_path_label': "*Файл буде створено на робочому столі, якщо шлях не вказано",
                'currency_label': "Оберіть валюту",
                'days_label': "Оберіть кількість днів",
                'get_rate_button': "Дізнатися курс валют",
                'status_success': "Дані успішно завантажені",
                'status_error': "Щось пішло не так"
            },
            'DE': {
                'path_label': "Geben Sie den Pfad zum Speichern der Datendatei an",
                'default_path_label': "*Die Datei wird auf dem Desktop erstellt, wenn der Pfad nicht angegeben ist",
                'currency_label': "Währung auswählen",
                'days_label': "Anzahl der Tage auswählen",
                'get_rate_button': "Wechselkurse abrufen",
                'status_success': "Daten erfolgreich geladen",
                'status_error': "Etwas ist schief gelaufen"
            }
        }

        self.language = tk.StringVar(value='EN')
        self.create_widgets()
        self.update_texts()

    def create_widgets(self):
        # Етикетка "Мова" / Beschriftung "Sprache" / Label "Language"
        language_frame = tk.Frame(self.root)
        language_frame.pack(anchor='ne', padx=10, pady=5)

        self.language_label = tk.Label(language_frame, text="Language:") # "Мова:"
        self.language_label.pack(side='left')

        self.language_combobox = ttk.Combobox(language_frame, textvariable=self.language)
        self.language_combobox['values'] = ("EN", "UK", "DE")
        self.language_combobox.pack(side='left', padx=5)
        self.language_combobox.bind("<<ComboboxSelected>>", self.change_language)

        self.path_label = tk.Label(self.root, bg='light blue', anchor='w')
        self.path_label.pack(fill='x', padx=10, pady=5)
        self.path_entry = tk.Entry(self.root, width=50)
        self.path_entry.pack(fill='x', padx=10, pady=5)
        self.default_path_label = tk.Label(self.root, bg='light yellow', anchor='w')
        self.default_path_label.pack(fill='x', padx=10, pady=5)

        self.currency_label = tk.Label(self.root, bg='light blue', anchor='w')
        self.currency_label.pack(fill='x', padx=10, pady=5)
        self.currency_var = tk.StringVar(value="EUR")
        self.currency_combobox = ttk.Combobox(self.root, textvariable=self.currency_var)
        self.currency_combobox['values'] = ("USD", "EUR", "CHF", "GBP", "PLZ", "SEK", "XAU", "CAD")
        self.currency_combobox.pack(fill='x', padx=10, pady=5)

        self.days_label = tk.Label(self.root, bg='light blue', anchor='w')
        self.days_label.pack(fill='x', padx=10, pady=5)
        self.days_var = tk.IntVar(value=1)
        self.days_combobox = ttk.Combobox(self.root, textvariable=self.days_var)
        self.days_combobox['values'] = [i for i in range(1, 11)]
        self.days_combobox.pack(fill='x', padx=10, pady=5)

        self.get_rate_button = tk.Button(self.root, command=self.get_exchange_rate)
        self.get_rate_button.pack(fill='x', padx=10, pady=20)

        self.status_label = tk.Label(self.root, text="", bg='light yellow', anchor='w')
        self.status_label.pack(fill='x', padx=10, pady=5)

    def update_texts(self):
        # Оновлення текстів / Aktualisierung der Texte / Updating texts
        lang = self.language.get()
        self.path_label.config(text=self.translations[lang]['path_label'])
        self.default_path_label.config(text=self.translations[lang]['default_path_label'])
        self.currency_label.config(text=self.translations[lang]['currency_label'])
        self.days_label.config(text=self.translations[lang]['days_label'])
        self.get_rate_button.config(text=self.translations[lang]['get_rate_button'])

    def change_language(self, event):
        # Зміна мови / Sprachwechsel / Changing language
        self.update_texts()

    async def fetch_exchange_rate(self, date):
        # Отримання курсу валют / Abrufen des Wechselkurses / Fetching exchange rate
        async with aiohttp.ClientSession() as session:
            url = f"https://api.privatbank.ua/p24api/exchange_rates?date={date}"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to fetch data: {response.status} {response.reason}")

    def save_to_json(self, data, path):
        # Збереження даних у JSON / Speichern der Daten in JSON / Saving data to JSON
        if not path:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            path = desktop

        filename = f"exchange_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        full_path = os.path.join(path, filename)

        formatted_data = []
        for date, rates in data.items():
            if 'exchangeRate' in rates:
                for rate in rates['exchangeRate']:
                    if rate.get('currency') == self.currency_var.get():
                        formatted_data.append({date: {self.currency_var.get(): {'sale': rate.get('saleRateNB', rate.get('saleRate')), 'purchase': rate.get('purchaseRateNB', rate.get('purchaseRate'))}}})

        with open(full_path, 'w') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=4)

    def get_exchange_rate(self):
        # Отримання курсу валют / Abrufen des Wechselkurses / Fetching exchange rate
        currency = self.currency_var.get()
        days = self.days_var.get()
        path = self.path_entry.get()

        try:
            asyncio.run(self.get_exchange_rate_async(currency, days, path))
        except Exception as e:
            self.status_label.config(text=self.translations[self.language.get()]['status_error'], bg='red')
            print(f"Error: {e}")

    async def get_exchange_rate_async(self, currency, days, path):
        # Асинхронне отримання курсу валют / Asynchrones Abrufen des Wechselkurses / Asynchronous fetching of exchange rate
        try:
            start_date = datetime.now()
            date_list = [(start_date - timedelta(days=i)).strftime('%d.%m.%Y') for i in range(days)]
            all_data = {}

            for date in date_list:
                data = await self.fetch_exchange_rate(date)
                all_data[date] = data

            self.save_to_json(all_data, path)
            sleep(2)
            self.status_label.config(text=self.translations[self.language.get()]['status_success'], bg='green')
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", bg='red')
            print(f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyApp(root)
    root.mainloop()
