import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from html.parser import HTMLParser

import requests
import streamlit as st

st.set_page_config(page_title='SHAKTI • Hazra Bari', page_icon='🔱', layout='wide')

TEMPLE = 'Hazra Bari Virtual Shakti Mandir'
ADDRESS = 'Sagarbhanga, Durgapur-11, Paschim Bardhaman, West Bengal - 713211, India'
PANCHANG_CITY = 'Durgapur, West Bengal'
DRIK_URL = 'https://www.drikpanchang.com/panchang/day-panchang.html?geoname-id=1272175'

NAVRATRI = [
    ('11 Oct 2026', 'Shailputri', 'Maroon'),
    ('12 Oct 2026', 'Brahmacharini', 'White'),
    ('13 Oct 2026', 'Chandraghanta', 'Red'),
    ('14 Oct 2026', 'Kushmanda', 'Green'),
    ('15 Oct 2026', 'Skandamata', 'Yellow'),
    ('16 Oct 2026', 'Katyayani', 'Silver'),
    ('17 Oct 2026', 'Kalaratri', 'Blue'),
    ('18 Oct 2026', 'Kalaratri', 'Dark Maroon'),
    ('19 Oct 2026', 'Mahagauri', 'Pinkish Red'),
    ('20 Oct 2026', 'Siddhidatri', 'Pinkish Red'),
    ('21 Oct 2026', 'Vijayadashami', 'Festival'),
]

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        value = data.strip()
        if value:
            self.parts.append(value)
    def get_text(self):
        return ' '.join(self.parts)

def india_now():
    return datetime.now(timezone.utc).astimezone(ZoneInfo('Asia/Kolkata'))

def clean(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()

def fetch_panchang():
    try:
        response = requests.get(DRIK_URL, timeout=12, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        parser = TextParser()
        parser.feed(response.text)
        text = parser.get_text()
        fields = {}
        patterns = {
            'Tithi': r'Tithi\s*([^|]{3,100}?)(?=Nakshatra|Yoga|Karana|Sunrise|Sunset|$)',
            'Nakshatra': r'Nakshatra\s*([^|]{3,100}?)(?=Yoga|Karana|Sunrise|Sunset|$)',
            'Sunrise': r'Sunrise\s*([0-9:APM ]{4,20})',
            'Sunset': r'Sunset\s*([0-9:APM ]{4,20})',
            'Paksha': r'(Shukla Paksha|Krishna Paksha)',
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.I)
            if match:
                fields[key] = clean(match.group(1))
        return fields, None
    except Exception as exc:
        return {}, str(exc)

def card(label, value, icon):
    st.markdown(f'''<div class="card"><div class="icon">{icon}</div><div class="label">{label}</div><div class="value">{value or 'Not available'}</div></div>''', unsafe_allow_html=True)

st.markdown('''
<style>
body { background:#12070f; }
.hero { padding:30px; border-radius:22px; background:linear-gradient(135deg,#3b071b,#7a102d,#b34218); color:white; margin-bottom:22px; box-shadow:0 12px 35px rgba(0,0,0,.25); }
.hero h1 { font-size:42px; margin:0; }
.hero p { margin:8px 0 0; font-size:17px; }
.card { padding:18px; border-radius:18px; background:rgba(120,20,45,.12); border:1px solid rgba(190,70,80,.28); min-height:125px; }
.icon { font-size:28px; }.label { opacity:.75; font-size:14px; margin-top:8px; }.value { font-size:19px; font-weight:700; margin-top:5px; }
</style>
''', unsafe_allow_html=True)

st.markdown(f'''<div class="hero"><h1>🔱 SHAKTI</h1><p>{TEMPLE}</p><p>{ADDRESS}</p></div>''', unsafe_allow_html=True)

page = st.sidebar.radio('SHAKTI MENU', ['🏠 Darshan', '🪔 Panchang', '🌺 Navratri', '🙏 Seva', '📿 Japa', '🕉️ Sankalp', 'ℹ️ Mandir'])
now = india_now()
st.sidebar.caption('IST • ' + now.strftime('%d %B %Y, %I:%M:%S %p'))

if page == '🏠 Darshan':
    st.subheader('🌺 Maa Shakti Darshan')
    st.info('Welcome to the digital darshan space of Hazra Bari.')
    a, b, c = st.columns(3)
    with a:
        if st.button('🪔 Light Diya', use_container_width=True):
            st.success('🪔 Your virtual diya is glowing.')
    with b:
        if st.button('🔔 Temple Bell', use_container_width=True):
            st.success('🔔 घंटा नाद • Jai Maa Shakti!')
    with c:
        if st.button('🌸 Pushpanjali', use_container_width=True):
            st.success('🌸 Pushpanjali offered with devotion.')
    st.markdown('### 🙏 Today at the Mandir')
    st.write('Darshan • Digital Diya • Pushpanjali • Mantra Japa • Sankalp')

elif page == '🪔 Panchang':
    st.subheader('🪔 Live Panchang')
    st.caption('Source: Drik Panchang • calculation location: Durgapur, West Bengal')
    data, error = fetch_panchang()
    if error:
        st.warning('Live Drik Panchang could not be read right now. Use the official page below.')
    cols = st.columns(4)
    items = [('Tithi', data.get('Tithi'), '🌙'), ('Nakshatra', data.get('Nakshatra'), '⭐'), ('Paksha', data.get('Paksha'), '🌗'), ('Sunrise', data.get('Sunrise'), '🌅')]
    for col, item in zip(cols, items):
        with col:
            card(*item)
    cols2 = st.columns(2)
    with cols2[0]: card('Sunset', data.get('Sunset'), '🌇')
    with cols2[1]: card('Location', PANCHANG_CITY, '📍')
    st.link_button('Open Drik Panchang', DRIK_URL)

elif page == '🌺 Navratri':
    st.subheader('🌺 Hazra Bari Shardiya Navratri 2026')
    for date, devi, dress in NAVRATRI:
        st.markdown(f"**{date} — {devi}**  \nDress: {dress}")
        st.divider()

elif page == '🙏 Seva':
    st.subheader('🙏 Digital Seva')
    seva = st.selectbox('Choose Seva', ['Virtual Diya', 'Pushpanjali', 'Digital Aarti', 'Bhog Offering'])
    name = st.text_input('Devotee Name')
    if st.button('Offer Seva', type='primary'):
        if name.strip():
            st.success(f'🙏 {seva} recorded for {name.strip()}. Jai Maa Shakti!')
        else:
            st.warning('Please enter your name.')

elif page == '📿 Japa':
    st.subheader('📿 108 Mantra Japa')
    if 'count' not in st.session_state:
        st.session_state.count = 0
    st.metric('Japa Count', f"{st.session_state.count}/108")
    x, y = st.columns(2)
    with x:
        if st.button('📿 Chant Once', use_container_width=True):
            st.session_state.count = min(108, st.session_state.count + 1)
            st.rerun()
    with y:
        if st.button('Reset', use_container_width=True):
            st.session_state.count = 0
            st.rerun()
    st.markdown('**ॐ ऐं ह्रीं क्लीं चामुण्डायै विच्चे**')

elif page == '🕉️ Sankalp':
    st.subheader('🕉️ Digital Sankalp')
    name = st.text_input('Name')
    prayer = st.text_area('Your Sankalp / Prayer')
    if st.button('🙏 Submit Sankalp', type='primary'):
        if name.strip() and prayer.strip():
            st.success('🙏 Sankalp accepted. May Maa Shakti bless you.')
        else:
            st.warning('Please enter your name and prayer.')

else:
    st.subheader('ℹ️ Hazra Bari Virtual Shakti Mandir')
    st.write('**Temple:**', TEMPLE)
    st.write('**Address:**', ADDRESS)
    st.write('**Panchang:** Drik Panchang — Durgapur, West Bengal')
    st.write('**App identity:** SHAKTI')

st.divider()
st.caption('© 2026 SHAKTI • Hazra Bari Virtual Shakti Mandir')
