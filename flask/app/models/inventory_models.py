import email
from email.policy import default
from turtle import position
from app import db
from sqlalchemy import ForeignKey
from datetime import datetime
import pytz


class Phy_Table(db.Model):
    __tablename__ = 'phy_table'
    site_id = db.Column(db.String(50), primary_key=True)
    region = db.Column(db.String(50))
    site_name = db.Column(db.String(50))
    latitude = db.Column(db.String(70))
    longitude = db.Column(db.String(70))
    city = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    status = db.Column(db.String(50))
    total_count = db.Column(db.Integer)
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    site_type = db.Column(db.String(100))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Rack_Table(db.Model):
    __tablename__ = 'rack_table'
    rack_id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.String(50), ForeignKey('phy_table.site_id'))
    rack_name = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    manufactuer_date = db.Column(db.Date, default=datetime(2000,1, 1))
    unit_position = db.Column(db.String(20))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz)) 
    status = db.Column(db.String(50))
    ru = db.Column(db.Integer)
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    height = db.Column(db.Integer)
    width = db.Column(db.Integer)
    depth = db.Column(db.Integer)
    pn_code = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    rack_model = db.Column(db.String(50))
    floor = db.Column(db.String(50))
    total_count = db.Column(db.Integer)
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Device_Table(db.Model):
    __tablename__ = 'device_table'
    device_id = db.Column(db.String(50), primary_key=True)
    site_id = db.Column(db.String(50), ForeignKey('phy_table.site_id'))
    rack_id = db.Column(db.Integer, ForeignKey('rack_table.rack_id'))
    ne_ip_address = db.Column(db.String(50))
    software_version = db.Column(db.String(50))
    patch_version = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz))#, onupdate=datetime.now(tz)) 
    status = db.Column(db.String(50))
    ru = db.Column(db.Integer)
    department = db.Column(db.String(50))
    section = db.Column(db.String(50))
    criticality = db.Column(db.String(20))
    function = db.Column(db.String(50))
    domain = db.Column(db.String(50))
    cisco_domain = db.Column(db.String(50))
    manufacturer = db.Column(db.String(50))
    hw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    hw_eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    sw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    sw_eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    virtual = db.Column(db.String(20))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    authentication = db.Column(db.String(10))
    serial_number = db.Column(db.String(50))
    pn_code = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    subrack_id_number = db.Column(db.String(50))
    manufactuer_date = db.Column(db.Date, default=datetime(2000,1, 1))
    hardware_version = db.Column(db.String(50))
    max_power = db.Column(db.String(50))
    device_name = db.Column(db.String(150))
    site_type = db.Column(db.String(50))
    source = db.Column(db.String(50))
    stack = db.Column(db.String(50))
    contract_number = db.Column(db.String(50))
    contract_expiry = db.Column(db.Date, default=datetime(2022,12, 31))
    item_code = db.Column(db.String(50))
    item_desc = db.Column(db.String(250))
    clei = db.Column(db.String(50))
    ims_status = db.Column(db.String(50))
    ims_function = db.Column(db.String(500))
    parent = db.Column(db.String(150))
    vuln_fix_plan_status = db.Column(db.String(50))
    vuln_ops_severity = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    integrated_with_aaa = db.Column(db.String(50))
    integrated_with_paam = db.Column(db.String(50))
    approved_mbss = db.Column(db.String(50))
    mbss_implemented = db.Column(db.String(50))
    mbss_integration_check = db.Column(db.String(50))
    integrated_with_siem = db.Column(db.String(50))
    threat_cases = db.Column(db.String(50))
    vulnerability_scanning = db.Column(db.String(50))
    vulnerability_severity = db.Column(db.String(50))
    dismantle_date = db.Column(db.Date)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Board_Table(db.Model):
    __tablename__ = 'board_table'
    board_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), ForeignKey('phy_table.site_id'))
    board_name = db.Column(db.String(250))
    device_slot_id = db.Column(db.String(250))
    hardware_version = db.Column(db.String(50))
    software_version = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    manufactuer_date = db.Column(db.Date, default=datetime(2000,1, 1))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz)) 
    status = db.Column(db.String(50))
    eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    pn_code = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    item_code = db.Column(db.String(50))
    item_desc = db.Column(db.String(250))
    clei = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    dismantle_date = db.Column(db.Date)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Subboard_Table(db.Model):
    __tablename__ = 'subboard_table'
    subboard_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), ForeignKey('phy_table.site_id'))
    subboard_name = db.Column(db.String(250))
    subboard_type = db.Column(db.String(150))
    subrack_id = db.Column(db.String(250))
    slot_number = db.Column(db.String(250))
    subslot_number = db.Column(db.String(250))
    hardware_version = db.Column(db.String(50))
    software_version = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz)) 
    status = db.Column(db.String(50))
    eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    tag_id = db.Column(db.String(50))
    pn_code = db.Column(db.String(50)) 
    item_code = db.Column(db.String(50))
    item_desc = db.Column(db.String(250))
    clei = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    dismantle_date = db.Column(db.Date)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class SFP_Table(db.Model):
    __tablename__ = 'sfp_table'
    sfp_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), ForeignKey('phy_table.site_id'))
    media_type = db.Column(db.String(50))
    port_name = db.Column(db.String(250))
    port_type = db.Column(db.String(50))
    connector = db.Column(db.String(50))
    mode = db.Column(db.String(50))
    speed = db.Column(db.String(50))
    wavelength = db.Column(db.String(50))
    manufacturer = db.Column(db.String(250))
    optical_direction_type = db.Column(db.String(50))
    pn_code = db.Column(db.String(50)) 
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz)) 
    status = db.Column(db.String(50))
    eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    tag_id = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    item_code = db.Column(db.String(50))
    item_desc = db.Column(db.String(250))
    clei = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    dismantle_date = db.Column(db.Date)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class License_Table(db.Model):
    __tablename__ = 'license_table'
    license_id = db.Column(db.Integer, primary_key=True)
    license_name = db.Column(db.String(250))
    license_description = db.Column(db.String(250))
    ne_name = db.Column(db.String(50))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    activation_date = db.Column(db.Date, default=datetime(2000,1, 1))
    expiry_date = db.Column(db.Date, default=datetime(2000,1, 1))
    grace_period = db.Column(db.String(10))
    serial_number = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz)) 
    status = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    capacity = db.Column(db.String(50))
    usage = db.Column(db.String(50))
    pn_code = db.Column(db.String(50))
    item_code = db.Column(db.String(50))
    item_desc = db.Column(db.String(250))
    clei = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    dismantle_date = db.Column(db.Date)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Seed(db.Model):
    __tablename__ = 'seed_table'
    seed_id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.String(50))
    '''
    region = db.Column(db.String(50))
    site_name = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    city = db.Column(db.String(50))
    datacentre_status = db.Column(db.String(50))
    '''
    rack_id = db.Column(db.String(50))
    '''
    floor = db.Column(db.String(50))
    rack_name = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    manufactuer_date = db.Column(db.Date, default=datetime(2000,1, 1))
    unit_position = db.Column(db.String(20))
    rack_status = db.Column(db.String(50))
    ru = db.Column(db.Integer)
    
    height = db.Column(db.Integer)
    width = db.Column(db.Integer)
    depth = db.Column(db.Integer)
    pn_code = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    rack_model = db.Column(db.String(50))
    '''
    tag_id = db.Column(db.String(50))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    device_id = db.Column(db.String(50))
    ne_ip_address = db.Column(db.String(50))
    device_ru = db.Column(db.Integer)
    department = db.Column(db.String(50))
    section = db.Column(db.String(50))
    criticality = db.Column(db.String(20))
    function = db.Column(db.String(50))
    #domain = db.Column(db.String(50))
    cisco_domain = db.Column(db.String(50))
    virtual = db.Column(db.String(20))
    authentication = db.Column(db.String(20))
    subrack_id_number = db.Column(db.String(50))
    hostname = db.Column(db.String(50))
    sw_type = db.Column(db.String(50))
    vendor = db.Column(db.String(50))
    asset_type = db.Column(db.String(50))
    operation_status = db.Column(db.String(50))
    onboard_status = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    contract_number = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    contract_expiry = db.Column(db.Date, default=datetime(2022,12, 31))
    item_code = db.Column(db.String(50))
    item_desc = db.Column(db.String(250))
    clei = db.Column(db.String(50))
    parent = db.Column(db.String(150))
    vuln_fix_plan_status = db.Column(db.String(50))
    vuln_ops_severity = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    integrated_with_aaa = db.Column(db.String(50))
    integrated_with_paam = db.Column(db.String(50))
    approved_mbss = db.Column(db.String(50))
    mbss_implemented = db.Column(db.String(50))
    mbss_integration_check = db.Column(db.String(50))
    integrated_with_siem = db.Column(db.String(50))
    threat_cases = db.Column(db.String(50))
    vulnerability_scanning = db.Column(db.String(50))
    vulnerability_severity = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_NET_Seed(db.Model):
    __tablename__ = 'edn_net_seed'
    edn_net_seed_id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50))
    segment = db.Column(db.String(50))
    switch_id = db.Column(db.String(250))
    switch_ip_address = db.Column(db.String(70))
    vendor = db.Column(db.String(50))
    os_type = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_SEC_Seed(db.Model):
    __tablename__ = 'edn_sec_seed'
    edn_sec_seed_id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50))
    segment = db.Column(db.String(50))
    fw_id = db.Column(db.String(250))
    fw_ip_address = db.Column(db.String(70))
    vendor = db.Column(db.String(50))
    os_type = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_Mapping(db.Model):
    __tablename__ = 'edn_mapping'
    edn_id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50))
    segment = db.Column(db.String(50))
    switch_name = db.Column(db.String(250))
    mac_address = db.Column(db.String(70))
    switch_interface = db.Column(db.String(250))
    interface_description = db.Column(db.String(250))
    vlan = db.Column(db.String(250))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    server_name = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    application_name= db.Column(db.String(50))
    owner_email= db.Column(db.String(50))
    owner_contact = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_IT_Seed(db.Model):
    __tablename__ = 'edn_it_seed'
    edn_it_seed_id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(250))
    ip_address = db.Column(db.String(50))
    application_name = db.Column(db.String(250))
    owner_email = db.Column(db.String(70))
    owner_contact = db.Column(db.String(70))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class SNTC_Table(db.Model):
    __tablename__ = 'sntc_table'
    sntc_id = db.Column(db.Integer, primary_key=True)
    pn_code = db.Column(db.String(50))
    hw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    hw_eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    sw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    sw_eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    manufactuer_date = db.Column(db.Date, default=datetime(2030,1, 1))
    item_desc = db.Column(db.String(250))
    item_code = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    vuln_fix_plan_status = db.Column(db.String(50))
    vuln_ops_severity = db.Column(db.String(50))


    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class PnCode_SNAP_Table(db.Model):
    __tablename__ = 'pncode_snap_table'
    id = db.Column(db.Integer, primary_key=True)
    pn_code = db.Column(db.String(50))
    igw_net = db.Column(db.Integer, default=0)
    igw_sys = db.Column(db.Integer, default=0)
    edn_net = db.Column(db.Integer, default=0)
    edn_sys = db.Column(db.Integer, default=0)
    edn_ipt = db.Column(db.Integer, default=0)
    edn_ipt_endpoints = db.Column(db.Integer, default=0)
    soc = db.Column(db.Integer, default=0)
    edn_ap = db.Column(db.Integer, default=0)
    rebd = db.Column(db.Integer, default=0)
    pos = db.Column(db.Integer, default=0)
    cdn = db.Column(db.Integer,default=0)
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User_Table(db.Model):
    __tablename__ = 'user_table'
    user_id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    role = db.Column(db.String(10))
    status = db.Column(db.String(10))
    account_type = db.Column(db.String(15))
    password = db.Column(db.String(512))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    last_login = db.Column(db.DateTime, default=datetime.now(tz))
    team = db.Column(db.String(20))
    vendor = db.Column(db.String(20))

    #token = db.Column(db.String(500))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IPT_Endpoints_Table(db.Model):
    __tablename__ = 'ipt_endpoints_table'
    hostname = db.Column(db.String(50), primary_key=True)
    ip_address = db.Column(db.String(50))
    mac_address = db.Column(db.String(50))
    user = db.Column(db.String(50))
    product_id = db.Column(db.String(50))
    description = db.Column(db.String(150))
    firmware = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    rfs_date = db.Column(db.Date)
    tag_id = db.Column(db.String(50))
    protocol = db.Column(db.String(50))
    calling_search_space = db.Column(db.String(50))
    device_pool_name = db.Column(db.String(50))
    location_name = db.Column(db.String(50))
    resource_list_name = db.Column(db.String(50))
    status = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    extensions = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IGW_IPAM_TABLE(db.Model):
    __tablename__='igw_ipam_table'
    id = db.Column(db.Integer,primary_key=True)
    region = db.Column(db.String(50))
    site_id = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    subnet_mask = db.Column(db.String(50))
    subnet = db.Column(db.String(50))
    interface_name = db.Column(db.String(50))
    protocol_status = db.Column(db.String(50))
    admin_status = db.Column(db.String(50))
    vlan = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    vlan_name = db.Column(db.String(50))
    virtual_ip = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    management_ip = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

class EDN_IPAM_TABLE(db.Model):
    __tablename__='edn_ipam_table'
    id = db.Column(db.Integer,primary_key=True)
    region = db.Column(db.String(50))
    site_id = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    subnet_mask = db.Column(db.String(50))
    subnet = db.Column(db.String(50))
    interface_name = db.Column(db.String(50))
    protocol_status = db.Column(db.String(50))
    admin_status = db.Column(db.String(50))
    vlan = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    vlan_name = db.Column(db.String(50))  
    virtual_ip = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    management_ip = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

class SOC_IPAM_TABLE(db.Model):
    __tablename__='soc_ipam_table'
    id = db.Column(db.Integer,primary_key=True)
    region = db.Column(db.String(50))
    site_id = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    subnet_mask = db.Column(db.String(50))
    subnet = db.Column(db.String(50))
    interface_name = db.Column(db.String(50))
    protocol_status = db.Column(db.String(50))
    admin_status = db.Column(db.String(50))
    vlan = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    vlan_name = db.Column(db.String(50))  
    virtual_ip = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    management_ip = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
        
class CDN_Table(db.Model):
    __tablename__ = 'cdn_table'
    technology = db.Column(db.String(50), primary_key=True)
    count = db.Column(db.Integer)
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

class POWER_FEEDS_TABLE(db.Model):
    __tablename__ = 'power_feeds_table'
    power_id= db.Column(db.Integer, primary_key=True)
    device_id= db.Column(db.String(50), ForeignKey('device_table.device_id'))
    #rack_id = db.Column(db.String(50), ForeignKey('rack_table.rack_id'))
    #site_id = db.Column(db.String(50), ForeignKey('phy_table.site_id'))
    power_source_type = db.Column(db.String(50)) ## Dummy primary key due to SQL Alchemy contraint
    number_of_power_sources = db.Column(db.String(50))
    psu1_fuse = db.Column(db.String(50))
    psu2_fuse = db.Column(db.String(50))
    psu3_fuse = db.Column(db.String(50))
    psu4_fuse = db.Column(db.String(50))
    psu5_fuse = db.Column(db.String(50))
    psu6_fuse = db.Column(db.String(50))
    psu1_pdu_details = db.Column(db.String(50))
    psu2_pdu_details = db.Column(db.String(50))
    psu3_pdu_details = db.Column(db.String(50))
    psu4_pdu_details = db.Column(db.String(50))
    psu5_pdu_details = db.Column(db.String(50))
    psu6_pdu_details = db.Column(db.String(50))
    psu1_dcdp_details = db.Column(db.String(50))
    psu2_dcdp_details = db.Column(db.String(50))
    psu3_dcdp_details = db.Column(db.String(50))
    psu4_dcdp_details = db.Column(db.String(50))
    psu5_dcdp_details = db.Column(db.String(50))
    psu6_dcdp_details = db.Column(db.String(50))
    status = db.Column(db.String(50))
    #created_by = db.Column(db.String(50))
    #modified_by = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    #creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    #modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz)) 
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    
class INVENTORY_SCRIPTS_STATUS(db.Model):
    __tablename__ = 'inventory_scripts_status'
    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String(50))
    status = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))

class EDN_DC_CAPACITY(db.Model):
    __tablename__ = 'edn_dc_capacity'
    edn_dc_capacity_id = db.Column(db.Integer,primary_key=True)
    device_ip= db.Column(db.String(50))
    site_id = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    os_version = db.Column(db.String(50))
    total_1g_ports = db.Column(db.Integer)
    total_10g_ports = db.Column(db.Integer)
    total_25g_ports = db.Column(db.Integer)
    total_40g_ports = db.Column(db.Integer)
    total_100g_ports = db.Column(db.Integer)
    total_fast_ethernet_ports = db.Column(db.Integer)
    connected_1g = db.Column(db.Integer)
    connected_10g = db.Column(db.Integer)
    connected_25g = db.Column(db.Integer)
    connected_40g = db.Column(db.Integer)
    connected_100g = db.Column(db.Integer)
    connected_fast_ethernet = db.Column(db.Integer)
    not_connected_1g = db.Column(db.Integer)
    not_connected_10g = db.Column(db.Integer)
    not_connected_25g = db.Column(db.Integer)
    not_connected_40g = db.Column(db.Integer)
    not_connected_100g = db.Column(db.Integer)
    not_connected_fast_ethernet = db.Column(db.Integer)
    unused_sfps_1g = db.Column(db.Integer)
    unused_sfps_10g = db.Column(db.Integer)
    unused_sfps_25g = db.Column(db.Integer)
    unused_sfps_40g = db.Column(db.Integer)
    unused_sfps_100g = db.Column(db.Integer)
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

class IGW_DC_CAPACITY(db.Model):
    __tablename__ = 'igw_dc_capacity'
    igw_dc_capacity_id = db.Column(db.Integer,primary_key=True)
    device_ip= db.Column(db.String(50))
    site_id = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    os_version = db.Column(db.String(50))
    total_1g_ports = db.Column(db.Integer)
    total_10g_ports = db.Column(db.Integer)
    total_25g_ports = db.Column(db.Integer)
    total_40g_ports = db.Column(db.Integer)
    total_100g_ports = db.Column(db.Integer)
    total_fast_ethernet_ports = db.Column(db.Integer)
    connected_1g = db.Column(db.Integer)
    connected_10g = db.Column(db.Integer)
    connected_25g = db.Column(db.Integer)
    connected_40g = db.Column(db.Integer)
    connected_100g = db.Column(db.Integer)
    connected_fast_ethernet = db.Column(db.Integer)
    not_connected_1g = db.Column(db.Integer)
    not_connected_10g = db.Column(db.Integer)
    not_connected_25g = db.Column(db.Integer)
    not_connected_40g = db.Column(db.Integer)
    not_connected_100g = db.Column(db.Integer)
    not_connected_fast_ethernet = db.Column(db.Integer)
    unused_sfps_1g = db.Column(db.Integer)
    unused_sfps_10g = db.Column(db.Integer)
    unused_sfps_25g = db.Column(db.Integer)
    unused_sfps_40g = db.Column(db.Integer)
    unused_sfps_100g = db.Column(db.Integer)
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))  
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))  
class EDN_EXCHANGE(db.Model):
    __tablename__ = 'edn_exchange'
    edn_exchange_id = db.Column(db.Integer,primary_key=True)
    device_ip= db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    vrf_name = db.Column(db.String(500))
    rd = db.Column(db.String(50))
    interfaces = db.Column(db.String(500))
    ibgp_ip = db.Column(db.String(50))
    ibgp_as = db.Column(db.String(50))
    ibgp_up_time = db.Column(db.String(50))
    ibgp_prefix = db.Column(db.String(50))
    ebgp_ip = db.Column(db.String(50))
    ebgp_as = db.Column(db.String(50))
    ebgp_up_time = db.Column(db.String(50))
    ebgp_prefix = db.Column(db.String(50))
    ebgp_advertised_routes = db.Column(db.String(3000))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(500))
    region = db.Column(db.String(50))
    site_id = db.Column(db.String(512))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

class EDN_CORE_ROUTING(db.Model):
    __tablename__ = 'edn_core_routing'
    edn_core_routing_id = db.Column(db.Integer,primary_key=True)
    device_ip= db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    subnet = db.Column(db.String(100))
    route_type = db.Column(db.String(50))
    next_hop = db.Column(db.String(50))
    originated_from_ip = db.Column(db.String(50))
    originator_name = db.Column(db.String(50))
    route_age = db.Column(db.String(50))
    process_id = db.Column(db.String(50))
    cost = db.Column(db.String(50))
    out_going_interface = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    region = db.Column(db.String(50))
    site_id = db.Column(db.String(512))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
class VRF_OWNERS(db.Model):
    __tablename__ = 'vrf_owners'
    vrf_owners_id = db.Column(db.Integer,primary_key=True)
    vrf_name = db.Column(db.String(500))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(500))
    owner_contact = db.Column(db.String(512))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

class VRF_ROUTES(db.Model):
    __tablename__ = 'vrf_routes'
    vrf_route_id = db.Column(db.Integer,primary_key=True)
    device_ip= db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    vrf_name = db.Column(db.String(500))
    route = db.Column(db.String(500))
    next_hop = db.Column(db.String(500))
    as_path = db.Column(db.String(500))
    origin = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))


class Access_Points_Table(db.Model):
    __tablename__ = 'access_points_table'
    access_point_id = db.Column(db.Integer,primary_key=True)
    device_id = db.Column(db.String(50))
    wlc_name = db.Column(db.String(50))
    site_id = db.Column(db.String(50) )
    ne_ip_address = db.Column(db.String(50))
    software_version = db.Column(db.String(50))
    patch_version = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz)) 
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    status = db.Column(db.String(50))
    ru = db.Column(db.Integer)
    department = db.Column(db.String(50))
    section = db.Column(db.String(50))
    criticality = db.Column(db.String(20))
    function = db.Column(db.String(50))
    domain = db.Column(db.String(50))
    cisco_domain = db.Column(db.String(50))
    manufacturer = db.Column(db.String(50))
    hw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    hw_eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    sw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    sw_eol_date = db.Column(db.Date, default=datetime(2030,1, 1))
    virtual = db.Column(db.String(20))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    authentication = db.Column(db.String(10))
    serial_number = db.Column(db.String(50))
    pn_code = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    subrack_id_number = db.Column(db.String(50))
    manufactuer_date = db.Column(db.Date, default=datetime(2000,1, 1))
    hardware_version = db.Column(db.String(50))
    max_power = db.Column(db.String(50))
    device_name = db.Column(db.String(150))
    site_type = db.Column(db.String(50))
    source = db.Column(db.String(50))
    stack = db.Column(db.String(50))
    contract_number = db.Column(db.String(50))
    contract_expiry = db.Column(db.Date, default=datetime(2022,12, 31))
    item_code = db.Column(db.String(50))
    item_desc = db.Column(db.String(250))
    clei = db.Column(db.String(50))
    ims_status = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Rebd_Table(db.Model):
    __tablename__ = 'rebd_table'
    rebd_id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.String(50))
    rack_id = db.Column(db.String(50))
    region = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    city = db.Column(db.String(50))
    floor = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    pn_code = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    device_id = db.Column(db.String(50))
    ne_ip_address = db.Column(db.String(50))
    device_ru = db.Column(db.Integer)
    department = db.Column(db.String(50))
    section = db.Column(db.String(50))
    criticality = db.Column(db.String(20))
    function = db.Column(db.String(50))
    domain = db.Column(db.String(50))
    virtual = db.Column(db.String(20))
    authentication = db.Column(db.String(20))
    hostname = db.Column(db.String(50))
    sw_type = db.Column(db.String(50))
    vendor = db.Column(db.String(50))
    operation_status = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    contract_number = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    contract_expiry = db.Column(db.Date, default=datetime(2022,12, 31))
    stack = db.Column(db.Integer)
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class Pos_Table(db.Model):
    __tablename__ = 'pos_table'
    pos_id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.String(50))
    rack_id = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    longitude= db.Column(db.String(50))
    region = db.Column(db.String(50))
    city = db.Column(db.String(50))
    floor = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    pn_code = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    rfs_date = db.Column(db.Date, default=datetime(2012,1, 1))
    device_id = db.Column(db.String(50))
    ne_ip_address = db.Column(db.String(50))
    device_ru = db.Column(db.Integer)
    department = db.Column(db.String(50))
    section = db.Column(db.String(50))
    criticality = db.Column(db.String(20))
    function = db.Column(db.String(50))
    domain = db.Column(db.String(50))
    virtual = db.Column(db.String(20))
    authentication = db.Column(db.String(20))
    hostname = db.Column(db.String(50))
    sw_type = db.Column(db.String(50))
    vendor = db.Column(db.String(50))
    operation_status = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    contract_number = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    contract_expiry = db.Column(db.Date, default=datetime(2022,12, 31))
    #asset_type = db.Column(db.String(50))
    #subrack_id_number = db.Column(db.String(50))
    stack = db.Column(db.Integer)
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FUNCTIONS_TABLE(db.Model):
    __tablename__ = 'functions_table'
    function_id = db.Column(db.Integer, primary_key=True)
    tfun = db.Column(db.String(50))
    function = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

class EDN_IOS_TRACKER(db.Model):
    __tablename__ = 'edn_ios_tracker'
    id = db.Column(db.Integer)
    device_id = db.Column(db.String(50), primary_key=True)   
    ip_address = db.Column(db.String(50))
    site_id = db.Column(db.String(50))
    region = db.Column(db.String(50))
    pid = db.Column(db.String(50))
    os_type = db.Column(db.String(50))
    current_os_version = db.Column(db.String(50))
    new_os_version = db.Column(db.String(50))
    assignee = db.Column(db.String(50))
    schedule = db.Column(db.Date, default=datetime(2030,1, 1))
    status = db.Column(db.String(50))    
    crq = db.Column(db.String(50))
    remarks = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))


    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_CMDB_TRACKER(db.Model):
    __tablename__ = 'edn_cmdb_tracker'
    id = db.Column(db.Integer, primary_key=True)
    crq_no = db.Column(db.String(50))
    activity_summary = db.Column(db.String(100))
    activity_type = db.Column(db.Text)
    approval_type = db.Column(db.Text)
    priority = db.Column(db.String(50))
    implementing_team = db.Column(db.Text)
    implementer = db.Column(db.Text)
    region = db.Column(db.Text)
    site = db.Column(db.String(100))
    date = db.Column(db.Date, default=datetime(2030,1, 1))
    status = db.Column(db.String(50))    
    service_impact = db.Column(db.String(100))
    domain = db.Column(db.Text)
    activity_category = db.Column(db.Text)
    ci = db.Column(db.String(100))
    reason_of_rollback = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))


    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_DEVICE_POWEROFF_TRACKER(db.Model):
    __tablename__ = 'edn_device_poweroff_tracker'
    poweroff_tracker_id = db.Column(db.Integer, primary_key=True)
    crq_no = db.Column(db.String(200))   
    ip_address = db.Column(db.String(100))
    device_id = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    serial_no = db.Column(db.String(50))
    function = db.Column(db.String(50))
    pn_code = db.Column(db.String(50))
    comments = db.Column(db.String(500))
    os_type = db.Column(db.String(50))
    region = db.Column(db.String(50))
    city = db.Column(db.String(50))
    site_name = db.Column(db.String(50))
    rack_name = db.Column(db.String(50))
    date_of_power_down = db.Column(db.Date, default=datetime(2000,1, 1))
    date_of_power_on = db.Column(db.Date, default=datetime(2000,1, 1))
    assigned_to = db.Column(db.String(500))    
    associated_circuit_id_details = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_HANDBACK_TRACKER(db.Model):
    __tablename__ = 'edn_handback_tracker'
    handback_tracker_id = db.Column(db.Integer, primary_key=True)
    crq_no = db.Column(db.String(200))   
    ip_address = db.Column(db.String(100))
    device_id = db.Column(db.String(50))
    tag_id = db.Column(db.String(50))
    region = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    function = db.Column(db.String(50))
    pn_code = db.Column(db.String(50))
    serial_no = db.Column(db.String(50))
    assigned_to = db.Column(db.String(50))
    handback_submission_date = db.Column(db.Date, default=datetime(2000,1, 1))
    handback_completion_date = db.Column(db.Date, default=datetime(2000,1, 1))
    handback_status = db.Column(db.String(50))    
    ip_decomissioning_crq = db.Column(db.String(100))
    project_representative = db.Column(db.String(100))
    po_no = db.Column(db.String(100))
    configuration_cleanup_status = db.Column(db.String(50))
    extra_old_devices = db.Column(db.String(100))
    associated_circuit_id_details = db.Column(db.String(100))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_HANDOVER_TRACKER(db.Model):
    __tablename__ = 'edn_handover_tracker'
    handover_tracker_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    project_type = db.Column(db.String(50))
    region = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    asset_type = db.Column(db.String(50))
    pn_code = db.Column(db.String(50))
    serial_no = db.Column(db.String(50))
    assigned_to = db.Column(db.String(50))
    handover_submission_date = db.Column(db.Date, default=datetime(2000,1, 1))
    handover_completion_date = db.Column(db.Date, default=datetime(2000,1, 1))
    handover_review_status = db.Column(db.String(50))    
    remedy_incident = db.Column(db.String(100))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    history = db.Column(db.Text)
    comment_history = db.Column(db.Text)
    onboard_status = db.Column(db.String(50))
    primary_handover_id = db.Column(db.String(50))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IP_ASSIGNMENT_TRACKER(db.Model):
    __tablename__ = 'ip_assignment_tracker'
    ip_assignment_tracker_id = db.Column(db.Integer, primary_key=True)
    employee_pf = db.Column(db.String(50))
    full_name = db.Column(db.String(50))
    organization = db.Column(db.String(50))
    position = db.Column(db.String(50))
    grade = db.Column(db.String(50))
    email = db.Column(db.String(50))
    ip_phone_model = db.Column(db.String(50))
    serial_no = db.Column(db.String(50))
    mac = db.Column(db.String(50))
    date_of_device_assignment = db.Column(db.Date, default=datetime(2030,1, 1))
    region = db.Column(db.String(50))
    registration_status = db.Column(db.String(50))
    assigned_by = db.Column(db.String(500))
    mobile_number = db.Column(db.String(100))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))


    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IP_CLEARANCE_TRACKER(db.Model):
    __tablename__ = 'ip_clearance_tracker'
    ip_clearance_tracker_id = db.Column(db.Integer, primary_key=True)
    employee_pf = db.Column(db.String(50))
    full_name = db.Column(db.String(50))
    organization = db.Column(db.String(50))
    position = db.Column(db.String(50))
    job = db.Column(db.String(50))
    grade = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    termination_date = db.Column(db.Date, default=datetime(2030,1, 1))
    email = db.Column(db.String(50))
    ipt_team_assignee = db.Column(db.String(50))
    ip_phone_model = db.Column(db.String(50))
    serial_no = db.Column(db.String(50))
    mac = db.Column(db.String(50))
    collection_date = db.Column(db.Date, default=datetime(2030,1, 1))
    region = db.Column(db.String(50))
    status = db.Column(db.String(50))
    remarks = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_PMR_TRACKER(db.Model):
    __tablename__ = 'edn_pmr_tracker'
    edn_pmr_tracker_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50) )
    ip_address = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    vendor = db.Column(db.String(50))
    model = db.Column(db.String(50))
    criticality = db.Column(db.String(50))
    domain = db.Column(db.String(50))
    virtual = db.Column(db.String(50))
    device_status = db.Column(db.String(500))
    device_remarks =db.Column(db.String(500))
    site_id = db.Column(db.String(50))
    site_type = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    longitude =db.Column(db.String(50))
    city = db.Column(db.String(50))
    region = db.Column(db.String(50))
    rack_id = db.Column(db.String(50))
    rack_name = db.Column(db.String(50))
    pmr_quarter = db.Column(db.String(500))
    pmr_crq = db.Column(db.String(500))
    pmr_date =  db.Column(db.Date)
    pmr_status = db.Column(db.String(500))
    pmr_remarks = db.Column(db.String(500))
    door_locks_status = db.Column(db.String(500))
    labels_status = db.Column(db.String(500))
    pmr_corrective_actions = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class DOMAINS_TABLE(db.Model):
    __tablename__ = 'domains_table'
    domain_id = db.Column(db.Integer, primary_key=True)
    cisco_domain = db.Column(db.String(50))
    department = db.Column(db.String(100))
    section = db.Column(db.String(100))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_EDN_IPAM(db.Model):
    __tablename__ = 'failed_devices_edn_ipam'
    edn_ipam_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class FAILED_DEVICES_IGW_IPAM(db.Model):
    __tablename__ = 'failed_devices_igw_ipam'
    igw_ipam_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class FAILED_DEVICES_SOC_IPAM(db.Model):
    __tablename__ = 'failed_devices_soc_ipam'
    soc_ipam_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_EDN_DC_CAPACITY(db.Model):
    __tablename__ = 'failed_devices_edn_dc_capacity'
    edn_dc_cpacity_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class FAILED_DEVICES_IGW_DC_CAPACITY(db.Model):
    __tablename__ = 'failed_devices_igw_dc_capacity'
    igw_dc_cpacity_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_ACCESS_POINTS(db.Model):
    __tablename__ = 'failed_devices_access_points'
    access_points_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_IPT_ENDPOINTS(db.Model):
    __tablename__ = 'failed_devices_ipt_endpoints'
    ipt_endpoints_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_EDN_EXCHANGE(db.Model):
    __tablename__ = 'failed_devices_edn_exchange'
    edn_exchange_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}				 						

class FAILED_DEVICES_EDN_LLDP(db.Model):
    __tablename__ = 'failed_devices_edn_lldp'
    edn_lldp_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_IGW_LLDP(db.Model):
    __tablename__ = 'failed_devices_igw_lldp'
    igw_lldp_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_EDN_CDP(db.Model):
    __tablename__ = 'failed_devices_edn_cdp'
    edn_cdp_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_IGW_CDP(db.Model):
    __tablename__ = 'failed_devices_igw_cdp'
    igw_cdp_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_EDN_MAC(db.Model):
    __tablename__ = 'failed_devices_edn_mac'
    edn_mac_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_IGW_MAC(db.Model):
    __tablename__ = 'failed_devices_igw_mac'
    igw_mac_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class FAILED_DEVICES_EDN_FIREWALL(db.Model):
    __tablename__ = 'failed_devices_edn_firewall'
    edn_firewall_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FAILED_DEVICES_F5(db.Model):
    __tablename__ = 'failed_devices_f5'
    f5_failed_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    reason = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    date = db.Column(db.DateTime, default=datetime.now(tz))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_EDN_ARCHER(db.Model):
    __tablename__ = 'vulnerability_edn_archer'
    vulnerability_archer_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    false_positive_date = db.Column(db.Date)
    severity = db.Column(db.String(1000))
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    last_detected = db.Column(db.Date)
    technical_contact = db.Column(db.String(1000))
    exception_requests = db.Column(db.String(1000))
    cve_id = db.Column(db.String(1000))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
'''
class VULNERABILITY_OPEN(db.Model):
    __tablename__ = 'vulnerability_open'
    vulnerability_open_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    false_positive_date = db.Column(db.Date)
    severity = db.Column(db.String(1000))
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    last_detected = db.Column(db.Date)
    technical_contact = db.Column(db.String(1000))
    exception_requests = db.Column(db.String(1000))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_INPROGRESS(db.Model):
    __tablename__ = 'vulnerability_inprogress'
    vulnerability_inprogress_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    false_positive_date = db.Column(db.Date)
    severity = db.Column(db.String(1000))
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    last_detected = db.Column(db.Date)
    technical_contact = db.Column(db.String(1000))
    exception_requests = db.Column(db.String(1000))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_OVERDUE(db.Model):
    __tablename__ = 'vulnerability_overdue'
    vulnerability_overdue_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    false_positive_date = db.Column(db.Date)
    severity = db.Column(db.String(1000))
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    last_detected = db.Column(db.Date)
    technical_contact = db.Column(db.String(1000))
    exception_requests = db.Column(db.String(1000))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_MANAGEDBY(db.Model):
    __tablename__ = 'vulnerability_managedby'
    vulnerability_managedby_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    false_positive_status = db.Column(db.String(1000))
    severity = db.Column(db.String(1000))
    technical_contact = db.Column(db.String(1000))
    #overall_status = db.Column(db.String(50))
    #qualys_vuln_status = db.Column(db.String(50))
    #last_detected = db.Column(db.Date)
    #exception_requests = db.Column(db.String(50))
    description =  db.Column(db.Text)
    cve_id = db.Column(db.String(1000))
    device_vendor = db.Column(db.String(1000))
    exception_expiry_date = db.Column(db.Date)
    grc_team_comments = db.Column(db.String(1000))
    grc_team_validation_response = db.Column(db.String(1000))
    remediation_comments = db.Column(db.String(1000))
    vulnerability_id = db.Column(db.String(1000))
    vendor_reference = db.Column(db.String(1000))
    vulnerability_details = db.Column(db.String(1000))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
'''
class VULNERABILITY_EDN_MASTER(db.Model):
    __tablename__ = 'vulnerability_edn_master'
    vulnerability_master_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    severity = db.Column(db.String(1000))
    cve_id = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    last_detected = db.Column(db.Date)
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    #inprogress_exceptions = db.Column(db.String(1000))
    all_exceptions = db.Column(db.String(1000))
    pn_code = db.Column(db.String(1000))
    hw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    vuln_fix_plan_status = db.Column(db.String(1000))
    vuln_ops_severity = db.Column(db.String(1000))
    technical_contact = db.Column(db.String(1000))
    
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_EDN_NO_PLAN(db.Model):
    __tablename__ = 'vulnerability_edn_no_plan'
    vulnerability_no_plan_id = db.Column(db.Integer, primary_key=True)
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    pn_code = db.Column(db.String(1000))
   
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_EDN_NOT_FOUND(db.Model):
    __tablename__ = 'vulnerability_edn_not_found'
    vulnerability_not_found_id = db.Column(db.Integer, primary_key=True)
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    correct_device_id = db.Column(db.String(1000))
   
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class F5(db.Model):
    __tablename__ = 'f5'
    f5_id = db.Column(db.Integer,primary_key=True)
    ip_address= db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    site_id = db.Column(db.String(50))
    vserver_name = db.Column(db.String(500))
    vip = db.Column(db.String(50))
    pool_name = db.Column(db.String(500))
    pool_member = db.Column(db.String(500))
    node = db.Column(db.String(500))
    service_port = db.Column(db.String(500))
    monitor_value = db.Column(db.String(500))
    monitor_status = db.Column(db.String(500))
    lb_method = db.Column(db.String(500))
    ssl_profile = db.Column(db.String(500))
    monitor_name = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    description = db.Column(db.String(500))


class VULNERABILITY_IGW_ARCHER(db.Model):
    __tablename__ = 'vulnerability_igw_archer'
    vulnerability_archer_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    false_positive_date = db.Column(db.Date)
    severity = db.Column(db.String(1000))
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    last_detected = db.Column(db.Date)
    technical_contact = db.Column(db.String(1000))
    exception_requests = db.Column(db.String(1000))
    cve_id = db.Column(db.String(1000))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_IGW_MASTER(db.Model):
    __tablename__ = 'vulnerability_igw_master'
    vulnerability_master_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    severity = db.Column(db.String(1000))
    cve_id = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    last_detected = db.Column(db.Date)
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    #inprogress_exceptions = db.Column(db.String(1000))
    all_exceptions = db.Column(db.String(1000))
    pn_code = db.Column(db.String(1000))
    hw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    vuln_fix_plan_status = db.Column(db.String(1000))
    vuln_ops_severity = db.Column(db.String(1000))
    technical_contact = db.Column(db.String(1000))
    
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_IGW_NO_PLAN(db.Model):
    __tablename__ = 'vulnerability_igw_no_plan'
    vulnerability_no_plan_id = db.Column(db.Integer, primary_key=True)
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    pn_code = db.Column(db.String(1000))
   
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_IGW_NOT_FOUND(db.Model):
    __tablename__ = 'vulnerability_igw_not_found'
    vulnerability_not_found_id = db.Column(db.Integer, primary_key=True)
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    correct_device_id = db.Column(db.String(1000))
   
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_SOC_ARCHER(db.Model):
    __tablename__ = 'vulnerability_soc_archer'
    vulnerability_archer_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    false_positive_date = db.Column(db.Date)
    severity = db.Column(db.String(1000))
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    last_detected = db.Column(db.Date)
    technical_contact = db.Column(db.String(1000))
    exception_requests = db.Column(db.String(1000))
    cve_id = db.Column(db.String(1000))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_SOC_MASTER(db.Model):
    __tablename__ = 'vulnerability_soc_master'
    vulnerability_master_id = db.Column(db.Integer, primary_key=True)
    scan_result_id = db.Column(db.String(1000) )
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    severity = db.Column(db.String(1000))
    cve_id = db.Column(db.String(1000))
    due_date = db.Column(db.Date)
    last_detected = db.Column(db.Date)
    overall_status = db.Column(db.String(1000))
    qualys_vuln_status = db.Column(db.String(1000))
    #inprogress_exceptions = db.Column(db.String(1000))
    all_exceptions = db.Column(db.String(1000))
    pn_code = db.Column(db.String(1000))
    hw_eos_date = db.Column(db.Date, default=datetime(2030,1, 1))
    vuln_fix_plan_status = db.Column(db.String(1000))
    vuln_ops_severity = db.Column(db.String(1000))
    technical_contact = db.Column(db.String(1000))
    
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_SOC_NO_PLAN(db.Model):
    __tablename__ = 'vulnerability_soc_no_plan'
    vulnerability_no_plan_id = db.Column(db.Integer, primary_key=True)
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    pn_code = db.Column(db.String(1000))
   
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class VULNERABILITY_SOC_NOT_FOUND(db.Model):
    __tablename__ = 'vulnerability_soc_not_found'
    vulnerability_not_found_id = db.Column(db.Integer, primary_key=True)
    device_ip = db.Column(db.String(1000))
    device_name = db.Column(db.String(1000))
    correct_device_id = db.Column(db.String(1000))
   
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class IPT_RMA_TRACKER(db.Model):
    __tablename__ = 'ipt_rma_tracker'
    ipt_rma_tracker_id = db.Column(db.Integer, primary_key=True)
    rma_order_number = db.Column(db.String(50))
    service_request_number = db.Column(db.String(50))
    serial_no = db.Column(db.String(50))
    mac = db.Column(db.String(50))
    user_id = db.Column(db.String(50))
    user_info_and_device_impacted_details = db.Column(db.String(500))
    rma_ordered_date = db.Column(db.Date, default=datetime(2030,1, 1))
    fe_receiving_the_rma_part_from_dhl = db.Column(db.String(500))
    current_status = db.Column(db.String(500))
    actual_rma_received_date = db.Column(db.Date, default=datetime(2030,1, 1))
    part_number = db.Column(db.String(500))
    engineer_handling_the_rma = db.Column(db.String(50))
    pickup_date_scheduled_in_airway_bill = db.Column(db.Date, default=datetime(2030,1, 1))
    fe_delivering_the_device_to_dhl = db.Column(db.String(500))
    delivery_location = db.Column(db.String(500))
    final_status = db.Column(db.String(500))
    attachments = db.Column(db.String(500))
    remarks = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class SNAGS(db.Model):
    __tablename__ = 'snags'
    snag_id = db.Column(db.Integer, primary_key=True)
    ho_ref_id = db.Column(db.Integer)
    device_name = db.Column(db.String(50))
    snag_name = db.Column(db.String(50))
    snag_status = db.Column(db.String(50))
    snag_criticality = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    reported_date = db.Column(db.DateTime, default=datetime(2000,12, 31))
    closure_date = db.Column(db.DateTime, default=datetime(2000,12, 31))
    snag_closure_date = db.Column(db.DateTime, default=datetime(2000,12, 31))
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    history = db.Column(db.Text)
    comment_history = db.Column(db.Text)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class EXTERNAL_VRF_ANALYSIS(db.Model):
    __tablename__ = 'external_vrf_analysis'
    external_vrf_analysis_id = db.Column(db.Integer, primary_key=True)
    vrf = db.Column(db.String(100))
    primary_site = db.Column(db.String(100))
    secondary_site = db.Column(db.String(100))
    no_of_received_routes = db.Column(db.String(100))
    missing_routes_in_secondary_site = db.Column(db.Text)
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class INTRANET_VRF_ANALYSIS(db.Model):
    __tablename__ = 'intranet_vrf_analysis'
    intranet_vrf_analysis_id = db.Column(db.Integer, primary_key=True)
    vrf = db.Column(db.String(100))
    region = db.Column(db.String(100))
    primary_site = db.Column(db.String(100))
    secondary_site = db.Column(db.String(100))
    no_of_received_routes = db.Column(db.String(100))
    missing_routes_in_secondary_site = db.Column(db.Text)
    missing_sites_in_secondary_site = db.Column(db.Text)
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class TableMappings(db.Model):
    __tablename__ = 'table_mappings'
    table_id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)

class Attachments(db.Model):
    __tablename__ = 'attachments'

    attachment_id = db.Column(db.Integer, primary_key=True)
    attachment_name = db.Column(db.String(500), nullable=False)
    attachment_path = db.Column(db.String(500), nullable=False)
    file_extension = db.Column(db.String(500), nullable=False)
    creation_date = db.Column(db.DateTime)
    modification_date = db.Column(db.DateTime)
    is_temp = db.Column(db.Boolean, default=True)
    table_id = db.Column(db.Integer)
    primary_id = db.Column(db.Integer)

class SECURITY_COMPLIANCE_TABLE(db.Model):
    __tablename__ = 'security_compliance_table'
    node_id = db.Column(db.Integer, primary_key=True)
    node_name = db.Column(db.String(100))
    function = db.Column(db.Text)
    pn_code = db.Column(db.Text)
    domain = db.Column(db.String(100))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
