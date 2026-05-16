import pandas as pd
import matplotlib
matplotlib.use('Agg') # Важно для Django: работа без графического окна
import matplotlib.pyplot as plt
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_pdf_buffer():
    # 1. Данные
    data = {
        'User': ['Admin', 'User1', 'User2', 'Guest'],
        'Actions': [35, 18, 5, 2],
    }
    df = pd.DataFrame(data)

    # 2. Создаем график Matplotlib
    plt.figure(figsize=(6, 4))
    plt.bar(df['User'], df['Actions'], color='skyblue')
    plt.title('User Activity') # Пока на английском, чтобы не упало без шрифтов
    plt.ylabel('Actions')
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close() # Очищаем память

    # 3. Создаем PDF через ReportLab
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Заголовок
    elements.append(Paragraph("Forum Activity Report", styles['Title']))
    elements.append(Spacer(1, 0.2*inch))

    # Таблица данных
    table_data = [df.columns.to_list()] + df.values.tolist()
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*inch))

    # Добавляем график
    report_img = Image(img_buffer, width=5*inch, height=3.5*inch)
    elements.append(report_img)

    # Собираем
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer
