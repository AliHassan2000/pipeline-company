import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select, DatePicker } from "antd";
import moment from "moment";
import axios, { baseUrl } from "../../../../utils/axios";

const AddDeviceModal = (props) => {
  const { Option } = Select;
  const getString = (str) => {
    return str ? str : "";
  };

  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////
  let [ip, setIp] = useState(device ? getString(device.license_id) : "");
  let [dismantleDate, setDismantleDate] = useState(
    device ? getString(device.dismantle_date) : ""
  );
  // let [itemCode, setItemCode] = useState(
  //   device ? getString(device.item_code) : ""
  // );
  // let [itemDesc, setItemDesc] = useState(
  //   device ? getString(device.item_desc) : ""
  // );
  let [clei, setClei] = useState(device ? getString(device.clei) : "");
  let [status, setStatus] = useState(device ? getString(device.status) : "");

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/editLicenses", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllLicenses")
              .then((response) => {
                console.log(response.data);
                props.setDataSource(response.data);
                props.setRowCount(response.data.length);
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
      license_id: ip,
      dismantle_date: dismantleDate,
      status,
      // item_code: itemCode,
      // item_desc: itemDesc,
      clei,
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
            <p style={{ fontSize: "22px" }}>
              {device ? "Edit" : "Add"} License
            </p>
          </Col>
          <Col span={24}>
            <InputWrapper>
              License Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
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
            </InputWrapper>
            <InputWrapper>
              Dismantle Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setDismantleDate(dateString);
                }}
                defaultValue={
                  dismantleDate ? moment(dismantleDate, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
            </InputWrapper>
            {/* <InputWrapper>
              Item Code:&nbsp;&nbsp;
              <StyledInput
                value={itemCode}
                onChange={(e) => setItemCode(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Item Desc: &nbsp;&nbsp;
              <StyledInput
                value={itemDesc}
                onChange={(e) => setItemDesc(e.target.value)}
                // required
              />
            </InputWrapper>
             */}
            <InputWrapper>
              Clei:&nbsp;&nbsp;
              <StyledInput
                value={clei}
                onChange={(e) => setClei(e.target.value)}
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
