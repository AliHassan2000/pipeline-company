import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select as SimpleSelect } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
import Select from "react-select";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  const getString = (str) => {
    return str ? str : "";
  };

  const getMultiSelectOptions = (comaSeparatedString) => {
    return comaSeparatedString?.split(",").map((element) => {
      return { value: element, label: element };
    });
  };

  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////
  let [ip, setIp] = useState(device ? getString(device.site_id) : "");
  let [region, setRegion] = useState(device ? getString(device.region) : "");
  let [siteName, setSiteName] = useState(
    device ? getString(device.site_name) : ""
  );
  let [city, setCity] = useState(device ? getString(device.city) : "");
  let [latitude, setLatitude] = useState(
    device ? getString(device.latitude) : ""
  );
  let [longitude, setLongitude] = useState(
    device ? getString(device.longitude) : ""
  );
  let [status, setStatus] = useState(
    device
      ? { value: device.status, label: device.status }
      : { value: "Production", label: "Production" }
  );
  let [siteType, setSiteType] = useState(
    device
      ? getMultiSelectOptions(device.site_type)
      : [{ value: "DC", label: "DC" }]
  );
  //   let [itemCode, setItemCode] = useState(
  //     device ? getString(device.item_code) : ""
  //   );
  //   let [itemDesc, setItemDesc] = useState(
  //     device ? getString(device.item_desc) : ""
  //   );
  // let [clei, setClei] = useState(device ? getString(device.clei) : "");

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/addSite", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllPhy")
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
    let siteTypes = siteType?.reduce((accumulator, currentValue, index) => {
      if (index !== siteType.length - 1) {
        return accumulator + currentValue.value + ",";
      } else {
        return accumulator + currentValue.value;
      }
    }, "");
    e.preventDefault();
    const device = {
      site_id: ip,
      site_type: siteTypes,
      region,
      site_name: siteName,
      city,
      latitude,
      longitude,
      status: status.value,
    };

    props.setIsModalVisible(false);
    console.log(device);
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

  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      background: "#fff",
      borderColor: "#9e9e9e",
      minHeight: "30px",
      height: "30px",
      boxShadow: state.isFocused ? null : null,
    }),

    valueContainer: (provided, state) => ({
      ...provided,
      height: "30px",
      padding: "0 6px",
    }),

    input: (provided, state) => ({
      ...provided,
      margin: "0px",
    }),
    indicatorSeparator: (state) => ({
      display: "none",
    }),
    indicatorsContainer: (provided, state) => ({
      ...provided,
      height: "30px",
    }),
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
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Site</p>
          </Col>
          <Col span={24}>
            <InputWrapper>
              Site Id: &nbsp;<span style={{ color: "red" }}>*</span>
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
              Region: &nbsp;&nbsp;
              <StyledInput
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Site Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={siteName} readonly />
              ) : (
                <StyledInput
                  value={siteName}
                  onChange={(e) => setSiteName(e.target.value)}
                  required
                />
              )}
            </InputWrapper>
            <InputWrapper>
              City: &nbsp;&nbsp;
              <StyledInput
                value={city}
                onChange={(e) => setCity(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Latitude: &nbsp;&nbsp;
              <StyledInput
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Longitude: &nbsp;&nbsp;
              <StyledInput
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                // required
              />
            </InputWrapper>

            <InputWrapper>
              Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <Select
                  styles={customStyles}
                  options={[
                    { value: "Production", label: "Production" },
                    { value: "Dismantle", label: "Dismantle" },
                  ]}
                  value={status}
                  style={{ width: "100%" }}
                  onChange={(e) => {
                    setStatus(e);
                  }}
                  required
                />
                {/* {getOptions(["Production", "Dismantle"])}
              </Select> */}
              </div>
              {/* <StyledInput
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                required
              /> */}
            </InputWrapper>
            <InputWrapper>
              Site Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <Select
                  isMulti
                  styles={customStyles}
                  value={siteType}
                  onChange={(e) => setSiteType(e)}
                  options={[
                    { value: "DC", label: "DC" },
                    { value: "DCN", label: "DCN" },
                    { value: "CO", label: "CO" },
                    { value: "FB", label: "FB" },
                    { value: "FS", label: "FS" },
                    { value: "KSK", label: "KSK" },
                    { value: "MFB", label: "MFB" },
                    { value: "MOI", label: "MOI" },
                  ]}
                />
              </div>
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
                required
              />
            </InputWrapper>
            */}
            {/* <InputWrapper>
              Clei:&nbsp;&nbsp;
              <StyledInput
                value={clei}
                onChange={(e) => setClei(e.target.value)}
                // required
              />
            </InputWrapper> */}
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
