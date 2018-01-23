import qb_common.parse as qbparse
from peewee import *

mysql_ini = qbparse.parse_ini_arguments('/etc/.pymysql-ini', 'mysqldb')
database = MySQLDatabase('MWA', **mysql_ini)
database.connect()

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Green2014(BaseModel):
    dej2000 = CharField(db_column='DEJ2000', null=True)
    dmaj = CharField(db_column='Dmaj', null=True)
    dmin = CharField(db_column='Dmin', null=True)
    names = CharField(db_column='Names', null=True)
    raj2000 = CharField(db_column='RAJ2000', null=True)
    s_1ghz_ = CharField(db_column='S(1GHz)', null=True)
    snr = CharField(db_column='SNR', null=True)
    _dej2000 = FloatField(db_column='_DEJ2000', null=True)
    _glat = FloatField(db_column='_Glat', null=True)
    _glon = FloatField(db_column='_Glon', null=True)
    _raj2000 = FloatField(db_column='_RAJ2000', null=True)
    alpha = CharField(null=True)
    idgreen_2014 = PrimaryKeyField(db_column='idGreen_2014')
    inmanitoba = CharField(db_column='inManitoba', null=True)
    l_s_1ghz_ = CharField(db_column='l_S(1GHz)', null=True)
    name = CharField(null=True)
    prdecj2000 = CharField(db_column='prDECJ2000', null=True)
    prraj2000 = CharField(db_column='prRAJ2000', null=True)
    type = CharField(null=True)
    u_dmin = CharField(db_column='u_Dmin', null=True)
    u_s_1ghz_ = CharField(db_column='u_S(1GHz)', null=True)
    u_alpha = CharField(null=True)

    class Meta:
        db_table = 'Green_2014'

class ManitobaCat(BaseModel):
    agile = CharField(db_column='AGILE', null=True)
    asca = CharField(db_column='ASCA', null=True)
    chandra = CharField(db_column='CHANDRA', null=True)
    fermi = CharField(db_column='FERMI', null=True)
    hess = CharField(db_column='HESS', null=True)
    id = CharField(db_column='ID', null=True)
    magic = CharField(db_column='MAGIC', null=True)
    milagro = CharField(db_column='MILAGRO', null=True)
    rosat = CharField(db_column='ROSAT', null=True)
    sn = CharField(db_column='SN', null=True)
    suzaku = CharField(db_column='SUZAKU', null=True)
    veritas = CharField(db_column='VERITAS', null=True)
    xmm = CharField(db_column='XMM', null=True)
    age = CharField(null=True)
    context = CharField(null=True)
    distance = CharField(null=True)
    idmanitoba_cat = PrimaryKeyField(db_column='idManitoba_cat')
    linkid = CharField(db_column='linkID', null=True)
    names = CharField(null=True)
    parsedid = CharField(db_column='parsedID', null=True)
    temp = CharField(null=True)
    type = CharField(null=True)

    class Meta:
        db_table = 'Manitoba_cat'

class ParsedManitobaCat(BaseModel):
    ddecj2000 = FloatField(db_column='DDECJ2000', null=True)
    draj2000 = FloatField(db_column='DRAJ2000', null=True)
    j2000_dec = CharField(db_column='J2000_DEC', null=True)
    j2000_ra = CharField(db_column='J2000_RA', null=True)
    j2000_from = CharField(db_column='J2000_from', null=True)
    x_ray_size = CharField(db_column='X_ray_size', null=True)
    age_pulsar = CharField(null=True)
    age_shell = CharField(null=True)
    cloud_interaction = CharField(null=True)
    constellation = CharField(null=True)
    context = CharField(null=True)
    distance_pulsar = CharField(null=True)
    distance_shell = CharField(null=True)
    idgreen_2014 = IntegerField(db_column='idGreen_2014', null=True, unique=True)
    idparsed_manitoba_cat = PrimaryKeyField(db_column='idParsed_Manitoba_cat')
    magnetic_field = CharField(null=True)
    majdiam = FloatField(db_column='majDiam', null=True)
    mindiam = FloatField(db_column='minDiam', null=True)
    name = CharField(null=True)
    other_names = CharField(null=True)
    previous_ids = CharField(db_column='previous_IDs', null=True)
    radio_index = CharField(null=True)
    radio_size = CharField(null=True)
    supernova_event = CharField(null=True)
    temp = CharField(null=True)
    type = CharField(null=True)
    unique = CharField(db_column='unique_ID', null=True)

    class Meta:
        db_table = 'Parsed_Manitoba_cat'

class Te(BaseModel):
    te = FloatField(db_column='Te', null=True)
    idpnmain = IntegerField(db_column='idPNMain', null=True, unique=True)
    reference = CharField(null=True)
    tmp = CharField(null=True)

    class Meta:
        db_table = 'Te'

class TeTmp(BaseModel):
    adf = FloatField(db_column='ADF', null=True)
    e_ne_n2_ = FloatField(db_column='E_Ne[N2]', null=True)
    e_ne_o2_ = FloatField(db_column='E_Ne[O2]', null=True)
    e_te_n2_ = FloatField(db_column='E_Te[N2]', null=True)
    e_te_o2_ = FloatField(db_column='E_Te[O2]', null=True)
    m = IntegerField(db_column='M', null=True)
    ne_n2_ = FloatField(db_column='Ne[N2]', null=True)
    ne_o2_ = FloatField(db_column='Ne[O2]', null=True)
    object = CharField(db_column='Object', null=True)
    simbadname = CharField(db_column='SimbadName', null=True)
    te_bj_ = FloatField(db_column='Te(Bj)', null=True)
    te_n2_ = FloatField(db_column='Te[N2]', null=True)
    te_o2_ = FloatField(db_column='Te[O2]', null=True)
    te_o3_ = FloatField(db_column='Te[O3]', null=True)
    _de = CharField(db_column='_DE', null=True)
    _ra = CharField(db_column='_RA', null=True)
    e1_ne_n2_ = FloatField(db_column='e1_Ne[N2]', null=True)
    e1_ne_o2_ = FloatField(db_column='e1_Ne[O2]', null=True)
    e1_te_n2_ = FloatField(db_column='e1_Te[N2]', null=True)
    e1_te_o2_ = FloatField(db_column='e1_Te[O2]', null=True)
    idpnmain = IntegerField(db_column='idPNMain', null=True)
    r_object = IntegerField(db_column='r_Object', null=True)
    r_te_bj_ = FloatField(db_column='r_Te(Bj)', null=True)
    r_te_o3_ = FloatField(db_column='r_Te[O3]', null=True)

    class Meta:
        db_table = 'Te_tmp'

class TeTmp2(BaseModel):
    e_ne_sii_ = FloatField(db_column='E_Ne[SII]', null=True)
    e_te_oiii_ = FloatField(db_column='E_Te[OIII]', null=True)
    ne_sii_ = FloatField(db_column='Ne[SII]', null=True)
    png = CharField(db_column='PNG', null=True)
    simbadname = CharField(db_column='SimbadName', null=True)
    te_oiii_ = FloatField(db_column='Te[OIII]', null=True)
    _de = CharField(db_column='_DE', null=True)
    _ra = CharField(db_column='_RA', null=True)
    e1_ne_sii_ = FloatField(db_column='e1_Ne[SII]', null=True)
    e1_te_oiii_ = FloatField(db_column='e1_Te[OIII]', null=True)
    idpnmain = IntegerField(db_column='idPNMain', null=True)
    n_png = CharField(db_column='n_PNG', null=True)
    q_ne_sii_ = CharField(db_column='q_Ne[SII]', null=True)
    q_te_oiii_ = CharField(db_column='q_Te[OIII]', null=True)

    class Meta:
        db_table = 'Te_tmp2'



class GleamResults(BaseModel):
    dej2000 = FloatField(db_column='DEJ2000', null=True)
    fintwide = FloatField(db_column='Fintwide', null=True)
    fpwide = FloatField(db_column='Fpwide', null=True)
    gleam = CharField(db_column='GLEAM', null=True)
    raj2000 = FloatField(db_column='RAJ2000', null=True)
    _1 = CharField(null=True)
    _dej2000 = FloatField(db_column='_DEJ2000', null=True)
    _raj2000 = FloatField(db_column='_RAJ2000', null=True)
    _r = CharField(null=True)
    eabsfpct = FloatField(db_column='eabsFpct', null=True)
    efitfpct = FloatField(db_column='efitFpct', null=True)
    name = IntegerField(null=True)

    class Meta:
        db_table = 'gleam_results'

class MwaCutoutsModel(BaseModel):
    BMAJ = FloatField(null=True)
    BMIN = FloatField(null=True)
    BPA = FloatField(null=True)
    BBLUR = FloatField(null=True)
    BUNIT = CharField(null=True)
    ddecj2000 = FloatField(db_column='DDECJ2000', null=True)
    draj2000 = FloatField(db_column='DRAJ2000', null=True)
    diam = FloatField(db_column='diam', null=True)
    catalogue = CharField(null=True)
    date = DateTimeField(null=True)
    band = CharField(db_column='band',null=True)
    idmwacutouts = PrimaryKeyField()
    imsize = FloatField(null=True)
    name = CharField(null=True)
    week = CharField(null=True)
    in_mos_image = CharField(null=True, unique=True)
    out_mos_image = CharField(null=True, unique=True)
    in_bkg_image = CharField(null=True, unique=True)
    out_bkg_image = CharField(null=True, unique=True)
    in_rms_image = CharField(null=True, unique=True)
    out_rms_image = CharField(null=True, unique=True)
    out_rebkg_image = CharField(null=True, unique=True)
    out_corr_image = CharField(null=True, unique=True)
    out_vo_image = CharField(null=True, unique=True)

    class Meta:
        db_table = 'mwacutouts'



class PneDetected(BaseModel):
    ddecj2000 = FloatField(db_column='DDECJ2000', null=True)
    decj2000 = CharField(db_column='DECJ2000', null=True)
    draj2000 = FloatField(db_column='DRAJ2000', null=True)
    majdiam = FloatField(db_column='MajDiam', null=True)
    raj2000 = CharField(db_column='RAJ2000', null=True)
    detected = CharField(null=True)
    idpnmain = IntegerField(db_column='idPNMain', null=True)
    idpne_detected = PrimaryKeyField()
    name = CharField(null=True, unique=True)
    skip_aegean = CharField(null=True)

    class Meta:
        db_table = 'pne_detected'


class Galacticsnrs(BaseModel):
    catalogue = CharField(db_column='Catalogue', null=True)
    coordsource = CharField(db_column='CoordSource', null=True)
    ddecj2000 = FloatField(db_column='DDECJ2000', null=True)
    decj2000 = CharField(db_column='DECJ2000', null=True)
    draj2000 = FloatField(db_column='DRAJ2000', null=True)
    diamsource = CharField(db_column='DiamSource', null=True)
    glat = FloatField(db_column='Glat', null=True)
    glon = FloatField(db_column='Glon', null=True)
    majdiam = FloatField(db_column='MajDiam', null=True)
    mindiam = FloatField(db_column='MinDiam', null=True)
    padiam = FloatField(db_column='PADiam', null=True)
    raj2000 = CharField(db_column='RAJ2000', null=True)
    idgalacticsnrs = PrimaryKeyField(db_column='idGalacticSNRs')
    name = CharField(null=True, unique=True)

    class Meta:
        db_table = 'GalacticSNRs'


class Photometry(BaseModel):
    annulus_in = FloatField(null=True)
    annulus_out = FloatField(null=True)
    use_blur = FloatField(null=True)
    use_bmaj = FloatField(null=True)
    use_bmin = FloatField(null=True)
    use_bpa = FloatField(null=True)
    conv = CharField(null=True)
    fit_posdec = FloatField(db_column='fit_posDEC', null=True)
    fit_posra = FloatField(db_column='fit_posRA', null=True)
    flux = FloatField(null=True)
    flux_err = FloatField(null=True)
    flux_unit = CharField(null=True)
    band = CharField(null=True)
    freqHz = IntegerField(db_column='freqHz', null=True)
    imfile = CharField(null=True, unique=True)
    inimage = CharField(null=True, unique=True)
    ispoint = CharField(null=True)
    m0 = FloatField(null=True)
    m1 = FloatField(null=True)
    maj_ax = FloatField(null=True)
    maj_ax_unit = CharField(null=True)
    maj_ax_err = FloatField(null=True)
    maj_ax_err_unit = CharField(null=True)
    maskedpng = CharField(null=True)
    mean = FloatField(null=True)
    medabsdevmed = FloatField(null=True)
    median = FloatField(null=True)
    min = FloatField(null=True)
    min_ax = FloatField(null=True)
    min_ax_unit = CharField(null=True)
    min_ax_err = FloatField(null=True)
    min_ax_err_unit = CharField(null=True)
    modelfile = CharField(null=True, unique=True)
    modelfits = CharField(null=True, unique=True)
    name = CharField(null=True)
    npts = IntegerField(null=True)
    noise_det = CharField(null=True)
    off_lat = FloatField(null=True)
    off_lat_unit = CharField(null=True)
    off_long = FloatField(null=True)
    off_long_unit = CharField(null=True)
    peak = FloatField(null=True)
    peak_err = FloatField(null=True)
    peak_unit = CharField(null=True)
    pngfile = CharField(null=True, unique=True)
    pa = FloatField(null=True)
    pa_unit = CharField(null=True)
    pa_err = FloatField(null=True)
    pa_err_unit  = CharField(null=True)
    q1 = FloatField(null=True)
    q3 = FloatField(null=True)
    quartile = FloatField(null=True)
    radius = FloatField(null=True)
    rms = FloatField(null=True)
    sigma = FloatField(null=True)
    sum = FloatField(null=True)
    summaryfile = CharField(null=True)
    sumsq = FloatField(null=True)
    type = CharField(null=True)
    use = CharField(null=True)
    visual_det = CharField(null=True)
    week = CharField(null=True)
    aprtr_sum = FloatField(null=True)
    aprtr_sigma = FloatField(null=True)
    aprtr_flux = FloatField(null=True)
    aprtr_mean = FloatField(null=True)
    aprtr_npts = FloatField(null=True)
    conf_level = FloatField(null=True)
    blob_dSNR = FloatField(null=True)
    blob_fSNR = FloatField(null=True)
    blob_minpix = FloatField(null=True)
    blob_sum = FloatField(null=True)
    blob_sigma = FloatField(null=True)
    blob_flux = FloatField(null=True)
    blob_mean = FloatField(null=True)
    blob_npts = FloatField(null=True)
    pick_flux = CharField(null=True)

    class Meta:
        db_table = 'Photometry'

