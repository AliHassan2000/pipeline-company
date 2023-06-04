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
  let [vrf, setVrf] = useState(device ? getString(device.vrf) : "");
  let [route, setRoute] = useState(device ? getString(device.route) : "");
  let [nextHop, setNextHop] = useState(
    device ? getString(device.next_hop) : ""
  );
  let [asPath, setAsPath] = useState(device ? getString(device.as_path) : "");
  let [origin, setOrigin] = useState(device ? getString(device.origin) : "");

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/externalVRFAnalysis", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllExternalVRFAnalysis")
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
      vrf,
      route,
      next_hop: nextHop,
      as_path: asPath,
      origin,
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
          <Col span={24}>
            {/* {device ? (
              <InputWrapper>
               VRF:&nbsp;&nbsp;
                <StyledInput value={vrf} readonly />
              </InputWrapper>
            ) : null} */}
            <InputWrapper>
              VRF: &nbsp;&nbsp;
              <StyledInput
                value={vrf}
                onChange={(e) => setVrf(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Route: &nbsp;&nbsp;
              <StyledInput
                value={route}
                onChange={(e) => setRoute(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Next Hop: &nbsp;&nbsp;
              <StyledInput
                value={nextHop}
                onChange={(e) => setNextHop(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              AS Path: &nbsp;&nbsp;
              <StyledInput
                value={asPath}
                onChange={(e) => setAsPath(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Origin: &nbsp;&nbsp;
              <StyledInput
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
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
