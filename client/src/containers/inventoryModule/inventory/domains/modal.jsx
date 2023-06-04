import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
// import axios from "axios";
// import { SEED_API } from "../../../GlobalVar";

const AddDeviceModal = (props) => {
  const getString = (str) => {
    return str ? str : "";
  };

  let [device, setDevice] = useState(props.editRecord);
  let [ip, setIp] = useState(device ? getString(device.domain_id) : "");
  let [domain, setDomain] = useState(device ? getString(device.domain) : "");
  let [section, setSection] = useState(device ? getString(device.section) : "");
  let [department, setDepartment] = useState(
    device ? getString(device.department) : ""
  );

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/addDomain", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllDomain")
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
      domain_id: ip,
      domain,
      section,
      department,
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
      width="50%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Domain</p>
          </Col>
          <Col span={24}>
            <InputWrapper>
              Domain: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Input
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Section: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Input
                value={section}
                onChange={(e) => setSection(e.target.value)}
                required
              />
            </InputWrapper>{" "}
            <InputWrapper>
              Department: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Input
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                required
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
