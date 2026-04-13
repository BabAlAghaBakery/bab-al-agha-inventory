import streamlit as st
import pandas as pd
import datetime
import os
import urllib.parse

# --- 1. إعدادات الصفحة والوقت ---
st.set_page_config(page_title="نظام جرد باب الآغا", layout="wide")

# إعداد الوقت بتوقيت العراق (تقريبي بناءً على توقيت النظام)
iraq_time = datetime.datetime.now() + datetime.timedelta(hours=0) # عدل الساعات إذا كان السيرفر بتوقيت مختلف
date_str = iraq_time.strftime("%Y-%m-%d")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    
    /* تنسيق ورقة الطباعة */
    .print-paper { background: white; padding: 30px; border: 1px solid #ddd; color: black; direction: rtl; }
    @media print {
        .no-print { display: none !important; }
        .print-paper { border: none; padding: 0; }
        body { background: white; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات (ملفات CSV) ---
DB_FILE = "bakery_inventory.csv"
ORDERS_FILE = "special_orders.csv"

if not os.path.exists(DB_FILE):
    # استخدام القائمة الأولية إذا لم يوجد الملف
    initial_data = [
        ["باكيت تركي", 50], ["باكيت فرنسي اسمر", 50], ["باكيت فرنسي ابيض", 50],
        ["صمون شاورما", 50], ["صمون سداسي", 50], ["جرك برازيلي", 150], ["توست ابيض", 130]
    ] # أضف البقية هنا كما في كودك الأصلي
    pd.DataFrame(initial_data, columns=["السلعة", "رقم الأمان"]).to_csv(DB_FILE, index=False)

if not os.path.exists(ORDERS_FILE):
    pd.DataFrame(columns=["الطلب", "التفاصيل"]).to_csv(ORDERS_FILE, index=False)

df_items = pd.read_csv(DB_FILE)
df_orders = pd.read_csv(ORDERS_FILE)

# --- 3. حفظ حالة المدخلات (Session State) ---
if 'inventory_inputs' not in st.session_state:
    st.session_state.inventory_inputs = {}
if 'rec_inputs' not in st.session_state:
    st.session_state.rec_inputs = {}

# --- 4. القائمة الجانبية ---
st.sidebar.title("🍞 نظام باب الآغا")
menu = st.sidebar.radio("انتقل إلى:", ["📋 الجرد الصباحي", "🛒 الطلبيات والوصايا", "⚙️ إدارة السلع"])

# --- 5. صفحة الجرد الصباحي ---
if menu == "📋 الجرد الصباحي":
    st.markdown("<div class='main-header'><h1>📋 جرد قسم التوست - الشفت الصباحي</h1></div>", unsafe_allow_html=True)
    
    st.subheader(f"📅 تاريخ اليوم: {date_str}")
    
    inventory_results = []
    
    # عرض الحقول وتخزينها في session_state
    for i, row in df_items.iterrows():
        col1, col2 = st.columns([2, 1])
        item_name = row['السلعة']
        
        with col1:
            val = st.number_input(f"{item_name} (الأمان: {row['رقم الأمان']})", 
                                 min_value=0, step=1, 
                                 key=f"inv_{i}", 
                                 value=st.session_state.inventory_inputs.get(i, 0))
            st.session_state.inventory_inputs[i] = val
            
        with col2:
            rec_val = st.number_input(f"المطلوب لـ {item_name}", 
                                     min_value=0, step=1, 
                                     key=f"rec_in_{i}", 
                                     value=st.session_state.rec_inputs.get(i, 0))
            st.session_state.rec_inputs[i] = rec_val
        
        status = "⚠️ نقص" if val <= row['رقم الأمان'] else "✅ كافٍ"
        inventory_results.append({
            "السلعة": item_name,
            "الموجود": val,
            "الحالة": status,
            "التوصية": rec_val
        })

    # --- منطقة الطباعة والواتساب ---
    st.divider()
    
    # تحضير نص الواتساب
    short_summary = f"*تقرير جرد باب الآغا - قسم التوست*\n*التاريخ:* {date_str}\n*المسؤول:* أيوب هاني\n\n*النواقص والطلبات:*\n"
    for item in inventory_results:
        if item['التوصية'] > 0:
            short_summary += f"• {item['السلعة']}: اطلب ({item['التوصية']})\n"

    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
                if st.button("🖨️ فتح نافذة الطباعة"):
                            if st.button("🖨️ فتح نافذة الطباعة"):
            js = "window.parent.focus(); window.parent.print();"
            st.markdown(f'<img src="x" onerror="{js}" style="display:none;">', unsafe_allow_html=True)

            

            
    with col_p2:
        wa_url = f"https://wa.me/9647510853103?text={urllib.parse.quote(short_summary)}"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="no-print"><button style="width:100%; background-color:#25d366; color:white; padding:12px; border-radius:10px; border:none; cursor:pointer;">📲 إرسال الجرد عبر الواتساب</button></a>', unsafe_allow_html=True)

    # عرض التقرير النهائي (المعاينة)
    report_html = f"""
    <div class="print-paper">
        <div style="text-align:center; border-bottom: 2px solid #333; padding-bottom:10px;">
            <h1 style="margin:0;">مخابز باب الآغا 🥖</h1>
            <p>قسم التوست - تقرير الجرد الصباحي</p>
            <p><b>التاريخ: {date_str} | المسؤول: أيوب هاني</b></p>
        </div>
        <table style="width:100%; border-collapse: collapse; margin-top:20px; direction: rtl;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid black; padding: 10px;">السلعة</th>
                    <th style="border: 1px solid black; padding: 10px;">الموجود</th>
                    <th style="border: 1px solid black; padding: 10px;">الحالة</th>
                    <th style="border: 1px solid black; padding: 10px;">الطلب المطلوب</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f"<tr><td style='border: 1px solid black; padding: 8px;'>{item['السلعة']}</td><td style='border: 1px solid black; padding: 8px; text-align:center;'>{item['الموجود']}</td><td style='border: 1px solid black; padding: 8px; text-align:center; color:{'red' if item['الحالة']=='⚠️ نقص' else 'green'};'>{item['الحالة']}</td><td style='border: 1px solid black; padding: 8px; text-align:center; font-weight:bold;'>{item['التوصية'] if item['التوصية'] > 0 else '-'}</td></tr>" for item in inventory_results])}
            </tbody>
        </table>
        <div style="margin-top:20px;">
            <h4>📌 وصايا وطلبيات خاصة:</h4>
            {"".join([f"<p>• <b>{r['الطلب']}:</b> {r['التفاصيل']}</p>" for _, r in df_orders.iterrows()]) if not df_orders.empty else "<p>لا توجد وصايا إضافية</p>"}
        </div>
        <div style="margin-top:40px; display: flex; justify-content: space-between;">
            <p>ختم الإدارة: _________</p>
            <p>توقيع المسؤول: أيوب هاني</p>
        </div>
    </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)

# --- صفحات الوصايا وإدارة السلع تبقى كما هي مع التأكد من حفظ الملفات ---
elif menu == "🛒 الطلبيات والوصايا":
    st.header("📌 تسجيل الطلبيات")
    with st.form("new_order", clear_on_submit=True):
        o_name = st.text_input("اسم صاحب الطلبية")
        o_text = st.text_area("التفاصيل")
        if st.form_submit_button("حفظ"):
            new_row = pd.DataFrame([[o_name, o_text]], columns=df_orders.columns)
            pd.concat([df_orders, new_row]).to_csv(ORDERS_FILE, index=False)
            st.success("تم الحفظ")
            st.rerun()
    
    # عرض الوصايا مع إمكانية الحذف
    for i, row in df_orders.iterrows():
        with st.expander(f"🔔 {row['الطلب']}"):
            st.write(row['التفاصيل'])
            if st.button("تم الإنجاز (حذف)", key=f"del_{i}"):
                df_orders.drop(i).to_csv(ORDERS_FILE, index=False)
                st.rerun()

elif menu == "⚙️ إدارة السلع":
    st.header("⚙️ تعديل القائمة")
    # كود الإضافة والحذف كما هو في نسختك
    with st.form("add_item"):
        n_name = st.text_input("اسم السلعة الجديدة")
        n_limit = st.number_input("حد الأمان", min_value=1, value=50)
        if st.form_submit_button("إضافة"):
            new_item = pd.DataFrame([[n_name, n_limit]], columns=df_items.columns)
            pd.concat([df_items, new_item]).to_csv(DB_FILE, index=False)
            st.rerun()

st.markdown(f"<div style='text-align:center; color:grey; margin-top:50px;'>نظام جرد باب الآغا - أيوب هاني © {iraq_time.year}</div>", unsafe_allow_html=True)
