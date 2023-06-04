import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import { getConfig } from "@testing-library/react";
import Swal from "sweetalert2";

const Index = (props) => {
  const { Option } = Select;
  let [deviceId, setDeviceId] = useState("");

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDeviceId = async (data) => {
    await axios
      .post(baseUrl + "/deleteSeedDevice", data)
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
        Swal.fire({
          title: "Something went wrong!",
          type: "warning",
          // icon: "success",
        });
      });
  };

  const handleSubmitId = (e) => {
    e.preventDefault();
    const data = {
      device_id: deviceId,
    };
    Swal.fire({
      title: "Are you sure, you want to delete this seed?",
      type: "warning",
      allowOutsideClick: false,
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Yes, I am sure!",
      cancelButtonText: "No, cancel it!",
    }).then(function (isConfirm) {
      if (isConfirm["value"]) {
        postDeviceId(data);
      }
    });
  };

  const handleCancelId = () => {
    setDeviceId("");
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
      <form onSubmit={handleSubmitId}>
        <StyledCard>
          <Row gutter={30}>
            <Col span={24} style={{ textAlign: "center" }}>
              <p style={{ fontSize: "22px" }}>Delete Seed By Device Id</p>
            </Col>
            <Col span={24}>
              <InputWrapper>
                Device Id: &nbsp;
                <span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput
                  value={deviceId}
                  onChange={(e) => setDeviceId(e.target.value)}
                  required
                />
              </InputWrapper>
            </Col>
            <Col span={24} style={{ textAlign: "center" }}>
              <StyledButton color="green" onClick={handleCancelId}>
                Cancel
              </StyledButton>
              &nbsp; &nbsp;{" "}
              <StyledSubmitButton color="red" type="submit" value="Delete" />
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
