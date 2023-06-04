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
  let [ip, setIp] = useState(device ? getString(device.edn_mpls_id) : "");
  let [siteId, setSiteId] = useState(device ? getString(device.site_id) : "");

  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );
  let [deviceIp, setDeviceIp] = useState(
    device ? getString(device.device_ip) : ""
  );
  let [total1GPorts, setTotal1GPorts] = useState(
    device ? getString(device.total_1g_ports) : ""
  );
  let [total10GPorts, setTotal10GPorts] = useState(
    device ? getString(device.total_10g_ports) : ""
  );
  let [total40GPorts, setTotal40GPorts] = useState(
    device ? getString(device.total_40g_ports) : ""
  );
  let [total100GPorts, setTotal100GPorts] = useState(
    device ? getString(device.total_100g_ports) : ""
  );
  let [connected1G, setConnected1G] = useState(
    device ? getString(device.connected_1g) : ""
  );
  let [connected10G, setConnected10G] = useState(
    device ? getString(device.connected_10g) : ""
  );
  let [connected40G, setConnected40G] = useState(
    device ? getString(device.connected_40g) : ""
  );
  let [connected100G, setConnected100G] = useState(
    device ? getString(device.connected_100g) : ""
  );
  let [notConnected1G, setNotConnected1G] = useState(
    device ? getString(device.not_connected_1g) : ""
  );
  let [notConnected10G, setNotConnected10G] = useState(
    device ? getString(device.not_connected_10g) : ""
  );
  let [notConnected40G, setNotConnected40G] = useState(
    device ? getString(device.not_connected_40g) : ""
  );
  let [notConnected100G, setNotConnected100G] = useState(
    device ? getString(device.not_connected_100g) : ""
  );
  let [unusedSFPs1G, setUnusedSFPs1G] = useState(
    device ? getString(device.unused_sfps_1g) : ""
  );
  let [unusedSFPs10G, setUnusedSFPs10G] = useState(
    device ? getString(device.unused_sfps_10g) : ""
  );
  let [unusedSFPs40G, setUnusedSFPs40G] = useState(
    device ? getString(device.unused_sfps_40g) : ""
  );
  let [unusedSFPs100G, setUnusedSFPs100G] = useState(
    device ? getString(device.unused_sfps_100g) : ""
  );

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/addEdnMplsDevice", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllEdnMpls")
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
      site_id: siteId,
      device_id: deviceId,
      device_ip: deviceIp,
      total_1g_ports: total1GPorts,
      total_10g_ports: total10GPorts,
      total_40g_ports: total40GPorts,
      total_100g_ports: total100GPorts,
      connected_1g: connected1G,
      connected_10g: connected10G,
      connected_40g: connected40G,
      connected_100g: connected100G,
      not_connected_1g: notConnected1G,
      not_connected_10g: notConnected10G,
      not_connected_40g: notConnected40G,
      not_connected_100g: notConnected100G,
      unused_sfps_1g: unusedSFPs1G,
      unused_sfps_10g: unusedSFPs10G,
      unused_sfps_40g: unusedSFPs40G,
      unused_sfps_100g: unusedSFPs100G,
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
      width="90%"
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
          <Col span={8}>
            {device ? (
              <InputWrapper>
                EDN MPLS Id:&nbsp;&nbsp;
                <StyledInput value={ip} readonly />
              </InputWrapper>
            ) : null}
            <InputWrapper>
              Site Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Device Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Device Ip: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deviceIp}
                onChange={(e) => setDeviceIp(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Total 1G Ports: &nbsp;&nbsp;
              <StyledInput
                value={total1GPorts}
                onChange={(e) => setTotal1GPorts(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Total 10G Ports: &nbsp;&nbsp;
              <StyledInput
                value={total10GPorts}
                onChange={(e) => setTotal10GPorts(e.target.value)}
              />
            </InputWrapper>

            <InputWrapper>
              Total 10G Ports: &nbsp;&nbsp;
              <StyledInput
                value={total40GPorts}
                onChange={(e) => setTotal40GPorts(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Total 100G Ports: &nbsp;&nbsp;
              <StyledInput
                value={total100GPorts}
                onChange={(e) => setTotal100GPorts(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Connected 1G: &nbsp;&nbsp;
              <StyledInput
                value={connected1G}
                onChange={(e) => setConnected1G(e.target.value)}
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Connected 10G: &nbsp;&nbsp;
              <StyledInput
                value={connected10G}
                onChange={(e) => setConnected10G(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Connected 40G: &nbsp;&nbsp;
              <StyledInput
                value={connected40G}
                onChange={(e) => setConnected40G(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Connected 100G: &nbsp;&nbsp;
              <StyledInput
                value={connected100G}
                onChange={(e) => setConnected100G(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Not Connected 1G: &nbsp;&nbsp;
              <StyledInput
                value={notConnected1G}
                onChange={(e) => setNotConnected1G(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Not Connected 10G:&nbsp;&nbsp;
              <StyledInput
                value={notConnected10G}
                onChange={(e) => setNotConnected10G(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Not Connected 40G:&nbsp;&nbsp;
              <StyledInput
                value={notConnected40G}
                onChange={(e) => setNotConnected40G(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Not Connected 100G:&nbsp;&nbsp;
              <StyledInput
                value={notConnected100G}
                onChange={(e) => setNotConnected100G(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Unused SFPs 1G:&nbsp;&nbsp;
              <StyledInput
                value={unusedSFPs1G}
                onChange={(e) => setUnusedSFPs1G(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Unused SFPs 10G:&nbsp;&nbsp;
              <StyledInput
                value={unusedSFPs10G}
                onChange={(e) => setUnusedSFPs10G(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Unused SFPs 40G:&nbsp;&nbsp;
              <StyledInput
                value={unusedSFPs40G}
                onChange={(e) => setUnusedSFPs40G(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Unused SFPs 100G:&nbsp;&nbsp;
              <StyledInput
                value={unusedSFPs100G}
                onChange={(e) => setUnusedSFPs100G(e.target.value)}
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
