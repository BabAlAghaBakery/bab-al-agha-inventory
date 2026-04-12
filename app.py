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

# --- 4. صفحة الجرد الصباحي (الأساسية) ---
if menu == "📋 الجرد الصباحي":
    st.markdown("<div class='main-header'><h1>📋 جرد قسم التوست - الشفت الصباحي</h1></div>", unsafe_allow_html=True)
    
    st.subheader("📝 أدخل الكميات المتوفرة على الرفوف:")
    inventory_data = []
    recommendations = {} # لتخزين الكميات المطلوب توصيتها
    
    # تقسيم السلع إلى أعمدة لتسهيل الإدخال من الموبايل
    for i, row in df_items.iterrows():
        col1, col2 = st.columns([2, 1])
        with col1:
            qty = st.number_input(f"{row['السلعة']} (الأمان: {row['رقم الأمان']})", min_value=0, key=f"item_{i}", step=1)
        with col2:
            # فقرة توصية السلعة (الأعداد التي تريد طلبها)
            rec_qty = st.number_input("توصية بالطلب", min_value=0, key=f"rec_{i}", step=1)
        
        status = "⚠️ نقص" if qty <= row['رقم الأمان'] else "✅ كافٍ"
        inventory_data.append({"السلعة": row['السلعة'], "الموجود": qty, "الحالة": status, "التوصية": rec_qty})

    if st.button("📄 توليد تقرير A4 النهائي"):
        st.session_state.report_ready = inventory_data
        st.rerun()

    # عرض ورقة الـ A4
    if 'report_ready' in st.session_state:
        st.divider()
        report_html = f"""
        <div id="printable_area" class="print-paper">
            <h1 style="text-align:center; margin:0;">مخابز باب الآغا 🥖</h1>
            <h2 style="text-align:center; margin:5px;">جرد قسم التوست</h2>
            <p style="text-align:center;"><b>الشفت الصباحي | التاريخ: {datetime.date.today()}</b></p>
            <hr>
            <table style="width:100%; border-collapse: collapse; text-align: right;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid black; padding: 8px;">اسم السلعة</th>
                    <th style="border: 1px solid black; padding: 8px;">الكمية الموجودة</th>
                    <th style="border: 1px solid black; padding: 8px;">الحالة</th>
                    <th style="border: 1px solid black; padding: 8px;">الكمية المطلوبة (التوصية)</th>
                </tr>
                {"".join([f"<tr><td style='border: 1px solid black; padding: 8px;'>{item['السلعة']}</td><td style='border: 1px solid black; padding: 8px;'>{item['الموجود']}</td><td style='border: 1px solid black; padding: 8px; color:{'red' if item['الحالة']=='⚠️ نقص' else 'black'}; font-weight:bold;'>{item['الحالة']}</td><td style='border: 1px solid black; padding: 8px; font-weight:bold;'>{item['التوصية'] if item['التوصية'] > 0 else '-'}</td></tr>" for item in st.session_state.report_ready])}
            </table>
            <br>
            <h4>📋 الطلبيات والوصايا الإضافية:</h4>
            <ul>
                {"".join([f"<li><b>{r['الطلب']}:</b> {r['التفاصيل']}</li>" for _, r in df_orders.iterrows()]) if not df_orders.empty else "<li>لا توجد وصايا إضافية</li>"}
            </ul>
            <br><br>
            <div style="display: flex; justify-content: space-between;">
                <p><b>إدارة مخابز باب الآغا</b></p>
                <div style="text-align: left;">
                    <p><b>توقيع مسؤول القسم:</b></p>
                    <p>أيوب هاني</p>
                </div>
            </div>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)
        
        # أزرار الإجراءات
        st.button("🖨️ طباعة التقرير (A4)", on_click=lambda: st.write('<script>window.print()</script>', unsafe_allow_html=True))
        
        # رابط الواتساب
        wa_msg = f"تقرير جرد باب الآغا - قسم التوست\nالمسؤول: أيوب هاني\nالتاريخ: {datetime.date.today()}\nلقد تم إكمال الجرد بنجاح."
        wa_url = f"https://wa.me/9647510853103?text={urllib.parse.quote(wa_msg)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-weight:bold;">📲 إرسال إشعار عبر الواتساب</button></a>', unsafe_allow_html=True)

# --- 5. صفحة الطلبيات والوصايا ---
elif menu == "🛒 الطلبيات والوصايا":
    st.header("📌 تسجيل الطلبيات لضمان عدم النسيان")
    with st.form("new_order"):
        o_name = st.text_input("اسم صاحب الطلبية أو الجهة")
        o_text = st.text_area("تفاصيل الوصية (مثلاً: محتاجين 50 كيس توست إضافي)")
        if st.form_submit_button("حفظ الوصية"):
            new_row = pd.DataFrame([[o_name, o_text]], columns=df_orders.columns)
            pd.concat([df_orders, new_row]).to_csv(ORDERS_FILE, index=False)
            st.rerun()
    
    st.subheader("📋 الوصايا الحالية:")
    for i, row in df_orders.iterrows():
        st.warning(f"🔔 {row['الطلب']}: {row['التفاصيل']}")
        if st.button(f"✅ تم الإنجاز - حذف", key=f"done_{i}"):
            df_orders.drop(i).to_csv(ORDERS_FILE, index=False)
            st.rerun()

# --- 6. صفحة إدارة السلع ---
elif menu == "⚙️ إدارة السلع":
    st.header("⚙️ تعديل قائمة السلع (إضافة أو حذف)")
    with st.form("add_item"):
        n_name = st.text_input("اسم السلعة الجديدة")
        n_limit = st.number_input("حد الأمان", min_value=1, value=50)
        if st.form_submit_button("➕ إضافة"):
            new_item = pd.DataFrame([[n_name, n_limit]], columns=df_items.columns)
            pd.concat([df_items, new_item]).to_csv(DB_FILE, index=False)
            st.rerun()
    
    st.subheader("🗑️ حذف سلعة من القائمة:")
    for i, row in df_items.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"{row['السلعة']} (حد الأمان: {row['رقم الأمان']})")
        if c2.button("حذف", key=f"del_item_{i}"):
            df_items.drop(i).to_csv(DB_FILE, index=False)
            st.rerun()

# --- الحقوق في الأسفل ---
st.markdown("<div class='footer-rights'>حقوق النظام محفوظة لـ مسؤول القسم: أيوب هاني © 2026</div>", unsafe_allow_html=
            # --- كود المحرك الاحترافي للطباعة (يُوضع في نهاية الملف) ---

import base64

def get_print_html(content_html):
    """تحويل المحتوى إلى رابط صفحة مستقلة لتجاوز حظر المتصفح"""
    full_html = f"<html><body style='direction:rtl; font-family:sans-serif; padding:20px;'>{content_html}</body></html>"
    b64 = base64.b64encode(full_html.encode()).decode()
    return f"data:text/html;base64,{b64}"

if 'report_ready' in st.session_state:
    st.markdown("---")
    st.subheader("🖨️ بوابة الطباعة النهائية")
    
    # بناء جدول البيانات بدقة لمنع دمج النصوص
    report_items = st.session_state.report_ready
    table_rows = "".join([
        f"<tr>"
        f"<td style='border:1px solid black; padding:8px;'>{item['السلعة']}</td>"
        f"<td style='border:1px solid black; padding:8px; text-align:center;'>{item['الموجود']}</td>"
        f"<td style='border:1px solid black; padding:8px; text-align:center;'>{item['التوصية'] if item['التوصية'] > 0 else '-'}</td>"
        f"</tr>" 
        for item in report_items
    ])
    
    final_content = f"""
    <div style="text-align:center; border:2px solid black; padding:20px;">
        <h1>مخابز باب الآغا</h1>
        <h3>جرد قسم التوست - الشفت الصباحي</h3>
        <p>التاريخ: {datetime.date.today()}</p>
        <table style="width:100%; border-collapse:collapse; direction:rtl;">
            <thead>
                <tr style="background:#eee;">
                    <th style="border:1px solid black; padding:8px;">السلعة</th>
                    <th style="border:1px solid black; padding:8px;">الموجود</th>
                    <th style="border:1px solid black; padding:8px;">التوصية</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
        <br><br>
        <div style="text-align:left; margin-left:20px;">
            <p>توقيع مسؤول القسم:</p>
            <p><b>أيوب هاني</b></p>
        </div>
    </div>
    """

    # إنشاء رابط الصفحة المستقلة
    href = get_print_html(final_content)
    
    st.markdown(f"""
        <div style="background:#f0f2f6; padding:20px; border-radius:15px; text-align:center;">
            <p>بسبب قيود الموبايل، يرجى الضغط على الرابط أدناه لفتح التقرير في صفحة مستقلة، ثم اختر 'طباعة' من قائمة المتصفح:</p>
            <a href="{href}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; background:#1e3a8a; color:white; padding:15px; border-radius:10px; font-size:18px; font-weight:bold; cursor:pointer; border:none;">
                    🔗 افتح التقرير للطباعة (نسخة الموبايل)
                </button>
            </a>
        </div>
    """, unsafe_allow_html=True)

    if st.button("✅ إنهاء الجرد"):
        del st.session_state.report_ready
        st.rerun()
