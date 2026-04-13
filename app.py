import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام جرد باب الآغا", layout="wide")

# ملفات تخزين البيانات
ITEMS_FILE = "bakery_items.csv"
ORDERS_FILE = "special_orders.csv"

# وظيفة لتحميل البيانات أو إنشائها
def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

# تحميل البيانات الأساسية
df_items = load_data(ITEMS_FILE, ["السلعة", "رقم الأمان"])
df_orders = load_data(ORDERS_FILE, ["الطلب", "التفاصيل"])

# --- القائمة الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1047/1047330.png", width=100)
    st.title("القائمة الرئيسية")
    menu = st.selectbox("اختر القسم:", ["📋 الجرد الصباحي", "🛒 الطلبيات والوصايا", "⚙️ إدارة السلع"])

# --- 1. قسم إدارة السلع (إضافة وحذف) ---
if menu == "⚙️ إدارة السلع":
    st.header("⚙️ إدارة قائمة السلع")
    
    # إضافة سلعة
    with st.expander("➕ إضافة سلعة جديدة"):
        new_item = st.text_input("اسم السلعة")
        safety_limit = st.number_input("حد الأمان (تنبيه النقص)", min_value=0, value=10)
        if st.button("إضافة"):
            if new_item:
                new_row = pd.DataFrame([{"السلعة": new_item, "رقم الأمان": safety_limit}])
                df_items = pd.concat([df_items, new_row], ignore_index=True)
                df_items.to_csv(ITEMS_FILE, index=False)
                st.success(f"تمت إضافة {new_item}")
                st.rerun()

    # عرض وحذف السلع
    st.subheader("📦 السلع المسجلة حالياً")
    if not df_items.empty:
        for i, row in df_items.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.write(f"**{row['السلعة']}** (حد الأمان: {row['رقم الأمان']})")
            if col2.button("حذف", key=f"del_{i}"):
                df_items = df_items.drop(i)
                df_items.to_csv(ITEMS_FILE, index=False)
                st.rerun()
    else:
        st.info("القائمة فارغة، أضف سلعاً للبدء.")

# --- 2. قسم الطلبيات والوصايا ---
elif menu == "🛒 الطلبيات والوصايا":
    st.header("📝 تسجيل الطلبيات والوصايا")
    with st.form("order_form"):
        order_name = st.text_input("اسم الطلب/الزبون")
        order_details = st.text_area("التفاصيل (مثلاً: بدون سمسم، توصيل ساعة 4)")
        if st.form_submit_button("حفظ الوصية"):
            new_order = pd.DataFrame([{"الطلب": order_name, "التفاصيل": order_details}])
            df_orders = pd.concat([df_orders, new_order], ignore_index=True)
            df_orders.to_csv(ORDERS_FILE, index=False)
            st.success("تم حفظ الوصية")
            st.rerun()
    
    st.subheader("📋 الوصايا الحالية")
    if not df_orders.empty:
        st.table(df_orders)
        if st.button("🗑️ مسح جميع الوصايا"):
            df_orders = pd.DataFrame(columns=["الطلب", "التفاصيل"])
            df_orders.to_csv(ORDERS_FILE, index=False)
            st.rerun()

# --- 3. قسم الجرد والطباعة والواتساب ---
elif menu == "📋 الجرد الصباحي":
    st.header("📋 جرد قسم التوست")
    
    # توقيت العراق (UTC+3)
    iraq_time = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%I:%M %p")
    today_date = datetime.date.today()

    inventory_data = []
    
    if df_items.empty:
        st.warning("يرجى إضافة سلع من قسم الإدارة أولاً.")
    else:
        for i, row in df_items.iterrows():
            st.markdown(f"### {row['السلعة']}")
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                qty = st.number_input("المتوفر", min_value=0, key=f"q_{i}")
            with c2:
                rec = st.number_input("التوصية", min_value=0, key=f"r_{i}")
            with c3:
                note = st.text_input("ملاحظات", key=f"n_{i}")
            
            inventory_data.append({
                "السلعة": row['السلعة'],
                "الموجود": qty,
                "التوصية": rec,
                "الملاحظة": note
            })
            st.divider()

        if st.button("🚀 اعتماد الجرد وتوليد التقرير"):
            st.session_state.final_report = inventory_data
            st.success("تم الاعتماد! انزل لخيارات الواتساب والطباعة.")

    # عرض خيارات التصدير
    if 'final_report' in st.session_state:
        report = st.session_state.final_report
        
        # --- رسالة الواتساب ---
        wa_text = f"📋 *جرد باب الآغا - قسم التوست*\n📅 {today_date} | 🕒 {iraq_time}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━\n"
        for item in report:
            if item['الموجود'] > 0 or item['التوصية'] > 0:
                wa_text += f"🔹 *{item['السلعة']}*\n   الموجود: {item['الموجود']} | الطلب: {item['التوصية']}\n"
                if item['الملاحظة']: wa_text += f"   📝 {item['الملاحظة']}\n"
        
        if not df_orders.empty:
            wa_text += "\n🛒 *وصايا إضافية:*\n"
            for _, r in df_orders.iterrows():
                wa_text += f"• {r['الطلب']}: {r['التفاصيل']}\n"
        
        wa_text += "━━━━━━━━━━━━"
        wa_url = f"https://wa.me/9647510853103?text={urllib.parse.quote(wa_text)}"
        
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25d366; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-weight:bold;">📲 إرسال التقرير للواتساب</button></a>', unsafe_allow_html=True)

        # --- الطباعة A4 ---
        rows_html = "".join([f"<tr><td>{x['السلعة']}</td><td>{x['الموجود']}</td><td>{x['التوصية']}</td><td>{x['الملاحظة']}</td></tr>" for x in report])
        
        orders_section = ""
        if not df_orders.empty:
            orders_section = "<h3>الوصايا والطلبيات:</h3><ul>" + "".join([f"<li>{r['الطلب']}: {r['التفاصيل']}</li>" for _, r in df_orders.iterrows()]) + "</ul>"

        print_html = f"""
        <div dir="rtl" style="font-family: Arial; padding: 30px; border: 2px solid black;">
            <center><h1>مخابز باب الآغا 🥖</h1><h2>تقرير جرد قسم التوست</h2></center>
            <p><b>التاريخ:</b> {today_date} | <b>الوقت:</b> {iraq_time}</p>
            <hr>
            {orders_section}
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background: #f2f2f2;"><th>السلعة</th><th>الموجود</th><th>التوصية</th><th>الملاحظات</th></tr>
                {rows_html}
            </table>
            <br><br>
            <div style="display: flex; justify-content: space-between;">
                <div>توقيع كابتن الصالة: ...................</div>
                <div>توقيع مسؤول القسم (أيوب): ...................</div>
            </div>
        </div>
        """
        
        b64 = base64.b64encode(print_html.encode('utf-8')).decode()
        st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button style="width:100%; background:#1e3a8a; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; margin-top:10px;">🖨️ طباعة التقرير (A4)</button></a>', unsafe_allow_html=True)
