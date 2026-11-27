"""Shot plan: The Tunnel (3D hologram style)."""
def S3(kind, w=1, **k): return (w, kind, k)
def X(kind, w=1, **k): return (w, kind, k)
def Q(lines, w=1, **k): return (w, 'quote', dict(lines=lines, bgimg='dark', **k))
D = lambda a, b, col='#d9a441': X('dial', items=[(a, b, col)], bgimg='dark')
L = lambda head, items: X('list', img='dark', head=head, items=items)
def G(view, cities, main, zoom=(1.0, 1.1), w=1): return (w, 'geo', dict(view=view, zoom=zoom, cities=[(c, l, 22, 12) for c, l in cities], main=main, hl='Mexico'))

PRON = [('Joaquín Guzmán', 'Wah-keen Gooz-mahn'), ('Guzmán', 'Gooz-mahn'), ('El Chapo', 'El Chah-po'), ('Chapo', 'Chah-po'), ('Altiplano', 'Al-tee-plah-no'), ('Almoloya de Juárez', 'Al-mo-lo-ya deh Hwah-res'), ('Toluca', 'To-loo-ka'), ('Puente Grande', 'Pwen-teh Gran-deh'), ('Jalisco', 'Ha-lees-ko'), ('Sinaloa', 'See-na-lo-ah'), ('Mazatlán', 'Ma-sat-lahn'), ('Enrique Peña Nieto', 'En-ree-keh Pen-ya Nyeh-to'), ('Kate del Castillo', 'Kate del Kas-tee-yo'), ('Los Mochis', 'Los Mo-chees'), ('Fausto Isidro Meza Flores', 'Fowsto Ee-seedro Meh-sa Flo-res'), ('Isidro', 'Ee-seedro'), ('Guasave', 'Gwa-sah-veh')]

VIEWS = {'mexico': (-118.5, -86.0, 14.0, 33.5), 'mxus': (-120, -70, 14, 42), 'central': (-104.5, -97.5, 18.0, 22.5), 'sinaloa': (-111.5, -104.0, 22.0, 28.0)}
CITIES = {'altiplano': (-99.75, 19.42), 'toluca': (-99.66, 19.29), 'cdmx': (-99.13, 19.43), 'puente': (-103.18, 20.56), 'gdl': (-103.35, 20.67), 'mazatlan': (-106.41, 23.25), 'mochis': (-108.99, 25.79), 'culiacan': (-107.39, 24.80), 'ny': (-73.99, 40.69), 'juarez': (-106.42, 31.69), 'florence': (-105.11, 38.39), 'guasave': (-108.47, 25.57)}
EXTRA = dict(o2=1.2, o4=1.0, a3=0.6, a4=0.4, b3=0.6, c3=0.8, d1=0.8, d4=1.0, e3=0.6, e5=1.2, f3=1.0, g1=0.8, g5=1.0, g6=1.0, h3=0.8, i3=0.6, i4=1.5, i5=2.5)
ROLL = ['dark']
_P = S3('prison', cap=None, a0=-2.2, a1=-1.4)
SEGROLL = dict(o=[S3('escape', phase='ride')], a=[S3('prison', a0=-1.0, a1=-0.3)], b=[S3('cart')], c=[S3('condo')], d=[S3('cell')], e=[S3('section'), S3('escape', phase='ride')], f=[S3('prison', a0=0.4, a1=1.2, hl='HIS CELL')], g=[S3('house', floors=2, lab='SAFE HOUSE', sewer=True), S3('chase')], h=[S3('court'), S3('adx')], i=[S3('prison', a0=1.5, a1=2.3)])

PLAN = {
    'o1': [S3('cell', cap='ALTIPLANO · JULY 11, 2015', sub='8:52 P.M.', w=1.4)],
    'o2': [S3('escape', phase='dive', w=1)],
    'o3': [S3('escape', phase='dive', cap='10 METERS DOWN'), S3('escape', phase='ride', cap='~1.5 KILOMETERS')],
    'o4': [X('dial', items=[('2001', 'FIRST ESCAPE', '#cfcfcf'), ('2015', 'SECOND ESCAPE', '#b3302a')], vs=False, bgimg='dark'), Q(['HE STAYED FREE', 'FOR *13 YEARS'])],
    'ch1': [X('chapter', num=1, title='The Prison That Could Not Be Escaped', bgimg='dark')],
    'a1': [G('central', [('altiplano', 'ALTIPLANO'), ('toluca', 'TOLUCA'), ('cdmx', 'MEXICO CITY')], 'altiplano'), S3('prison', cap='ALTIPLANO', sub='FEDERAL SOCIAL READAPTATION CENTER NO. 1')],
    'a2': [X('timeline', marks=[]) if False else D('1991', 'FIRST INMATES', '#cfcfcf'), D('~700', 'PRISONERS · THE MOST DANGEROUS', '#d9a441')],
    'a3': [L('PUBLISHED DESCRIPTIONS', ['WALLS UP TO 1 M THICK', 'RESTRICTED AIRSPACE', 'PHONE SIGNALS BLOCKED']), S3('prison', a0=-0.6, a1=0.2, cap='"IMPOSSIBLE TO ESCAPE"')],
    'a4': [X('title', title='SUBSCRIBE', sub="HOW THE WORLD'S MOST NOTORIOUS PRISONS REALLY WORK", size=150)],
    'ch2': [X('chapter', num=2, title='The First Time', bgimg='dark')],
    'b1': [G('central', [('puente', 'PUENTE GRANDE'), ('gdl', 'GUADALAJARA'), ('cdmx', 'MEXICO CITY')], 'puente'), D('JAN 2001', 'PUENTE GRANDE · JALISCO', '#b3302a')],
    'b2': [S3('cart', cap='PUENTE GRANDE · 2001', sub='AS DESCRIBED IN PUBLISHED ACCOUNTS', w=1.6)],
    'b3': [L('PUBLISHED ACCOUNTS', ['GUARDS BRIBED', 'DOZENS IMPLICATED', 'PRISON DIRECTOR JAILED', 'SOME DETAILS DISPUTED'])],
    'b4': [Q(['13 YEARS.', 'THE *SINALOA CARTEL'])],
    'ch3': [X('chapter', num=3, title='Mazatlán', bgimg='dark')],
    'c1': [G('sinaloa', [('mazatlan', 'MAZATLÁN'), ('culiacan', 'CULIACÁN')], 'mazatlan'), S3('condo', lab='4TH FLOOR', cap='MAZATLÁN · FEB 22, 2014', w=1.4)],
    'c2': [X('dial', items=[('ARRESTED', 'OFFICIAL ACCOUNT', '#d9a441'), ('QUESTIONED', 'LATER, BY A FEDERAL COURT', '#cfcfcf')], vs=False, bgimg='dark')],
    'c3': [S3('prison', w=2, hl='HIS CELL', cap='BACK TO ALTIPLANO', a0=-2.6, a1=-1.8)],
    'ch4': [X('chapter', num=4, title='The Blind Spot', bgimg='dark')],
    'd1': [S3('prison', hl='HIS CELL', a0=-1.5, a1=-1.0, r0=120, r1=80)],
    'd2': [S3('cell', cap='THE CELL', w=1.6)],
    'd3': [S3('cell', cap='JULY 11, 2015', sub='FOOTAGE RELEASED BY MEXICAN AUTHORITIES'), D('8:52 P.M.', 'OUT OF VIEW', '#b3302a')],
    'd4': [S3('cell', blind='OPENING · ~50 CM', cap='UNDER THE SHOWER', w=1.4)],
    'ch5': [X('chapter', num=5, title='The Tunnel', bgimg='dark')],
    'e1': [S3('escape', phase='dive', cap='A SHAFT ~10 M DEEP')],
    'e2': [S3('section', cap='THE TUNNEL', hl='~1.7 M HIGH', wl='~75 CM WIDE', w=1.4), S3('topdown', cap='~1.5 KILOMETERS', house='CONSTRUCTION SITE')],
    'e3': [S3('section', cap='LIGHTS · AIR · A MOTORCYCLE', hl='LIGHTING', wl='RAILS'), S3('escape', phase='ride', cap='A MOTORCYCLE ON RAILS', sub='ACCORDING TO MEXICAN OFFICIALS')],
    'e4': [S3('escape', phase='ride', cap='THE EXIT', sub='A BUILDING UNDER CONSTRUCTION'), S3('topdown', cap='OUTSIDE THE PRISON', house='HALF-BUILT HOUSE')],
    'e5': [Q(['HOW DID THEY KNOW', 'WHERE HIS *CELL WAS?'])],
    'ch6': [X('chapter', num=6, title='Affront', bgimg='dark')],
    'f1': [X('dial', items=[('~120', 'STAFF ON DUTY', '#cfcfcf'), ('31', 'QUESTIONED', '#d9a441')], vs=False, bgimg='dark'), L('AFTERWARDS', ['PRISON DIRECTOR QUESTIONED', 'OFFICIALS CHARGED', 'NUMBERS DIFFER IN REPORTS'])],
    'f2': [Q(['PEÑA NIETO:', 'AN *AFFRONT']), D('60,000,000', 'PESOS · REWARD', '#d9a441')],
    'f3': [Q(['A SECOND ESCAPE:', '*"UNFORGIVABLE"'])],
    'f4': [X('doc', head='WALL STREET JOURNAL · JULY 2015', lines=['U.S. OFFICIALS SAID THEY HAD WARNED', '*HE WAS PLOTTING AN ESCAPE'])],
    'ch7': [X('chapter', num=7, title='Black Swan', bgimg='dark')],
    'g1': [D('6 MONTHS', 'THE MANHUNT', '#d9a441')],
    'g2': [D('OCT 2015', 'THE INTERVIEW · SEAN PENN AND KATE DEL CASTILLO', '#cfcfcf'), X('doc', head='ROLLING STONE · JAN 2016', lines=['"EL CHAPO SPEAKS"', '*CONTACTS REPORTEDLY HELPED TRACK HIM'])],
    'g3': [G('sinaloa', [('mochis', 'LOS MOCHIS'), ('culiacan', 'CULIACÁN')], 'mochis'), S3('house', floors=2, lab='SAFE HOUSE', cap='LOS MOCHIS · JAN 8, 2016', sub='OPERATION BLACK SWAN', w=1.4)],
    'g4': [S3('house', floors=2, lab='SAFE HOUSE', sewer=True, cap='THE DRAINS', w=1.4)],
    'g5': [S3('chase', cap='HIGHWAY SOUTH OF LOS MOCHIS'), Q(['"YOU ARE ALL', 'GOING TO *DIE"'])],
    'g6': [S3('prison', hl='BACK AGAIN', cap='ALTIPLANO · AGAIN', a0=0.3, a1=1.0)],
    'ch8': [X('chapter', num=8, title='Brooklyn', bgimg='dark')],
    'h1': [G('mxus', [('juarez', 'CIUDAD JUÁREZ'), ('ny', 'NEW YORK')], 'ny', zoom=(1.0, 1.05)), D('JAN 19, 2017', 'EXTRADITED', '#d9a441')],
    'h2': [S3('court', cap='BROOKLYN · 2018-2019', lab='JOAQUÍN GUZMÁN'), X('dial', items=[('FEB 12, 2019', 'GUILTY ON ALL COUNTS', '#b3302a'), ('JULY 17, 2019', 'LIFE + 30 YEARS', '#d9a441')], vs=False, bgimg='dark')],
    'h3': [S3('adx', cap='ADX FLORENCE', sub='COLORADO', w=1.6)],
    'ch9': [X('chapter', num=9, title='The Prison Today', bgimg='dark')],
    'i1': [S3('prison', cap='ALTIPLANO · 2026', a0=2.0, a1=2.8)],
    'i2': [G('sinaloa', [('guasave', 'GUASAVE')], 'guasave'), X('fugitive', num='NOV 2026', alias='CHAPO ISIDRO', name='FAUSTO ISIDRO MEZA FLORES', lines=['FBI TEN MOST WANTED', 'REPORTED TRANSFER: ALTIPLANO'], stamp=None)],
    'i3': [X('dial', items=[('MEXICO', 'TRIAL FIRST', '#d9a441'), ('USA', 'EXTRADITION REQUESTED', '#cfcfcf')], vs=True, bgimg='dark')],
    'i4': [S3('prison', hl='CAN IT HOLD HIM?', cap='THE QUESTION', a0=-2.8, a1=-2.0)],
    'i5': [X('title', title='CAN ALTIPLANO HOLD HIM?', sub='TELL US IN THE COMMENTS', size=110)],
}
CAP = (4.5, 5.5)
