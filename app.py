import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# 1. تعريف الذاكرة (هذا يمنع ضياع الأرقام والأخطاء الحمراء)
if 'items_list' not in st.session_state:
    st.session_state.items_list = ["باكيت تركي", "جرك بالحليب", "توست ابيض"]

if 'orders_list' not in st.session_state:
    st.session_state.orders_list = []

# 2. إعدادات الوقت (توقيت بغداد)
iraq_time = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%Y-%m-%d %I:%M %p")

# 3. القائمة الجانبية للتنقل
st.sidebar.title("🍞 لوحة التحكم")
menu = st.sidebar.radio("انتقل إلى:", ["📋 الجرد", "🛒 الطلبيات", "⚙️ الإعدادات"])

# --- القسم الأول: الجرد ---
if menu == "📋 الجرد":
    st.title("📋 نظام الجرد")
    st.write(f"⏰ الوقت الحالي: {iraq_time}")
    
    results = []
    # عرض السلع كـ "بطاقات" سهلة الاستخدام على الموبايل
    for item in st.session_state.items_list:
        with st.expander(f"📦 {item}", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                # الـ key هنا هو السر في حفظ الرقم حتى لو تنقلت بين الأقسام
                m = st.number_input("الموجود (م)", min_value=0, key=f"m_{item}")
            with c2:
                t = st.number_input("التوصية (ت)", min_value=0, key=f"t_{item}")
            results.append({"السلعة": item, "م": m, "ت": t})

    if st.button("🚀 إرسال التقرير للواتساب"):
        # بناء الرسالة
        msg = f"📋 *تقرير جرد باب الآغا*\n⏰ {iraq_time}\n👤 المسؤول: أيوب هاني\n\n"
        for r in results:
            if r['م'] > 0 or r['ت'] > 0:
                msg += f"🔹 *{r['السلعة']}* -> م: {r['م']} | ت: {r['ت']}\n"
        
        if st.session_state.orders_list:
            msg += "\n🛒 *الطلبيات الإضافية:*\n"
            for o in st.session_state.orders_list:
                msg += f"• {o}\n"
        
        # تحويل الرسالة لرابط واتساب
        link = f"https://wa.me/9647510853103?text={urllib.parse.quote(msg)}"
        st.success("✅ التقرير جاهز!")
        st.markdown(f"### [اضغط هنا للإرسال 📲]({link})")
        
        # عرض جدول بسيط للمعاينة
        st.table(pd.DataFrame([r for r in results if r['م'] > 0 or r['ت'] > 0]))

# --- القسم الثاني: الطلبيات ---
elif menu == "🛒 الطلبيات":
    st.title("🛒 تسجيل الوصايا")
    new_order = st.text_area("اكتب تفاصيل الطلب:")
    if st.button("حفظ الطلب"):
        if new_order:
            st.session_state.orders_list.append(new_order)
            st.success("✅ تم الحفظ")
    
    for i, o in enumerate(st.session_state.orders_list):
        st.info(f"{i+1}. {o}")
    
    if st.button("🗑️ مسح الكل"):
        st.session_state.orders_list = []
        st.rerun()

# --- القسم الثالث: الإعدادات ---
elif menu == "⚙️ الإعدادات":
    st.title("⚙️ إدارة الأصناف")
    add_item = st.text_input("اسم الصنف الجديد:")
    if st.button("إضافة"):
        if add_item and add_item not in st.session_state.items_list:
            st.session_state.items_list.append(add_item)
            st.rerun()
