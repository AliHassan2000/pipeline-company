from app import db
from sqlalchemy import ForeignKey
from datetime import datetime
import pytz
class EDN_CDP_LEGACY(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_cdp_legacy'
    edn_cdp_legacy_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    modified_by = db.Column(db.String(100))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class EDN_LLDP_LEGACY(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_lldp_legacy'
    edn_lldp_legacy_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    modified_by = db.Column(db.String(100))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
class EDN_MAC_LEGACY(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_mac_legacy'
    edn_mac_legacy_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(1500))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    arp_source_name = db.Column(db.String(5000))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(500))
    service_matched_by= db.Column(db.String(100))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz))
    modified_by = db.Column(db.String(100))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    device_a_tx = db.Column(db.String(100))
    device_a_rx = db.Column(db.String(100))
    f5_lb = db.Column(db.Text)
    f5_vip = db.Column(db.Text)
    f5_node_status = db.Column(db.Text)
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EDN_LLDP_ACI(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_lldp_aci'
    edn_lldp_aci_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(1500))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    modified_by = db.Column(db.String(100))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IGW_LLDP_ACI(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'igw_lldp_aci'
    igw_lldp_aci_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(1500))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    modified_by = db.Column(db.String(100))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IGW_CDP_LEGACY(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'igw_cdp_legacy'
    igw_cdp_legacy_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    modified_by = db.Column(db.String(100))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))

class IGW_LLDP_LEGACY(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'igw_lldp_legacy'
    igw_lldp_legacy_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    modified_by = db.Column(db.String(100))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))

class EDN_MPLS(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_mpls'
    edn_mpls_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    server_name = db.Column(db.String(100))
    server_os = db.Column(db.String(100))
    app_name = db.Column(db.String(1000))
    owner_name = db.Column(db.String(1000))
    owner_email = db.Column(db.String(1000))
    owner_contact = db.Column(db.String(1000))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))

class IGW_SYSTEM(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'igw_system'
    igw_system_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    server_name = db.Column(db.String(100))
    server_os = db.Column(db.String(100))
    app_name = db.Column(db.String(1000))
    owner_name = db.Column(db.String(1000))
    owner_email = db.Column(db.String(1000))
    owner_contact = db.Column(db.String(1000))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))

class EDN_SYSTEM(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_system'
    edn_system_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    server_name = db.Column(db.String(100))
    server_os = db.Column(db.String(100))
    app_name = db.Column(db.String(1000))
    owner_name = db.Column(db.String(1000))
    owner_email = db.Column(db.String(1000))
    owner_contact = db.Column(db.String(1000))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))

class EDN_SECURITY(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_security'
    edn_security_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    server_name = db.Column(db.String(100))
    server_os = db.Column(db.String(100))
    app_name = db.Column(db.String(1000))
    owner_name = db.Column(db.String(1000))
    owner_email = db.Column(db.String(1000))
    owner_contact = db.Column(db.String(1000))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))
class EDN_IPT(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_ipt'
    edn_ipt_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    time = datetime.now()
    creation_date = db.Column(db.DateTime, default=time)
    modification_date = db.Column(db.DateTime, default=time, onupdate=time)
    server_name = db.Column(db.String(100))
    server_os = db.Column(db.String(100))
    app_name = db.Column(db.String(1000))
    owner_name = db.Column(db.String(1000))
    owner_email = db.Column(db.String(1000))
    owner_contact = db.Column(db.String(1000))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))
class EDN_EXEC_VIDEO_EPS(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_exec_video_eps'
    ipt_exec_video_eps_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    time=datetime.now(tz)
    creation_date = db.Column(db.DateTime, default=time)
    modification_date = db.Column(db.DateTime, default=time, onupdate=time)
    server_name = db.Column(db.String(100))
    server_os = db.Column(db.String(100))
    app_name = db.Column(db.String(1000))
    owner_name = db.Column(db.String(1000))
    owner_email = db.Column(db.String(1000))
    owner_contact = db.Column(db.String(1000))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    modified_by = db.Column(db.String(100))
class EDN_SERVICE_MAPPING(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_service_mapping'
    edn_service_mapping_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.Text)
    device_b_mac = db.Column(db.Text)
    device_b_system_name = db.Column(db.String(100))
    device_b_type = db.Column(db.String(50))
    server_name = db.Column(db.String(100))
    server_os = db.Column(db.String(100))
    app_name = db.Column(db.String(1000))
    owner_name = db.Column(db.String(1000))
    owner_email = db.Column(db.String(1000))
    owner_contact = db.Column(db.String(1000))
    modified_by = db.Column(db.String(100))
    tz = pytz.timezone('Asia/Riyadh')
    time=datetime.now(tz)
    creation_date = db.Column(db.DateTime, default=time)
    modification_date = db.Column(db.DateTime, default=time, onupdate=time)
    service_vendor = db.Column(db.String(100))

    def __repr__(self) -> str:
        return f"Table Name: edn_service_mapping, Mapping_id: {self.edn_service_mapping_id}"
    
class IGW_SERVICE_MAPPING(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'igw_service_mapping'
    igw_service_mapping_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_type = db.Column(db.String(50))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(1000))
    tz = pytz.timezone('Asia/Riyadh')
    time=datetime.now(tz)
    creation_date = db.Column(db.DateTime, default=time)
    creation_date = db.Column(db.DateTime, default=time)
    modification_date = db.Column(db.DateTime, default=time, onupdate=time)
    modified_by = db.Column(db.String(100))
class EDN_FIREWALL_ARP(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'edn_firewall_arp'
    edn_firewall_arp_id = db.Column(db.Integer, primary_key=True)
    firewall_id = db.Column(db.String(5000))
    mac = db.Column(db.String(50))
    ip = db.Column(db.String(2000))
    dc = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    arp_source_type = db.Column(db.String(5000))

class SCRIPT_STATUS(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'script_status'
    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String(50))
    status = db.Column(db.String(50))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))

class IT_PHYSICAL_SERVERS_TABLE(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'it_physical_servers_table'
    server_id = db.Column(db.Integer, primary_key=True)   
    server_name = db.Column(db.String(500))
    vm_name = db.Column(db.String(500))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now())

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IT_APP_TABLE(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'it_app_table'
    app_id = db.Column(db.Integer, primary_key=True)   
    vm_name = db.Column(db.String(500))
    sw_component = db.Column(db.String(1000))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now())

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IT_OS_TABLE(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'it_os_table'
    os_id = db.Column(db.Integer, primary_key=True)   
    vm_name = db.Column(db.String(500))
    operating_system = db.Column(db.String(1000))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now())

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IT_MAC_TABLE(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'it_mac_table'
    mac_id = db.Column(db.Integer, primary_key=True)   
    vm_name = db.Column(db.String(500))
    mac_address = db.Column(db.String(1000))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now())

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IT_IP_TABLE(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'it_ip_table'
    ip_id = db.Column(db.Integer, primary_key=True)   
    vm_name = db.Column(db.String(500))
    ip_address = db.Column(db.String(1000))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now())

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IT_OWNER_TABLE(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'it_owner_table'
    owner_id = db.Column(db.Integer, primary_key=True)   
    vm_name = db.Column(db.String(500))
    owner_name = db.Column(db.String(1000))
    owner_email = db.Column(db.String(1000))
    owner_contact = db.Column(db.String(1000))
    app_name = db.Column(db.String(1000))
    status = db.Column(db.String(100))
    instance_id = db.Column(db.String(100))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now())

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IGW_MAC_LEGACY(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'igw_mac_legacy'
    igw_mac_legacy_id = db.Column(db.Integer, primary_key=True)
    device_a_name = db.Column(db.String(50))
    device_a_interface = db.Column(db.String(50))
    device_a_trunk_name = db.Column(db.String(50))
    device_a_ip = db.Column(db.String(50))
    device_b_system_name = db.Column(db.String(50))
    device_b_interface = db.Column(db.String(50))
    device_b_ip = db.Column(db.String(1500))
    device_b_type = db.Column(db.String(50))
    device_b_port_desc = db.Column(db.String(1000))
    device_a_mac = db.Column(db.String(50))
    device_b_mac = db.Column(db.String(50))
    device_a_port_desc = db.Column(db.String(1000))
    device_a_vlan = db.Column(db.String(50))
    device_a_vlan_name = db.Column(db.String(50))
    server_name = db.Column(db.String(50))
    server_os = db.Column(db.String(50))
    app_name = db.Column(db.String(50))
    owner_name = db.Column(db.String(50))
    owner_email = db.Column(db.String(50))
    owner_contact = db.Column(db.String(500))
    tz = pytz.timezone('Asia/Riyadh')
    creation_date = db.Column(db.DateTime, default=datetime.now(tz))
    modification_date = db.Column(db.DateTime, default=datetime.now(tz), onupdate=datetime.now(tz))
    modified_by = db.Column(db.String(100))
    service_matched_by = db.Column(db.String(100))
    arp_source_name = db.Column(db.String(5000))
    arp_source_type = db.Column(db.String(5000))
    device_b_mac_vendor = db.Column(db.String(100))
    service_vendor = db.Column(db.String(100))
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IGW_LINKS(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'igw_links'
    igw_links_id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50))
    provider = db.Column(db.String(50))
    router = db.Column(db.String(50))
    interface = db.Column(db.String(50))
    local_ipv4 = db.Column(db.String(50))
    neighbor_ipv4 = db.Column(db.String(50))
    local_ipv6 = db.Column(db.String(50))
    neighbor_ipv6 = db.Column(db.String(50))
    neighbor_asn = db.Column(db.String(50))
    ipv4_egress_policy = db.Column(db.String(100))
    community = db.Column(db.String(50))
    ipv4_ingress_policy = db.Column(db.String(100))
    ipv4_local_preference = db.Column(db.String(50))
    ipv6_egress_policy = db.Column(db.String(100))
    ipv6_ingress_policy = db.Column(db.String(100))
    ipv6_local_preference = db.Column(db.String(50))
    ipv4_advertised_routes_count = db.Column(db.String(1000))
    ipv4_received_routes_count = db.Column(db.String(1000))
    ipv6_advertised_routes_count = db.Column(db.String(1000))
    ipv6_received_routes_count = db.Column(db.String(1000))
    created_by = db.Column(db.String(50))
    modified_by = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    modification_date = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class IT_SERVICES_SNAPSHOTS_TABLE(db.Model):
    __bind_key__ = 'phymapping'
    __tablename__ = 'it_services_snapshots_table'
    snapshot_id = db.Column(db.Integer, primary_key=True)   
    physical_servers_inserted = db.Column(db.Integer)
    apps_inserted = db.Column(db.Integer)
    os_inserted = db.Column(db.Integer)
    ips_inserted = db.Column(db.Integer)
    macs_inserted = db.Column(db.Integer)
    owners_inserted = db.Column(db.Integer)
    physical_servers_updated = db.Column(db.Integer)
    apps_updated = db.Column(db.Integer)
    os_updated = db.Column(db.Integer)
    ips_updated = db.Column(db.Integer)
    macs_updated = db.Column(db.Integer)
    owners_updated = db.Column(db.Integer)
    creation_date = db.Column(db.DateTime)
    modification_date = db.Column(db.DateTime)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
