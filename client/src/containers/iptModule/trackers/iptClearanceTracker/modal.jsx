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
import axios, { baseUrl } from "../../../../utils/axios";
import Swal from "sweetalert2";
import moment from "moment";

// import axios from "axios";
// import { SEED_API } from "../../../GlobalVar";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  const getString = (str) => {
    return str ? str : "";
  };
  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";

  let [device, setDevice] = useState(props.editRecord);

  let [ip, setIp] = useState(
    device ? getString(device.ip_clearance_tracker_id) : ""
  );

  let [employeePf, setEmployeePf] = useState(
    device ? getString(device.employee_pf) : ""
  );
  let [fullName, setFullName] = useState(
    device ? getString(device.full_name) : ""
  );
  let [organization, setOrganization] = useState(
    device ? getString(device.organization) : ""
  );
  let [position, setPosition] = useState(
    device ? getString(device.position) : ""
  );
  let [job, setJob] = useState(device ? getString(device.job) : "");
  let [grade, setGrade] = useState(device ? getString(device.grade) : "");
  let [nationality, setNationality] = useState(
    device ? getString(device.nationality) : ""
  );

  let [terminationDate, setTerminationDate] = useState(
    device ? getString(device.termination_date) : null
  );
  let [email, setEmail] = useState(device ? getString(device.email) : "");
  let [iptTeamAssignee, setIPTTeamAssignee] = useState(
    device ? getString(device.ipt_team_assignee) : ""
  );
  let [ipPhoneModel, setIPPhoneModel] = useState(
    device ? getString(device.ip_phone_model) : ""
  );
  let [serialNumber, setSerialNumber] = useState(
    device ? getString(device.serial_number) : ""
  );
  let [mac, setMac] = useState(device ? getString(device.mac) : "");
  let [collectionDate, setCollectionDate] = useState(
    device ? getString(device.collection_date) : null
  );
  let [region, setRegion] = useState(device ? getString(device.region) : "");
  let [status, setStatus] = useState(device ? getString(device.status) : "");
  let [remarks, setRemarks] = useState(device ? getString(device.remarks) : "");

  let [iptProductIds, setIptProductIds] = useState([]);
  let [iptProductIdsOptions, setIptProductIdsOptions] = useState([]);

  let [assignees, setAssignees] = useState([]);
  let [assigneesOptions, seAssigneesOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getIptProductIds");
        setIptProductIds(res1.data);
        if (ipPhoneModel === "") {
          setIPPhoneModel(res1?.data[0]);
        }

        const res2 = await axios.get(baseUrl + "/getAssigneesTracker");
        setAssignees(res2.data);
        if (iptTeamAssignee === "") {
          setIPTTeamAssignee(res2?.data[0]);
        }
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  useEffect(() => {
    getIptProductIdsOptions(iptProductIds);
    getAssigneeOptions(assignees);
  }, [iptProductIds, assignees]);

  const getIptProductIdsOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setIptProductIdsOptions(options);
  };

  const getAssigneeOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    seAssigneesOptions(options);
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
        .post(baseUrl + "/ipClearanceTracker", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/ipClearanceTracker")
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
    const device = [
      {
        ip_clearance_tracker_id: ip,
        employee_pf: employeePf,
        full_name: fullName,
        organization,
        position,
        job,
        grade,
        nationality,
        termination_date: terminationDate,
        email,
        ipt_team_assignee: iptTeamAssignee,
        ip_phone_model: ipPhoneModel,
        serial_number: serialNumber,
        mac,
        collection_date: collectionDate,
        region,
        status,
        remarks,
      },
    ];

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const onChange = (date, dateString) => {
    console.log(date, dateString);
    setCollectionDate(dateString);
  };

  const onTerminationChange = (date, dateString) => {
    console.log(date, dateString);
    setTerminationDate(dateString);
  };

  return (
    <Modal
      style={{ marginTop: "0px", zIndex: "99999" }}
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
              {device ? "Edit" : "Add"} IPT Clearance Tracker
            </p>
          </Col>
          <Col span={12}>
            {device ? (
              <InputWrapper>
                Serial Number: &nbsp;<span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput value={serialNumber} readonly />
              </InputWrapper>
            ) : (
              <InputWrapper>
                Serial Number: &nbsp;<span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <StyledInput
                  value={serialNumber}
                  onChange={(e) => setSerialNumber(e.target.value)}
                  required
                />
              </InputWrapper>
            )}
            <InputWrapper>
              Employee PF:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={employeePf}
                onChange={(e) => setEmployeePf(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Full Name:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Organization:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Position:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={position}
                onChange={(e) => setPosition(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Job:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={job}
                onChange={(e) => setJob(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Grade:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={grade}
                onChange={(e) => setGrade(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Nationality:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={nationality}
                onChange={(e) => setNationality(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Email:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Termination Date:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <DatePicker
                onChange={onTerminationChange}
                defaultValue={
                  terminationDate ? moment(terminationDate, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
            </InputWrapper>
            <InputWrapper>
              IPT Team Assignee: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={iptTeamAssignee}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setIPTTeamAssignee(value);
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
              IPT Team Assignee: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={IPTTeamAssignee}
                onChange={(e) => setIPTTeamAssignee(e.target.value)}
                required
              />
            </InputWrapper> */}

            <InputWrapper>
              IP Phone Model: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={ipPhoneModel}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setIPPhoneModel(value);
                }}
                showSearch
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {iptProductIdsOptions}
              </Select>
            </InputWrapper>
            <InputWrapper>
              Mac:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={mac}
                onChange={(e) => setMac(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Collection Date:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <DatePicker
                onChange={onChange}
                defaultValue={
                  collectionDate ? moment(collectionDate, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
              {/* <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={collectionDate}
                onChange={(e) => setCollectionDate(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Region:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Status:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Remarks:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
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
