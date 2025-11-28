🛒 Smart Amazon Price Tracker

A lightweight, modern Python application that tracks the price of any Amazon product and alerts you instantly when it drops to your target amount.
Built using CustomTkinter, Requests, and BeautifulSoup, this tool delivers a smooth GUI experience with real-time background price monitoring.

✨ Features

🔍 Real-time Price Tracking — Monitors product prices every 60 seconds.

⚡ Instant Alert Popup — Beautiful notification window when the price drops.

🎨 Modern Dark UI — Built with CustomTkinter for a sleek and clean interface.

🧵 Threaded Execution — Keeps the app responsive while tracking in background.

🔗 Direct Product Link — Opens the Amazon product page in one click.

📸 Preview

(Add your own screenshot here)

[ GUI Screenshot Placeholder ]

🚀 Installation
1. Clone the repository
git clone https://github.com/yourusername/amazon-price-tracker.git
cd amazon-price-tracker

2. Install Dependencies
pip install customtkinter requests beautifulsoup4

3. Run the Application
python price_tracker.py

🧠 How It Works

Paste any Amazon product URL

Enter your desired target price

Click Start Tracking

The app checks the price continuously

If the price ≤ target → an alert popup appears 🚨

⚠️ Notes

Amazon may block requests occasionally (normal for scraping).

This project is for educational use only.

GUI may behave differently on older Python/Tk versions.

🛠️ Future Enhancements

Multi-product tracking

System tray background mode

Email / Telegram notifications

Price history graph

📄 License

This project is licensed under the MIT License — free to use, modify, and distribute.
