import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select, Spin } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import moment from "moment";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  let [column, setColumn] = useState("");
  let [newValue, setNewValue] = useState("");
  let [loading, setLoading] = useState(false);

  const postDevice = async (device) => {
    try {
      setLoading(true);
      await axios
        .post(baseUrl + "/bulkUpdateDeviceColumn", device)
        .then((res) => {
          setLoading(false);
          console.log(res);
          alert("successfully updated");
        })
        .catch((err) => {
          setLoading(false);
          alert(err);
          console.log(err);
        });
    } catch (err) {
      setLoading(false);
      alert(err);
      console.log(err);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const device = {
      filters: {
        device_id: props.deviceId,
        ip_address: props.ipAddress,
        function: props.functiond,
      },
      column,
      value: newValue,
    };

    if (column !== "") {
      // props.setIsModalVisible(false);
      postDevice(device);
    } else {
      alert("You have not selected the column to update");
    }
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const getOptions = (columnsArray = []) => {
    let options = [];
    columnsArray?.map((item) => {
      options.push(<Option value={item.value}>{item.label}</Option>);
    });
    return options;
  };

  return (
    <Spin spinning={loading}>
      <Modal
        style={{ marginTop: "40px", zIndex: "99999" }}
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
                Update Column For Searched Rows
              </p>
            </Col>
            <Col span={24}>
              <Spin tip="Loading..." spinning={loading}>
                <InputWrapper>
                  Column: &nbsp;<span style={{ color: "red" }}>*</span>
                  &nbsp;&nbsp;
                  <Select
                    value={column}
                    style={{ width: "100%" }}
                    onChange={(value) => {
                      setColumn(value);
                    }}
                  >
                    {getOptions(props.columnsArray)}
                  </Select>
                </InputWrapper>
              </Spin>
              <InputWrapper>
                New Value: &nbsp;<span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  required
                />
              </InputWrapper>
            </Col>
            <Col span={24} style={{ textAlign: "center", paddingTop: "20px" }}>
              <StyledButton color={"red"} onClick={handleCancel}>
                Cancel
              </StyledButton>
              &nbsp; &nbsp;{" "}
              <StyledSubmitButton
                color={"green"}
                type="submit"
                value="Update"
              />
            </Col>
          </Row>
        </form>
      </Modal>
    </Spin>
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
