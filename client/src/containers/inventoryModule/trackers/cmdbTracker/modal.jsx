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
import MultiSelect from "react-select";

// import axios from "axios";
// import { SEED_API } from "../../../GlobalVar";

const AddDeviceModal = (props) => {
  const { Option } = Select;
  const getString = (str) => {
    return str ? str : "";
  };

  const getMultiSelectOptions = (comaSeparatedString) => {
    if (comaSeparatedString !== "") {
      return comaSeparatedString?.split(",").map((element) => {
        return { value: element, label: element };
      });
    } else return "";
  };

  let [device, setDevice] = useState(props.editRecord);

  const [crqNo, setCRQNo] = useState(device ? getString(device.crq_no) : "");
  const [activitySummary, setActivitySummary] = useState(
    device ? getString(device.activity_summary) : ""
  );

  const [activityType, setActivityType] = useState(
    device ? getMultiSelectOptions(device.activity_type) : ""
  );
  const [approvalType, setApprovalType] = useState(
    device ? getMultiSelectOptions(device.approval_type) : ""
  );
  // const [priority, setPriority] = useState(
  //   device
  //     ? getMultiSelectOptions(device.priority)
  //     : [{ value: "Critical", label: "Critical" }]
  // );

  const [priority, setPriority] = useState(device ? device.priority : "");

  const [implementingTeam, setImplementingTeam] = useState(
    device ? getMultiSelectOptions(device.implementing_team) : ""
  );
  const [implementer, setImplementer] = useState(
    device ? getMultiSelectOptions(device.implementer) : ""
  );
  const [region, setRegion] = useState(
    device ? getMultiSelectOptions(device.region) : ""
  );
  const [site, setSite] = useState(device ? getString(device.site) : "");

  const [date, setDate] = useState(device ? getString(device.date) : "");
  // const [status, setStatus] = useState(
  //   device
  //     ? getMultiSelectOptions(device.status)
  //     : [{ value: "Success", label: "Success" }]
  // );
  const [status, setStatus] = useState(device ? device.status : "");
  const [serviceImpact, setServiceImpact] = useState(
    device ? getString(device.service_impact) : ""
  );
  const [domain, setDomain] = useState(
    device ? getMultiSelectOptions(device.domain) : ""
  );

  const [activityCategory, setActivityCategory] = useState(
    device ? getMultiSelectOptions(device.activity_category) : ""
  );
  const [ci, setCI] = useState(device ? getString(device.ci) : "");
  const [reasonOfRollback, setReasonOfRollback] = useState(
    device ? getString(device.reason_of_rollback) : ""
  );

  const [implementers, setImplementers] = useState([]);
  const [implementerOptions, setImplementerOptions] = useState([]);

  const getOptions = (data) => {
    return data.map((item) => {
      return { label: item, value: item };
    });
  };

  useEffect(() => {
    (async () => {
      try {
        const res = await axios.get(baseUrl + "/getImplementers");
        // setImplementers(res.data);
        let io = getOptions(res.data);
        // if (io.length > 0 && implementer == "") {
        //   setImplementer([io[0]]);
        // }
        setImplementerOptions(io);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  // useEffect(() => {
  //   getImplementerOptions(implementers);
  // }, [implementers]);

  // const getImplementerOptions = (values = []) => {
  //   let options = [];
  //   values.map((value) => {
  //     options.push(<Option value={value}>{value}</Option>);
  //   });
  //   setImplementerOptions(options);
  // };

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/cmdbTracker", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/cmdbTracker")
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

  const generateCommaSeparatedString = (options) => {
    let css = "";
    console.log("opt", options);
    if (options !== "") {
      css = options?.reduce((accumulator, currentValue, index) => {
        if (index !== options.length - 1) {
          return accumulator + currentValue.value + ",";
        } else {
          return accumulator + currentValue.value;
        }
      }, "");
    }
    return css;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    let activityTypeString = generateCommaSeparatedString(activityType);
    let approvalTypeString = generateCommaSeparatedString(approvalType);
    // let priorityString = generateCommaSeparatedString(priority);
    let implementingTeamString = generateCommaSeparatedString(implementingTeam);
    let implementerString = generateCommaSeparatedString(implementer);
    let regionString = generateCommaSeparatedString(region);
    // let statusString = generateCommaSeparatedString(status);
    let domainString = generateCommaSeparatedString(domain);
    let activityCategoryString = generateCommaSeparatedString(activityCategory);
    if (
      activityTypeString == "" ||
      approvalTypeString == "" ||
      priority == "" ||
      implementingTeamString == "" ||
      implementerString == "" ||
      regionString == "" ||
      status == "" ||
      domainString == "" ||
      activityCategoryString == ""
    ) {
      alert("Please fill all the required fields");
    } else {
      const device = [
        {
          crq_no: crqNo,
          activity_summary: activitySummary,
          activity_type: activityTypeString,
          approval_type: approvalTypeString,
          priority: priority,
          implementing_team: implementingTeamString,
          implementer: implementerString,
          region: regionString,
          site,
          date,
          status: status,
          service_impact: serviceImpact,
          domain: domainString,
          activity_category: activityCategoryString,
          ci,
          reason_of_rollback: reasonOfRollback,
        },
      ];

      props.setIsModalVisible(false);
      postDevice(device);
    }
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const onChange = (date, dateString) => {
    console.log(date, dateString);
    setDate(dateString);
  };

  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      background: "#fff",
      borderColor: "#9e9e9e",
      minHeight: "30px",
      // height: "30px",
      boxShadow: state.isFocused ? null : null,
    }),

    valueContainer: (provided, state) => ({
      ...provided,
      // height: "30px",
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
              {device ? "Edit" : "Add"} CMDB Tracker
            </p>
          </Col>
          <Col span={12}>
            <InputWrapper>
              CRQ No.: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={crqNo}
                onChange={(e) => setCRQNo(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Activity Summary:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={activitySummary}
                onChange={(e) => setActivitySummary(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Activity Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={activityType}
                  onChange={(e) => setActivityType(e)}
                  options={[
                    { value: "MDT", label: "MDT" },
                    { value: "TCN", label: "TCN" },
                    { value: "Site Access", label: "Site Access" },
                    { value: "OCR", label: "OCR" },
                    { value: "SOR", label: "SOR" },
                  ]}
                />
              </div>
              {/* <Select
                value={activityType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setActivityType(value);
                }}
              >
                <Option value="MDT">MDT</Option>
                <Option value="TCN">TCN</Option>
                <Option value="Site Access">Site Access</Option>
                <Option value="OCR">OCR</Option>
                <Option value="SOR">SOR</Option>
              </Select> */}
            </InputWrapper>
            <InputWrapper>
              Approval Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={approvalType}
                  onChange={(e) => setApprovalType(e)}
                  options={[
                    { value: "Normal Approval", label: "Normal Approval" },
                    { value: "Fast track", label: "Fast track" },
                    { value: "Day Time", label: "Day Time" },
                    { value: "Corrective Action", label: "Corrective Action" },
                    { value: "Freezing Period", label: "Freezing Period" },
                  ]}
                />
              </div>
              {/* <Select
                value={approvalType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setApprovalType(value);
                }}
              >
                <Option value="Normal Approval">Normal Approval</Option>
                <Option value="Fast track">Fast track</Option>
                <Option value="Day Time">Day Time</Option>
                <Option value="Corrective Action">Corrective Action</Option>
                <Option value="Freezing Period">Freezing Period</Option>
              </Select> */}
            </InputWrapper>
            <InputWrapper>
              Priority: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {/* <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={priority}
                  onChange={(e) => setPriority(e)}
                  options={[
                    { value: "Critical", label: "Critical" },
                    { value: "High", label: "High" },
                    { value: "Medium", label: "Medium" },
                    { value: "Low", label: "Low" },
                  ]}
                />
              </div> */}
              <Select
                value={priority}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setPriority(value);
                }}
              >
                <Option value="Critical">Critical</Option>
                <Option value="High">High</Option>
                <Option value="Medium">Medium</Option>
                <Option value="Low">Low</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Implementing Team: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={implementingTeam}
                  onChange={(e) => setImplementingTeam(e)}
                  options={[
                    { value: "Operation", label: "Operation" },
                    { value: "Project", label: "Project" },
                    { value: "Cabling team", label: "Cabling team" },
                  ]}
                />
              </div>
              {/* <Select
                value={implementingTeam}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setImplementingTeam(value);
                }}
              >
                <Option value="Operation">Operation</Option>
                <Option value="Project">Project</Option>
                <Option value="Cabling team">Cabling team</Option>
              </Select> */}
            </InputWrapper>
            <InputWrapper>
              Implementer: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={implementer}
                  onChange={(e) => setImplementer(e)}
                  options={implementerOptions}
                />
              </div>
              {/* <Select
                value={implementer}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setImplementer(value);
                }}
                showSearch
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {implementerOptions}
              </Select> */}
            </InputWrapper>
            <InputWrapper>
              Region: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={region}
                  onChange={(e) => setRegion(e)}
                  options={[
                    { value: "Central", label: "Central" },
                    { value: "Western", label: "Western" },
                    { value: "Eastern", label: "Eastern" },
                  ]}
                />
              </div>
              {/* <Select
                value={region}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setRegion(value);
                }}
              >
                <Option value="Central">Central</Option>
                <Option value="Western">Western</Option>
                <Option value="Eastern">Eastern</Option>
              </Select> */}
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Site:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={site}
                onChange={(e) => setSite(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Date:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <DatePicker
                onChange={onChange}
                defaultValue={date ? moment(date, "DD-MM-YYYY") : null}
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
            </InputWrapper>
            <InputWrapper>
              Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {/* <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={status}
                  onChange={(e) => setStatus(e)}
                  options={[
                    { value: "Success", label: "Success" },
                    {
                      value: "Partially Completed",
                      label: "Partially Completed",
                    },
                    { value: "Rolled Back", label: "Rolled Back" },
                    { value: "Cancelled", label: "Cancelled" },
                    { value: "Failed", label: "Failed" },
                    { value: "Cancelled", label: "Cancelled" },
                    { value: "Rescheduled", label: "Rescheduled" },
                  ]}
                />
              </div> */}
              <Select
                value={status}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setStatus(value);
                }}
              >
                <Option value="Success">Success</Option>
                <Option value="Partially Completed">Partially Completed</Option>
                <Option value="Rolled Back">Rolled Back</Option>
                <Option value="Cancelled">Cancelled</Option>
                <Option value="Failed">Failed</Option>
                <Option value="Rescheduled">Rescheduled</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Service Impact:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={serviceImpact}
                onChange={(e) => setServiceImpact(e.target.value)}
              />
            </InputWrapper>

            <InputWrapper>
              Domain: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={domain}
                  onChange={(e) => setDomain(e)}
                  options={[
                    { value: "EDN-OPS", label: "EDN-OPS" },
                    { value: "EDN-Proj", label: "EDN-Proj" },
                    { value: "IPT-OPS", label: "IPT-OPS" },
                    { value: "IPT-Proj", label: "IPT-Proj" },
                    { value: "SYS-OPS-EDN", label: "SYS-OPS-EDN" },
                    { value: "SYS-OPS-IGW", label: "SYS-OPS-IGW" },
                    { value: "SYS-OPS-DDos", label: "SYS-OPS-DDos" },
                    { value: "SYS-Proj-EDN", label: "SYS-Proj-EDN" },
                    { value: "SYS-Proj-IGW", label: "SYS-Proj-IGW" },
                    { value: "SYS-Proj-DDoS", label: "SYS-Proj-DDoS" },
                    { value: "IGW-OPS", label: "IGW-OPS" },
                    { value: "IGW-Proj", label: "IGW-Proj" },
                    { value: "POS-OPS", label: "POS-OPS" },
                    { value: "POS-Proj", label: "POS-Proj" },
                    { value: "SOC", label: "SOC" },
                    { value: "SIC", label: "SIC" },
                    { value: "SE", label: "SE" },
                  ]}
                />
              </div>
              {/* <Select
                value={domain}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setDomain(value);
                }}
              >
                <Option value="EDN-OPS">EDN-OPS</Option>
                <Option value="EDN-Proj">EDN-Proj</Option>
                <Option value="IPT-OPS">IPT-OPS</Option>
                <Option value="IPT-Proj">IPT-Proj</Option>
                <Option value="SYS-OPS-EDN">SYS-OPS-EDN</Option>
                <Option value="SYS-OPS-IGW">SYS-OPS-IGW</Option>
                <Option value="SYS-OPS-DDos">SYS-OPS-DDos</Option>
                <Option value="SYS-Proj-EDN">SYS-Proj-EDN</Option>
                <Option value="SYS-Proj-IGW">SYS-Proj-IGW</Option>
                <Option value="SYS-Proj-DDoS">SYS-Proj-DDoS</Option>
                <Option value="IGW-OPS">IGW-OPS</Option>
                <Option value="IGW-Proj">IGW-Proj</Option>
                <Option value="POS-OPS">POS-OPS</Option>
                <Option value="POS-Proj">POS-Proj</Option>
                <Option value="SOC">SOC</Option>
                <Option value="SIC">SIC</Option>
                <Option value="SE">SE</Option>
              </Select> */}
            </InputWrapper>
            <InputWrapper>
              Activity Category: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={activityCategory}
                  onChange={(e) => setActivityCategory(e)}
                  options={[
                    { value: "Operation Changes", label: "Operation Changes" },
                    { value: "Project Changes", label: "Project Changes" },
                    { value: "Audit", label: "Audit" },
                    { value: "P-Maintenance", label: "P-Maintenance" },
                    { value: "Upgrade", label: "Upgrade" },
                    { value: "RMA", label: "RMA" },
                  ]}
                />
              </div>
              {/* <Select
                value={activityCategory}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setActivityCategory(value);
                }}
              >
                <Option value="Operation Changes">Operation Changes</Option>
                <Option value="Project Changes">Project Changes</Option>
                <Option value="Audit">Audit</Option>
                <Option value="P-Maintenance">P-Maintenance</Option>
                <Option value="Upgrade">Upgrade</Option>
                <Option value="RMA">RMA</Option>
              </Select> */}
            </InputWrapper>
            <InputWrapper>
              CI:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput value={ci} onChange={(e) => setCI(e.target.value)} />
            </InputWrapper>
            <InputWrapper>
              Reason Of Rollback:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={reasonOfRollback}
                onChange={(e) => setReasonOfRollback(e.target.value)}
              />
            </InputWrapper>
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
