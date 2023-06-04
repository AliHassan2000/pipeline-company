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

// import axios from "axios";
// import { SEED_API } from "../../../GlobalVar";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  let [iptProductIds, setIptProductIds] = useState([]);
  let [iptProductIdsOptions, setIptProductIdsOptions] = useState([]);
  let [deviceIds, setDeviceIds] = useState([]);
  let [deviceIdOptions, setDeviceIdOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getDeviceId");
        setDeviceIds(res1.data);
        const res2 = await axios.get(baseUrl + "/getIptProductIds");
        setIptProductIds(res2.data);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  useEffect(() => {
    getDeviceOptions(deviceIds);
    getIptProductIdsOptions(iptProductIds);
  }, [deviceIds, iptProductIds]);

  const getDeviceOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setDeviceIdOptions(options);
    // return options;
  };

  const getIptProductIdsOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setIptProductIdsOptions(options);
  };

  const getString = (str) => {
    return str ? str : "";
  };
  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";

  let [device, setDevice] = useState(props.editRecord);
  let [ip, setIp] = useState(
    device ? getString(device.poweroff_tracker_id) : ""
  );
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );
  let [crqNo, setCRQNo] = useState(device ? getString(device.crq_no) : "");
  let [comments, setComments] = useState(
    device ? getString(device.comments) : ""
  );
  let [assignedTo, setAssignedTo] = useState(
    device ? getString(device.assigned_to) : ""
  );
  let [associatedCircuitIdDetails, setAssociatedCircuitIdDetails] = useState(
    device ? getString(device.associated_circuit_id_details) : ""
  );
  let [dateOfPowerDown, setDateOfPowerDown] = useState(
    device ? getString(device.date_of_power_down) : null
  );
  let [dateOfPowerOn, setDateOfPowerOn] = useState(
    device ? getString(device.date_of_power_on) : null
  );
  let [mgtIp, setMGTIp] = useState(device ? getString(device.mgt_ip) : "");
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
        .post(baseUrl + "/ednPowerOffTracker", device)
        .then((response) => {
          console.log("post modal power off");
          console.log(response?.response);
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/ednPowerOffTracker")
              .then((response) => {
                console.log("get modal power off");
                console.log(response);
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
    if (dateOfPowerDown) {
      const device = [
        {
          poweroff_tracker_id: ip,
          device_id: deviceId,
          crq_no: crqNo,
          comments,
          assigned_to: assignedTo,
          associated_circuit_id_details: associatedCircuitIdDetails,
          date_of_power_down: dateOfPowerDown,
          date_of_power_on: dateOfPowerOn,
          // mgt_ip: mgtIp,
        },
      ];

      props.setIsModalVisible(false);
      postDevice(device);
    } else {
      alert("date of power down can not be empty");
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
              {device ? "Edit" : "Add"} EDN Power Off Tracker
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
              Assigned To:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
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
              CRQ No: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={crqNo}
                onChange={(e) => setCRQNo(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Comments:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>

          <Col span={12}>
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
              Date Of Power Down: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setDateOfPowerDown(dateString);
                }}
                defaultValue={
                  dateOfPowerDown ? moment(dateOfPowerDown, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
                required
              />
            </InputWrapper>
            <InputWrapper>
              Date Of Power On: &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setDateOfPowerOn(dateString);
                }}
                defaultValue={
                  dateOfPowerOn ? moment(dateOfPowerOn, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
            </InputWrapper>
            {/* <InputWrapper>
              MGT IP: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={mgtIp}
                onChange={(e) => setMGTIp(e.target.value)}
                required
              />
            </InputWrapper> */}
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
