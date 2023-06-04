import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";

const AddDeviceModal = (props) => {
  const correctDatePattern = (date) => {
    if (date != null) {
      let d = date.split(date[10]);
      return d[0] + " " + d[1];
    } else return;
  };

  const getString = (str) => {
    return str ? str : "";
  };

  const getDateString = (dateStr) => {
    return dateStr; // ? correctDatePattern(dateStr) : "";
  };

  // const regex =
  //   "^[0-9]{4}-(0[1-9]|[1][012])-(0[1-9]|[12][0-9]|3[01]) ([0-1][0-9]|2[0123]):([0-5][0-9]):([0-5][0-9])$";
  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////
  let [ip, setIp] = useState(
    device ? getString(device.igw_service_mapping_id) : ""
  );
  let [deviceAName, setDeviceAName] = useState(
    device ? getString(device.device_a_name) : ""
  );

  let [interfaceAName, setInterfaceAName] = useState(
    device ? getString(device.device_a_interface) : ""
  );
  let [deviceBIp, setDeviceBIp] = useState(
    device ? getString(device.device_b_ip) : ""
  );
  let [deviceBMac, setDeviceBMac] = useState(
    device ? getString(device.device_b_mac) : ""
  );
  let [deviceBSystemName, setDeviceBSystemName] = useState(
    device ? getString(device.device_b_system_name) : ""
  );
  let [deviceBType, setDeviceBType] = useState(
    device ? getString(device.device_b_type) : ""
  );
  let [serverName, setServerName] = useState(
    device ? getString(device.server_name) : ""
  );
  let [serverOS, setServerOS] = useState(
    device ? getString(device.server_os) : ""
  );
  let [appName, setAppName] = useState(
    device ? getString(device.app_name) : ""
  );
  let [ownerName, setOwnerName] = useState(
    device ? getString(device.owner_name) : ""
  );
  let [ownerEmail, setOwnerEmail] = useState(
    device ? getString(device.owner_email) : ""
  );
  let [ownerContact, setOwnerContact] = useState(
    device ? getString(device.owner_contact) : ""
  );

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/addIgwService", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllIgwServices")
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
      igw_service_mapping_id: ip,
      device_a_name: deviceAName,
      device_a_interface: interfaceAName,
      device_b_ip: deviceBIp,
      device_b_mac: deviceBMac,
      device_b_system_name: deviceBSystemName,
      device_b_type: deviceBType,
      server_name: serverName,
      server_os: serverOS,
      app_name: appName,
      owner_name: ownerName,
      owner_email: ownerEmail,
      owner_contact: ownerContact,
    };

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  return (
    <Modal
      style={{ marginTop: "30px", zIndex: "99999" }}
      width="60%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Record</p>
          </Col>
          <Col span={12}>
            {device ? (
              <InputWrapper>
                Igw Service Mapping Id:&nbsp;&nbsp;
                <StyledInput value={ip} readonly />
              </InputWrapper>
            ) : null}
            <InputWrapper>
              Device A Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deviceAName}
                onChange={(e) => setDeviceAName(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Device A Interface: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={interfaceAName}
                onChange={(e) => setInterfaceAName(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Device B Ip: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deviceBIp}
                onChange={(e) => setDeviceBIp(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Device B Mac: &nbsp;&nbsp;
              <StyledInput
                value={deviceBMac}
                onChange={(e) => setDeviceBMac(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Device B System Name: &nbsp;&nbsp;
              <StyledInput
                value={deviceBSystemName}
                onChange={(e) => setDeviceBSystemName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Device B Type: &nbsp;&nbsp;
              <StyledInput
                value={deviceBType}
                onChange={(e) => setDeviceBType(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Server Name: &nbsp;&nbsp;
              <StyledInput
                value={serverName}
                onChange={(e) => setServerName(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Server OS: &nbsp;&nbsp;
              <StyledInput
                value={serverOS}
                onChange={(e) => setServerOS(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              App Name: &nbsp;&nbsp;
              <StyledInput
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Owner Name: &nbsp;&nbsp;
              <StyledInput
                value={ownerName}
                onChange={(e) => setOwnerName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Owner Email: &nbsp;&nbsp;
              <StyledInput
                value={ownerEmail}
                onChange={(e) => setOwnerEmail(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Owner Contact: &nbsp;&nbsp;
              <StyledInput
                value={ownerContact}
                onChange={(e) => setOwnerContact(e.target.value)}
              />
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center", paddingTop: "20px" }}>
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
