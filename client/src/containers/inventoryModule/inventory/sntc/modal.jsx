import React, { useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";

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

  // const regex =
  //   "^[0-9]{4}-(0[1-9]|[1][012])-(0[1-9]|[12][0-9]|3[01]) ([0-1][0-9]|2[0123]):([0-5][0-9]):([0-5][0-9])$";
  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////
  let [sntcId, setSNTCId] = useState(device ? getString(device.sntc_id) : "");

  let [pnCode, setPnCode] = useState(device ? getString(device.pn_code) : "");
  let [itemCode, setItemCode] = useState(
    device ? getString(device.item_code) : ""
  );
  let [itemDesc, setItemDesc] = useState(
    device ? getString(device.item_desc) : ""
  );
  let [vulnFixPlanStatus, setVulnFixPlanStatus] = useState(
    device ? getString(device.vuln_fix_plan_status) : "No Plan"
  );
  let [vlanOpsSeverity, setVlanOpsSeverity] = useState(
    device ? getString(device.vuln_ops_severity) : "Low"
  );
  let [hwEosDate, setHwEosDate] = useState(
    device ? getString(device.hw_eos_date) : ""
  );
  let [hwEolDate, setHwEolDate] = useState(
    device ? getString(device.hw_eol_date) : ""
  );
  let [swEosDate, setSwEosDate] = useState(
    device ? getString(device.sw_eos_date) : ""
  );
  let [swEolDate, setSwEolDate] = useState(
    device ? getString(device.sw_eol_date) : ""
  );
  let [manufactureDate, setManufactureDate] = useState(
    device ? getDateString(device.manufactuer_date) : ""
  );

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/editSntc", device)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getSNTC")
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
      sntc_id: sntcId,
      pn_code: pnCode,
      item_code: itemCode,
      item_desc: itemDesc,
      vuln_fix_plan_status: vulnFixPlanStatus,
      vuln_ops_severity: vlanOpsSeverity,
      hw_eos_date: hwEosDate,
      hw_eol_date: hwEolDate,
      sw_eos_date: swEosDate,
      sw_eol_date: swEolDate,
      manufactuer_date: manufactureDate,
    };

    props.setIsModalVisible(false);
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
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} SNTC</p>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Pn Code: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={pnCode} readonly />
              ) : (
                <StyledInput
                  value={pnCode}
                  onChange={(e) => setPnCode(e.target.value)}
                  required
                />
              )}
            </InputWrapper>
            <InputWrapper>
              Item Code:&nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={itemCode}
                onChange={(e) => setItemCode(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Item Desc: &nbsp;&nbsp;
              <StyledInput
                value={itemDesc}
                onChange={(e) => setItemDesc(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              VULN Fix Plan Status:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Select
                value={vulnFixPlanStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVulnFixPlanStatus(value);
                }}
              >
                {getOptions([
                  "No Plan",
                  "EOX",
                  "Upgrade Planned",
                  "Upgrade in Progress",
                  "Project Planned",
                  "Project in Progress",
                ])}
              </Select>
            </InputWrapper>
            <InputWrapper>
              VULN OPS Severity:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Select
                value={vlanOpsSeverity}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVlanOpsSeverity(value);
                }}
              >
                {getOptions(["Low", "Critical", "High"])}
              </Select>
            </InputWrapper>
            <InputWrapper>
              HW EOS Date: &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={hwEosDate}
                onChange={(e) => setHwEosDate(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              HW EOL Date: &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={hwEolDate}
                onChange={(e) => setHwEolDate(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              SW EOS Date: &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={swEosDate}
                onChange={(e) => setSwEosDate(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              SW EOL Date: &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={swEolDate}
                onChange={(e) => setSwEolDate(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Manufacture Date: &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={manufactureDate}
                onChange={(e) => setManufactureDate(e.target.value)}
                // required
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
