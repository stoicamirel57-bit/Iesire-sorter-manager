import streamlit as st
import pandas as pd
import qrcode
import io
import base64

st.set_page_config(page_title="Iesire Sorter Manager", layout="wide")

st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#ffffff;}
[data-testid="stHeader"]{background:#ffffff;}
h1{font-size:28px!important;font-weight:800!important;color:#111!important;}
div[data-testid="metric-container"]{background:#f8f8f8;border:1px solid #e8e8e8;border-radius:8px;padding:12px 20px;}
.legend-box{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 20px 0;}
.leg{padding:8px 16px;border-radius:6px;font-size:13px;font-weight:600;}
.leg-verde{background:#c8f0c8;color:#1a5c1a;}
.leg-rosu{background:#f44336;color:#fff;}
.leg-mov{background:#ce93d8;color:#4a1060;}
.leg-galben{background:#f9e79f;color:#7a6000;}
table{width:100%;border-collapse:collapse;font-size:13px;}
th{background:#f5f5f5;padding:10px 14px;text-align:left;border-bottom:2px solid #e0e0e0;color:#444;font-weight:600;}
td{padding:9px 14px;border-bottom:1px solid #f0f0f0;vertical-align:middle;text-align:center;}
.ag{display:inline-block;padding:3px 10px;border-radius:4px;font-size:12px;font-weight:500;}
.ag-verde{background:#eafaea;color:#1a5c1a;}
.ag-rosu{background:#fdecea;color:#c62828;}
.ag-mov{background:#f3e5f5;color:#6a1b9a;}
.ag-galben{background:#fffde7;color:#7a6000;}
.row-verde{background:#f6fff6;}
.row-rosu{background:#fff5f5;}
.row-mov{background:#fdf5ff;}
.row-galben{background:#fffef0;}
.status-badge{background:#e8f5e9;color:#2e7d32;padding:3px 10px;border-radius:4px;font-size:12px;font-weight:500;}
.colet{font-family:monospace;font-size:12px;color:#555;}
.date{font-size:12px;color:#888;}
</style>""", unsafe_allow_html=True)

SUD = {'GL','BR','VN','BZ','IL','CL','GR','TR','CT','TL','PH','DB','AG'}
NORDV = {'IS','NT','BC','VS','BT','SV','MM','BH','SM','SJ','CJ','BN','MS','HR','CV','BV','SB','AB','HD','TM','AR','CS','MH','GJ','VL','OT','DJ'}

def get_zone(agency):
    if not agency or str(agency).strip() == '' or str(agency) == 'nan':
        return 'galben'
    prefix = str(agency).split('_')[0].upper()
    if prefix == 'B':
        return 'mov'
    if prefix in SUD:
        return 'verde'
    if prefix in NORDV:
        return 'rosu'
    return 'galben'

def generate_qr(text):
    try:
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(str(text))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        b64 = base64.b64encode(buffer.getvalue()).decode()
        return '<img src="data:image/png;base64,' + b64 + '" width="70" height="70"/>'
    except:
        return ''

def build_table(data, show_qr):
    rows = []
    for _, row in data.iterrows():
        nr = str(row.get('Nr colet', ''))
        dr = str(row.get('Data receptie', ''))
        dus = str(row.get('Data ultim status', ''))
        status = str(row.get('Status', ''))
        rid = str(row.get('Agentie ridicare', ''))
        liv = str(row.get('Agentie livrare', ''))
        zr = get_zone(rid)
        zl = get_zone(liv)
        tr = '<tr class="row-' + zl + '">'
        if show_qr:
            tr += '<td>' + generate_qr(nr) + '</td>'
        tr += '<td class="colet">' + nr + '</td>'
        tr += '<td class="date">' + dr + '</td>'
        tr += '<td class="date">' + dus + '</td>'
        tr += '<td><span class="status-badge">' + status + '</span></td>'
        tr += '<td><span class="ag ag-' + zr + '">' + rid + '</span></td>'
        tr += '<td><span class="ag ag-' + zl + '">' + liv + '</span></td>'
        tr += '</tr>'
        rows.append(tr)
    if show_qr:
        header = '<table><thead><tr><th>QR Code</th><th>Nr. Colet</th><th>Data Receptie</th><th>Data Ultim Status</th><th>Status</th><th>Agentie Ridicare</th><th>Agentie Livrare</th></tr></thead><tbody>'
    else:
        header = '<table><thead><tr><th>Nr. Colet</th><th>Data Receptie</th><th>Data Ultim Status</th><th>Status</th><th>Agentie Ridicare</th><th>Agentie Livrare</th></tr></thead><tbody>'
    return header + ''.join(rows) + '</tbody></table>'

st.title("Iesire Sorter Manager")
st.markdown("---")

uploaded = st.file_uploader("Incarca fisier CSV sau Excel", type=["csv", "xlsx", "xls"])

if uploaded:
    try:
        if uploaded.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
    except Exception as e:
        st.error("Eroare la citirea fisierului")
        st.stop()

    df = df.fillna('')
    st.success("Fisier incarcat: " + uploaded.name)
    st.markdown("---")

    st.markdown("### Statistici Generale")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Colete", str(len(df)))
    c2.metric("Agentii Ridicare", str(df['Agentie ridicare'].nunique()))
    c3.metric("Agentii Livrare", str(df['Agentie livrare'].nunique()))
    c4.metric("Statusuri Unice", str(df['Status'].nunique()))
    c5.metric("Fisiere incarcate", "1")

    st.markdown("**Legenda culori:**")
    st.markdown('<div class="legend-box"><div class="leg leg-verde">Verde - Sud</div><div class="leg leg-rosu">Rosu - Nord / Vest / International</div><div class="leg leg-mov">Mov - Bucuresti / Hub-uri</div><div class="leg leg-galben">Galben - Alte zone</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    col_f, col_s1, col_s2 = st.columns([3, 1, 1])
    with col_f:
        search = st.text_input("Cauta dupa colet, agentie, status...", "")
    with col_s1:
        sort_col = st.selectbox("Sorteaza dupa:", ["Agentie livrare", "Agentie ridicare", "Nr colet", "Status", "Data receptie", "Data ultim status"])
    with col_s2:
        sort_dir = st.radio("Directie:", ["A-Z", "Z-A"], horizontal=True)

    show_qr = st.checkbox("Afiseaza coloana QR Code", value=True)

    view = df.copy()
    if search.strip():
        mask = view.apply(lambda r: r.astype(str).str.contains(search, case=False, na=False).any(), axis=1)
        view = view[mask]

    view = view.sort_values(by=sort_col, ascending=(sort_dir == "A-Z"), na_position='last')

    rpp_col, _, cnt_col = st.columns([1, 3, 1])
    with rpp_col:
        rpp = st.selectbox("Randuri per pagina:", [10, 25, 50], index=0)
    with cnt_col:
        st.markdown("<div style='padding-top:28px;font-size:13px;color:#555;'><b>" + str(len(view)) + "</b> randuri</div>", unsafe_allow_html=True)

    total_pages = max(1, (len(view) - 1) // rpp + 1)
    page = st.number_input("Pagina:", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * rpp
    page_data = view.iloc[start:start + rpp]

    st.markdown(build_table(page_data, show_qr), unsafe_allow_html=True)

    st.markdown("---")
    st.download_button("Descarca datele filtrate (CSV)", data=view.to_csv(index=False).encode('utf-8'), file_name="iesire_sorter_export.csv", mime="text/csv")

else:
    st.info("Incarca un fisier CSV sau Excel pentru a incepe.")
