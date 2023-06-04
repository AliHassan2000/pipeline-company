import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select, DatePicker } from "antd";
import axios, { baseUrl } from "../../../../../utils/axios";
import Swal from "sweetalert2";
import moment from "moment";
import Attachment from "./attachment";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  const getString = (str) => {
    return str ? str : "";
  };

  let [device, setDevice] = useState(props.editRecord);

  let [id, setId] = useState(
    device ? getString(device.handover_tracker_id) : ""
  );
  let [primaryHOId, setPrimaryHOId] = useState(
    device
      ? getString(device.primary_ho_id)
      : props.parentPrimaryHOId
      ? props.parentPrimaryHOId
      : ""
  );
  let [ipAddress, setIpAddress] = useState(
    device ? getString(device.ip_address) : ""
  );
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );
  let [assignedTo, setAssignedTo] = useState(
    device ? getString(device.assigned_to) : ""
  );
  let [projectType, setProjectType] = useState(
    device ? getString(device.project_type) : ""
  );
  let [hoSubmission, setHOSubmission] = useState(
    device ? getString(device.handover_submisson_date) : ""
  );
  let [hoCompletion, setHOCompletion] = useState(
    device ? getString(device.handover_completion_date) : null
  );
  let [hoReviewStatus, setHOReviewStatus] = useState(
    device ? getString(device.handover_review_status) : null
  );
  let [remedyIncident, setRemedyIncident] = useState(
    device ? getString(device.remedy_incident) : ""
  );
  const [region, setRegion] = useState(device ? getString(device.region) : "");
  const [siteType, setSiteType] = useState(
    device ? getString(device.site_type) : "DC"
  );
  const [assetType, setAssetType] = useState(
    device ? getString(device.asset_type) : "EDN"
  );
  const [pid, setPID] = useState(device ? getString(device.pid) : "");
  const [serialNumber, setSerialNumber] = useState(
    device ? getString(device.serial_number) : ""
  );
  const [comment, setComment] = useState(
    device ? getString(device.comment) : ""
  );
  const [commentsHistory, setCommentsHistory] = useState(
    device ? getString(device.comments_history) : ""
  );
  let [attachments, setAttachments] = useState([]);

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
    let url = "";
    if (id === "" && primaryHOId !== "") {
      url = "/addEdnHandoverTracker?category=edn_ho_tracker";
    } else {
      url = "/ednHandoverTracker?category=edn_ho_tracker";
    }
    try {
      await axios
        .post(baseUrl + url, device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/ednHandoverTracker")
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
    let ho = {
      handover_tracker_id: id,
      ip_address: ipAddress, //Not Null
      device_id: deviceId, //drop down (Completed/Pending)
      assigned_to: assignedTo, //drop down from endpoint "/getAssignees"
      project_type: projectType, //Not Null
      handover_submisson_date: hoSubmission,
      handover_completion_date: hoCompletion, //Not Null
      handover_review_status: hoReviewStatus,
      remedy_incident: remedyIncident, //Not Null
      region,
      site_type: siteType,
      asset_type: assetType,
      pid,
      serial_number: serialNumber,
      comment,
      attachments,
    };

    if (primaryHOId !== "") {
      ho["primary_ho_id"] = primaryHOId;
    }
    const device = [ho];

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  return (
    <Modal
      style={{ marginTop: "-30px", zIndex: "99999" }}
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
              {device ? "Edit" : "Add"} EDN Handover Tracker
            </p>
          </Col>
          <Col span={12}>
            {device ? (
              <InputWrapper>
                Primary HO Id:
                {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
                &nbsp;&nbsp;
                <StyledInput
                  value={primaryHOId}
                  onChange={(e) => setPrimaryHOId(e.target.value)}
                  // required
                  disabled
                />
              </InputWrapper>
            ) : props.parentPrimaryHOId ? (
              <InputWrapper>
                Primary HO Id:
                {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
                &nbsp;&nbsp;
                <StyledInput
                  value={primaryHOId}
                  onChange={(e) => setPrimaryHOId(e.target.value)}
                  // required
                  disabled
                />
              </InputWrapper>
            ) : null}

            <InputWrapper>
              Ip Address: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
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
              Region: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={region}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setRegion(value);
                }}
              >
                <Option value="Central">Central</Option>
                <Option value="Eastern">Eastern</Option>
                <Option value="Western">Western</Option>
              </Select>
              {/* <StyledInput
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                required
              /> */}
            </InputWrapper>
            <InputWrapper>
              Site Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={siteType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setSiteType(value);
                }}
              >
                <Option value="DC">DC</Option>
                <Option value="DCN">DCN</Option>
                <Option value="CO">CO</Option>
                <Option value="FB">FB</Option>
                <Option value="FS">FS</Option>
                <Option value="KSK">KSK</Option>
                <Option value="MFB">MFB</Option>
                <Option value="MOI">MOI</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Asset Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={assetType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setAssetType(value);
                }}
              >
                <Option value="EDN">EDN</Option>
                <Option value="AP">AP</Option>
                <Option value="Arbor-Sec">Arbor-Sec</Option>
                <Option value="ASA96">ASA96</Option>
                <Option value="ASA-SOC">ASA-SOC</Option>
                <Option value="FireEye-SOC">FireEye-SOC</Option>
                <Option value="FirepowerServer">FirepowerServer</Option>
                <Option value="FirepowerSSH">FirepowerSSH</Option>
                <Option value="Fortinet-Sec">Fortinet-Sec</Option>
                <Option value="Hardware">Hardware</Option>
                <Option value="IGW">IGW</Option>
                <Option value="IPT-ESXI">IPT-ESXI</Option>
                <Option value="IPT-ROUTER">IPT-ROUTER</Option>
                <Option value="IPT-UCS">IPT-UCS</Option>
                <Option value="Juniper-Screenos">Juniper-Screenos</Option>
                <Option value="Juniper-Sec">Juniper-Sec</Option>
                <Option value="PaloAlto">PaloAlto</Option>
                <Option value="PulseSecure">PulseSecure</Option>
                <Option value="REBD">REBD</Option>
                <Option value="SYSTEMS">SYSTEMS</Option>
                <Option value="WireFilter">WireFilter</Option>
                <Option value="Symantec-SOC">Symantec-SOC</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              PID: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={pid}
                onChange={(e) => setPID(e.target.value)}
                required
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Serial Number: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={serialNumber}
                onChange={(e) => setSerialNumber(e.target.value)}
                required
              />
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
              Project Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={projectType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setProjectType(value);
                }}
              >
                <Option value="EOX Upgrade">EOX Upgrade</Option>
                <Option value="Expansion">Expansion</Option>
                <Option value="Hardware Upgrade">Hardware Upgrade</Option>
                <Option value="New Backup Link">New Backup Link</Option>
                <Option value="New Redundant Link">New Redundant Link</Option>
                <Option value="New Site Integration">
                  New Site Integration
                </Option>
                <Option value="WAN Link Migration">WAN Link Migration</Option>
                <Option value="Service Migration">Service Migration</Option>
              </Select>
              {/* <StyledInput
                value={projectType}
                onChange={(e) => setProjectType(e.target.value)}
                required
              /> */}
            </InputWrapper>
            <InputWrapper>
              Handover Submission Date:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setHOSubmission(dateString);
                }}
                defaultValue={
                  hoSubmission ? moment(hoCompletion, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
            </InputWrapper>
            <InputWrapper>
              Handover Completion Date:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setHOCompletion(dateString);
                }}
                defaultValue={
                  hoCompletion ? moment(hoCompletion, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
            </InputWrapper>
            <InputWrapper>
              Handover Review Status: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={hoReviewStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setHOReviewStatus(value);
                }}
              >
                <Option value="Review Closed with Snags">
                  Review Closed with Snags
                </Option>
                <Option value="Pending with Projects">
                  Pending with Projects
                </Option>
                <Option value="Review Closed without Snags">
                  Review Closed without Snags
                </Option>
              </Select>
              {/* <StyledInput
                value={hoReviewStatus}
                onChange={(e) => setHOReviewStatus(e.target.value)}
                required
              /> */}
            </InputWrapper>
          </Col>
          <Col span={24}>
            <InputWrapper>
              Remedy Incident:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={remedyIncident}
                onChange={(e) => setRemedyIncident(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Comment: &nbsp;&nbsp;
              <Input.TextArea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                // required
              />
            </InputWrapper>
            {/* <InputWrapper>
              Comments History: &nbsp;&nbsp;
              <Input.TextArea
                value={commentsHistory}
                onChange={(e) => setCommentsHistory(e.target.value)}
                disabled
                // required
              />
            </InputWrapper> */}
          </Col>
          <Col span={12}>
            <Attachment response={attachments} setResponse={setAttachments} />
          </Col>
          <Col span={24} style={{ textAlign: "center", paddingTop: "20px" }}>
            <StyledButton color={"red"} onClick={handleCancel}>
              Cancel
            </StyledButton>
            &nbsp; &nbsp;{" "}
            <StyledSubmitButton color={"green"} type="submit" value="Done" />
          </Col>
        </Row>
        <br />
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
