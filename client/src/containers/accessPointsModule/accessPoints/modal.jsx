import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import Swal from "sweetalert2";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  const getString = (str) => {
    return str ? str : "";
  };

  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////
  let [serialNumber, setSerialNumber] = useState(
    device ? getString(device.serial_number) : ""
  );
  let [wlcName, setWLCName] = useState(
    device ? getString(device.wlc_name) : ""
  );
  let [ip, setIp] = useState(device ? getString(device.device_id) : "");
  let [deviceName, setDeviceName] = useState(
    device ? getString(device.device_name) : ""
  );
  let [tagId, setTagId] = useState(device ? getString(device.tag_id) : "");
  let [rfsDate, setRfsDate] = useState(
    device ? getString(device.rfs_date) : ""
  );
  let [functiond, setFunction] = useState(
    device ? getString(device.function) : ""
  );
  let [itemCode, setItemCode] = useState(
    device?.item_code ? device.item_code : "TBF"
  );
  let [itemDesc, setItemDesc] = useState(
    device?.item_desc ? device.item_desc : "TBF"
  );
  let [clei, setClei] = useState(device?.clei ? device.clei : "TBF");

  let [rackId, setRackId] = useState(device ? getString(device.rack_id) : "");
  let [siteId, setSiteId] = useState(device ? getString(device.site_id) : "");
  let [manufactureDate, setManufactureDate] = useState(
    device ? getString(device.manufactuer_date) : ""
  );
  let [virtual, setVirtual] = useState(
    device ? getString(device.virtual) : "Not Virtual"
  );
  let [authentication, setAuthentication] = useState(
    device ? getString(device.authentication) : "AAA"
  );
  let [subrackIdNumber, setSubrackIdNumber] = useState(
    device ? getString(device.subrack_id_number) : ""
  );
  let [hwEosDate, setHwEosDate] = useState(
    device ? getString(device.hw_eos_date) : ""
  );
  let [hwEolDate, setHwEolDate] = useState(
    device ? getString(device.hw_eol_date) : ""
  );
  let [swEosDate, setSwEosDate] = useState(
    device ? getString(device.sw_eos_date) : ""
  );
  let [criticality, setCriticality] = useState(
    device ? getString(device.criticality) : "Low"
  );
  let [ciscoDomain, setCiscoDomain] = useState(
    device ? getString(device.cisco_domain) : "EDN-NET"
  );
  let [patchVersion, setPatchVersion] = useState(
    device ? getString(device.patch_version) : ""
  );
  let [section, setSection] = useState(
    device ? getString(device.section) : "Cloud & Virtualization Systems"
  );
  let [softwareVersion, setSoftwareVersion] = useState(
    device ? getString(device.software_version) : ""
  );

  let [hardwareVersion, setHardwareVersion] = useState(
    device ? getString(device.hardware_version) : ""
  );
  let [department, setDepartment] = useState(
    device ? getString(device.department) : "Network Operations Center"
  );
  let [pnCode, setPnCode] = useState(device ? getString(device.pn_code) : "");
  let [maxPower, setMaxPower] = useState(
    device ? getString(device.max_power) : ""
  );
  let [deviceRu, setDeviceRu] = useState(
    device ? getString(device.device_ru) : ""
  );
  let [manufacturer, setManufacturer] = useState(
    device ? getString(device.manufacturer) : ""
  );
  let [stack, setStack] = useState(device ? getString(device.stack) : "");
  let [source, setSource] = useState(device ? getString(device.source) : "");
  let [siteType, setSiteType] = useState(
    device ? getString(device.site_type) : "DC"
  );

  let [contractNumber, setContractNumber] = useState(
    device ? getString(device.contract_number) : ""
  );
  let [contractExpiry, setContractExpiry] = useState(
    device ? getString(device.contract_expiry) : ""
  );
  let [status, setStatus] = useState(device ? getString(device.status) : "");

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/editAccesspoints", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Device Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllAccesspoints")
              .then((response) => {
                props.setDataSource(response.data);
                props.setRowCount(response.data.length);
                props.excelData = response.data;
              })
              .catch((error) => {
                // openSweetAlert("Something Went Wrong!", "error");
                console.log(error);
              })
          );
          return Promise.all(promises);
        })
        .catch((err) => {
          // openSweetAlert("Something Went Wrong!", "error");
          console.log(err);
        });
    } catch (err) {
      // openSweetAlert("Something Went Wrong!", "error");
      console.log(err);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const device = {
      serial_number: serialNumber,
      wlc_name: wlcName,
      device_id: ip,
      device_name: deviceName,
      tag_id: tagId,
      rfs_date: rfsDate,
      // function: functiond,
      item_code: itemCode,
      item_desc: itemDesc,
      clei,

      // rack_id: rackId,
      // site_id: siteId,
      manufactuer_date: manufactureDate,
      // virtual,
      // authentication,

      // subrack_id_number: subrackIdNumber,
      // hw_eos_date: hwEosDate,
      // hw_eol_date: hwEolDate,
      // sw_eos_date: swEosDate,
      // criticality,

      // cisco_domain: ciscoDomain,
      // patch_version: patchVersion,
      // section,
      // software_version: softwareVersion,
      // hardware_version: hardwareVersion,
      // department,

      // pn_code: pnCode,

      max_power: maxPower,
      // device_ru: deviceRu,
      // manufacturer,
      // stack,
      // source,
      // site_type: siteType,
      contract_number: contractNumber,
      contract_expiry: contractExpiry,
      // status,
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
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Device</p>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Device Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? <StyledInput value={deviceName} readonly /> : null}
            </InputWrapper>
            <InputWrapper>
              Device Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={ip}
                onChange={(e) => setIp(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Device Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                required
              />
            </InputWrapper>
            {/* <InputWrapper>
              Function: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={functiond}
                onChange={(e) => setFunction(e.target.value)}
                required
              />
            </InputWrapper> */}
            <InputWrapper>
              Tag Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={tagId}
                onChange={(e) => setTagId(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              RFS Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={rfsDate}
                onChange={(e) => setRfsDate(e.target.value)}
                required
              />
            </InputWrapper>

            {/* -------------------------------------------------------------------------- */}
            {/* <InputWrapper>
              Rack Id:&nbsp;&nbsp;
              <StyledInput
                value={rackId}
                onChange={(e) => setRackId(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Site Id:&nbsp;&nbsp;
              <StyledInput
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
              />
            </InputWrapper> */}

            {/* <InputWrapper>
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
            </InputWrapper> */}
          </Col>
          <Col span={8}>
            <InputWrapper>
              Item Code:&nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={itemCode}
                onChange={(e) => setItemCode(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Item Desc: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={itemDesc}
                onChange={(e) => setItemDesc(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Clei:&nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={clei}
                onChange={(e) => setClei(e.target.value)}
                required
              />
            </InputWrapper>
            {/* <InputWrapper>
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
            </InputWrapper> */}
            {/* <InputWrapper>
              Subrack Id Number:&nbsp;&nbsp;
              <StyledInput
                value={subrackIdNumber}
                onChange={(e) => setSubrackIdNumber(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Hw Eos Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={hwEosDate}
                onChange={(e) => setHwEosDate(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Hw Eol Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={hwEolDate}
                onChange={(e) => setHwEolDate(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Sw Eos Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={swEosDate}
                onChange={(e) => setSwEosDate(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
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
            </InputWrapper> */}
            {/* <InputWrapper>
              Cisco Domain: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={ciscoDomain}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setCiscoDomain(value);
                }}
                required
              >
                {getOptions([
                  "EDN-NET",
                  "EDN-IPT",
                  "EDN-SYS",
                  "IGW-NET",
                  "IGW-SYS",
                  "POS",
                  "SOC",
                  "REBD",
                ])}
              </Select> 
            </InputWrapper> */}
            {/* <InputWrapper>
              Patch Version:&nbsp;&nbsp;
              <StyledInput
                value={patchVersion}
                onChange={(e) => setPatchVersion(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Section: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={section}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setSection(value);
                }}
              >
                {getOptions([
                  "Cloud & Virtualization Systems",
                  "End point Protection",
                  "Security Infrastructure Management",
                ])}
              </Select>
            </InputWrapper> */}
            {/* <InputWrapper>
              Software Version:&nbsp;&nbsp;
              <StyledInput
                value={softwareVersion}
                onChange={(e) => setSoftwareVersion(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Hardware Version:&nbsp;&nbsp;
              <StyledInput
                value={hardwareVersion}
                onChange={(e) => setHardwareVersion(e.target.value)}
              />
            </InputWrapper> */}
          </Col>
          <Col span={8}>
            {/* <InputWrapper>
              Department: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={department}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setDepartment(value);
                }}
              >
                {getOptions([
                  "Network Operations Center",
                  "Security Operations Center",
                ])}
              </Select>
            </InputWrapper> */}
            {/* <InputWrapper>
              Pn Code:&nbsp;&nbsp;
              <StyledInput
                value={pnCode}
                onChange={(e) => setPnCode(e.target.value)}
              />
            </InputWrapper> */}
            <InputWrapper>
              Max Power:&nbsp;&nbsp;
              <StyledInput
                value={maxPower}
                onChange={(e) => setMaxPower(e.target.value)}
              />
            </InputWrapper>
            {/* <InputWrapper>
              Device Ru:&nbsp;&nbsp;
              <StyledInput
                value={deviceRu}
                onChange={(e) => setDeviceRu(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Manufacturer:&nbsp;&nbsp;
              <StyledInput
                value={manufacturer}
                onChange={(e) => setManufacturer(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Stack:&nbsp;&nbsp;
              <StyledInput
                value={stack}
                onChange={(e) => setStack(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Source:&nbsp;&nbsp;
              <StyledInput
                value={source}
                onChange={(e) => setSource(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
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
            </InputWrapper> */}
            <InputWrapper>
              Contract Number:&nbsp;&nbsp;
              <StyledInput
                value={contractNumber}
                onChange={(e) => setContractNumber(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Contract Expiry:&nbsp;&nbsp;
              <StyledInput
                value={contractExpiry}
                onChange={(e) => setContractExpiry(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Manufacture Date:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={manufactureDate}
                onChange={(e) => setManufactureDate(e.target.value)}
                // required
              />
            </InputWrapper>
            {/* <InputWrapper>
              Status:&nbsp;&nbsp;
              <Select
                value={status}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setStatus(value);
                }}
              >
                <Option value="Production">Production</Option>
                <Option value="Dismantle">Dismantle</Option>
                <Option value="Offloaded">Offloaded</Option>
                <Option value="Powered Off">Powered Off</Option>
                <Option value="Excluded">Excluded</Option>
              </Select>
            </InputWrapper> */}
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

const StyledInput = styled(Input)`
  height: 1.6rem;
`;

const InputWrapper = styled.div`
  font-size: 12px;
  white-space: nowrap;
  display: flex;
  justify-content: space-between;
  padding-bottom: 10px;
`;

const StyledSubmitButton = styled(Input)`
  font-size: 11px;
  font-weight: bolder;
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
  height: 27px;
  font-size: 11px;
  font-weight: bolder;
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

export default AddDeviceModal;
