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
import moment from "moment";

// import axios from "axios";
// import { SEED_API } from "../../../GlobalVar";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  let [deviceIds, setDeviceIds] = useState([]);
  let [deviceIdOptions, setDeviceIdOptions] = useState([]);
  let [assignees, setAssignees] = useState([]);
  let [assigneesOptions, seAssigneesOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getDeviceId");
        setDeviceIds(res1.data);
        const res2 = await axios.get(baseUrl + "/getAssignees");
        setAssignees(res2.data);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  useEffect(() => {
    getDeviceOptions(deviceIds);
    getAssigneeOptions(assignees);
  }, [deviceIds, assignees]);

  const getDeviceOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setDeviceIdOptions(options);
    // return options;
  };

  const getAssigneeOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    seAssigneesOptions(options);
    // return options;
  };

  const getString = (str) => {
    return str ? str : "";
  };
  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  // let [ip, setIp] = useState(device ? getString(device.switch_ip_address) : "");
  // let [siteId, setSiteId] = useState(device ? getString(device.site_id) : "");
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );
  let [assignee, setAssignee] = useState(
    device ? getString(device.assignee) : ""
  );
  let [status, setStatus] = useState(
    device ? getString(device.status) : "Completed"
  );
  let [remarks, setRemarks] = useState(device ? getString(device.remarks) : "");
  let [crq, setCrq] = useState(device ? getString(device.crq) : "");
  // let [currentOsVersion, setCurrentOsVersion] = useState(
  //   device ? getString(device.current_os_version) : ""
  // );
  let [newOsVersion, setNewOsVersion] = useState(
    device ? getString(device.new_os_version) : ""
  );
  let [schedule, setSchedule] = useState(
    device ? getString(device.schedule) : null
  );
  // let [osType, setOsType] = useState(
  //   device ? getString(device.op_type) : ""
  // );
  // let [region, setRegion] = useState(device ? getString(device.region) : "");

  let [ipAddress, setIPAddress] = useState(
    device ? getString(device.ip_address) : ""
  );

  const [assigneeArray, setAssigneeArray] = useState([]);

  useEffect(() => {
    const getAssigneeDropdown = async () => {
      // setLoading(true);

      try {
        const res = await axios.get(baseUrl + "/getAssignees");

        console.log("getAssignees", res);
        setAssigneeArray(res.data);
        if (assignee === "") {
          setAssignee(res?.data[0]);
        }
        // setLoading(false);
      } catch (err) {
        console.log(err.response);
        // setLoading(false);
      }
    };
    getAssigneeDropdown();
  }, []);

  const [deviceArray, setDeviceArray] = useState([]);

  useEffect(() => {
    const getDeviceDropdown = async () => {
      // setLoading(true);

      try {
        const res = await axios.get(baseUrl + "/getDeviceId");

        console.log(" Device ID ", res);
        setDeviceArray(res.data);
        setDeviceId(deviceId);

        // setLoading(false);
      } catch (err) {
        console.log(err.response);
        // setLoading(false);
      }
    };
    getDeviceDropdown();
  }, []);

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/iosTracker", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/iosTracker")
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
    if (schedule) {
      const device = [
        {
          // switch_ip_address: ip,
          device_id: deviceId,
          new_os_version: newOsVersion,
          assignee,
          schedule,
          crq,
          remarks,
          status,
        },
      ];

      props.setIsModalVisible(false);
      postDevice(device);
    } else {
      alert("schedule can not be empty");
    }
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const onChange = (date, dateString) => {
    console.log(date, dateString);
    setSchedule(dateString);
  };

  return (
    <Modal
      style={{ marginTop: "0px", zIndex: "99999" }}
      width="40%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>
              {device ? "Edit" : "Add"} IOS Tracker
            </p>
          </Col>
          <Col span={24}>
            {/* <InputWrapper>
              Switch IP-Address: &nbsp;&nbsp;
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
            {/* <InputWrapper>
              Device ID:
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={deviceId} readonly />
              ) : (
                <StyledInput
                  value={deviceId}
                  onChange={(e) => setDeviceId(e.target.value)}
                  required
                />
              )}
            </InputWrapper> */}

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
              Assignee: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={assignee}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setAssignee(value);
                }}
                showSearch
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {assigneesOptions}
              </Select>
            </InputWrapper>

            {/* <InputWrapper>
              Device ID:
               &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={deviceId} readonly />
              ) : (
              <select
                style={{ width: "100%" }}
                value={deviceId}
                onChange={(e) => {
                  setDeviceId(e.target.value);
                }}
              >
                 <option value="">select device id</option>
                {deviceArray.map((item, index) => {
                  return (
                    <>
                      <option key={index}>{item}</option>
                    </>
                  );
                })}
              </select>
              )}
            </InputWrapper> */}
            {/* <InputWrapper>
              Assignee: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <select
                style={{ width: "100%" }}
                value={assignee}
                onChange={(e) => {
                  setAssignee(e.target.value);
                }}
              >
                <option value="">select Assignee</option>

                {assigneeArray.map((item, index) => {
                  return (
                    <>
                      <option key={index}>{item}</option>
                    </>
                  );
                })}
              </select>
            </InputWrapper> */}
            <InputWrapper>
              New OS Version:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={newOsVersion}
                onChange={(e) => setNewOsVersion(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              CRQ:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={crq}
                onChange={(e) => setCrq(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={status}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setStatus(value);
                }}
              >
                <Option value="Completed">Completed</Option>
                <Option value="Planned">Planned</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Remarks:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
              />
            </InputWrapper>

            <InputWrapper>
              Schedule: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {/* <DatePicker defaultValue={moment('01-01-2015', dateFormatList[0])} format={dateFormatList}
                placeholder="dd-mm-yyyy"
              
              style={{width:"100%"}}
              value={schedule}
              onChange={(e) => setSchedule(e.target.value)}
              required
              /> */}
              <DatePicker
                onChange={onChange}
                defaultValue={schedule ? moment(schedule, "DD-MM-YYYY") : null}
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
              {/* <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={schedule}
                onChange={(e) => setSchedule(e.target.value)}
                required
              /> */}
            </InputWrapper>

            {/* <InputWrapper>
              Schedule:
           &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={schedule} 

                onChange={(e) => setSchedule(e.target.value)}
                />
              ) : (
              <StyledInput
              type="date"
                value={schedule}
                // type="number"
                // min={0}
                onChange={(e) => setSchedule(e.target.value)}
                 required
              />
              )}
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
