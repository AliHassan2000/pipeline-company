import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
// import axios from "axios";
// import { SEED_API } from "../../../GlobalVar";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  const getString = (str) => {
    return str ? str : "";
  };

  let [device, setDevice] = useState(props.editRecord);
  // let [ip, setIp] = useState(device ? getString(device.switch_ip_address) : "");
  let [siteId, setSiteId] = useState(device ? getString(device.site_id) : "");
  let [rackId, setRackId] = useState(device ? getString(device.rack_id) : "");
  let [tagId, setTagId] = useState(device ? getString(device.tag_id) : "TBF");
  let [rfsDate, setRfs_date] = useState(
    device ? getString(device.rfs_date) : ""
  );
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );
  let [region, setRegion] = useState(
    device ? getString(device.region) : "CENTRAL"
  );
  let [longitude, setLongitude] = useState(
    device ? getString(device.longitude) : ""
  );
  let [latitude, setLatitude] = useState(
    device ? getString(device.latitude) : ""
  );
  let [city, setCity] = useState(device ? getString(device.city) : "");
  let [floor, setFloor] = useState(device ? getString(device.floor) : "");
  let [serialNumber, setSerialNumber] = useState(
    device ? getString(device.serial_number) : ""
  );
  let [pnCode, setPnCode] = useState(device ? getString(device.pn_code) : "");
  let [neIpAddress, setNeIpAddress] = useState(
    device ? getString(device.ne_ip_address) : ""
  );
  let [deviceRu, setDeviceRu] = useState(
    device ? getString(device.device_ru) : ""
  );
  let [department, setDepartment] = useState(
    device ? getString(device.department) : ""
  );
  let [section, setSection] = useState(device ? getString(device.section) : "");
  let [criticality, setCriticality] = useState(
    device ? getString(device.criticality) : "Low"
  );
  let [myFunction, setMyFunction] = useState(
    device ? getString(device.myFunction) : ""
  );
  let [domain, setDomain] = useState(device ? getString(device.domain) : "");
  let [virtual, setVirtual] = useState(
    device ? getString(device.virtual) : "Not Virtual"
  );
  let [authentication, setAuthentication] = useState(
    device ? getString(device.authentication) : "AAA"
  );
  let [hostname, setHostname] = useState(
    device ? getString(device.hostname) : ""
  );
  let [swType, setSwType] = useState(
    device ? getString(device.sw_type) : "IOS"
  );
  let [vendor, setVendor] = useState(
    device ? getString(device.vendor) : "Cisco"
  );
  let [operationStatus, setOperationStatus] = useState(
    device ? getString(device.operation_status) : "production"
  );
  let [siteType, setSiteType] = useState(
    device ? getString(device.site_type) : "DC"
  );
  let [contractExpiry, setContractExpiry] = useState(
    device ? getString(device.contract_expiry) : ""
  );
  let [contractNumber, setContractNumber] = useState(
    device ? getString(device.contract_number) : ""
  );
  let [stack, setStack] = useState(device ? getString(device.stack) : "");

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/addRebd", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllRebds")
              .then((response) => {
                console.log(response.data);
                props.setDataSource(response.data);
                props.excelData = response.data;
              })
              .catch((error) => {
                console.log(error);
              })
          );
          return Promise.all(promises);
        })
        .catch((err) => {
          console.log(err);
        });
    } catch (err) {
      console.log(err);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const device = {
      // switch_ip_address: ip,
      site_id: siteId,
      rack_id: rackId,
      region,
      longitude,
      latitude,
      city,
      floor,
      serial_number: serialNumber,
      pn_code: pnCode,
      tag_id: tagId,
      rfs_date: rfsDate,
      device_id: deviceId,
      ne_ip_address: neIpAddress,
      device_ru: deviceRu,
      department,
      section,
      criticality,
      function: myFunction,
      domain,
      virtual,
      authentication,
      hostname,
      sw_type: swType,
      vendor,
      operation_status: operationStatus,
      site_type: siteType,
      contract_expiry: contractExpiry,
      contract_number: contractNumber,
      stack,
    };

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const getOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  return (
    <Modal
      style={{ marginTop: "0px", zIndex: "99999" }}
      width="80%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} REBD</p>
          </Col>
          <Col span={8}>
            {/* <InputWrapper>
              Switch IP-Address: &nbsp;&nbsp;
              {device ? (
                <StyledInput value={ip} readonly />
              ) : (
                <StyledInput
                  value={ip}
                  onChange={(e) => setIp(e.target.value)}
                  required
                />
              )}
            </InputWrapper> */}
            <InputWrapper>
              Device ID:
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={deviceId} readonly />
              ) : (
                <StyledInput
                  value={deviceId}
                  onChange={(e) => setDeviceId(e.target.value)}
                  required
                />
              )}
            </InputWrapper>

            <InputWrapper>
              NE IP Address: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={neIpAddress} readonly />
              ) : (
                <Input
                  value={neIpAddress}
                  onChange={(e) => setNeIpAddress(e.target.value)}
                  // required
                />
              )}
            </InputWrapper>
            <InputWrapper>
              Site ID:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Rack Id:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={rackId}
                // type="number"
                // min={0}
                onChange={(e) => setRackId(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Tag ID:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={tagId}
                onChange={(e) => setTagId(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              RFS Date :{/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={rfsDate}
                onChange={(e) => setRfs_date(e.target.value)}
                // required
              />
            </InputWrapper>

            <InputWrapper>
              Device RU:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={deviceRu}
                onChange={(e) => setDeviceRu(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Department:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Region:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Longitude:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Section:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={section}
                onChange={(e) => setSection(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Criticality: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={criticality}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setCriticality(value);
                }}
              >
                {getOptions([
                  "Low",
                  "Moderate",
                  "High",
                  "Significant",
                  "Critical",
                ])}
              </Select>
              {/* <StyledInput
                value={criticality}
                onChange={(e) => setCriticality(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Function:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={myFunction}
                onChange={(e) => setMyFunction(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Domain:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Virtual: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={virtual}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVirtual(value);
                }}
              >
                <Option value="Virtual">Virtual</Option>
                <Option value="Not Virtual">Not Virtual</Option>
                <Option value="Passive">Passive</Option>
                <Option value="Managed Module">Managed Module</Option>
              </Select>
              {/* <StyledInput
                value={virtual}
                onChange={(e) => setVirtual(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Authentication: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={authentication}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setAuthentication(value);
                }}
              >
                <Option value="AAA">AAA</Option>
                <Option value="PAM">PAM</Option>
                <Option value="Local">Local</Option>
              </Select>
              {/* <StyledInput
                value={authentication}
                onChange={(e) => setAuthentication(e.target.value)}
                required
              /> */}
            </InputWrapper>
            <InputWrapper>
              Hostname:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={hostname}
                onChange={(e) => setHostname(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Latitude:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              City:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={city}
                onChange={(e) => setCity(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PN Code:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={pnCode}
                onChange={(e) => setPnCode(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              SW Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={swType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setSwType(value);
                }}
              >
                {getOptions([
                  "IOS",
                  "A10",
                  "ACI-LEAF",
                  "ACI-SPINE",
                  "AP",
                  "APIC",
                  "Arbor",
                  "Arbor-Sec",
                  "Arista",
                  "ASA96",
                  "ASA-SOC",
                  "BeyondTrust",
                  "DNS Filtering",
                  "F5",
                  "FireEye",
                  "FirepowerServer",
                  "Firepower-SSH",
                  "Fortinet-Sec",
                  "Greatbay",
                  "HPAruba",
                  "Infoblox",
                  "IOS-XE",
                  "IOS-XR",
                  "IPT",
                  "Juniper-Screenos",
                  "Juniper-Sec",
                  "Linux",
                  "Microsoft",
                  "MobileIron",
                  "Nutanix",
                  "NX-OS",
                  "Ookla",
                  "oscilloquartz",
                  "PaloAlto",
                  "PRIME",
                  "PulseSecure",
                  "Qualys",
                  "SolarWind",
                  "SolarWinds",
                  "StorMagic",
                  "Symantec",
                  "UCS",
                  "UCS-CIMC",
                  "UCS-SYS",
                  "vcenter",
                  "WireFilter",
                  "WLC",
                ])}
              </Select>
              {/* <StyledInput
                value={swType}
                onChange={(e) => setSwType(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Vendor: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={vendor}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVendor(value);
                }}
              >
                <Option value="Cisco">Cisco</Option>
                <Option value="A10">A10</Option>
                <Option value="Arbor">Arbor</Option>
                <Option value="Arista">Arista</Option>
                <Option value="Aruba Networks">Aruba Networks</Option>
                <Option value="BeyondTrust">BeyondTrust</Option>
                <Option value="Dell">Dell</Option>
                <Option value="F5">F5</Option>
                <Option value="FireEye">FireEye</Option>
                <Option value="Fortinet">Fortinet</Option>
                <Option value="Greatbay">Greatbay</Option>
                <Option value="HP">HP</Option>
                <Option value="HPAruba">HPAruba</Option>
                <Option value="Infoblox">Infoblox</Option>
                <Option value="Juniper">Juniper</Option>
                <Option value="Microsoft">Microsoft</Option>
                <Option value="MobileIron">MobileIron</Option>
                <Option value="Newnet">Newnet</Option>
                <Option value="Nutanix">Nutanix</Option>
                <Option value="Ookla">Ookla</Option>
                <Option value="oscilloquartz">oscilloquartz</Option>
                <Option value="Others">Others</Option>
                <Option value="PaloAlto">PaloAlto</Option>
                <Option value="PulseSecure">PulseSecure</Option>
                <Option value="Qualys">Qualys</Option>
                <Option value="SolarWinds">SolarWinds</Option>
                <Option value="StorMagic">StorMagic</Option>
                <Option value="SUN">SUN</Option>
                <Option value="Symantec">Symantec</Option>
                <Option value="Virtual">Virtual</Option>
                <Option value="Vmware">Vmware</Option>
                <Option value="WireFilter">WireFilter</Option>
              </Select>
              {/* <StyledInput
                value={vendor}
                onChange={(e) => setVendor(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Operation Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={operationStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setOperationStatus(value);
                }}
              >
                <Option value="Production">Production</Option>
                <Option value="Not Handedover">Not Handedover</Option>
                <Option value="Dismantle">Dismantle</Option>
                <Option value="Power Off">Power Off</Option>
                <Option value="Exclude">Exclude</Option>

                {/* <Option value="Offloaded">Offloaded</Option> */}
              </Select>
              {/* <StyledInput
                value={operationStatus}
                onChange={(e) => setOperationStatus(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Site Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={siteType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setSiteType(value);
                }}
              >
                <Option value="DC">DC</Option>
                <Option value="DCN">DCN</Option>
                <Option value="CO">CO</Option>
                <Option value="FB">FB</Option>
                <Option value="FS">FS</Option>
                <Option value="KSK">KSK</Option>
                <Option value="MFB">MFB</Option>
                <Option value="MOI">MOI</Option>
              </Select>
              {/* <StyledInput
                value={siteType}
                onChange={(e) => setSiteType(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Contract Expiry:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={contractExpiry}
                onChange={(e) => setContractExpiry(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Contract Number:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={contractNumber}
                onChange={(e) => setContractNumber(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Stack:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={stack}
                onChange={(e) => setStack(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Floor:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={floor}
                onChange={(e) => setFloor(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Serial Number:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Input
                value={serialNumber}
                onChange={(e) => setSerialNumber(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>

          <Col span={24} style={{ textAlign: "center" }}>
            <StyledButton color={"red"} onClick={handleCancel}>
              Cancel
            </StyledButton>
            &nbsp; &nbsp;{" "}
            <StyledSubmitButton color={"green"} type="submit" value="Done" />
          </Col>
        </Row>
      </form>
    </Modal>
  );
};

export default AddDeviceModal;

const StyledInput = styled(Input)`
  height: 1.8rem;
`;

const InputWrapper = styled.div`
  white-space: nowrap;
  display: flex;
  justify-content: space-between;
  padding-bottom: 10px;
`;

const StyledSubmitButton = styled(Input)`
  width: 15%;
  font-family: Montserrat-Regular;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: ${(props) => props.color};
  border-color: ${(props) => props.color};
  color: white;
  border-radius: 5px;
  &:focus,
  &:hover {
    background-color: ${(props) => props.color};
    border-color: ${(props) => props.color};
    color: white;
    opacity: 0.8;
  }
`;

const StyledButton = styled(Button)`
  width: 15%;
  font-family: Montserrat-Regular;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: ${(props) => props.color};
  border-color: ${(props) => props.color};
  color: white;
  border-radius: 5px;
  &:focus,
  &:hover {
    background-color: ${(props) => props.color};
    border-color: ${(props) => props.color};
    color: white;
    opacity: 0.8;
  }
`;
