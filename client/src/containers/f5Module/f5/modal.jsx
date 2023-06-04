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

  let [ip, setIp] = useState(device ? getString(device.f5_id) : "");
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );
  let [ipAddress, setIpAddress] = useState(
    device ? getString(device.ip_address) : ""
  );
  let [vServerName, setVServerName] = useState(
    device ? getString(device.vserver_name) : ""
  );
  let [vip, setVIP] = useState(device ? getString(device.vip) : "");
  let [poolName, setPoolName] = useState(
    device ? getString(device.pool_name) : ""
  );
  let [poolMember, setPoolMember] = useState(
    device ? getString(device.pool_member) : ""
  );
  let [node, setNode] = useState(device ? getString(device.node) : "");
  let [servicePort, setServicePort] = useState(
    device ? getString(device.service_port) : ""
  );
  let [monitorValue, setMonitorValue] = useState(
    device ? getString(device.monitor_value) : ""
  );
  let [monitorStatus, setMonitorStatus] = useState(
    device ? getString(device.monitor_status) : ""
  );
  let [lbMethod, setLBMethod] = useState(
    device ? getString(device.lb_method) : ""
  );

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/editF5", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllF5")
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
      f5_id: ip,
      device_id: deviceId,
      ip_address: ipAddress,
      vserver_name: vServerName,
      vip: vip,
      pool_name: poolName,
      pool_member: poolMember,
      node,
      service_port: servicePort,
      monitor_value: monitorValue,
      monitor_status: monitorStatus,
      lb_method: lbMethod,
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
            <InputWrapper>
              Device Id: &nbsp;&nbsp;
              <StyledInput
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Ip Address: &nbsp;&nbsp;
              <StyledInput
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              V Server Name: &nbsp;&nbsp;
              <StyledInput
                value={vServerName}
                onChange={(e) => setVServerName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              VIP: &nbsp;&nbsp;
              <StyledInput
                value={vip}
                onChange={(e) => setVIP(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Pool Name: &nbsp;&nbsp;
              <StyledInput
                value={poolName}
                onChange={(e) => setPoolName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              LB Method: &nbsp;&nbsp;
              <StyledInput
                value={lbMethod}
                onChange={(e) => setLBMethod(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Pool Member: &nbsp;&nbsp;
              <StyledInput
                value={poolMember}
                onChange={(e) => setPoolMember(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Node: &nbsp;&nbsp;
              <StyledInput
                value={node}
                onChange={(e) => setNode(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Service Port: &nbsp;&nbsp;
              <StyledInput
                value={servicePort}
                onChange={(e) => setServicePort(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Monitor Value: &nbsp;&nbsp;
              <StyledInput
                value={monitorValue}
                onChange={(e) => setMonitorValue(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Monitor Status: &nbsp;&nbsp;
              <StyledInput
                value={monitorStatus}
                onChange={(e) => setMonitorStatus(e.target.value)}
              />
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center" }}>
            <br />
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
