import streamlit as st
import pandas as pd
import datetime
import os
import urllib.parse

# --- 1. إعدادات المظهر ---
st.set_page_config(page_title="جرد قسم التوست - باب الآغا", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .report-card { background: white; padding: 20px; border: 2px solid #1e3a8a; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات ---
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

# --- 3. القائمة الجانبية ---
menu = st.sidebar.radio("القائمة:", ["📋 الجرد والتوصية", "🛒 الوصايا الإضافية", "⚙️ إدارة الأصناف"])

# --- 4. صفحة الجرد والتوصية ---
if menu == "📋 الجرد والتوصية":
    st.markdown("<div class='main-header'><h1>🥖 جرد قسم التوست - باب الآغا</h1><p>المسؤول: أيوب هاني</p></div>", unsafe_allow_html=True)
    
    inventory_results = []
    st.subheader("📝 الجرد الفعلي والتوصيات:")
    
    for i, row in df_items.iterrows():
        c1, c2 = st.columns([2, 1])
        with c1:
            qty = st.number_input(f"{row['السلعة']}", min_value=0, key=f"inv_{i}")
        with c2:
            rec = st.number_input("العدد المطلوب", min_value=0, key=f"rec_{i}")
        
        status = "🔴 نقص" if qty <= row['رقم الأمان'] else "🟢 متوفر"
        inventory_results.append({"الاسم": row['السلعة'], "موجود": qty, "حالة": status, "طلب": rec})

    if st.button("📊 إنشاء رسالة التقرير للواتساب"):
        # بناء نص الرسالة بشكل مرتب جداً
        msg = f"📋 *تقرير جرد قسم التوست - باب الآغا*\n"
        msg += f"📅 *التاريخ:* {datetime.date.today()}\n"
        msg += f"👤 *المسؤول:* أيوب هاني\n"
        msg += f"━━━━━━━━━━━━━━━\n"
        
        has_low_stock = False
        for item in inventory_results:
            if item['طلب'] > 0 or item['حالة'] == "🔴 نقص":
                msg += f"🔹 *{item['الاسم']}*:\n   - الموجود: {item['موجود']} | {item['حالة']}\n"
                if item['طلب'] > 0:
                    msg += f"   - 📥 *التوصية بطلب: {item['طلب']}*\n"
                msg += f"-----------"
                has_low_stock = True
        
        if not has_low_stock:
            msg += "\n✅ جميع السلع متوفرة ولا يوجد طلبات."
            
        if not df_orders.empty:
            msg += f"\n\n🛒 *وصايا وطلبيات إضافية:*\n"
            for _, r in df_orders.iterrows():
                msg += f"• {r['الطلب']}: {r['التفاصيل']}\n"
        
        msg += f"\n━━━━━━━━━━━━━━━\nحقوق النظام محفوظة لـ أيوب هاني ©"
        
        # تخزين الرسالة في الجلسة لعرضها
        st.session_state.wa_msg = msg
        st.success("تم تجهيز التقرير بنجاح!")

    if 'wa_msg' in st.session_state:
        st.markdown("### 📄 معاينة الرسالة قبل الإرسال:")
        st.code(st.session_state.wa_msg)
        
        # رابط الواتساب المباشر
        encoded_msg = urllib.parse.quote(st.session_state.wa_msg)
        wa_url = f"https://wa.me/9647510853103?text={encoded_msg}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank">
                <button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-size:18px; font-weight:bold;">
                    📲 إرسال التقرير الآن عبر الواتساب
                </button>
            </a>
        ''', unsafe_allow_html=True)

# --- 5. بقية الصفحات (الطلبيات والإدارة) ---
elif menu == "🛒 الوصايا الإضافية":
    st.header("📌 تسجيل وصايا خارجية")
    with st.form("orders"):
        name = st.text_input("صاحب الوصية")
        detail = st.text_area("التفاصيل")
        if st.form_submit_button("حفظ"):
            pd.concat([df_orders, pd.DataFrame([[name, detail]], columns=df_orders.columns)]).to_csv(ORDERS_FILE, index=False)
            st.rerun()
    for i, r in df_orders.iterrows():
        st.info(f"{r['الطلب']}: {r['التفاصيل']}")
        if st.button(f"حذف {i}"):
            df_orders.drop(i).to_csv(ORDERS_FILE, index=False)
            st.rerun()

elif menu == "⚙️ إدارة الأصناف":
    st.header("⚙️ إضافة أو حذف سلع")
    with st.form("add"):
        n = st.text_input("اسم السلعة")
        l = st.number_input("حد الأمان", value=50)
        if st.form_submit_button("إضافة"):
            pd.concat([df_items, pd.DataFrame([[n, l]], columns=df_items.columns)]).to_csv(DB_FILE, index=False)
            st.rerun()
    for i, r in df_items.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"{r['السلعة']} ({r['رقم الأمان']})")
        if c2.button("حذف", key=f"d_{i}"):
            df_items.drop(i).to_csv(DB_FILE, index=False)
            st.rerun()
