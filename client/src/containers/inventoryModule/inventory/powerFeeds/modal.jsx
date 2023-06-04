import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
import Swal from "sweetalert2";

const AddDeviceModal = (props) => {
  const { Option } = Select;

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

  let [deviceIds, setDeviceIds] = useState([]);
  let [deviceIdOptions, setDeviceIdOptions] = useState([]);
  // let [siteIds, setSiteIds] = useState([]);
  // let [siteIdOptions, setSiteIdOptions] = useState([]);
  // let [rackIds, setRackIds] = useState([]);
  // let [rackIdOptions, setRackIdOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await axios.get(baseUrl + "/getAllDeviceIDs");
        setDeviceIds(res.data);
        // const res1 = await axios.get(baseUrl + "/getAllSiteIDs");
        // setSiteIds(res1.data);
        // const res2 = await axios.get(baseUrl + "/getAllRackIDs");
        // setRackIds(res2.data);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  useEffect(() => {
    getDeviceIdOptions(deviceIds);
    // getSiteIdOptions(siteIds);
    // getRackIdOptions(rackIds);
  }, [deviceIds]);
  // }, [siteIds, rackIds]);

  const getDeviceIdOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setDeviceIdOptions(options);
    // return options;
  };

  // const getSiteIdOptions = (values = []) => {
  //   let options = [];
  //   values.map((value) => {
  //     options.push(<Option value={value}>{value}</Option>);
  //   });
  //   setSiteIdOptions(options);
  //   // return options;
  // };

  // const getRackIdOptions = (values = []) => {
  //   let options = [];
  //   values.map((value) => {
  //     options.push(<Option value={value}>{value}</Option>);
  //   });
  //   setRackIdOptions(options);
  //   // return options;
  // };

  // const regex =
  //   "^[0-9]{4}-(0[1-9]|[1][012])-(0[1-9]|[12][0-9]|3[01]) ([0-1][0-9]|2[0123]):([0-5][0-9]):([0-5][0-9])$";
  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////

  let [id, setId] = useState(device ? getString(device.power_id) : "");
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );

  // let [siteId, setSiteId] = useState(device ? getString(device.site_id) : "");
  // let [rackId, setRackId] = useState(device ? getString(device.rack_id) : "");
  let [powerSourceType, setPowerSourceType] = useState(
    device ? getString(device.power_source_type) : "AC"
  );
  let [numberOfPowerSources, setNumberOfPowerSources] = useState(
    device ? getString(device.number_of_power_sources) : "1"
  );
  let [pSU1Fuse, setPSU1Fuse] = useState(
    device ? getString(device.psu1_fuse) : ""
  );
  let [pSU2Fuse, setPSU2Fuse] = useState(
    device ? getString(device.psu2_fuse) : ""
  );
  let [pSU3Fuse, setPSU3Fuse] = useState(
    device ? getString(device.psu3_fuse) : ""
  );
  let [pSU4Fuse, setPSU4Fuse] = useState(
    device ? getString(device.psu4_fuse) : ""
  );
  let [pSU5Fuse, setPSU5Fuse] = useState(
    device ? getString(device.psu5_fuse) : ""
  );
  let [pSU6Fuse, setPSU6Fuse] = useState(
    device ? getString(device.psu6_fuse) : ""
  );

  let [pSU1PDUDetails, setPSU1PDUDetails] = useState(
    device ? getString(device.psu1_pdu_details) : ""
  );
  let [pSU2PDUDetails, setPSU2PDUDetails] = useState(
    device ? getString(device.psu2_pdu_details) : ""
  );
  let [pSU3PDUDetails, setPSU3PDUDetails] = useState(
    device ? getString(device.psu3_pdu_details) : ""
  );
  let [pSU4PDUDetails, setPSU4PDUDetails] = useState(
    device ? getString(device.psu4_pdu_details) : ""
  );
  let [pSU5PDUDetails, setPSU5PDUDetails] = useState(
    device ? getString(device.psu5_pdu_details) : ""
  );
  let [pSU6PDUDetails, setPSU6PDUDetails] = useState(
    device ? getString(device.psu6_pdu_details) : ""
  );

  let [pSU1DCDPDetails, setPSU1DCDPDetails] = useState(
    device ? getString(device.psu1_dcdp_details) : ""
  );
  let [pSU2DCDPDetails, setPSU2DCDPDetails] = useState(
    device ? getString(device.psu2_dcdp_details) : ""
  );
  let [pSU3DCDPDetails, setPSU3DCDPDetails] = useState(
    device ? getString(device.psu3_dcdp_details) : ""
  );
  let [pSU4DCDPDetails, setPSU4DCDPDetails] = useState(
    device ? getString(device.psu4_dcdp_details) : ""
  );
  let [pSU5DCDPDetails, setPSU5DCDPDetails] = useState(
    device ? getString(device.psu5_dcdp_details) : ""
  );
  let [pSU6DCDPDetails, setPSU6DCDPDetails] = useState(
    device ? getString(device.psu6_dcdp_details) : ""
  );

  let [status, setStatus] = useState(device ? getString(device.status) : "");

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/addPower", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert(
              `Power ${device ? "Updated" : "Added"} Successfully`,
              "success"
            );
            const promises = [];
            promises.push(
              axios
                .get(baseUrl + "/getPower")
                .then((response) => {
                  console.log(response.data);
                  props.setDataSource(response.data);
                  props.excelData = response.data;
                  props.setRowCount(response.data.length);
                  props.excelData = response.data;
                })
                .catch((error) => {
                  console.log(error);
                  //  openSweetAlert("Something Went Wrong!", "error");
                })
            );
            return Promise.all(promises);
          }
        })
        .catch((error) => {
          console.log("in add seed device catch ==> " + error);
          // openSweetAlert("Something Went Wrong!", "error");
        });
    } catch (err) {
      console.log(err);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const device = {
      power_id: id,
      device_id: deviceId,
      // status,
      // site_id: siteId,
      // rack_id: rackId,
      power_source_type: powerSourceType,
      number_of_power_sources: numberOfPowerSources,
      psu1_fuse: pSU1Fuse,
      psu2_fuse: pSU2Fuse,
      psu3_fuse: pSU3Fuse,
      psu4_fuse: pSU4Fuse,
      psu5_fuse: pSU5Fuse,
      psu6_fuse: pSU6Fuse,
      psu1_pdu_details: pSU1PDUDetails,
      psu2_pdu_details: pSU2PDUDetails,
      psu3_pdu_details: pSU3PDUDetails,
      psu4_pdu_details: pSU4PDUDetails,
      psu5_pdu_details: pSU5PDUDetails,
      psu6_pdu_details: pSU6PDUDetails,
      psu1_dcdp_details: pSU1DCDPDetails,
      psu2_dcdp_details: pSU2DCDPDetails,
      psu3_dcdp_details: pSU3DCDPDetails,
      psu4_dcdp_details: pSU4DCDPDetails,
      psu5_dcdp_details: pSU5DCDPDetails,
      psu6_dcdp_details: pSU6DCDPDetails,
    };

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  // function disabledDate(current) {
  //   // Can not select days before today and today
  //   return current && current < moment().endOf("day");
  // }

  // function range(start, end) {
  //   const result = [];
  //   for (let i = start; i < end; i++) {
  //     result.push(i);
  //   }
  //   return result;
  // }

  // function disabledDateTime() {
  //   return {
  //     disabledHours: () => range(0, 24).splice(4, 20),
  //     disabledMinutes: () => range(30, 60),
  //     disabledSeconds: () => [55, 56],
  //   };
  // }

  // const setAdjustedDate = (date, dateField) => {
  //   let tempDate = date?.toISOString().replace("T", " ").split(".")[0];
  //   let myString = tempDate.split(" ")[1];
  //   let myStringParts = myString.split(":");
  //   let hourDelta = myStringParts[0];
  //   let minuteDelta = myStringParts[1];
  //   let secondsDelta = myStringParts[2];
  //   let adjustedDate = date
  //     .subtract({
  //       hours: hourDelta,
  //       minutes: minuteDelta,
  //       seconds: secondsDelta,
  //     })
  //     ?.toISOString()
  //     .replace("T", " ")
  //     .split(".")[0];
  //   //console.log(adjustedDate);
  //   dateField === "manufacture"
  //     ? setManufactureDate(adjustedDate)
  //     : setRfsDate(adjustedDate);
  // };

  const getOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  return (
    <Modal
      style={{ marginTop: "-20px", zIndex: "99999" }}
      width="60%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>
              {device ? "Edit" : "Add"} Power Feed
            </p>
          </Col>
          <Col span={12}>
            {/* <InputWrapper>
              Ip: &nbsp;<span style={{ color: "red" }}>*</span>
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
            </InputWrapper> */}
            <InputWrapper>
              Device Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={deviceId} readonly />
              ) : (
                <Select
                  value={deviceId}
                  style={{ width: "100%" }}
                  onChange={(value) => {
                    setDeviceId(value);
                  }}
                  showSearch
                  // placeholder="Select a person"
                  optionFilterProp="children"
                  // onSearch={onSearch}
                  filterOption={(input, option) =>
                    option.children
                      .toLowerCase()
                      .indexOf(input.toLowerCase()) >= 0
                  }
                >
                  {deviceIdOptions}
                </Select>
              )}
            </InputWrapper>
            {/* <InputWrapper>
              Site Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={siteId} readonly />
              ) : (
                <Select
                  value={siteId}
                  style={{ width: "100%" }}
                  onChange={(value) => {
                    setSiteId(value);
                  }}
                  showSearch
                  // placeholder="Select a person"
                  optionFilterProp="children"
                  // onSearch={onSearch}
                  filterOption={(input, option) =>
                    option.children
                      .toLowerCase()
                      .indexOf(input.toLowerCase()) >= 0
                  }
                >
                  {siteIdOptions}
                </Select>
              )}
            </InputWrapper>
            <InputWrapper>
              Rack Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={rackId} readonly />
              ) : (
                <Select
                  value={rackId}
                  style={{ width: "100%" }}
                  onChange={(value) => {
                    setRackId(value);
                  }}
                  showSearch
                  optionFilterProp="children"
                  filterOption={(input, option) =>
                    option.children
                      .toLowerCase()
                      .indexOf(input.toLowerCase()) >= 0
                  }
                >
                  {rackIdOptions}
                </Select>
              )}
            </InputWrapper> */}
            {/* <InputWrapper>
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
            </InputWrapper> */}
            <InputWrapper>
              Power Source Type: &nbsp;&nbsp;
              <Select
                value={powerSourceType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setPowerSourceType(value);
                }}
              >
                {getOptions(["AC", "DC"])}
              </Select>
              {/* <StyledInput
                value={powerSourceType}
                onChange={(e) => setPowerSourceType(e.target.value)}
                // required
              /> */}
            </InputWrapper>
            <InputWrapper>
              No. Of Power Sources: &nbsp;&nbsp;
              <Select
                value={numberOfPowerSources}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setNumberOfPowerSources(value);
                }}
              >
                {getOptions(["1", "2"])}
              </Select>
              {/* <StyledInput
                value={numberOfPowerSources}
                onChange={(e) => setNumberOfPowerSources(e.target.value)}
                // required
              /> */}
            </InputWrapper>
            <InputWrapper>
              PSU1 Fuse: &nbsp;&nbsp;
              <StyledInput
                value={pSU1Fuse}
                onChange={(e) => setPSU1Fuse(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU2 Fuse: &nbsp;&nbsp;
              <StyledInput
                value={pSU2Fuse}
                onChange={(e) => setPSU2Fuse(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU3 Fuse: &nbsp;&nbsp;
              <StyledInput
                value={pSU3Fuse}
                onChange={(e) => setPSU3Fuse(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU4 Fuse: &nbsp;&nbsp;
              <StyledInput
                value={pSU4Fuse}
                onChange={(e) => setPSU4Fuse(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU5 Fuse: &nbsp;&nbsp;
              <StyledInput
                value={pSU5Fuse}
                onChange={(e) => setPSU5Fuse(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU6 Fuse: &nbsp;&nbsp;
              <StyledInput
                value={pSU6Fuse}
                onChange={(e) => setPSU6Fuse(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU1 PDU Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU1PDUDetails}
                onChange={(e) => setPSU1PDUDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU2 PDU Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU2PDUDetails}
                onChange={(e) => setPSU2PDUDetails(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              PSU3 PDU Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU3PDUDetails}
                onChange={(e) => setPSU3PDUDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU4 PDU Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU4PDUDetails}
                onChange={(e) => setPSU4PDUDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU5 PDU Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU5PDUDetails}
                onChange={(e) => setPSU5PDUDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU6 PDU Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU6PDUDetails}
                onChange={(e) => setPSU6PDUDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU1 DCDP Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU1DCDPDetails}
                onChange={(e) => setPSU1DCDPDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU2 DCDP Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU2DCDPDetails}
                onChange={(e) => setPSU2DCDPDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU3 DCDP Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU3DCDPDetails}
                onChange={(e) => setPSU3DCDPDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU4 DCDP Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU4DCDPDetails}
                onChange={(e) => setPSU4DCDPDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU5 DCDP Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU5DCDPDetails}
                onChange={(e) => setPSU5DCDPDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              PSU6 DCDP Details: &nbsp;&nbsp;
              <StyledInput
                value={pSU6DCDPDetails}
                onChange={(e) => setPSU6DCDPDetails(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center" }}>
            <br />
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
