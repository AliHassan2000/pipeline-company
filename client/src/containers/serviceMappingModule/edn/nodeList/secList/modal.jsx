import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../../../utils/axios";
// import axios from "axios";
// import { SEED_API } from "../../../GlobalVar";

const AddDeviceModal = (props) => {
  const { Option } = Select;
  const getString = (str) => {
    return str ? str : "";
  };

  let [device, setDevice] = useState(props.editRecord);
  let [ip, setIp] = useState(device ? getString(device.fw_ip_address) : "");
  let [region, setRegion] = useState(device ? getString(device.region) : "");
  let [segment, setSegment] = useState(device ? getString(device.segment) : "");

  let [fwId, setFwId] = useState(device ? getString(device.fw_id) : "");
  let [vendor, setVendor] = useState(device ? getString(device.vendor) : "");
  let [osType, setOsType] = useState(device ? getString(device.os_type) : "");

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/addSecDevice", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllSecIps")
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
      fw_ip_address: ip,
      region,
      segment,
      fw_id: fwId,
      vendor,
      os_type: osType,
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
              FW IP-Address: &nbsp;&nbsp;
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
              FW Id: &nbsp;&nbsp;
              <StyledInput
                value={fwId}
                onChange={(e) => setFwId(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Region: &nbsp;&nbsp;
              <StyledInput
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
            </InputWrapper>

            <InputWrapper>
              Segment: &nbsp;&nbsp;
              <Input
                value={segment}
                onChange={(e) => setSegment(e.target.value)}
              />
            </InputWrapper>

            <InputWrapper>
              Vendor: &nbsp;&nbsp;
              <Input
                value={vendor}
                onChange={(e) => setVendor(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Os Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={osType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setOsType(value);
                }}
              >
                <Option value="IOS">IOS</Option>
                <Option value="NX-OS">NX-OS</Option>
                <Option value="FOS">FOS</Option>
                <Option value="Junos">Junos</Option>
                <Option value="ASA">ASA</Option>
                <Option value="F5">F5</Option>
              </Select>
            </InputWrapper>
            {/* <InputWrapper>
              Os Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Input
                value={osType}
                onChange={(e) => setOsType(e.target.value)}
                required
              />
            </InputWrapper> */}
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
