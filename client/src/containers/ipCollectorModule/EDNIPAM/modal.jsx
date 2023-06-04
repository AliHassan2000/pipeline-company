import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button } from "antd";
import axios, { baseUrl } from "../../../utils/axios";

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
  let [ip, setIp] = useState(device ? getString(device.edn_mpls_id) : "");
  let [deviceAName, setDeviceAName] = useState(
    device ? getString(device.device_a_name) : ""
  );

  let [deviceAInterface, setDeviceAInterface] = useState(
    device ? getString(device.device_a_interface) : ""
  );
  let [deviceATrunkName, setDeviceATrunkName] = useState(
    device ? getString(device.device_a_trunk_name) : ""
  );
  let [deviceAIp, setDeviceAIp] = useState(
    device ? getString(device.device_a_ip) : ""
  );
  let [deviceBSystemName, setDeviceBSystemName] = useState(
    device ? getString(device.device_b_system_name) : ""
  );
  let [deviceBInterface, setDeviceBInterface] = useState(
    device ? getString(device.device_b_interface) : ""
  );
  let [deviceBIp, setDeviceBIp] = useState(
    device ? getString(device.device_b_ip) : ""
  );
  let [deviceBType, setDeviceBType] = useState(
    device ? getString(device.device_b_type) : ""
  );
  let [deviceBPortDesc, setDeviceBPortDesc] = useState(
    device ? getString(device.device_b_port_desc) : ""
  );
  let [deviceAMac, setDeviceAMac] = useState(
    device ? getString(device.device_a_mac) : ""
  );
  let [deviceBMac, setDeviceBMac] = useState(
    device ? getString(device.device_b_mac) : ""
  );
  let [deviceAPortDesc, setDeviceAPortDesc] = useState(
    device ? getString(device.device_a_port_desc) : ""
  );
  let [deviceAVlan, setDeviceAVlan] = useState(
    device ? getString(device.device_a_vlan) : ""
  );
  let [deviceAVlanName, setDeviceAVlanName] = useState(
    device ? getString(device.device_a_vlan_name) : ""
  );

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/addEdnMplsDevice", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllEdnMpls")
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
      edn_mpls_id: ip,
      device_a_name: deviceAName,
      device_a_interface: deviceAInterface,
      device_a_trunk_name: deviceATrunkName,
      device_a_ip: deviceAIp,
      device_b_system_name: deviceBSystemName,
      device_b_interface: deviceBInterface,
      device_b_ip: deviceBIp,
      device_b_type: deviceBType,
      device_b_port_desc: deviceBPortDesc,
      device_a_mac: deviceAMac,
      device_b_mac: deviceBMac,
      device_a_port_desc: deviceAPortDesc,
      device_a_vlan: deviceAVlan,
      device_a_vlan_name: deviceAVlanName,
    };

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  return (
    <Modal
      style={{ marginTop: "0px", zIndex: "99999" }}
      width="90%"
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
          <Col span={8}>
            {device ? (
              <InputWrapper>
                EDN MPLS Id:&nbsp;&nbsp;
                <StyledInput value={ip} readonly />
              </InputWrapper>
            ) : null}
            <InputWrapper>
              Device A Ip: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deviceAIp}
                onChange={(e) => setDeviceAIp(e.target.value)}
                required
              />
            </InputWrapper>
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
                value={deviceAInterface}
                onChange={(e) => setDeviceAInterface(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Device A Trunk Name: &nbsp;&nbsp;
              <StyledInput
                value={deviceATrunkName}
                onChange={(e) => setDeviceATrunkName(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Device B System Name: &nbsp;&nbsp;
              <StyledInput
                value={deviceBSystemName}
                onChange={(e) => setDeviceBSystemName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Device B Interface: &nbsp;&nbsp;
              <StyledInput
                value={deviceBInterface}
                onChange={(e) => setDeviceBInterface(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Device B Ip: &nbsp;&nbsp;
              <StyledInput
                value={deviceBIp}
                onChange={(e) => setDeviceBIp(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Device B Type: &nbsp;&nbsp;
              <StyledInput
                value={deviceBType}
                onChange={(e) => setDeviceBType(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              deviceBPortDesc: &nbsp;&nbsp;
              <StyledInput
                value={deviceBPortDesc}
                onChange={(e) => setDeviceBPortDesc(e.target.value)}
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Device A Mac: &nbsp;&nbsp;
              <StyledInput
                value={deviceAMac}
                onChange={(e) => setDeviceAMac(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Device B Mac: &nbsp;&nbsp;
              <StyledInput
                value={deviceBMac}
                onChange={(e) => setDeviceBMac(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Device A Port Desc: &nbsp;&nbsp;
              <StyledInput
                value={deviceAPortDesc}
                onChange={(e) => setDeviceAPortDesc(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Device A Vlan:&nbsp;&nbsp;
              <StyledInput
                value={deviceAVlan}
                onChange={(e) => setDeviceAVlan(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Device A Vlan Name:&nbsp;&nbsp;
              <StyledInput
                value={deviceAVlanName}
                onChange={(e) => setDeviceAVlanName(e.target.value)}
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
