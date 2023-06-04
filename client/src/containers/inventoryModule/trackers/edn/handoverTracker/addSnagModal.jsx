import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select, DatePicker } from "antd";
import axios, { baseUrl } from "../../../../../utils/axios";
import Swal from "sweetalert2";
import moment from "moment";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  const getString = (str) => {
    return str ? str : "";
  };

  let [device, setDevice] = useState(props.editRecord);
  let [id, setId] = useState(device ? getString(device.snag_id) : "");
  let [hoRefId, setHoRefId] = useState(
    device ? getString(device.ho_ref_id) : props.hoRefId
  );
  let [deviceName, setDeviceName] = useState(
    device ? getString(device.device_name) : ""
  );
  let [snagStatus, setSnagStatus] = useState(
    device ? getString(device.snag_status) : ""
  );
  let [snagCriticality, setSnagCriticality] = useState(
    device ? getString(device.snag_criticality) : ""
  );
  let [reportedDate, setReportedDate] = useState(
    device ? getString(device.reported_date) : null
  );
  let [closureDate, setClosureDate] = useState(
    device ? getString(device.closure_date) : null
  );
  let [snagClosureDate, setSnagClosureDate] = useState(
    device ? getString(device.snag_closure_date) : ""
  );
  const [snagName, setSnagName] = useState(
    device ? getString(device.snag_name) : ""
  );
  const [comment, setComment] = useState(
    device ? getString(device.comments) : ""
  );
  const [commentsHistory, setCommentsHistory] = useState(
    device ? getString(device.comments_history) : ""
  );

  const [snagNameCriticality, setSnagNameCriticality] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getAllSnagsStaticColumns");
        setSnagNameCriticality(res1.data);
        setSnagName(res1?.data[0]?.snag_name);
        setSnagCriticality(res1?.data[0]?.snag_criticality);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  const setCriticalityValue = (value) => {
    let sc = snagNameCriticality.find((element) => {
      return element.snag_name === value;
    });
    setSnagCriticality(sc.snag_criticality);
  };

  //   let [assignedTos, setAssignedTos] = useState([]);
  //   let [assignedToOptions, setAssignedToOptions] = useState([]);

  //   useEffect(() => {
  //     (async () => {
  //       try {
  //         const res1 = await axios.get(baseUrl + "/getAssignees");
  //         setAssignedTos(res1.data);
  //         setAssignedTo(res1?.data[0]);
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
        .post(baseUrl + "/snags", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/snags/" + hoRefId)
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
      snag_id: id,
      ho_ref_id: hoRefId,
      device_name: deviceName,
      snag_criticality: snagCriticality,
      closure_date: closureDate,
      snag_status: snagStatus,
      reported_date: reportedDate,
      snag_closure_date: snagClosureDate,
      snag_name: snagName,
      comment,
    };

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const getOptions = (values = []) => {
    let options = [];
    values?.map((value) => {
      options.push(<Option value={value.snag_name}>{value.snag_name}</Option>);
    });
    return options;
  };

  return (
    // <Modal
    //   style={{ marginTop: "30px", zIndex: "99999" }}
    //   width="60%"
    //   title=""
    //   closable={false}
    //   visible={props.isModalVisible}
    //   footer=""
    // >
    <form onSubmit={handleSubmit}>
      <Row gutter={30}>
        <Col span={24} style={{ textAlign: "center" }}>
          <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Snag</p>
        </Col>
        <Col span={12}>
          {/* <InputWrapper>
            Id:
            &nbsp;<span style={{ color: "red" }}>*</span>
            &nbsp;&nbsp;
            <StyledInput
              value={id}
              onChange={(e) => setId(e.target.value)}
              required
            />
          </InputWrapper> */}
          <InputWrapper>
            HO REF Id: &nbsp;<span style={{ color: "red" }}>*</span>
            &nbsp;&nbsp;
            <StyledInput
              value={hoRefId}
              onChange={(e) => setHoRefId(e.target.value)}
              required
              disabled
            />
          </InputWrapper>
          <InputWrapper>
            Device Name: &nbsp;<span style={{ color: "red" }}>*</span>
            &nbsp;&nbsp;
            <StyledInput
              value={deviceName}
              onChange={(e) => setDeviceName(e.target.value)}
              required
            />
          </InputWrapper>
          <InputWrapper>
            Snag Name: &nbsp;<span style={{ color: "red" }}>*</span>
            &nbsp;&nbsp;
            <Select
              value={snagName}
              style={{ width: "100%" }}
              onChange={(value) => {
                setSnagName(value);
                setCriticalityValue(value);
              }}
            >
              {getOptions(snagNameCriticality)}
            </Select>
          </InputWrapper>
          <InputWrapper>
            Snag Status: &nbsp;<span style={{ color: "red" }}>*</span>
            &nbsp;&nbsp;
            <Select
              value={snagStatus}
              style={{ width: "100%" }}
              onChange={(value) => {
                setSnagStatus(value);
              }}
            >
              <Option value="Closed">Closed</Option>
              <Option value="Exception">Exception</Option>
              <Option value="Pending with Projects">
                Pending with Projects
              </Option>
            </Select>
          </InputWrapper>
        </Col>

        <Col span={12}>
          <InputWrapper>
            Snag Criticality: &nbsp;<span style={{ color: "red" }}>*</span>
            &nbsp;&nbsp;
            <StyledInput
              value={snagCriticality}
              onChange={(e) => setSnagCriticality(e.target.value)}
              required
              disabled
            />
          </InputWrapper>
          <InputWrapper>
            Reported Date: &nbsp;<span style={{ color: "red" }}>*</span>
            &nbsp;&nbsp;
            <DatePicker
              onChange={(date, dateString) => {
                setReportedDate(dateString);
              }}
              defaultValue={
                reportedDate ? moment(reportedDate, "DD-MM-YYYY") : null
              }
              style={{ width: "100%" }}
              format="DD-MM-YYYY"
            />
          </InputWrapper>
          <InputWrapper>
            Closure Date:
            {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
            &nbsp;&nbsp;
            <DatePicker
              onChange={(date, dateString) => {
                setClosureDate(dateString);
              }}
              defaultValue={
                closureDate ? moment(closureDate, "DD-MM-YYYY") : null
              }
              style={{ width: "100%" }}
              format="DD-MM-YYYY"
            />
          </InputWrapper>
          <InputWrapper>
            Snag Closure Date:
            {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
            &nbsp;&nbsp;
            <DatePicker
              onChange={(date, dateString) => {
                setSnagClosureDate(dateString);
              }}
              defaultValue={
                snagClosureDate ? moment(snagClosureDate, "DD-MM-YYYY") : null
              }
              style={{ width: "100%" }}
              format="DD-MM-YYYY"
            />
          </InputWrapper>
        </Col>
        <Col span={24}>
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
    // </Modal>
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
