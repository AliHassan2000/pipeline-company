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
        const res1 = await axios.get(baseUrl + "/getDismantleDeviceId");
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

  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";

  let [device, setDevice] = useState(props.editRecord);

  let [ip, setIp] = useState(
    device ? getString(device.handback_tracker_id) : ""
  );
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );
  let [crqNo, setCRQNo] = useState(device ? getString(device.crq_no) : "");
  let [handbackStatus, setHandbackStatus] = useState(
    device ? getString(device.handback_status) : "Completed"
  );
  let [assignedTo, setAssignedTo] = useState(
    device ? getString(device.assigned_to) : ""
  );
  let [associatedCircuitIdDetails, setAssociatedCircuitIdDetails] = useState(
    device ? getString(device.associated_circuit_id_details) : ""
  );
  let [ipDecomissioningCRQ, setIpDecomissioningCRQ] = useState(
    device ? getString(device.ip_decomissioning_crq) : ""
  );
  let [projectRepresentative, setProjectRepresentative] = useState(
    device ? getString(device.project_representative) : ""
  );
  let [poNo, setPoNo] = useState(device ? getString(device.po_no) : "");
  let [configurationCleanupStatus, setConfigurationCleanupStatus] = useState(
    device ? getString(device.configuration_cleanup_status) : "Yes"
  );
  let [extraOldDevices, setExtraOldDevices] = useState(
    device ? getString(device.extra_old_devices) : ""
  );
  let [handbackSubmissionDate, setHandbackSubmissionDate] = useState(
    device ? getString(device.handback_submission_date) : null
  );
  let [handbackCompletionDate, setHandbackCompletionDate] = useState(
    device ? getString(device.handback_completion_date) : null
  );
  let [ipAddress, setIpAddress] = useState(
    device ? getString(device.ip_address) : ""
  );
  let [assignedTos, setAssignedTos] = useState([]);
  let [assignedToOptions, setAssignedToOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getAssignees");
        setAssignedTos(res1.data);
        if (assignedTo === "") {
          setAssignedTo(res1?.data[0]);
        }
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  useEffect(() => {
    getAssignedToOptions(assignedTos);
  }, [assignedTos]);

  const getAssignedToOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setAssignedToOptions(options);
  };

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/ednHandbackTracker", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/ednHandbackTracker")
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
    if (handbackSubmissionDate && deviceId) {
      const device = [
        {
          handback_tracker_id: ip,
          device_id: deviceId,
          crq_no: crqNo, //Not Null
          handback_status: handbackStatus, //drop down (Completed/Pending)
          assigned_to: assignedTo, //drop down from endpoint "/getAssignees"
          associated_circuit_id_details: associatedCircuitIdDetails,
          ip_decomissioning_crq: ipDecomissioningCRQ,
          project_representative: projectRepresentative,
          po_no: poNo, //Not Null
          configuration_cleanup_status: configurationCleanupStatus, //drop down (Yes/No)
          extra_old_devices: extraOldDevices,
          associated_circuit_id_details: associatedCircuitIdDetails,
          handback_submission_date: handbackSubmissionDate, //Not Null
          handback_completion_date: handbackCompletionDate,
          // ip_address: ipAddress, //Not Null
        },
      ];

      props.setIsModalVisible(false);
      postDevice(device);
    } else {
      alert("Device id and handback submission date can not be empty");
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
              {device ? "Edit" : "Add"} EDN Handback Tracker
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
            <InputWrapper>
              CRQ No: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={crqNo}
                onChange={(e) => setCRQNo(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Handback Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={handbackStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setHandbackStatus(value);
                }}
                required
              >
                <Option value="Completed">Completed</Option>
                <Option value="Pending">Pending</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Assigned To: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={assignedTo}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setAssignedTo(value);
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
            </InputWrapper>
            <InputWrapper>
              Associated Circuit Id Details:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={associatedCircuitIdDetails}
                onChange={(e) => setAssociatedCircuitIdDetails(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Ip DeComissioning CRQ:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={ipDecomissioningCRQ}
                onChange={(e) => setIpDecomissioningCRQ(e.target.value)}
                // required
              />
            </InputWrapper>{" "}
          </Col>

          <Col span={12}>
            <InputWrapper>
              Project Representative:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={projectRepresentative}
                onChange={(e) => setProjectRepresentative(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Po No:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={poNo}
                onChange={(e) => setPoNo(e.target.value)}
                // required
              />
            </InputWrapper>{" "}
            <InputWrapper>
              Configuration Cleanup Status: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={configurationCleanupStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setConfigurationCleanupStatus(value);
                }}
                required
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
              </Select>
            </InputWrapper>{" "}
            <InputWrapper>
              Extra Old Devices:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={extraOldDevices}
                onChange={(e) => setExtraOldDevices(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Handback Submission Date: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setHandbackSubmissionDate(dateString);
                }}
                defaultValue={
                  handbackSubmissionDate
                    ? moment(handbackSubmissionDate, "DD-MM-YYYY")
                    : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
                required
              />
            </InputWrapper>
            <InputWrapper>
              Handback Completion Date: &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setHandbackCompletionDate(dateString);
                }}
                defaultValue={
                  handbackCompletionDate
                    ? moment(handbackCompletionDate, "DD-MM-YYYY")
                    : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
            </InputWrapper>
            {/* <InputWrapper>
              IP Address: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
                required
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
