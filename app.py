import streamlit as st
import pandas as pd
import datetime
import os
import urllib.parse
import base64

# --- 1. إعدادات المظهر واللغة ---
st.set_page_config(page_title="نظام جرد باب الآغا - أيوب هاني", layout="wide")

# تخصيص الخطوط والتنسيق ليدعم العربية بشكل مثالي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #1e3a8a; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والذاكرة (Session State) ---
# هذه الوظيفة تضمن أن الأرقام لا تختفي عند التنقل بين الأقسام
def init_data():
    if 'items_list' not in st.session_state:
        # القائمة التي أرسلتها مع حدود الأمان
        initial_data = [
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
        st.session_state.items_list = pd.DataFrame(initial_data, columns=["السلعة", "رقم الأمان"])
    
    if 'orders_list' not in st.session_state:
        st.session_state.orders_list = pd.DataFrame(columns=["الطلب", "التفاصيل"])
    
    # ذاكرة حفظ المدخلات اللحظية
    if 'inv_vals' not in st.session_state: st.session_state.inv_vals = {}
    if 'rec_vals' not in st.session_state: st.session_state.rec_vals = {}
    if 'note_vals' not in st.session_state: st.session_state.note_vals = {}

init_data()

# --- 3. القائمة الجانبية ---
st.sidebar.title("🍞 نظام باب الآغا")
menu = st.sidebar.radio("انتقل إلى:", ["📋 الجرد الصباحي", "🛒 الطلبيات والوصايا", "⚙️ إدارة السلع"])

# --- 4. قسم الجرد الصباحي ---
if menu == "📋 الجرد الصباحي":
    st.markdown("<div class='main-header'><h1>📋 جرد قسم التوست - الشفت الصباحي</h1></div>", unsafe_allow_html=True)
    
    # توقيت العراق (UTC+3)
    iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
    iraq_time = iraq_now.strftime("%I:%M %p")
    iraq_date = iraq_now.strftime("%Y-%m-%d")

    inventory_results = []
    
    st.subheader("📝 أدخل الكميات والملاحظات:")
    for i, row in st.session_state.items_list.iterrows():
        st.markdown(f"**📦 {row['السلعة']}**")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            q = st.number_input("الموجود", min_value=0, key=f"q_{i}", value=st.session_state.inv_vals.get(i, 0))
            st.session_state.inv_vals[i] = q
        with col2:
            r = st.number_input("التوصية", min_value=0, key=f"r_{i}", value=st.session_state.rec_vals.get(i, 0))
            st.session_state.rec_vals[i] = r
        with col3:
            n = st.text_input("ملاحظة", key=f"n_{i}", value=st.session_state.note_vals.get(i, ""), placeholder="اكتب ملاحظة...")
            st.session_state.note_vals[i] = n
        
        status = "⚠️ نقص" if q <= row['رقم الأمان'] else "✅ كافٍ"
        inventory_results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n, "الحالة": status})
        st.divider()

    if st.button("🚀 اعتماد الجرد وتجهيز التقرير"):
        st.session_state.final_report = inventory_results
        st.success("تم الحفظ بنجاح! راجع التقرير في الأسفل.")

    if 'final_report' in st.session_state:
        st.divider()
        st.subheader("📄 معاينة التقرير النهائي")
        
        # بناء محتوى الجداول للطباعة والرسائل
        rows_html = ""
        wa_items_text = ""
        for item in st.session_state.final_report:
            if item['الموجود'] > 0 or item['التوصية'] > 0:
                # للطباعة
                rows_html += f"<tr><td>{item['السلعة']}</td><td>{item['الموجود']}</td><td>{item['التوصية']}</td><td>{item['الملاحظة']}</td></tr>"
                # للواتساب
                wa_items_text += f"🔹 *{item['السلعة']}*\n   - موجود: {item['الموجود']} | توصية: {item['التوصية']}\n"
                if item['الملاحظة']: wa_items_text += f"   - 📝 {item['الملاحظة']}\n"

        # بناء قالب الطباعة (حل مشكلة العربي واللغة)
        report_template = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; padding: 30px; border: 3px solid black; background: white; color: black;">
            <center>
                <h1>مخابز باب الآغا 🥖</h1>
                <h2>تقرير جرد الشفت الصباحي</h2>
            </center>
            <p><b>التاريخ:</b> {iraq_date} | <b>الوقت:</b> {iraq_time}</p>
            <p><b>المسؤول:</b> أيوب هاني</p>
            <hr>
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background: #f2f2f2;">
                    <th>اسم السلعة</th><th>الموجود</th><th>التوصية</th><th>الملاحظة</th>
                </tr>
                {rows_html}
            </table>
            <br>
            <h3>🛒 وصايا وطلبيات إضافية:</h3>
            {"".join([f"<li>{r['الطلب']}: {r['التفاصيل']}</li>" for _, r in st.session_state.orders_list.iterrows()]) if not st.session_state.orders_list.empty else "لا يوجد"}
            <br><br>
            <table style="width:100%; border:none;">
                <tr>
                    <td style="border:none;">توقيع كابتن الصالة: ...................</td>
                    <td style="border:none; text-align:left;">توقيع مسؤول القسم (أيوب هاني): ...................</td>
                </tr>
            </table>
        </div>
        """
        st.markdown(report_template, unsafe_allow_html=True)

        # زر الواتساب (إرسال التقرير كامل)
        wa_header = f"📋 *تقرير جرد باب الآغا - قسم التوست*\n📅 {iraq_date} | 🕒 {iraq_time}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━━━\n"
        wa_footer = "\n━━━━━━━━━━━━━━\nتم الجرد بواسطة نظام أيوب هاني"
        full_wa_msg = wa_header + wa_items_text + wa_footer
        
        wa_url = f"https://wa.me/9647510853103?text={urllib.parse.quote(full_wa_msg)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25d366; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-weight:bold;">📲 إرسال الجرد كاملاً عبر الواتساب</button></a>', unsafe_allow_html=True)

        # تحويل المحتوى إلى Base64 مع إضافة تعريف اللغة العربية UTF-8
b64 = base64.b64encode(report_template.encode('utf-8')).decode()

# السطر المهم جداً لحل مشكلة الرموز الغريبة:
href = f"data:text/html;charset=utf-8;base64,{b64}"

# عرض الزر
st.markdown(f'<a href="{href}" target="_blank"><button style="width:100%; background:#1e3a8a; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; margin-top:10px; font-weight:bold; font-size:16px;">🖨️ فتح نسخة الطباعة (A4)</button></a>', unsafe_allow_html=True)


# --- 5. قسم الطلبيات والوصايا ---
elif menu == "🛒 الطلبيات والوصايا":
    st.header("📌 تسجيل وصايا وطلبيات الزبائن")
    with st.form("orders_form", clear_on_submit=True):
        o_title = st.text_input("اسم الطلب")
        o_desc = st.text_area("تفاصيل الوصية")
        if st.form_submit_button("حفظ"):
            new_o = pd.DataFrame([{"الطلب": o_title, "التفاصيل": o_desc}])
            st.session_state.orders_list = pd.concat([st.session_state.orders_list, new_o], ignore_index=True)
            st.success("تم الحفظ")
            st.rerun()

    st.subheader("📋 الوصايا المسجلة:")
    for i, row in st.session_state.orders_list.iterrows():
        st.info(f"**{row['الطلب']}**: {row['التفاصيل']}")
        if st.button(f"حذف الوصية {i}", key=f"del_o_{i}"):
            st.session_state.orders_list = st.session_state.orders_list.drop(i).reset_index(drop=True)
            st.rerun()

# --- 6. قسم إدارة السلع ---
elif menu == "⚙️ إدارة السلع":
    st.header("⚙️ تعديل قائمة الأصناف")
    with st.expander("➕ إضافة صنف جديد"):
        n_name = st.text_input("اسم الصنف")
        n_safe = st.number_input("حد الأمان", min_value=1, value=50)
        if st.button("إضافة"):
            new_item = pd.DataFrame([{"السلعة": n_name, "رقم الأمان": n_safe}])
            st.session_state.items_list = pd.concat([st.session_state.items_list, new_item], ignore_index=True)
            st.rerun()

    st.subheader("🗑️ حذف صنف من القائمة")
    for i, row in st.session_state.items_list.iterrows():
        col1, col2 = st.columns([4, 1])
        col1.write(f"{row['السلعة']} (حد الأمان: {row['رقم الأمان']})")
        if col2.button("حذف", key=f"del_{i}"):
            st.session_state.items_list = st.session_state.items_list.drop(i).reset_index(drop=True)
            st.rerun()

st.markdown("<div style='text-align:center; color:gray; margin-top:50px;'>نظام جرد باب الآغا - تطوير وإدارة: أيوب هاني © 2026</div>", unsafe_allow_html=True)
