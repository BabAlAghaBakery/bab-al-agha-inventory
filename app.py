import streamlit as st
import pandas as pd
import datetime

# --- 1. إعدادات المظهر العام (ذوق احترافي) ---
# جعل الصفحة عريضة لتناسب الحاسبة والموبايل
st.set_page_config(page_title="جرد قسم التوست - باب الآغا", layout="wide")

# إضافة لمسات جمالية واحترافية (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تغيير الخط وتنسيق النص للعربية */
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        text-align: right;
        direction: rtl;
    }
    
    /* تصميم رأس الصفحة المميز */
    .main-header {
        background-color: #1e3a8a; /* أزرق داكن واحترافي */
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* تنسيق معلومات الوقت والتاريخ */
    .info-bar {
        background-color: #f1f5f9;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* تنسيق زر الحفظ ليكون واضحاً وقوياً */
    .stButton>button {
        width: 100%;
        background-color: #1e3a8a;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات الأولية والذاكرة (Session State) ---
# القائمة الأساسية التي زودتني بها سابقاً (سنستخدم 5 منها كعينة)
if 'items_data' not in st.session_state:
    initial_items = [
        ["باكيت تركي", 50], ["جرك بالحليب", 100], ["توست ابيض", 130],
        ["توست اسمر ساده", 80], ["سميط شعير", 60]
    ]
    # يمكنك إضافة باقي الأصناف (لفه خميرة، كرواسون، كيك...) هنا لاحقاً
    st.session_state.items_data = pd.DataFrame(initial_items, columns=["السلعة", "رقم الأمان"])

# --- 3. حساب الوقت والتاريخ (توقيت العراق/بغداد) ---
# إضافة 3 ساعات لتوقيت الخادم العالمي
iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
iraq_date = iraq_now.strftime("%Y-%m-%d")
iraq_time = iraq_now.strftime("%I:%M %p")

# --- 4. تصميم الواجهة الرئيسية ---
# رأس الصفحة المميز
st.markdown("""
    <div class='main-header'>
        <h1>🥖 نظام جرد باب الآغا - قسم التوست</h1>
        <p>الاحترافية والذكاء في الإدارة</p>
    </div>
    """, unsafe_allow_html=True)

# بار المعلومات
st.markdown(f"""
    <div class='info-bar'>
        <span>📅 التاريخ: <b>{iraq_date}</b></span> | 
        <span>🕒 الوقت: <b>{iraq_time}</b></span> | 
        <span>👤 المسؤول: <b>أيوب هاني</b></span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 5. جدول الجرد الذكي والمنظم ---
st.subheader("📝 أدخل بيانات الجرد اليومي للمنتجات:")

# استخدام "النموذج" (Form) لمنع أي مشاكل في تعليق الكتابة على الموبايل
with st.form("inventory_main_form"):
    
    # رأس الجدول (للحاسبة) - سيتم إخفاؤه في الموبايل عبر التنسيق
    with st.container():
        cols_header = st.columns([2, 1, 1, 2])
        cols_header[0].markdown("**اسم السلعة**")
        cols_header[1].markdown("**الموجود**")
        cols_header[2].markdown("**التوصية**")
        cols_header[3].markdown("**الملاحظات**")
        st.divider()

    temp_results = []
    
    # عرض كل صف من صفوف الجرد
    for i, row in st.session_state.items_data.iterrows():
        # تقسيم السلعة إلى أعمدة متوازنة (2:1:1:2) لتناسب شاشات الحاسبة والموبايل
        col_item, col_qty, col_rec, col_note = st.columns([2, 1, 1, 2])
        
        with col_item:
            # عرض اسم السلعة بوضوح
            st.markdown(f"**🔹 {row['السلعة']}**")
        
        with col_qty:
            # إدخال الكمية المتوفرة حالياً
            # ربط كل حقل بـ 'value' من الذاكرة لضمان عدم ضياع الأرقام
            q = st.number_input("الموجود", min_value=0, value=0, key=f"q_{i}", label_visibility="collapsed")
            
        with col_rec:
            # إدخال الكمية المطلوب توصيتها (الطلب)
            r = st.number_input("التوصية", min_value=0, value=0, key=f"r_{i}", label_visibility="collapsed")
            
        with col_note:
            # إدخال أي ملاحظات أو تفاصيل إضافية
            n = st.text_input("الملاحظات", key=f"n_{i}", placeholder="أضف ملاحظة...", label_visibility="collapsed")
            
        temp_results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})
        st.divider() # فاصل بين السلعة والأخرى لزيادة الوضوح في الموبايل

    # زر الاعتماد الرئيسي والقوي
    submit_inventory = st.form_submit_button("🚀 اعتماد الجرد وتوليد التقرير")

# --- 6. الإجراء بعد الاعتماد ---
if submit_inventory:
    # حفظ النتائج النهائية في ذاكرة النظام لتجهيزها للخطوات القادمة
    st.session_state.inventory_ready = temp_results
    st.success("✅ تم حفظ الجرد الأولي بنجاح يا بطل! التقرير جاهز للانتقال للخطوة التالية.")
    
    # بالونات احتفال بنجاح حفظ الجرد!
    st.balloons()
# --- 7. قسم الطلبيات والوصايا الإضافية ---
st.divider()
st.subheader("🛒 تسجيل الطلبيات والوصايا الإضافية")
with st.expander("اضغط هنا لإضافة طلبية جديدة (مثلاً: طلب خاص لزبون)"):
    with st.form("orders_form", clear_on_submit=True):
        o_title = st.text_input("اسم صاحب الطلب")
        o_details = st.text_area("تفاصيل الوصية")
        if st.form_submit_button("حفظ الوصية"):
            new_order = pd.DataFrame([{"الطلب": o_title, "التفاصيل": o_details}])
            st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_order], ignore_index=True)
            st.success("تم حفظ الوصية بنجاح!")

# عرض الوصايا الحالية
if not st.session_state.orders_df.empty:
    st.write("📋 الوصايا المسجلة الآن:")
    st.dataframe(st.session_state.orders_df, use_container_width=True)

# --- 8. المعاينة النهائية والطباعة والواتساب ---
if 'inventory_ready' in st.session_state:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>📄 المعاينة النهائية للتقرير</h2>", unsafe_allow_html=True)
    
    # بناء محتوى التقرير (HTML) للطباعة
    rows_html = ""
    wa_msg = f"📋 *تقرير جرد باب الآغا*\n📅 {iraq_date} | 🕒 {iraq_time}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━\n"
    
    for item in st.session_state.inventory_ready:
        # ندرج فقط السلع التي بها حركة (موجود أو توصية) ليكون التقرير مرتباً
        if item['الموجود'] > 0 or item['التوصية'] > 0:
            rows_html += f"<tr><td>{item['السلعة']}</td><td>{item['الموجود']}</td><td>{item['التوصية']}</td><td>{item['الملاحظة']}</td></tr>"
            wa_msg += f"🔹 *{item['السلعة']}*\n   - موجود: {item['الموجود']} | توصية: {item['التوصية']}\n"
            if item['الملاحظة']: wa_msg += f"   - 📝 {item['الملاحظة']}\n"

    # إضافة الوصايا للتقرير والواتساب
    orders_html = ""
    if not st.session_state.orders_df.empty:
        wa_msg += "\n🛒 *الوصايا الإضافية:*\n"
        orders_html = "<h3>🛒 الطلبيات والوصايا الإضافية:</h3><ul>"
        for _, row in st.session_state.orders_df.iterrows():
            orders_html += f"<li><b>{row['الطلب']}:</b> {row['التفاصيل']}</li>"
            wa_msg += f"• {row['الطلب']}: {row['التفاصيل']}\n"
        orders_html += "</ul>"

    # تصميم ورقة الـ A4 النهائية
    report_design = f"""
    <div dir="rtl" style="font-family: 'Arial'; padding: 30px; border: 2px solid black; background-color: white; color: black;">
        <h1 style="text-align:center;">مخابز باب الآغا 🥖</h1>
        <h3 style="text-align:center;">جرد قسم التوست - الشفت الصباحي</h3>
        <p><b>التاريخ:</b> {iraq_date} | <b>الوقت:</b> {iraq_time}</p>
        <p><b>المسؤول:</b> أيوب هاني</p>
        <hr>
        <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
            <tr style="background-color: #f2f2f2;">
                <th>اسم السلعة</th><th>الكمية المتوفرة</th><th>التوصية</th><th>الملاحظات</th>
            </tr>
            {rows_html}
        </table>
        {orders_html}
        <br><br>
        <div style="display: flex; justify-content: space-between;">
            <p>توقيع مسؤول القسم: ...................</p>
            <p>توقيع كابتن الصالة: ...................</p>
        </div>
    </div>
    """
    
    # عرض المعاينة في التطبيق
    st.markdown(report_design, unsafe_allow_html=True)
    
    # --- أزرار الإجراءات النهائية ---
    col_wa, col_print = st.columns(2)
    
    with col_wa:
        # زر الواتساب
        encoded_msg = urllib.parse.quote(wa_msg + "\nتم بواسطة نظام أيوب هاني")
        wa_url = f"https://wa.me/9647510853103?text={encoded_msg}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-weight:bold;">📲 إرسال التقرير للواتساب</button></a>', unsafe_allow_html=True)

    with col_print:
        # زر الطباعة (حل مشكلة اللغة العربية)
        import base64
        b64 = base64.b64encode(report_design.encode('utf-8')).decode()
        st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button style="width:100%; background-color:#1e3a8a; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-weight:bold;">🖨️ فتح نسخة الطباعة (A4)</button></a>', unsafe_allow_html=True)
