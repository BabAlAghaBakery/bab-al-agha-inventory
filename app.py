import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# --- 1. إعدادات الصفحة والمظهر الاحترافي ---
st.set_page_config(page_title="نظام باب الآغا - أيوب هاني", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1e3a8a; color: white; font-weight: bold; padding: 12px; border: none; }
    .stButton>button:hover { background-color: #2563eb; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الذاكرة (Session State) لضمان عدم حدوث أخطاء ---
if 'items_df' not in st.session_state:
    # القائمة الأساسية الافتراضية
    initial_data = [
        ["باكيت تركي", 50], ["جرك بالحليب", 100], ["توست ابيض", 130],
        ["توست اسمر ساده", 80], ["سميط شعير", 60], ["كرواسون ابيض", 800]
    ]
    st.session_state.items_df = pd.DataFrame(initial_data, columns=["السلعة", "رقم الأمان"])

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])

# دوال مساعدة لحفظ مدخلات الجرد مؤقتاً
if 'tmp_inventory' not in st.session_state: st.session_state.tmp_inventory = {}
if 'tmp_recommend' not in st.session_state: st.session_state.tmp_recommend = {}
if 'tmp_notes' not in st.session_state: st.session_state.tmp_notes = {}

# --- 3. القائمة الجانبية للتنقل (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🍞 لوحة التحكم</h2>", unsafe_allow_html=True)
    menu = st.radio("انتقل إلى القسم:", ["📋 الجرد والطباعة", "🛒 إدارة الطلبيات", "🛠️ إعدادات السلع"])
    st.divider()
    st.info(f"المسؤول: أيوب هاني")

# توقيت العراق (UTC+3)
iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
iraq_date = iraq_now.strftime("%Y-%m-%d")
iraq_time = iraq_now.strftime("%I:%M %p")

# --- 4. الأقسام الرئيسية للنظام ---

# --- القسم الأول: الجرد والطباعة ---
if menu == "📋 الجرد والطباعة":
    st.markdown("<div class='main-header'><h1>📋 جرد قسم التوست والحلويات</h1></div>", unsafe_allow_html=True)
    st.write(f"📅 التاريخ: **{iraq_date}** | 🕒 الوقت: **{iraq_time}**")

    # استخدام Form لمنع تعليق الكيبورد في الموبايل
    with st.form("inventory_master_form"):
        st.subheader("📝 أدخل بيانات الجرد:")
        
        # رأس الجدول
        h1, h2, h3, h4 = st.columns([2, 1, 1, 2])
        h1.markdown("**اسم السلعة**")
        h2.markdown("**الموجود**")
        h3.markdown("**التوصية**")
        h4.markdown("**الملاحظة**")
        st.divider()

        current_inventory = []
        for i, row in st.session_state.items_df.iterrows():
            c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
            with c1: st.markdown(f"**{row['السلعة']}**")
            with c2: 
                q = st.number_input("م", min_value=0, key=f"q_{i}", value=st.session_state.tmp_inventory.get(i, 0), label_visibility="collapsed")
                st.session_state.tmp_inventory[i] = q
            with c3: 
                r = st.number_input("ت", min_value=0, key=f"r_{i}", value=st.session_state.tmp_recommend.get(i, 0), label_visibility="collapsed")
                st.session_state.tmp_recommend[i] = r
            with c4: 
                n = st.text_input("ن", key=f"n_{i}", value=st.session_state.tmp_notes.get(i, ""), placeholder="ملاحظة..", label_visibility="collapsed")
                st.session_state.tmp_notes[i] = n
            
            current_inventory.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})
        
        submit_btn = st.form_submit_button("🚀 اعتماد الجرد وتوليد التقرير")

    if submit_btn:
        st.session_state.final_report_data = current_inventory
        st.success("✅ تم حفظ الجرد بنجاح!")

    # عرض التقرير النهائي للطباعة والواتساب
    if 'final_report_data' in st.session_state:
        st.divider()
        st.subheader("📄 معاينة التقرير النهائي")
        
        rows_html = ""
        wa_msg = f"📋 *تقرير جرد باب الآغا*\n📅 {iraq_date} | {iraq_time}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━\n"
        
        for item in st.session_state.final_report_data:
            if item['الموجود'] > 0 or item['التوصية'] > 0:
                rows_html += f"<tr><td>{item['السلعة']}</td><td>{item['الموجود']}</td><td>{item['التوصية']}</td><td>{item['الملاحظة']}</td></tr>"
                wa_msg += f"🔹 *{item['السلعة']}*\n   الموجود: {item['الموجود']} | التوصية: {item['التوصية']}\n"

        # إضافة الوصايا للتقرير
        orders_html = ""
        if not st.session_state.orders_df.empty:
            wa_msg += "\n🛒 *الوصايا الإضافية:*\n"
            orders_html = "<h3>🛒 الطلبيات والوصايا الإضافية:</h3><ul>"
            for _, row in st.session_state.orders_df.iterrows():
                orders_html += f"<li><b>{row['الطلب']}:</b> {row['التفاصيل']}</li>"
                wa_msg += f"• {row['الطلب']}: {row['التفاصيل']}\n"
            orders_html += "</ul>"

        full_report_html = f"""
        <div dir="rtl" style="font-family: Arial; padding: 25px; border: 3px solid #1e3a8a; background: white; color: black;">
            <center><h1 style="color:#1e3a8a;">مخابز باب الآغا 🥖</h1><h2>تقرير جرد القسم</h2></center>
            <p><b>التاريخ:</b> {iraq_date} | <b>الوقت:</b> {iraq_time} | <b>المسؤول:</b> أيوب هاني</p>
            <hr>
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background: #eee;"><th>السلعة</th><th>الموجود</th><th>التوصية</th><th>الملاحظة</th></tr>
                {rows_html}
            </table>
            {orders_html}
            <br><br>
            <div style="display: flex; justify-content: space-between;">
                <span>توقيع كابتن الصالة: .............</span>
                <span>توقيع المسؤول (أيوب هاني): .............</span>
            </div>
        </div>
        """
        st.markdown(full_report_html, unsafe_allow_html=True)

        # أزرار الإجراءات
        col_wa, col_pr = st.columns(2)
        with col_wa:
            encoded_wa = urllib.parse.quote(wa_msg + "\nتم بواسطة نظام أيوب الذكي")
            st.markdown(f'<a href="https://wa.me/9647510853103?text={encoded_wa}" target="_blank"><button style="background:#25d366;">📲 إرسال للواتساب</button></a>', unsafe_allow_html=True)
        with col_pr:
            b64 = base64.b64encode(full_report_html.encode('utf-8')).decode()
            st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button>🖨️ فتح نسخة الطباعة (A4)</button></a>', unsafe_allow_html=True)

# --- القسم الثاني: إدارة الطلبيات ---
elif menu == "🛒 إدارة الطلبيات":
    st.header("🛒 سجل الطلبيات والوصايا")
    with st.form("add_order_form", clear_on_submit=True):
        o_name = st.text_input("اسم صاحب الطلب")
        o_desc = st.text_area("تفاصيل الوصية")
        if st.form_submit_button("حفظ الطلبية"):
            new_o = pd.DataFrame([{"الطلب": o_name, "التفاصيل": o_desc}])
            st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_o], ignore_index=True)
            st.success("تم الحفظ!")
            st.rerun()

    st.subheader("📋 القائمة الحالية:")
    st.dataframe(st.session_state.orders_df, use_container_width=True)
    if st.button("🗑️ مسح جميع الطلبيات"):
        st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])
        st.rerun()

# --- القسم الثالث: إعدادات السلع ---
elif menu == "🛠️ إعدادات السلع":
    st.header("🛠️ التحكم في قائمة المنتجات")
    c_add, c_del = st.columns(2)
    
    with c_add:
        st.subheader("➕ إضافة صنف جديد")
        new_i = st.text_input("اسم المنتج")
        new_s = st.number_input("حد الأمان", value=50)
        if st.button("إضافة الآن"):
            if new_i:
                new_entry = pd.DataFrame([{"السلعة": new_i, "رقم الأمان": new_s}])
                st.session_state.items_df = pd.concat([st.session_state.items_df, new_entry], ignore_index=True)
                st.success(f"تمت إضافة {new_i}")
                st.rerun()
            else: st.error("يرجى كتابة اسم المنتج")

    with c_del:
        st.subheader("🗑️ حذف صنف")
        if not st.session_state.items_df.empty:
            to_del = st.selectbox("اختر الصنف المراد حذفه:", st.session_state.items_df["السلعة"])
            if st.button("تأكيد الحذف"):
                st.session_state.items_df = st.session_state.items_df[st.session_state.items_df["السلعة"] != to_del]
                st.rerun()
