import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# --- إعدادات الصفحة واللغة ---
st.set_page_config(page_title="نظام باب الآغا - أيوب هاني", layout="wide")

# 1. قائمة السلع الخاصة بك مع حدود الأمان (التي زودتني بها سابقاً)
if 'df_items' not in st.session_state:
    data = {
        "السلعة": ["توست أبيض", "توست أسمر", "توست حبوب", "توست عائلي", "صمون فرنسي", "جرك سادة", "جرك محشي"],
        "رقم الأمان": [20, 15, 10, 25, 50, 30, 20]
    }
    st.session_state.df_items = pd.DataFrame(data)

if 'df_orders' not in st.session_state:
    st.session_state.df_orders = pd.DataFrame(columns=["الطلب", "التفاصيل"])

# --- القائمة الجانبية ---
menu = st.sidebar.selectbox("القائمة", ["📋 الجرد الصباحي", "🛒 الطلبيات والوصايا", "⚙️ إدارة القائمة"])

# --- إدارة القائمة (إضافة وحذف سلع) ---
if menu == "⚙️ إدارة القائمة":
    st.header("⚙️ تعديل قائمة السلع")
    with st.form("add_item"):
        n_item = st.text_input("اسم السلعة الجديدة")
        s_limit = st.number_input("حد الأمان", min_value=0, value=10)
        if st.form_submit_button("إضافة للقمة"):
            new_row = pd.DataFrame([{"السلعة": n_item, "رقم الأمان": s_limit}])
            st.session_state.df_items = pd.concat([st.session_state.df_items, new_row], ignore_index=True)
            st.rerun()
    st.table(st.session_state.df_items)

# --- قسم الطلبيات والوصايا ---
elif menu == "🛒 الطلبيات والوصايا":
    st.header("📌 تسجيل الوصايا والطلبيات")
    with st.form("orders"):
        o_name = st.text_input("اسم الطلب")
        o_desc = st.text_area("تفاصيل الوصية")
        if st.form_submit_button("حفظ الوصية"):
            new_o = pd.DataFrame([{"الطلب": o_name, "التفاصيل": o_desc}])
            st.session_state.df_orders = pd.concat([st.session_state.df_orders, new_o], ignore_index=True)
            st.rerun()
    st.table(st.session_state.df_orders)
    if st.button("🗑️ مسح الكل"):
        st.session_state.df_orders = pd.DataFrame(columns=["الطلب", "التفاصيل"])
        st.rerun()

# --- قسم الجرد والطباعة (الأهم) ---
elif menu == "📋 الجرد الصباحي":
    st.header("🥖 جرد قسم التوست - المسؤول: أيوب هاني")
    
    # ضبط وقت العراق (GMT+3)
    iraq_time = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%I:%M %p")
    today = datetime.date.today()

    inventory_results = []
    for i, row in st.session_state.df_items.iterrows():
        st.markdown(f"**{row['السلعة']}**")
        c1, c2, c3 = st.columns([1,1,2])
        qty = c1.number_input("الموجود", min_value=0, key=f"q_{i}")
        rec = c2.number_input("التوصية", min_value=0, key=f"r_{i}")
        note = c3.text_input("ملاحظة", key=f"n_{i}")
        inventory_results.append({"السلعة": row['السلعة'], "الموجود": qty, "التوصية": rec, "الملاحظة": note})

    if st.button("✅ اعتماد الجرد وإظهار التقرير"):
        st.session_state.active_report = inventory_results
        st.success("تم تجهيز التقرير! انزل للأسفل للمعاينة والطباعة.")

    if 'active_report' in st.session_state:
        st.divider()
        st.subheader("📄 معاينة التقرير النهائي")
        
        # بناء التقرير للطباعة (حل مشكلة اللغة)
        rows_html = "".join([f"<tr><td>{x['السلعة']}</td><td>{x['الموجود']}</td><td>{x['التوصية']}</td><td>{x['الملاحظة']}</td></tr>" for x in st.session_state.active_report if x['الموجود'] > 0 or x['التوصية'] > 0])
        
        orders_html = ""
        if not st.session_state.df_orders.empty:
            orders_html = "<h3>🛒 الوصايا الإضافية:</h3><ul>" + "".join([f"<li>{r['الطلب']}: {r['التفاصيل']}</li>" for _, r in st.session_state.df_orders.iterrows()]) + "</ul>"

        final_html = f"""
        <div dir="rtl" style="font-family: Arial; padding: 20px; border: 3px solid black; background: white; color: black;">
            <center><h1>مخابز باب الآغا 🥖</h1><h2>تقرير جرد قسم التوست</h2></center>
            <p><b>التاريخ:</b> {today} | <b>الوقت:</b> {iraq_time}</p>
            <hr>
            {orders_html}
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background: #f2f2f2;"><th>السلعة</th><th>الموجود</th><th>التوصية</th><th>الملاحظة</th></tr>
                {rows_html}
            </table>
            <br><br>
            <table style="width:100%; border:none;">
                <tr>
                    <td style="border:none;">توقيع كابتن الصالة: ________</td>
                    <td style="border:none;">توقيع مسؤول القسم (أيوب هاني): ________</td>
                </tr>
            </table>
        </div>
        """
        
        # عرض المعاينة داخل التطبيق
        st.markdown(final_html, unsafe_allow_html=True)

        # زر الواتساب
        wa_msg = f"📋 تقرير جرد باب الآغا\nالمسؤول: أيوب هاني\nالوقت: {iraq_time}\n"
        wa_url = f"https://wa.me/9647510853103?text={urllib.parse.quote(wa_msg + ' (راجع رابط الطباعة للملحقات)')}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25d366; color:white; padding:12px; border:none; border-radius:8px; cursor:pointer;">📲 إرسال تنبيه عبر الواتساب</button></a>', unsafe_allow_html=True)

        # زر الطباعة (حل مشكلة اللغة النهائي)
        b64 = base64.b64encode(final_html.encode('utf-8')).decode()
        st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button style="width:100%; background:#1e3a8a; color:white; padding:12px; border:none; border-radius:8px; cursor:pointer; margin-top:10px;">🖨️ فتح نسخة الطباعة (العربية جاهزة)</button></a>', unsafe_allow_html=True)
