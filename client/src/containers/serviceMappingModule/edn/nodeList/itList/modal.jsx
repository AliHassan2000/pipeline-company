import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
// import axios from "axios";
// import { SEED_API } from "../../../GlobalVar";

const AddDeviceModal = (props) => {
  const getString = (str) => {
    return str ? str : "";
  };

  let [device, setDevice] = useState(props.editRecord);
  let [ip, setIp] = useState(device ? getString(device.ip_address) : "");
  let [serverName, setServerName] = useState(
    device ? getString(device.server_name) : ""
  );
  let [applicationName, setApplicationName] = useState(
    device ? getString(device.application_name) : ""
  );
  let [ownerEmail, setOwnerEmail] = useState(
    device ? getString(device.owner_email) : ""
  );
  let [ownerContact, setOwnerContact] = useState(
    device ? getString(device.owner_contact) : ""
  );

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/addItDevice", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllItIps")
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
      ip_address: ip,
      server_name: serverName,
      application_name: applicationName,
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
      style={{ marginTop: "0px", zIndex: "99999" }}
      width="40%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>
              {device ? "Edit" : "Add"} Device{" "}
            </p>
          </Col>
          <Col span={24}>
            <InputWrapper>
              IP-Address: &nbsp;&nbsp;
              {device ? (
                <StyledInput value={ip} readonly />
              ) : (
                <StyledInput
                  value={ip}
                  onChange={(e) => setIp(e.target.value)}
                  required
                />
              )}
            </InputWrapper>
            <InputWrapper>
              Server Name: &nbsp;&nbsp;
              <Input
                value={serverName}
                onChange={(e) => setServerName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Application Name: &nbsp;&nbsp;
              <StyledInput
                value={applicationName}
                onChange={(e) => setApplicationName(e.target.value)}
              />
            </InputWrapper>

            <InputWrapper>
              Owner Email: &nbsp;&nbsp;
              <Input
                value={ownerEmail}
                onChange={(e) => setOwnerEmail(e.target.value)}
              />
            </InputWrapper>

            <InputWrapper>
              Owner Contact: &nbsp;&nbsp;
              <Input
                value={ownerContact}
                onChange={(e) => setOwnerContact(e.target.value)}
              />
            </InputWrapper>
          </Col>

          <Col span={24} style={{ textAlign: "center" }}>
            {" "}
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
