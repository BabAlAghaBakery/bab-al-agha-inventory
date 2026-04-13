import streamlit as st
import pandas as pd
import datetime
import os
import urllib.parse

# --- 1. إعدادات المظهر العام (ذوق احترافي) ---
st.set_page_config(page_title="جرد قسم التوست - باب الآغا", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .footer-rights { text-align: center; color: #64748b; font-size: 12px; margin-top: 50px; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .print-paper { background: white; padding: 40px; border: 2px solid #333; color: black; line-height: 1.5; font-family: 'Cairo', sans-serif; }
    @media print { .no-print { display: none !important; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات الأولية (القائمة التي أرسلتها) ---
INITIAL_ITEMS = [
    ["باكيت تركي", 50], ["باكيت فرنسي اسمر", 50], ["باكيت فرنسي ابيض", 50],
    ["صمون شاورما", 50], ["صمون سداسي", 50], ["صمون كنتاكي حمام", 25],
    ["صمون كنتاكي دائري", 30], ["صمون مني بركر", 30], ["صمون بركر وسط", 20],
    ["صمون اسمر سداسي", 25], ["صمون كنتاكي اسمر", 25], ["صمون بطاطا", 40],
    ["صمون بركر دبل", 30], ["جرك بالحليب", 100], ["جرك تمر", 40],
    ["جرك حلقوم", 40], ["جرك بالجبن", 60], ["جرك كاكاو (علبة)", 70],
    ["جرك كاكاو ( قطع )", 30], ["جرك برازيلي", 150], ["جرك بربراوزا", 70],
    ["جرك مغربية", 15], ["خبز سمسم حلو", 40], ["خبز شعير 7 حبات", 60],
    ["خبز شعير اصلي", 100], ["خبز تركي بالجبن", 50], ["خبز محيرجه", 40],
    ["لفه خميرة", 70], ["ملفوف دارسين", 70], ["توست اسمر ساده", 80],
    ["توست اسمر 7 حبات", 50], ["توست اسمر شوفان", 50], ["توست ابيض", 130],
    ["توست شعير 7 حبات", 45], ["توست شعير اصلي", 45], ["توست جاودار", 25],
    ["توست بطاطا", 40], ["توست كاكاو", 30], ["توست فراولة", 30],
    ["توست حلبي", 20], ["توست طماطم", 20], ["توست زيتون", 30],
    ["توست بالحليب", 30], ["توست بريوش كاكاو", 30], ["توست جبن", 50],
    ["خلية نحل كاكاو", 70], ["خلية نحل كاكاو نوتيلا", 40], ["خلية نحل جبن", 50],
    ["خلية نحل حليب مكثف", 70], ["خلية نحل نوتيلا", 30], ["خلية نحل تمر وحلقوم", 70],
    ["لقمة صغير", 10], ["كرواسون كرز", 150], ["كرواسون نستله", 200],
    ["كرواسون ابيض", 800], ["كرواسون زبده حيوانيه", 50], ["كيك جنين حنطة مخلوط", 100],
    ["كيك جنين حنطة اصلي", 60], ["سميط شعير", 60], ["محلب تركي", 30],
    ["محلب تمر", 30], ["محلب حلقوم", 30], ["محلب مبروش", 30], ["محلب سمسم", 30]
]

DB_FILE = "bakery_inventory.csv"
ORDERS_FILE = "special_orders.csv"

if not os.path.exists(DB_FILE):
    pd.DataFrame(INITIAL_ITEMS, columns=["السلعة", "رقم الأمان"]).to_csv(DB_FILE, index=False)
if not os.path.exists(ORDERS_FILE):
    pd.DataFrame(columns=["الطلب", "التفاصيل"]).to_csv(ORDERS_FILE, index=False)

df_items = pd.read_csv(DB_FILE)
df_orders = pd.read_csv(ORDERS_FILE)

# --- 3. تصميم القائمة الجانبية ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3014/3014535.png", width=100)
st.sidebar.title("نظام باب الآغا")
menu = st.sidebar.radio("انتقل إلى:", ["📋 الجرد الصباحي", "🛒 الطلبيات والوصايا", "⚙️ إدارة السلع"])

# --- قسم الجرد والتوصية ---
if menu == "📋 الجرد الصباحي":
    st.markdown("<div class='main-header'><h1>🥖 جرد قسم التوست - باب الآغا</h1></div>", unsafe_allow_html=True)
    
    # استخدام ذاكرة الجلسة لضمان عدم ضياع البيانات عند التنقل
    if 'inventory_values' not in st.session_state: st.session_state.inventory_values = {}
    if 'rec_values' not in st.session_state: st.session_state.rec_values = {}
    if 'note_values' not in st.session_state: st.session_state.note_values = {}

    inventory_results = []
    
    st.info("💡 أدخل البيانات أدناه ثم اضغط على زر الاعتماد في الأسفل.")
    
    for i, row in df_items.iterrows():
        st.markdown(f"### 📦 {row['السلعة']}")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            qty = st.number_input("الموجود", min_value=0, key=f"inv_{i}", value=st.session_state.inventory_values.get(f"inv_{i}", 0))
            st.session_state.inventory_values[f"inv_{i}"] = qty
        with col2:
            rec = st.number_input("التوصية", min_value=0, key=f"rec_{i}", value=st.session_state.rec_values.get(f"rec_{i}", 0))
            st.session_state.rec_values[f"rec_{i}"] = rec
        with col3:
            note = st.text_input("ملاحظة", key=f"note_{i}", value=st.session_state.note_values.get(f"note_{i}", ""), placeholder="أضف ملاحظة هنا...")
            st.session_state.note_values[f"note_{i}"] = note
            
        inventory_results.append({"السلعة": row['السلعة'], "الموجود": qty, "التوصية": rec, "الملاحظة": note})
        st.markdown("---")

    if st.button("✅ اعتماد الجرد وتجهيز التقرير والواتساب"):
        st.session_state.report_ready = inventory_results
        st.success("تم التجهيز! انزل للأسفل للإرسال أو الطباعة.")

# --- قسم الطباعة والإرسال (يظهر بعد الاعتماد) ---
if 'report_ready' in st.session_state:
    st.markdown("## 📤 خيارات التصدير (واتساب وطباعة)")
    
    report_items = st.session_state.report_ready
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    
    # 1. تجهيز رسالة الواتساب الشاملة
    wa_msg = f"📋 *تقرير جرد قسم التوست - باب الآغا*\n"
    wa_msg += f"📅 *التاريخ:* {datetime.date.today()} | 🕒 *الوقت:* {current_time}\n"
    wa_msg += f"👤 *المسؤول:* أيوب هاني\n"
    wa_msg += f"━━━━━━━━━━━━━━━\n"
    
    for item in report_items:
        # إرسال المواد التي بها جرد فقط لتجنب طول الرسالة الزائد، أو إرسال الكل حسب رغبتك
        if item['الموجود'] > 0 or item['التوصية'] > 0:
            wa_msg += f"🔹 *{item['السلعة']}*:\n"
            wa_msg += f"   - الموجود: {item['الموجود']} | التوصية: {item['التوصية']}\n"
            if item['الملاحظة']: wa_msg += f"   - 📝 ملاحظة: {item['الملاحظة']}\n"
            wa_msg += f"-----------"

    # إضافة الوصايا والطلبيات (جدول الوصايا) للواتساب
    if not df_orders.empty:
        wa_msg += f"\n\n🛒 *وصايا وطلبيات إضافية:*\n"
        for _, r in df_orders.iterrows():
            wa_msg += f"• {r['الطلب']}: {r['التفاصيل']}\n"
    
    wa_msg += f"\n━━━━━━━━━━━━━━━\nتم الجرد بواسطة نظام أيوب هاني الذكي"

    # زر الواتساب
    import urllib.parse
    encoded_msg = urllib.parse.quote(wa_msg)
    wa_url = f"https://wa.me/9647510853103?text={encoded_msg}"
    
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25d366; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-size:18px; font-weight:bold;">📲 إرسال الجرد كاملاً عبر الواتساب</button></a>', unsafe_allow_html=True)

    # 2. تجهيز الطباعة (حل مشكلة اللغة نهائياً)
    table_rows = "".join([
        f"<tr><td style='border:1px solid black; padding:8px;'>{item['السلعة']}</td><td style='border:1px solid black; padding:8px; text-align:center;'>{item['الموجود']}</td><td style='border:1px solid black; padding:8px; text-align:center;'>{item['التوصية']}</td><td style='border:1px solid black; padding:8px;'>{item['الملاحظة']}</td></tr>"
        for item in report_items if item['الموجود'] > 0 or item['التوصية'] > 0
    ])

    final_print_html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"></head>
    <body style="font-family:Arial; direction:rtl; text-align:right; padding:20px;">
        <div style="border:2px solid black; padding:15px; text-align:center;">
            <h1>مخابز باب الآغا 🥖</h1>
            <p>التاريخ: {datetime.date.today()} | الوقت: {current_time}</p>
            <p>المسؤول: أيوب هاني</p>
            <hr>
            <table style="width:100%; border-collapse:collapse;">
                <thead><tr style="background:#eee;"><th>السلعة</th><th>موجود</th><th>طلب</th><th>ملاحظة</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    import base64
    b64_print = base64.b64encode(final_print_html.encode('utf-8')).decode()
    print_href = f"data:text/html;charset=utf-8;base64,{b64_print}"
    
    st.markdown(f'<a href="{print_href}" target="_blank"><button style="width:100%; background:#1e3a8a; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; margin-top:10px;">🖨️ فتح نسخة الطباعة (A4)</button></a>', unsafe_allow_html=True)

    if st.button("❌ إنهاء العملية"):
        del st.session_state.report_ready
        st.rerun()
