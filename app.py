import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse

# إعدادات الصفحة
st.set_page_config(page_title="جرد قسم التوست - أيوب هاني", layout="wide")

# توقيت العراق (UTC+3)
iraq_time = datetime.utcnow() + timedelta(hours=3)
current_date = iraq_time.strftime("%Y-%m-%d")
current_time = iraq_time.strftime("%H:%M:%S")

# حقوق الملكية في التذييل
footer = """
    <style>
    .footer { position: fixed; bottom: 0; width: 100%; text-align: center; padding: 10px; background: #f1f1f1; }
    </style>
    <div class="footer">حقوق الطبع محفوظة لـ أيوب هاني © 2026</div>
"""
st.markdown(footer, unsafe_allow_html=True)
# تهيئة البيانات الأساسية (قائمة السلع التي زودتني بها)
if 'inventory' not in st.session_state:
    data = {
        "السلعة": ["باكيت تركي", "باكيت فرنسي اسمر", "باكيت فرنسي ابيض", "صمون شاورما", "صمون سداسي", "صمون كنتاكي حمام", "صمون كنتاكي دائري", "صمون مني بركر", "صمون بركر وسط", "صمون اسمر سداسي", "صمون كنتاكي اسمر", "صمون بطاطا", "صمون بركر دبل", "جرك بالحليب", "جرك تمر", "جرك حلقوم", "جرك بالجبن", "جرك كاكاو (علبة)", "جرك كاكاو ( قطع )", "جرك برازيلي", "جرك بربراوزا", "جرك مغربية", "خبز سمسم حلو", "خبز شعير 7 حبات", "خبز شعير اصلي", "خبز تركي بالجبن", "خبز محيرجه", "لفه خميرة", "ملفوف دارسين", "توست اسمر ساده", "توست اسمر 7 حبات", "توست اسمر شوفان", "توست ابيض", "توست شعير 7 حبات", "توست شعير اصلي", "توست جاودار", "توست بطاطا", "توست كاكاو", "توست فراولة", "توست حلبي", "توست طماطم", "توست زيتون", "توست بالحليب", "توست بريوش كاكاو", "توست جبن", "خلية نحل كاكاو", "خلية نحل كاكاو محشية نوتيلا", "خلية نحل جبن", "خلية نحل بالحليب المكثف", "خلية نحل محشية نوتيلا", "خلية نحل تمر وحلقوم", "لقمة صغير", "كرواسون كرز", "كرواسون نستله", "كرواسون ابيض", "كرواسون بالزبده الحيوانيه", "كيك جنين الحنطة مخلوط", "كيك جنين الحنطة اصلي", "سميط شعير", "محلب تركي", "محلب تمر", "محلب حلقوم", "محلب مبروش", "محلب سمسم"],
        "حد الأمان": [50, 50, 50, 50, 50, 25, 30, 30, 20, 25, 25, 40, 30, 100, 40, 40, 60, 70, 30, 150, 70, 15, 40, 60, 100, 50, 40, 70, 70, 80, 50, 50, 130, 45, 45, 25, 40, 30, 30, 20, 20, 30, 30, 30, 50, 70, 40, 50, 70, 30, 70, 10, 150, 200, 800, 50, 100, 60, 60, 10, 10, 10, 10, 10],
        "الكمية الحالية": [0]*64
    }
    st.session_state.inventory = pd.DataFrame(data)

if 'orders' not in st.session_state:
    st.session_state.orders = []
st.title("🍞 جرد قسم التوست - الشفت الصباحي")
st.subheader(f"المسؤول: أيوب هاني | التاريخ: {current_date} | الوقت: {current_time}")

tabs = st.tabs(["📊 جدول الجرد", "📋 إدارة السلع", "📦 الطلبيات والتوصيات", "🖨️ تقرير A4 & واتساب"])

with tabs[0]:
    st.markdown("### حالة السلع الحالية")
    # عرض الجدول مع إمكانية التعديل
    edited_df = st.data_editor(st.session_state.inventory, use_container_width=True)
    
    # حساب حالة الأمان
    def check_safety(row):
        if row['الكمية الحالية'] >= row['حد الأمان']:
            return "✅ كافية"
        return "⚠️ غير كافية"
    
    edited_df['الحالة'] = edited_df.apply(check_safety, axis=1)
    st.session_state.inventory = edited_df
    st.dataframe(edited_df.style.applymap(lambda x: 'color: red' if x == "⚠️ غير كافية" else 'color: green', subset=['الحالة']))

with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ➕ إضافة سلعة جديدة")
        new_item = st.text_input("اسم السلعة")
        new_safety = st.number_input("حد الأمان", min_value=1)
        if st.button("إضافة"):
            new_row = pd.DataFrame({"السلعة": [new_item], "حد الأمان": [new_safety], "الكمية الحالية": [0]})
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
            st.success("تمت الإضافة")
            
    with col2:
        st.markdown("### 🗑️ حذف سلعة")
        item_to_delete = st.selectbox("اختر السلعة للحذف", st.session_state.inventory['السلعة'])
        if st.button("حذف"):
            st.session_state.inventory = st.session_state.inventory[st.session_state.inventory['السلعة'] != item_to_delete]
            st.warning("تم حذف السلعة")
with tabs[2]:
    st.markdown("### 📝 تسجيل طلبية أو توصية")
    item_rec = st.selectbox("السلعة المطلوبة", st.session_state.inventory['السلعة'])
    qty_rec = st.number_input("العدد المطلوب (توصية)", min_value=1)
    note = st.text_area("تفاصيل إضافية")
    if st.button("حفظ التوصية"):
        st.session_state.orders.append({"السلعة": item_rec, "العدد": qty_rec, "التفاصيل": note})
        st.info("تمت إضافة التوصية للتقرير")

with tabs[3]:
    st.markdown("### 📄 معاينة ورقة الجرد (تنسيق A4)")
    report_content = f"""
    جرد قسم التوست - الشفت الصباحي
    ---------------------------
    المسؤول: أيوب هاني
    التاريخ: {current_date}
    الوقت: {current_time}
    ---------------------------
    السلع غير الكافية (تحتاج تعويض):
    """
    short_items = st.session_state.inventory[st.session_state.inventory['الكمية الحالية'] < st.session_state.inventory['حد الأمان']]
    for idx, row in short_items.iterrows():
        report_content += f"\n- {row['السلعة']}: الحالي ({row['الكمية الحالية']}) / الأمان ({row['حد الأمان']})"
    
    report_content += "\n\nالتوصيات والطلبيات الحالية:"
    for order in st.session_state.orders:
        report_content += f"\n- {order['السلعة']}: العدد {order['العدد']} ({order['التفاصيل']})"

    st.text_area("معاينة النص", report_content, height=300)
    
    # رابط الواتساب
    phone = "07510853103"
    msg = urllib.parse.quote(report_content)
    whatsapp_url = f"https://wa.me/{phone}?text={msg}"
    
    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px; border-radius:5px; border:none; cursor:pointer;">📲 تحويل الجرد إلى واتساب</button></a>', unsafe_allow_html=True)
