import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button } from "antd";
import axios, { baseUrl } from "../../../../../utils/axios";

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
  // let [ip, setIp] = useState(device ? getString(device.owner_id) : "");
  let [vmName, setVMName] = useState(device ? getString(device.vm_name) : "");

  let [ownerName, setOwnerName] = useState(
    device ? getString(device.owner_name) : ""
  );

  let [ownerEmail, setOwnerEmail] = useState(
    device ? getString(device.owner_email) : ""
  );

  let [ownerContact, setOwnerContact] = useState(
    device ? getString(device.owner_contact) : ""
  );

  let [appName, setAppName] = useState(
    device ? getString(device.app_name) : ""
  );

  let [status, setStatus] = useState(device ? getString(device.status) : "");
  let [instanceId, setInstanceId] = useState(
    device ? getString(device.instance_id) : ""
  );

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/ownersNew", [device])
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/owners")
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
      // owner_id: ip,
      vm_name: vmName,
      owner_name: ownerName,
      owner_email: ownerEmail,
      owner_contact: ownerContact,
      app_name: appName,
      status: status,
      instance_id: instanceId,
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
      width="50%"
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
          <Col span={24}>
            {/* {device ? (
              <InputWrapper>
                Owner Id:&nbsp;&nbsp;
                <StyledInput value={ip} readonly />
              </InputWrapper>
            ) : null} */}
            <InputWrapper>
              VM Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={vmName}
                onChange={(e) => setVMName(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Owner Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={ownerName}
                onChange={(e) => setOwnerName(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Owner Email: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={ownerEmail}
                onChange={(e) => setOwnerEmail(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Owner Contact: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={ownerContact}
                onChange={(e) => setOwnerContact(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              App Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Instance Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={instanceId}
                onChange={(e) => setInstanceId(e.target.value)}
                required
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
