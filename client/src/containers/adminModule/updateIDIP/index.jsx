import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import { getConfig } from "@testing-library/react";
import Swal from "sweetalert2";

const Index = (props) => {
  const { Option } = Select;

  let [oldDeviceIp, setOldDeviceIp] = useState("");
  let [newDeviceIp, setNewDeviceIp] = useState("");

  let [oldDeviceId, setOldDeviceId] = useState("");
  let [newDeviceId, setNewDeviceId] = useState("");

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDeviceIP = async (data) => {
    try {
      await axios
        .post(baseUrl + "/editDeviceIp", data)
        .then((res) => {
          console.log(res);
          console.log(res.data);
          if (data?.code === "200") {
            openSweetAlert(res.data.response, "success");
          } else {
            openSweetAlert(res.data.response, "danger");
          }
        })
        .catch((err) => {
          console.log(err);
        });
    } catch (err) {
      console.log(err);
    }
  };

  const postDeviceID = async (data) => {
    try {
      await axios
        .post(baseUrl + "/editDeviceId", data)
        .then((res) => {
          console.log(res.data);
          if (data?.code === "200") {
            openSweetAlert(res.data.response, "success");
          } else {
            openSweetAlert(res.data.response, "danger");
          }
        })
        .catch((err) => {
          console.log(err);
        });
    } catch (err) {
      console.log(err);
    }
  };

  const handleSubmitIP = (e) => {
    e.preventDefault();
    const data = {
      old_device_ip: oldDeviceIp,
      new_device_ip: newDeviceIp,
    };

    postDeviceIP(data);
  };

  const handleSubmitID = (e) => {
    e.preventDefault();
    const data = {
      old_device_id: oldDeviceId,
      new_device_id: newDeviceId,
    };

    postDeviceID(data);
  };

  const handleCancelIP = () => {
    setOldDeviceIp("");
    setNewDeviceIp("");
  };

  const handleCancelID = () => {
    setOldDeviceId("");
    setNewDeviceId("");
  };

  const getOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  return (
    <div>
      <form onSubmit={handleSubmitID}>
        <StyledCard>
          <Row gutter={30}>
            <Col span={24} style={{ textAlign: "center" }}>
              <p style={{ fontSize: "22px" }}>Update ID</p>
            </Col>
            <Col span={24}>
              <InputWrapper>
                Existing ID: &nbsp;&nbsp;&nbsp;
                <span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput
                  value={oldDeviceId}
                  onChange={(e) => setOldDeviceId(e.target.value)}
                  required
                />
              </InputWrapper>
              <InputWrapper>
                New ID: &nbsp;<span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput
                  value={newDeviceId}
                  onChange={(e) => setNewDeviceId(e.target.value)}
                  required
                />
              </InputWrapper>
            </Col>
            <Col span={24} style={{ textAlign: "center" }}>
              <StyledButton color={"red"} onClick={handleCancelID}>
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
        </StyledCard>
      </form>
      <form onSubmit={handleSubmitIP}>
        <StyledCard>
          <Row gutter={30}>
            <Col span={24} style={{ textAlign: "center" }}>
              <p style={{ fontSize: "22px" }}>Update IP</p>
            </Col>
            <Col span={24}>
              <InputWrapper>
                Existing IP: &nbsp;
                <span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput
                  value={oldDeviceIp}
                  onChange={(e) => setOldDeviceIp(e.target.value)}
                  required
                />
              </InputWrapper>
              <InputWrapper>
                New IP: &nbsp;<span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput
                  value={newDeviceIp}
                  onChange={(e) => setNewDeviceIp(e.target.value)}
                  required
                />
              </InputWrapper>
            </Col>
            <Col span={24} style={{ textAlign: "center" }}>
              <StyledButton color={"red"} onClick={handleCancelIP}>
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
        </StyledCard>
      </form>
    </div>
  );
};

const StyledCard = styled.div`
  /* margin-top: -10px; */
  margin-bottom: 20px;
  height: 100%;
  /* text-align: center; */
  background-color: white;
  border-radius: 10px;
  padding: 10px 20px 20px 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;

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
