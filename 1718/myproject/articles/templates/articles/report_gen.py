import datetime

# Имитация данных из вашего форума
data = [
    {'user': 'Admin', 'visits': 25, 'last_seen': '2023-10-01'},
    {'user': 'Moderator', 'visits': 18, 'last_seen': '2023-10-02'},
    {'user': 'User123', 'visits': 5, 'last_seen': '2023-10-05'},
]

def generate_html_report(report_data):
    html_content = f"""
    <html>
    <head>
        <title>Отчет посещаемости</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            h2 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h2>Отчет о посещаемости форума</h2>
        <p>Дата генерации: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        <table>
            <tr><th>Пользователь</th><th>Визиты</th><th>Последний вход</th></tr>
            {"".join([f"<tr><td>{i['user']}</td><td>{i['visits']}</td><td>{i['last_seen']}</td></tr>" for i in report_data])}
        </table>
    </body>
    </html>
    """
    with open("forum_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Отчет создан: forum_report.html")

generate_html_report(data)
