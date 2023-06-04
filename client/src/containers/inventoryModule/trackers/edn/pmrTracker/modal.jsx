import React, { useState, useEffect } from "react";
import styled from "styled-components";
import {
  Row,
  Col,
  Modal,
  Input,
  Button,
  Select,
  DatePicker,
  Space,
} from "antd";
import axios, { baseUrl } from "../../../../../utils/axios";
import Swal from "sweetalert2";
import moment from "moment";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  let [deviceIds, setDeviceIds] = useState([]);
  let [deviceIdOptions, setDeviceIdOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getDeviceId");
        setDeviceIds(res1.data);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);
  useEffect(() => {
    getDeviceOptions(deviceIds);
  }, [deviceIds]);

  const getDeviceOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setDeviceIdOptions(options);
  };

  const getString = (str) => {
    return str ? str : "";
  };

  let [device, setDevice] = useState(props.editRecord);

  let [ip, setIp] = useState(
    device ? getString(device.edn_pmr_tracker_id) : ""
  );
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );
  let [ipAddress, setIpAddress] = useState(
    device ? getString(device.ip_address) : ""
  );
  let [serialNumber, setSerialNumber] = useState(
    device ? getString(device.serial_number) : "Completed"
  );
  let [vendor, setVendor] = useState(device ? getString(device.vendor) : "");
  let [model, setModel] = useState(device ? getString(device.model) : "");
  let [criticality, setCriticality] = useState(
    device ? getString(device.criticality) : ""
  );
  let [domain, setDomain] = useState(device ? getString(device.domain) : "");
  let [virtual, setVirtual] = useState(device ? getString(device.virtual) : "");
  let [deviceStatus, setDeviceStatus] = useState(
    device ? getString(device.device_status) : "Yes"
  );
  let [deviceRemarks, setDeviceRemarks] = useState(
    device ? getString(device.device_remarks) : ""
  );
  let [siteId, setSiteId] = useState(device ? getString(device.site_id) : null);
  let [siteType, setSiteType] = useState(
    device ? getString(device.site_type) : null
  );
  let [latitude, setLatitude] = useState(
    device ? getString(device.latitude) : ""
  );

  let [longitude, setLongitude] = useState(
    device ? getString(device.longitude) : ""
  );
  let [city, setCity] = useState(device ? getString(device.city) : "");
  let [region, setRegion] = useState(device ? getString(device.region) : "");
  let [rackId, setRackId] = useState(device ? getString(device.rack_id) : "");
  let [rackName, setRackName] = useState(
    device ? getString(device.rack_name) : ""
  );
  let [pmrQuarter, setPMRQuarter] = useState(
    device ? getString(device.pmr_quarter) : "Q1"
  );
  let [pmrCRQ, setPMRCRQ] = useState(device ? getString(device.pmr_crq) : "");
  let [pmrDate, setPMRDate] = useState(
    device ? getString(device.pmr_date) : ""
  );
  let [pmrStatus, setPMRStatus] = useState(
    device ? getString(device.pmr_status) : ""
  );
  let [pmrRemarks, setPMRRemarks] = useState(
    device ? getString(device.pmr_remarks) : ""
  );

  let [doorLocksStatus, setDoorLocksStatus] = useState(
    device ? getString(device.door_locks_status) : ""
  );
  let [labelsStatus, setLabelsStatus] = useState(
    device ? getString(device.labels_status) : ""
  );
  let [pmrCorrectiveActions, setPMRCorrectiveActions] = useState(
    device ? getString(device.pmr_corrective_actions) : ""
  );

  //   let [assignedTos, setAssignedTos] = useState([]);
  //   let [assignedToOptions, setAssignedToOptions] = useState([]);

  //   useEffect(() => {
  //     (async () => {
  //       try {
  //         const res1 = await axios.get(baseUrl + "/getAssignees");
  //         setAssignedTos(res1.data);
  //         // setAssignedTo(res1?.data[0]);
  //       } catch (err) {
  //         console.log(err.response);
  //       }
  //     })();
  //   }, []);

  //   useEffect(() => {
  //     getAssignedToOptions(assignedTos);
  //   }, [assignedTos]);

  //   const getAssignedToOptions = (values = []) => {
  //     let options = [];
  //     values.map((value) => {
  //       options.push(<Option value={value}>{value}</Option>);
  //     });
  //     setAssignedToOptions(options);
  //   };

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/ednPMRTracker", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/ednPMRTracker")
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
    if (deviceId && pmrDate) {
      const device = [
        {
          edn_pmr_tracker_id: ip,
          device_id: deviceId,
          ip_address: ipAddress,
          serial_number: serialNumber,
          vendor,
          model,
          criticality,
          domain,
          virtual,
          device_status: deviceStatus,
          device_remarks: deviceRemarks,
          site_id: siteId,
          site_type: siteType,
          latitude,
          longitude,
          city,
          region,
          rack_id: rackId,
          rack_name: rackName,
          pmr_quarter: pmrQuarter,
          pmr_crq: pmrCRQ,
          pmr_date: pmrDate,
          pmr_status: pmrStatus,
          pmr_remarks: pmrRemarks,
          door_locks_status: doorLocksStatus,
          labels_status: labelsStatus,
          pmr_corrective_actions: pmrCorrectiveActions,
        },
      ];

      props.setIsModalVisible(false);
      postDevice(device);
    } else {
      alert("Device id and PMR date can not be empty");
    }
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
            <p style={{ fontSize: "22px" }}>
              {device ? "Edit" : "Add"} EDN PMR Tracker
            </p>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Device Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <Select style={{ width: "100%" }} value={deviceId} disabled />
              ) : (
                <Select
                  value={deviceId}
                  style={{ width: "100%" }}
                  onChange={(value) => {
                    setDeviceId(value);
                  }}
                  showSearch
                  optionFilterProp="children"
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
              Ip Address: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Serial Number: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={serialNumber}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setSerialNumber(value);
                }}
                required
              >
                <Option value="Completed">Completed</Option>
                <Option value="Pending">Pending</Option>
              </Select>
            </InputWrapper> */}
            {/* <InputWrapper>
            Vendor: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={vendor}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVendor(value);
                }}
                showSearch
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {assignedToOptions}
              </Select>
            </InputWrapper> */}
            {/* <InputWrapper>
            Model:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={model}
                onChange={(e) => setModel(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Criticality:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={criticality}
                onChange={(e) => setCriticality(e.target.value)}
                // required
              />
            </InputWrapper> */}

            {/* <InputWrapper>
            Domain:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Virtual:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={virtual}
                onChange={(e) => setVirtual(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Device Status: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={deviceStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setDeviceStatus(value);
                }}
                required
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
              </Select>
            </InputWrapper> */}
            <InputWrapper>
              Device Remarks:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={deviceRemarks}
                onChange={(e) => setDeviceRemarks(e.target.value)}
                // required
              />
            </InputWrapper>
            {/* <InputWrapper>
            Site Id:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Site Type:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={siteType}
                onChange={(e) => setSiteType(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Latitude:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Longitude:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            City:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={city}
                onChange={(e) => setCity(e.target.value)}
                // required
              />
            </InputWrapper> */}

            {/* <InputWrapper>
            Region:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Rack Id:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={rackId}
                onChange={(e) => setRackId(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
            Rack Name:
              &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={rackName}
                onChange={(e) => setRackName(e.target.value)}
                // required
              />
            </InputWrapper> */}

            <InputWrapper>
              PMR Quarter: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={pmrQuarter}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setPMRQuarter(value);
                }}
              >
                <Option value="Q1">Q1</Option>
                <Option value="Q2">Q2</Option>
                <Option value="Q3">Q3</Option>
                <Option value="Q4">Q4</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              PMR CRQ: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={pmrCRQ}
                onChange={(e) => setPMRCRQ(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              PMR Date: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setPMRDate(dateString);
                }}
                defaultValue={pmrDate ? moment(pmrDate, "DD-MM-YYYY") : null}
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
                required
              />
            </InputWrapper>
          </Col>

          <Col span={12}>
            <InputWrapper>
              PMR Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={pmrStatus}
                onChange={(e) => setPMRStatus(e.target.value)}
                required
              />
            </InputWrapper>

            <InputWrapper>
              PMR Remarks:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={pmrRemarks}
                onChange={(e) => setPMRRemarks(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Door Lock Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={doorLocksStatus}
                onChange={(e) => setDoorLocksStatus(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Labels Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={labelsStatus}
                onChange={(e) => setLabelsStatus(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              PMR Corrective Actions: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={pmrCorrectiveActions}
                onChange={(e) => setPMRCorrectiveActions(e.target.value)}
                required
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
