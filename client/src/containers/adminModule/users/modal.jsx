import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import { getConfig } from "@testing-library/react";

const Index = (props) => {
  const { Option } = Select;
  const getString = (str) => {
    return str ? str : "";
  };
  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  console.log(props.editRecord);
  let [device, setDevice] = useState(props.editRecord);

  let [userId, setUserId] = useState(device ? getString(device.user_id) : "");
  let [emailAddress, setEmailAddress] = useState(
    device ? getString(device.email_address) : ""
  );
  let [name, setName] = useState(device ? getString(device.name) : "");
  let [password, setPassword] = useState(
    device ? getString(device.password) : ""
  );
  let [role, setRole] = useState(device ? getString(device.role) : "");
  let [status, setStatus] = useState(device ? getString(device.status) : false);
  let [accountType, setAccountType] = useState(
    device ? getString(device.account_type) : false
  );
  let [team, setTeam] = useState(
    device
      ? getString(device.team)
        ? getString(device.team)
        : "PERFORMANCE"
      : "PERFORMANCE"
  );
  let [vendor, setVendor] = useState(
    device
      ? getString(device.vendor)
        ? getString(device.vendor)
        : "Cisco"
      : "Cisco"
  );
  const roles = ["Admin", "User", "Executive", "Engineer"];
  const teams = [
    "PERFORMANCE",
    "DEVELOPMENT",
    "EDN",
    "IGW",
    "SOC",
    "SYSTEMS",
    "FO",
    "CABLING",
    "IPT",
    "EDN-SM",
    "IT",
    "Others",
  ];
  const vendors = ["Cisco", "Mobily"];

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/editUser", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllUsers")
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
      user_id: userId,
      email_address: emailAddress,
      password,
      name,
      role,
      status,
      account_type: accountType,
      team,
      vendor,
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
      style={{ marginTop: "-25px", zIndex: "99999" }}
      width="50%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Member</p>
          </Col>
          <Col span={24}>
            <InputWrapper>
              User Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={userId} readonly />
              ) : (
                <StyledInput
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  required
                />
              )}
            </InputWrapper>
            <InputWrapper>
              Email Address: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </InputWrapper>
            {accountType === "Local User" ? (
              <InputWrapper>
                Password: &nbsp;<span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput
                  placeholder="******"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  // required
                />
              </InputWrapper>
            ) : null}
            <InputWrapper>
              Role: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={role ? role : "User"}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setRole(value);
                }}
              >
                {roles.map((role, index) => {
                  return (
                    <Option key={index} value={role}>
                      {role}
                    </Option>
                  );
                })}
              </Select>
            </InputWrapper>
            <InputWrapper>
              Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={status}
                defaultActiveFirstOption={true}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setStatus(value);
                }}
              >
                <Option value={"Active"}>Active</Option>
                <Option value={"Inactive"}>Inactive</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Account Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={accountType}
                defaultActiveFirstOption={true}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setAccountType(value);
                }}
              >
                <Option value={"Local User"}>Local User</Option>
                <Option value={"Non Local User"}>Non Local User</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Team: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={team}
                defaultActiveFirstOption={true}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setTeam(value);
                }}
              >
                {getOptions(teams)}
              </Select>
            </InputWrapper>
            <InputWrapper>
              Vendor: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={vendor}
                defaultActiveFirstOption={true}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVendor(value);
                }}
              >
                {getOptions(vendors)}
              </Select>
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

export default Index;
