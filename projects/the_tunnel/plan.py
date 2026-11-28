"""Shot plan: The Tunnel (3D hologram style)."""
def S3(kind, w=1, **k): return (w, kind, k)
def X(kind, w=1, **k): return (w, kind, k)
def Q(lines, w=1, **k): return (w, 'quote', dict(lines=lines, bgimg='dark', **k))
D = lambda a, b, col='#d9a441': X('dial', items=[(a, b, col)], bgimg='dark')
L = lambda head, items: X('list', img='dark', head=head, items=items)
def G(view, cities, main, zoom=(1.0, 1.1), w=1): return (w, 'geo', dict(view=view, zoom=zoom, cities=[(c, l, 22, 12) for c, l in cities], main=main, hl='Mexico'))

PRON = [('Badiraguato', 'Ba-dee-ra-gwah-to'), ('La Tuna', 'La Too-na'), ('Beltrán Leyva', 'Bel-trahn Lay-va'), ('Héctor Palma', 'Ek-tor Pal-ma'), ('Miguel Ángel Félix Gallardo', 'Mee-gel Ahn-hel Feh-leeks Ga-yar-do'), ('Félix Gallardo', 'Feh-leeks Ga-yar-do'), ('Agua Prieta', 'Ah-gwa Pree-eh-ta'), ('Juan Jesús Posadas Ocampo', 'Hwan Heh-soos Po-sah-das Oh-kahm-po'), ('Culiacán', 'Koo-lee-ah-kahn'), ('Emma Coronel', 'Emma Ko-ro-nel'), ('Joaquín Guzmán López', 'Wah-keen Gooz-mahn Lo-pes'), ('Ismael Zambada', 'Ees-ma-el Sam-bah-da'), ('Joaquín Guzmán', 'Wah-keen Gooz-mahn'), ('Guzmán', 'Gooz-mahn'), ('El Chapo', 'El Chah-po'), ('Chapo', 'Chah-po'), ('Altiplano', 'Al-tee-plah-no'), ('Almoloya de Juárez', 'Al-mo-lo-ya deh Hwah-res'), ('Toluca', 'To-loo-ka'), ('Puente Grande', 'Pwen-teh Gran-deh'), ('Jalisco', 'Ha-lees-ko'), ('Sinaloa', 'See-na-lo-ah'), ('Mazatlán', 'Ma-sat-lahn'), ('Enrique Peña Nieto', 'En-ree-keh Pen-ya Nyeh-to'), ('Kate del Castillo', 'Kate del Kas-tee-yo'), ('Los Mochis', 'Los Mo-chees'), ('Fausto Isidro Meza Flores', 'Fowsto Ee-seedro Meh-sa Flo-res'), ('Isidro', 'Ee-seedro'), ('Guasave', 'Gwa-sah-veh')]

VIEWS = {'mexico': (-118.5, -86.0, 14.0, 33.5), 'mxus': (-120, -70, 14, 42), 'central': (-104.5, -97.5, 18.0, 22.5), 'sinaloa': (-111.5, -104.0, 22.0, 28.0)}
CITIES = {'altiplano': (-99.75, 19.42), 'toluca': (-99.66, 19.29), 'cdmx': (-99.13, 19.43), 'puente': (-103.18, 20.56), 'gdl': (-103.35, 20.67), 'mazatlan': (-106.41, 23.25), 'mochis': (-108.99, 25.79), 'culiacan': (-107.39, 24.80), 'ny': (-73.99, 40.69), 'juarez': (-106.42, 31.69), 'florence': (-105.11, 38.39), 'guasave': (-108.47, 25.57)}
EXTRA_OLD = dict(o2=1.2, o4=1.0, a3=0.6, a4=0.4, b3=0.6, c3=0.8, d1=0.8, d4=1.0, e3=0.6, e5=1.2, f3=1.0, g1=0.8, g5=1.0, g6=1.0, h3=0.8, i3=0.6, i4=1.5, i5=2.5)
ROLL = ['dark']
EXTRA = dict(o2=1.2, o4=1.0, a3=0.8, a6=0.4, b1=0.8, b5=1.0, c2=0.8, d1=0.6, d4=0.8, e2=0.6, e4=0.8, f3=0.8, g1=0.8, g4=1.0, h4=0.6, h5=1.2, i3=0.8, j1=0.8, j6=1.0, j7=1.0, k4=0.8, l3=0.6, l4=1.5, l5=2.5)
_P = S3('prison', cap=None, a0=-2.2, a1=-1.4)
SEGROLL_OLD = dict(o=[S3('escape', phase='ride')], a=[S3('prison', a0=-1.0, a1=-0.3)], b=[S3('cart')], c=[S3('condo')], d=[S3('cell')], e=[S3('section'), S3('escape', phase='ride')], f=[S3('prison', a0=0.4, a1=1.2, hl='HIS CELL')], g=[S3('house', floors=2, lab='SAFE HOUSE', sewer=True), S3('chase')], h=[S3('court'), S3('adx')], i=[S3('prison', a0=1.5, a1=2.3)])


import os as _os
_IMG = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'img')
def I(n): return n if _os.path.exists(_os.path.join(_IMG, n + '.jpg')) else 'dark'
def PL(img, w=1, **k): return (w, 'plain', dict(img=I(img), **k))
AUTOTAG_OLD = dict(booking='DEA BOOKING PHOTO · JAN 2017', doj='U.S. DEPARTMENT OF JUSTICE PHOTO · 2017', dea='DEA PHOTO · JAN 19, 2017', arrive='ARRIVING IN NEW YORK · JAN 19, 2017 (DEA)', ex1c='U.S. GOVERNMENT TRIAL EXHIBIT 1C · 2019')
VIEWS.update({'border': (-112.5, -107.5, 30.3, 32.6), 'gdl': (-108, -86, 12, 24)})
CITIES.update({'latuna': (-107.35, 25.53), 'badiraguato': (-107.55, 25.36), 'aguaprieta': (-109.55, 31.33), 'douglas': (-109.55, 31.35), 'tijuana': (-117.04, 32.51), 'guatemala': (-90.51, 14.63), 'tapachula': (-92.26, 14.9)})
_M = (1, 'geo', dict(view='mexico', zoom=(1.0, 1.06), cities=[('culiacan', 'SINALOA', 22, 12)], main='culiacan', hl='Mexico'))
_S = (1, 'geo', dict(view='sinaloa', zoom=(1.0, 1.08), cities=[('culiacan', 'CULIACÁN', 22, 12), ('mazatlan', 'MAZATLÁN', 22, 12)], main='culiacan', hl='Mexico'))
_C = (1, 'geo', dict(view='central', zoom=(1.0, 1.08), cities=[('gdl', 'GUADALAJARA', 22, 12), ('cdmx', 'MEXICO CITY', 22, 12)], main='gdl', hl='Mexico'))
AUTOTAG = dict(booking='DEA BOOKING PHOTO · JAN 2017', doj='U.S. DEPARTMENT OF JUSTICE PHOTO · 2017', dea='DEA PHOTO · JAN 19, 2017', arrive='ARRIVING IN NEW YORK · JAN 19, 2017 (DEA)', ex1c='U.S. GOVERNMENT TRIAL EXHIBIT 1C · 2019', uniform="EL CHAPO'S MEXICAN PRISON UNIFORM (DEA PHOTO)", tunnel='OTAY MESA TUNNEL · DISCOVERED JAN 2006 (DEA GRAPHIC)', badi='BADIRAGUATO, SINALOA', sierra='THE SIERRA, SINALOA', culiacan='CULIACÁN, SINALOA', mzt1='THE MALECÓN, MAZATLÁN', mzt2='MAZATLÁN', gdlair='GUADALAJARA AIRPORT TODAY', border1='DOUGLAS-AGUA PRIETA PORT OF ENTRY · 2026 (USDA)', bkfed='FEDERAL COURTHOUSE, BROOKLYN', adx='ADX FLORENCE, COLORADO (BOP)', epn='ENRIQUE PEÑA NIETO', holder='ERIC HOLDER, U.S. ATTORNEY GENERAL', penn='SEAN PENN (FILE PHOTO)', marines='MEXICAN NAVY MARINES IN TRAINING (FILE PHOTO)', marines2='MEXICAN NAVY MARINES (FILE PHOTO)')
SEGROLL = dict(o=[PL('doj'), PL('dea')], a=[PL('badi'), (1, 'geo', dict(view='sinaloa', zoom=(1.0, 1.08), cities=[('culiacan', 'CULIACÁN', 22, 12)], main='culiacan', hl='Mexico'))], b=[PL('border1'), PL('tunnel')], c=[PL('gdlair'), _C], d=[_C, _M], e=[PL('mzt2'), PL('marines')], f=[PL('uniform'), S3('prison', a0=-0.8, a1=-0.2)], g=[S3('cell'), PL('booking')], h=[S3('section'), PL('dea'), _C], i=[PL('doj'), _M], j=[PL('marines', z0=1.1, z1=1.0), _S], k=[PL('bkfed'), PL('dea')], l=[_S, PL('uniform'), _M])
CAP = (4.5, 5.5)

PLAN = {
    'o1': [PL('dea', z0=1.0, z1=1.12), D('JULY 11, 2015', 'ALTIPLANO PRISON · 8:52 P.M.', '#b3302a')],
    'o2': [PL('booking', z0=1.05, z1=1.18)],
    'o3': [S3('escape', phase='dive', cap='UNDER THE SHOWER'), S3('escape', phase='ride', cap='~1.5 KILOMETERS')],
    'o4': [PL('doj', z0=1.0, z1=1.1), X('dial', items=[('2001', 'FIRST ESCAPE', '#cfcfcf'), ('2015', 'SECOND ESCAPE', '#b3302a')], vs=False, bgimg='dark')],
    'ch1': [X('chapter', num=1, title='The Boy from La Tuna', bgimg=I('badi'))],
    'a1': [PL('badi', z0=1.0, z1=1.12), G('sinaloa', [('latuna', 'LA TUNA'), ('culiacan', 'CULIACÁN')], 'latuna')],
    'a2': [PL('badi'), L('THE MOUNTAINS', ['MARIJUANA', 'OPIUM POPPIES', 'GROWING AT 15 (REPORTED)', 'COUSINS: THE BELTRÁN LEYVAS'])],
    'a3': [Q(['"EL *CHAPO"', 'SHORTY'])],
    'a4': [(1, 'geo', dict(view='sinaloa', zoom=(1.0, 1.08), cities=[('culiacan', 'CULIACÁN', 22, 12)], main='culiacan', hl='Mexico')), L('HIS RISE (PUBLISHED ACCOUNTS)', ['HÉCTOR "EL GÜERO" PALMA', 'MIGUEL ÁNGEL FÉLIX GALLARDO', 'THE GUADALAJARA CARTEL'])],
    'a5': [D('1989', 'FÉLIX GALLARDO ARRESTED · THE EMPIRE SPLITS', '#b3302a'), X('title', title='SINALOA CARTEL', sub='FROM THE SPLIT', size=140)],
    'a6': [X('title', title='SUBSCRIBE', sub='HOW THE MOST NOTORIOUS CRIMINALS AND PRISONS REALLY WORK', size=150)],
    'ch2': [X('chapter', num=2, title='Under the Border', bgimg=I('border1'))],
    'b1': [PL('border1', z0=1.0, z1=1.1), Q(['IF YOU CAN\'T GO OVER IT,', 'GO *UNDER IT'])],
    'b2': [PL('border1', z0=1.1, z1=1.2), S3('border', cap='AGUA PRIETA TO DOUGLAS', sub='DISCOVERED MAY 1990', la='AGUA PRIETA, SONORA', lb='DOUGLAS, ARIZONA')],
    'b3': [D('~1,500 FT', 'TIJUANA · 1993 · "TAJ MAHAL" (DEA)', '#b3302a'), PL('border1', z0=1.15, z1=1.05)],
    'b4': [PL('tunnel', z0=1.0, z1=1.12, f0=(0.5, 0.3), f1=(0.5, 0.7)), L('TIJUANA · 2011 (REPORTED)', ['ELEVATOR', 'ELECTRIC RAIL CARS', 'UNDER THE AIRPORT'])],
    'b5': [L('BEFORE HE NEEDED ONE', ['RAILS', 'LIGHTS', 'VENTILATION'])],
    'ch3': [X('chapter', num=3, title='The Airport', bgimg=I('gdlair'))],
    'c1': [PL('gdlair', z0=1.0, z1=1.12), D('MAY 24, 1993', 'GUADALAJARA AIRPORT', '#b3302a'), X('dial', items=[('CARDINAL POSADAS', 'KILLED', '#b3302a'), ('6', 'OTHERS KILLED', '#cfcfcf')], vs=False, bgimg='dark')],
    'c2': [X('dial', items=[('CROSSFIRE', 'OFFICIAL VERSION', '#cfcfcf'), ('DOUBTS', 'PARTS OF THE CHURCH', '#b3302a')], vs=True, bgimg='dark')],
    'c3': [G('gdl', [('tapachula', 'GUATEMALAN BORDER'), ('gdl', 'GUADALAJARA')], 'tapachula'), D('JUNE 9, 1993', 'ARRESTED BY THE GUATEMALAN ARMY', '#d9a441')],
    'c4': [D('20+ YEARS', 'SENTENCE', '#cfcfcf'), G('central', [('puente', 'PUENTE GRANDE'), ('gdl', 'GUADALAJARA')], 'puente')],
    'ch4': [X('chapter', num=4, title='The First Escape', bgimg='dark')],
    'd1': [D('JAN 19, 2001', 'PUENTE GRANDE', '#b3302a')],
    'd2': [L('PUBLISHED ACCOUNTS', ['A GUARD OPENED HIS CELL', 'A LAUNDRY CART', 'THE TRUNK OF A CAR'])],
    'd3': [L('AFTERWARDS', ['GUARDS BRIBED', 'DOZENS IMPLICATED', 'PRISON DIRECTOR JAILED', 'SOME DETAILS DISPUTED'])],
    'd4': [PL('mzt2', z0=1.1, z1=1.0), X('doc', head='FORBES', lines=['THE WORLD\'S BILLIONAIRES', '*JOAQUÍN GUZMÁN'])],
    'ch5': [X('chapter', num=5, title='Mazatlán', bgimg=I('mzt2'))],
    'e1': [(1, 'geo', dict(view='sinaloa', zoom=(1.0, 1.08), cities=[('culiacan', 'CULIACÁN', 22, 12)], main='culiacan', hl='Mexico')), D('FEB 16, 2014', 'CULIACÁN · A STEEL DOOR', '#cfcfcf')],
    'e2': [Q(['SECRET TUNNELS', 'BETWEEN *SEVERAL HOUSES']), PL('marines')],
    'e3': [PL('mzt2', z0=1.0, z1=1.12), G('sinaloa', [('mazatlan', 'MAZATLÁN'), ('culiacan', 'CULIACÁN')], 'mazatlan'), PL('mzt1'), D('FEB 22, 2014', '4TH FLOOR · ARRESTED', '#b3302a')],
    'e4': [Q(['"A *LANDMARK', 'ACHIEVEMENT"']), X('dial', items=[('ARRESTED', 'OFFICIAL ACCOUNT', '#d9a441'), ('QUESTIONED', 'LATER, BY A FEDERAL COURT', '#cfcfcf')], vs=False, bgimg='dark')],
    'ch6': [X('chapter', num=6, title='Altiplano', bgimg='dark')],
    'f1': [G('central', [('altiplano', 'ALTIPLANO'), ('toluca', 'TOLUCA'), ('cdmx', 'MEXICO CITY')], 'altiplano'), PL('uniform')],
    'f2': [L('PUBLISHED DESCRIPTIONS', ['~700 PRISONERS', 'WALLS UP TO 1 M THICK', 'RESTRICTED AIRSPACE', 'PHONE SIGNALS BLOCKED']), S3('prison', cap='ALTIPLANO')],
    'f3': [Q(['HE HAD BEEN', 'HERE *BEFORE']), PL('booking', z0=1.0, z1=1.1)],
    'ch7': [X('chapter', num=7, title='The Blind Spot', bgimg='dark')],
    'g1': [Q(['EVERY CELL', 'WATCHED BY *CAMERAS'])],
    'g2': [S3('cell', cap='THE CELL', w=1.4)],
    'g3': [PL('dea', z0=1.0, z1=1.12), D('8:52 P.M.', 'OUT OF VIEW', '#b3302a')],
    'g4': [Q(['AN OPENING', '*~50 CM WIDE']), X('doc', head='INVESTIGATORS', lines=['DUG UP FROM BELOW', '*EXACTLY UNDER HIS SHOWER'])],
    'ch8': [X('chapter', num=8, title='The Tunnel', bgimg='dark')],
    'h1': [S3('escape', phase='dive', cap='A SHAFT ~10 M DEEP')],
    'h2': [S3('section', cap='THE TUNNEL', hl='~1.7 M HIGH', wl='~75 CM WIDE'), S3('topdown', cap='~1.5 KILOMETERS', house='CONSTRUCTION SITE')],
    'h3': [L('INSIDE THE TUNNEL', ['ELECTRIC LIGHTS', 'AIR PIPES', 'A MOTORCYCLE ON RAILS (OFFICIALS)']), S3('escape', phase='ride', cap='A MOTORCYCLE ON RAILS', sub='ACCORDING TO MEXICAN OFFICIALS')],
    'h4': [Q(['A BUILDING', 'UNDER *CONSTRUCTION'])],
    'h5': [Q(['HOW DID THEY KNOW', 'WHERE HIS *CELL WAS?'])],
    'ch9': [X('chapter', num=9, title='Affront', bgimg='dark')],
    'i1': [X('dial', items=[('~120', 'STAFF ON DUTY', '#cfcfcf'), ('31', 'QUESTIONED', '#d9a441')], vs=False, bgimg='dark'), L('AFTERWARDS', ['PRISON DIRECTOR QUESTIONED', 'OFFICIALS CHARGED', 'NUMBERS DIFFER IN REPORTS'])],
    'i2': [Q(['PEÑA NIETO:', 'AN *AFFRONT']), D('60,000,000', 'PESOS · REWARD', '#d9a441')],
    'i3': [Q(['A SECOND ESCAPE:', '*"UNFORGIVABLE"']), X('doc', head='WALL STREET JOURNAL · JULY 2015', lines=['U.S. OFFICIALS SAID THEY HAD WARNED', '*AN ESCAPE WAS BEING PLOTTED'])],
    'ch10': [X('chapter', num=10, title='Black Swan', bgimg=I('marines'))],
    'j1': [PL('marines', z0=1.1, z1=1.0), D('6 MONTHS', 'THE MANHUNT', '#d9a441')],
    'j2': [PL('penn', z0=1.0, z1=1.1), D('OCT 2015', 'THE INTERVIEW · SEAN PENN AND KATE DEL CASTILLO', '#cfcfcf'), X('doc', head='ROLLING STONE · JAN 2016', lines=['"EL CHAPO SPEAKS"', '*SUBMARINES, AIRPLANES, TRUCKS, BOATS'])],
    'j3': [G('sinaloa', [('mochis', 'LOS MOCHIS'), ('culiacan', 'CULIACÁN')], 'mochis'), Q(['"GRANDMA"', 'IS *ARRIVING'])],
    'j4': [PL('marines', z0=1.0, z1=1.1), X('dial', items=[('5', 'GUNMEN KILLED', '#b3302a'), ('1', 'MARINE WOUNDED', '#cfcfcf')], vs=False, bgimg='dark')],
    'j5': [S3('house', floors=2, lab='SAFE HOUSE', sewer=True, cap='THE HIDDEN PASSAGE', sub='LOS MOCHIS · JAN 8, 2016')],
    'j6': [Q(['"YOU ARE ALL', 'GOING TO *DIE"']), L('ON THE HIGHWAY (REPORTED)', ['MONEY', 'PROPERTY', 'JOBS', 'REFUSED'])],
    'j7': [Q(['A MOTEL.', '*WAITING FOR THE MARINES']), PL('uniform', z0=1.0, z1=1.1)],
    'ch11': [X('chapter', num=11, title='Brooklyn', bgimg=I('bkfed'))],
    'k1': [PL('dea', z0=1.0, z1=1.08), G('mxus', [('juarez', 'CIUDAD JUÁREZ'), ('ny', 'NEW YORK')], 'ny', zoom=(1.0, 1.05))],
    'k2': [PL('bkfed', z0=1.0, z1=1.1), L('THE TRIAL', ['ANONYMOUS JURORS', 'ARMED ESCORTS', 'FORMER PARTNERS TESTIFY'])],
    'k3': [X('dial', items=[('FEB 12, 2019', 'GUILTY ON ALL COUNTS', '#b3302a'), ('JULY 17, 2019', 'LIFE + 30 YEARS', '#d9a441')], vs=False, bgimg='dark'), D('$12.6 BILLION', 'ORDERED TO FORFEIT', '#d9a441'), PL('booking', z0=1.05, z1=1.15)],
    'k4': [PL('adx', z0=1.0, z1=1.1), S3('adx', cap='ADX FLORENCE', sub='COLORADO')],
    'ch12': [X('chapter', num=12, title='The Prison Today', bgimg='dark')],
    'l1': [L('AFTER HIM', ['2021: EMMA CORONEL ARRESTED', '3-YEAR SENTENCE', '2024: SON + "EL MAYO" ZAMBADA ARRESTED']), D('JULY 2024', 'EL PASO, TEXAS', '#cfcfcf')],
    'l2': [PL('uniform'), Q(['ALTIPLANO', 'IS *STILL OPEN'])],
    'l3': [G('sinaloa', [('guasave', 'GUASAVE')], 'guasave'), X('fugitive', num='NOV 2026', alias='CHAPO ISIDRO', name='FAUSTO ISIDRO MEZA FLORES', lines=['FBI TEN MOST WANTED', 'REPORTED TRANSFER: ALTIPLANO'], stamp=None)],
    'l4': [Q(['CAN ALTIPLANO', '*HOLD HIM?'])],
    'l5': [X('title', title='CAN ALTIPLANO HOLD HIM?', sub='TELL US IN THE COMMENTS', size=110)],
}
MUSIC = [('o1', 'Interloper', 0.22), ('ch1', 'Long Note Four', 0.20), ('ch2', 'Investigations', 0.20), ('ch3', 'Darkling', 0.20), ('ch4', 'Crypto', 0.18), ('ch5', 'Hitman', 0.18), ('ch6', 'Ossuary 6 - Air', 0.22), ('ch7', 'Unseen Horrors', 0.18), ('ch8', 'Lightless Dawn', 0.20), ('ch9', 'Dark Times', 0.18), ('ch10', 'Mistake the Getaway', 0.18), ('ch11', 'Night Vigil', 0.20), ('ch12', 'Echoes of Time v2', 0.20)]
