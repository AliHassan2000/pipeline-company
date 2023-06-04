import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";

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
  let [ip, setIp] = useState(device ? getString(device.igw_links_id) : "");
  let [serviceType, setServiceType] = useState(
    device ? getString(device.service_type) : ""
  );

  let [provider, setProvider] = useState(
    device ? getString(device.provider) : ""
  );
  let [router, setRouter] = useState(device ? getString(device.router) : "");
  let [_Interface, setInterface] = useState(
    device ? getString(device.interface) : ""
  );
  let [localIPV4, setLocalIPV4] = useState(
    device ? getString(device.local_ipv4) : ""
  );
  let [neighborIPV4, setNeighborIPV4] = useState(
    device ? getString(device.neighbor_ipv4) : ""
  );
  let [localIPV6, setLocalIPV6] = useState(
    device ? getString(device.local_ipv6) : ""
  );
  let [neighborIPV6, setNeighborIPV6] = useState(
    device ? getString(device.neighbor_ipv6) : ""
  );
  let [neighborASN, setNeighborASN] = useState(
    device ? getString(device.neighbor_asn) : ""
  );
  let [ipv4EgressPolicy, setIPV4EgressPolicy] = useState(
    device ? getString(device.ipv4_egress_policy) : ""
  );
  let [community, setCommunity] = useState(
    device ? getString(device.community) : ""
  );
  let [ipv4IngressPolicy, setIPV4IngressPolicy] = useState(
    device ? getString(device.ipv4_ingress_policy) : ""
  );

  let [ipv4LocalPreference, setIPV4LocalPreference] = useState(
    device ? getString(device.ipv4_local_preference) : ""
  );
  let [ipv6EgressPolicy, setIPV6EgressPolicy] = useState(
    device ? getString(device.ipv6_egress_policy) : ""
  );
  let [ipv6IngressPolicy, setIPV6IngressPolicy] = useState(
    device ? getString(device.ipv6_ingress_policy) : ""
  );
  let [ipv6LocalPreference, setIPV6LocalPreference] = useState(
    device ? getString(device.ipv6_local_preference) : ""
  );
  let [ipv4AdvertisedRoutesCount, setIPV4AdvertisedRoutesCount] = useState(
    device ? getString(device.ipv4_advertised_routes_count) : ""
  );
  let [ipv4ReceivedRoutesCount, setIPV4ReceivedRoutesCount] = useState(
    device ? getString(device.ipv4_received_routes_count) : ""
  );
  let [ipv6AdvertisedRoutesCount, setIPV6AdvertisedRoutesCount] = useState(
    device ? getString(device.ipv6_advertised_routes_count) : ""
  );
  let [ipv6ReceivedRoutesCount, setIPV6ReceivedRoutesCount] = useState(
    device ? getString(device.ipv6_received_routes_count) : ""
  );

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/addIgwLink", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllIgwLinks")
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
      igw_links_id: ip,
      service_type: serviceType,
      provider,
      router,
      interface: _Interface,
      local_ipv4: localIPV4,
      neighbor_ipv4: neighborIPV4,
      local_ipv6: localIPV6,
      neighbor_ipv6: neighborIPV6,
      neighbor_asn: neighborASN,
      ipv4_egress_policy: ipv4EgressPolicy,
      community,
      ipv4_ingress_policy: ipv4IngressPolicy,
      ipv4_local_preference: ipv4LocalPreference,
      ipv6_egress_policy: ipv6EgressPolicy,
      ipv6_ingress_policy: ipv6IngressPolicy,
      ipv6_local_preference: ipv6LocalPreference,
      ipv4_advertised_routes_count: ipv4AdvertisedRoutesCount,
      ipv4_received_routes_count: ipv4ReceivedRoutesCount,
      ipv6_advertised_routes_count: ipv6AdvertisedRoutesCount,
      ipv6_received_routes_count: ipv6ReceivedRoutesCount,
    };

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  return (
    <Modal
      style={{ marginTop: "30px", zIndex: "99999" }}
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
          <Col span={12}>
            {device ? (
              <InputWrapper>
                Igw Links Id:&nbsp;&nbsp;
                <StyledInput value={ip} readonly />
              </InputWrapper>
            ) : null}
            <InputWrapper>
              Service Type:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Provider:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Router:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={router}
                onChange={(e) => setRouter(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Interface: &nbsp;&nbsp;
              <StyledInput
                value={_Interface}
                onChange={(e) => setInterface(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Local IPV4: &nbsp;&nbsp;
              <StyledInput
                value={localIPV4}
                onChange={(e) => setLocalIPV4(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Neighbor IPV4: &nbsp;&nbsp;
              <StyledInput
                value={neighborIPV4}
                onChange={(e) => setNeighborIPV4(e.target.value)}
                // required
              />
            </InputWrapper>

            <InputWrapper>
              Local IPV6: &nbsp;&nbsp;
              <StyledInput
                value={localIPV6}
                onChange={(e) => setLocalIPV6(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Neighbor IPV6: &nbsp;&nbsp;
              <StyledInput
                value={neighborIPV6}
                onChange={(e) => setNeighborIPV6(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Neighbor ASN: &nbsp;&nbsp;
              <StyledInput
                value={neighborASN}
                onChange={(e) => setNeighborASN(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV4 Egress Policy: &nbsp;&nbsp;
              <StyledInput
                value={ipv4EgressPolicy}
                onChange={(e) => setIPV4EgressPolicy(e.target.value)}
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Community: &nbsp;&nbsp;
              <StyledInput
                value={community}
                onChange={(e) => setCommunity(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV4 Ingress Policy: &nbsp;&nbsp;
              <StyledInput
                value={ipv4IngressPolicy}
                onChange={(e) => setIPV4IngressPolicy(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV4 Local Preference: &nbsp;&nbsp;
              <StyledInput
                value={ipv4LocalPreference}
                onChange={(e) => setIPV4LocalPreference(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV6 Egress Policy: &nbsp;&nbsp;
              <StyledInput
                value={ipv6EgressPolicy}
                onChange={(e) => setIPV6EgressPolicy(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV6 Ingress Policy: &nbsp;&nbsp;
              <StyledInput
                value={ipv6IngressPolicy}
                onChange={(e) => setIPV6IngressPolicy(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV6 Local Preference: &nbsp;&nbsp;
              <StyledInput
                value={ipv6LocalPreference}
                onChange={(e) => setIPV6LocalPreference(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV4 Advertised Routes Count: &nbsp;&nbsp;
              <StyledInput
                value={ipv4AdvertisedRoutesCount}
                onChange={(e) => setIPV4AdvertisedRoutesCount(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV4 Received Routes Count: &nbsp;&nbsp;
              <StyledInput
                value={ipv4ReceivedRoutesCount}
                onChange={(e) => setIPV4ReceivedRoutesCount(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV6 Advertised Routes Count: &nbsp;&nbsp;
              <StyledInput
                value={ipv6AdvertisedRoutesCount}
                onChange={(e) => setIPV6AdvertisedRoutesCount(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              IPV6 Received Routes Count: &nbsp;&nbsp;
              <StyledInput
                value={ipv6ReceivedRoutesCount}
                onChange={(e) => setIPV6ReceivedRoutesCount(e.target.value)}
              />
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center", paddingTop: "20px" }}>
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
