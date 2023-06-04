import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select, DatePicker } from "antd";
import moment from "moment";
import axios, { baseUrl } from "../../../../utils/axios";
import Swal from "sweetalert2";
import MultiSelect from "react-select";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  const getString = (str) => {
    return str ? str : "";
  };

  let [siteIds, setSiteIds] = useState([]);
  let [siteIdOptions, setSiteIdOptions] = useState([]);
  let [rackIds, setRackIds] = useState([]);
  let [rackIdOptions, setRackIdOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getAllSiteIDs");
        setSiteIds(res1.data);
        const res2 = await axios.get(baseUrl + "/getAllRackIDs");
        setRackIds(res2.data);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  useEffect(() => {
    getSiteIdOptions(siteIds);
    getRackIdOptions(rackIds);
  }, [siteIds, rackIds]);

  const getSiteIdOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setSiteIdOptions(options);
    // return options;
  };

  const getRackIdOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setRackIdOptions(options);
    // return options;
  };

  const getMultiSelectOptions = (comaSeparatedString) => {
    if (comaSeparatedString !== "") {
      return comaSeparatedString?.split(",").map((element) => {
        return { value: element, label: element };
      });
    } else return "";
  };

  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////
  let [ip, setIp] = useState(device ? getString(device.device_id) : "");
  let [deviceName, setDeviceName] = useState(
    device ? getString(device.device_name) : ""
  );
  let [tagId, setTagId] = useState(device ? getString(device.tag_id) : "");
  let [rfsDate, setRfsDate] = useState(
    device ? getString(device.rfs_date) : ""
  );
  let [dismantleDate, setDismantleDate] = useState(
    device ? getString(device.dismantle_date) : ""
  );
  let [neIpAddress, setNeIpAddress] = useState(
    device ? getString(device.ne_ip_address) : ""
  );
  let [functiond, setFunction] = useState(
    device ? getString(device.function) : ""
  );
  // let [itemCode, setItemCode] = useState(
  //   device?.item_code ? device.item_code : "TBF"
  // );
  // let [itemDesc, setItemDesc] = useState(
  //   device?.item_desc ? device.item_desc : "TBF"
  // );
  let [clei, setClei] = useState(device?.clei ? device.clei : "TBF");

  let [rackId, setRackId] = useState(device ? getString(device.rack_id) : "");
  let [siteId, setSiteId] = useState(device ? getString(device.site_id) : "");
  // let [manufactureDate, setManufactureDate] = useState(
  //   device ? getString(device.manufactuer_date) : ""
  // );
  let [virtual, setVirtual] = useState(
    device ? getString(device.virtual) : "Not Virtual"
  );
  let [authentication, setAuthentication] = useState(
    device ? getString(device.authentication) : "AAA"
  );
  let [subrackIdNumber, setSubrackIdNumber] = useState(
    device ? getString(device.subrack_id_number) : ""
  );
  // let [hwEosDate, setHwEosDate] = useState(
  //   device ? getString(device.hw_eos_date) : ""
  // );
  // let [hwEolDate, setHwEolDate] = useState(
  //   device ? getString(device.hw_eol_date) : ""
  // );
  // let [swEosDate, setSwEosDate] = useState(
  //   device ? getString(device.sw_eos_date) : ""
  // );
  let [criticality, setCriticality] = useState(
    device ? getString(device.criticality) : "Low"
  );
  let [ciscoDomain, setCiscoDomain] = useState(
    device ? getString(device.cisco_domain) : "EDN-NET"
  );
  let [patchVersion, setPatchVersion] = useState(
    device ? getString(device.patch_version) : ""
  );
  // let [section, setSection] = useState(
  //   device ? getString(device.section) : "Cloud & Virtualization Systems"
  // );
  let [softwareVersion, setSoftwareVersion] = useState(
    device ? getString(device.software_version) : ""
  );

  let [hardwareVersion, setHardwareVersion] = useState(
    device ? getString(device.hardware_version) : ""
  );
  // let [department, setDepartment] = useState(
  //   device ? getString(device.department) : "Network Operations Center"
  // );
  let [serialNumber, setSerialNumber] = useState(
    device ? getString(device.serial_number) : ""
  );
  let [pnCode, setPnCode] = useState(device ? getString(device.pn_code) : "");
  let [maxPower, setMaxPower] = useState(
    device ? getString(device.max_power) : ""
  );
  let [deviceRu, setDeviceRu] = useState(
    device ? getString(device.device_ru) : ""
  );
  let [manufacturer, setManufacturer] = useState(
    device ? getString(device.manufacturer) : ""
  );
  let [stack, setStack] = useState(device ? getString(device.stack) : "");
  let [source, setSource] = useState(device ? getString(device.source) : "");
  let [siteType, setSiteType] = useState(
    device ? getString(device.site_type) : "DC"
  );

  let [contractNumber, setContractNumber] = useState(
    device ? getString(device.contract_number) : ""
  );
  let [contractExpiry, setContractExpiry] = useState(
    device ? getString(device.contract_expiry) : ""
  );
  let [status, setStatus] = useState(device ? getString(device.status) : "");
  let [parent, setParent] = useState(device ? getString(device.parent) : "");
  let [vulnFixPlanStatus, setVulnFixPlanStatus] = useState(
    device ? getString(device.vuln_fix_plan_status) : "No Plan"
  );
  let [vlanOpsSeverity, setVlanOpsSeverity] = useState(
    device ? getString(device.vuln_ops_severity) : "Low"
  );

  const [integratedWithAAA, setIntegratedWithAAA] = useState(
    device ? getString(device.integrated_with_aaa) : "Yes"
  );
  const [integratedWithPAAM, setIntegratedWithPAAM] = useState(
    device ? getString(device.integrated_with_paam) : "NA"
  );
  const [approvedMBSS, setApprovedMBSS] = useState(
    device ? getString(device.approved_mbss) : "Yes"
  );
  const [mbssImplemented, setMBSSImplemented] = useState(
    device ? getString(device.mbss_implemented) : "Yes"
  );
  const [mbssIntegrationCheck, setMBSSIntegrationCheck] = useState(
    device ? getString(device.mbss_integration_check) : "Yes"
  );
  const [integratedWithSiem, setIntegratedWithSiem] = useState(
    device ? getString(device.integrated_with_siem) : "NA"
  );
  const [threatCases, setThreatCases] = useState(
    device ? getString(device.threat_cases) : "NA"
  );
  const [vulnerabilityScanning, setVulnerabilityScanning] = useState(
    device ? getString(device.vulnerability_scanning) : "Yes"
  );
  const [vulnerabilitySeverity, setVulnerabilitySeverity] = useState(
    device ? getMultiSelectOptions(device.vulnerability_severity) : ""
  );

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
        .post(baseUrl + "/editDevices", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Device Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllDevices")
              .then((response) => {
                props.setDataSource(response.data);
                props.setRowCount(response.data.length);
                props.excelData = response.data;
              })
              .catch((error) => {
                // openSweetAlert("Something Went Wrong!", "error");
                console.log(error);
              })
          );
          return Promise.all(promises);
        })
        .catch((err) => {
          // openSweetAlert("Something Went Wrong!", "error");
          console.log(err);
        });
    } catch (err) {
      // openSweetAlert("Something Went Wrong!", "error");
      console.log(err);
    }
  };

  const handleSubmit = (e) => {
    let vS = "";
    if (vulnerabilitySeverity !== "") {
      vS = vulnerabilitySeverity?.reduce((accumulator, currentValue, index) => {
        if (index !== vulnerabilitySeverity.length - 1) {
          return accumulator + currentValue.value + ",";
        } else {
          return accumulator + currentValue.value;
        }
      }, "");
    }

    e.preventDefault();
    const device = {
      device_id: ip,
      device_name: deviceName,
      tag_id: tagId,
      rfs_date: rfsDate,
      dismantle_date: dismantleDate,
      function: functiond,
      // item_code: itemCode,
      // item_desc: itemDesc,
      clei,
      parent,
      vuln_fix_plan_status: vulnFixPlanStatus,
      vuln_ops_severity: vlanOpsSeverity,
      rack_id: rackId,
      site_id: siteId,
      // manufactuer_date: manufactureDate,
      virtual,
      authentication,
      ne_ip_address: neIpAddress,
      subrack_id_number: subrackIdNumber,
      // hw_eos_date: hwEosDate,
      // hw_eol_date: hwEolDate,
      // sw_eos_date: swEosDate,
      criticality,

      cisco_domain: ciscoDomain,
      patch_version: patchVersion,
      // section,
      software_version: softwareVersion,
      hardware_version: hardwareVersion,
      // department,
      serial_number: serialNumber,

      pn_code: pnCode,

      max_power: maxPower,
      device_ru: deviceRu,
      manufacturer,
      stack,
      source,
      site_type: siteType,
      contract_number: contractNumber,
      contract_expiry: contractExpiry,
      status,

      integrated_with_aaa: integratedWithAAA,
      integrated_with_paam: integratedWithPAAM,
      approved_mbss: approvedMBSS,
      mbss_implemented: mbssImplemented,
      mbss_integration_check: mbssIntegrationCheck,
      integrated_with_siem: integratedWithSiem,
      threat_cases: threatCases,
      vulnerability_scanning: vulnerabilityScanning,
      vulnerability_severity: vS,
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

  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      background: "#fff",
      borderColor: "#9e9e9e",
      minHeight: "30px",
      height: "30px",
      boxShadow: state.isFocused ? null : null,
    }),

    valueContainer: (provided, state) => ({
      ...provided,
      height: "30px",
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
      style={{ marginTop: "-40px", zIndex: "99999" }}
      width="80%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Device</p>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Device Id: &nbsp;<span style={{ color: "red" }}>*</span>
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
              Function: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={functiond}
                onChange={(e) => setFunction(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Tag Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={tagId}
                onChange={(e) => setTagId(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              IP Address: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={neIpAddress}
                onChange={(e) => setNeIpAddress(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              RFS Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setRfsDate(dateString);
                }}
                defaultValue={rfsDate ? moment(rfsDate, "DD-MM-YYYY") : null}
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
              {/* <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={rfsDate}
                onChange={(e) => setRfsDate(e.target.value)}
                required
              /> */}
            </InputWrapper>
            <InputWrapper>
              Dismantle Date:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setDismantleDate(dateString);
                }}
                defaultValue={
                  dismantleDate ? moment(dismantleDate, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
              />
            </InputWrapper>
            {/* <InputWrapper>
              Item Code:&nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={itemCode}
                onChange={(e) => setItemCode(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Item Desc: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={itemDesc}
                onChange={(e) => setItemDesc(e.target.value)}
                required
              />
            </InputWrapper> */}
            <InputWrapper>
              Clei:&nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={clei}
                onChange={(e) => setClei(e.target.value)}
                required
              />
            </InputWrapper>
            {/* -------------------------------------------------------------------------- */}
            <InputWrapper>
              Rack Id:&nbsp;&nbsp;
              <Select
                value={rackId}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setRackId(value);
                }}
                showSearch
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {rackIdOptions}
              </Select>
            </InputWrapper>
            {/* <InputWrapper>
              Rack Id:&nbsp;&nbsp;
              <StyledInput
                value={rackId}
                onChange={(e) => setRackId(e.target.value)}
              />
            </InputWrapper> */}
            <InputWrapper>
              Site Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
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
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {siteIdOptions}
              </Select>
              {/* <StyledInput
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
                required
              /> */}
            </InputWrapper>
            {/* <InputWrapper>
              Site Id:&nbsp;&nbsp;
              <StyledInput
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
              />
            </InputWrapper> */}

            {/* <InputWrapper>
              Manufacture Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={manufactureDate}
                onChange={(e) => setManufactureDate(e.target.value)}
                required
              />
            </InputWrapper> */}

            <InputWrapper>
              Virtual: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={virtual}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVirtual(value);
                }}
              >
                <Option value="Virtual">Virtual</Option>
                <Option value="Not Virtual">Not Virtual</Option>
                <Option value="Passive">Passive</Option>
                <Option value="Managed Module">Managed Module</Option>
              </Select>
              {/* <StyledInput
                value={virtual}
                onChange={(e) => setVirtual(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Software Version:&nbsp;&nbsp;
              <StyledInput
                value={softwareVersion}
                onChange={(e) => setSoftwareVersion(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Hardware Version:&nbsp;&nbsp;
              <StyledInput
                value={hardwareVersion}
                onChange={(e) => setHardwareVersion(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Subrack Id Number:&nbsp;&nbsp;
              <StyledInput
                value={subrackIdNumber}
                onChange={(e) => setSubrackIdNumber(e.target.value)}
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Integrated With AAA: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={integratedWithAAA}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setIntegratedWithAAA(value);
                }}
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
                <Option value="NA">NA</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Integrated With PAAM: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={integratedWithPAAM}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setIntegratedWithPAAM(value);
                }}
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
                <Option value="NA">NA</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Approved MBSS: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={approvedMBSS}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setApprovedMBSS(value);
                }}
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
                <Option value="NA">NA</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              MBSS Implemented : &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={mbssImplemented}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setMBSSImplemented(value);
                }}
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
                <Option value="NA">NA</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              MBSS Integration Check: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={mbssIntegrationCheck}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setMBSSIntegrationCheck(value);
                }}
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
                <Option value="NA">NA</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Integrated With Siem: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={integratedWithSiem}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setIntegratedWithSiem(value);
                }}
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
                <Option value="NA">NA</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Threat Cases: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={threatCases}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setThreatCases(value);
                }}
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
                <Option value="NA">NA</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Vulnerability Scanning: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={vulnerabilityScanning}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVulnerabilityScanning(value);
                }}
              >
                <Option value="Yes">Yes</Option>
                <Option value="No">No</Option>
                <Option value="NA">NA</Option>
              </Select>
            </InputWrapper>
            <InputWrapper>
              Vulnerability Severity:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <div style={{ width: "100%" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={vulnerabilitySeverity}
                  onChange={(e) => setVulnerabilitySeverity(e)}
                  options={[
                    { value: "SL1", label: "SL1" },
                    { value: "SL2", label: "SL2" },
                    { value: "SL3", label: "SL3" },
                    { value: "SL4", label: "SL4" },
                    { value: "SL5", label: "SL5" },
                  ]}
                />
              </div>
              {/* <StyledInput
                value={vulnerabilitySeverity}
                onChange={(e) => setVulnerabilitySeverity(e.target.value)}
                // required
              /> */}
            </InputWrapper>
            <InputWrapper>
              Authentication: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={authentication}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setAuthentication(value);
                }}
              >
                <Option value="AAA">AAA</Option>
                <Option value="PAM">PAM</Option>
                <Option value="Local">Local</Option>
              </Select>
              {/* <StyledInput
                value={authentication}
                onChange={(e) => setAuthentication(e.target.value)}
                required
              /> */}
            </InputWrapper>
            {/* <InputWrapper>
              Hw Eos Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={hwEosDate}
                onChange={(e) => setHwEosDate(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Hw Eol Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={hwEolDate}
                onChange={(e) => setHwEolDate(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Sw Eos Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={swEosDate}
                onChange={(e) => setSwEosDate(e.target.value)}
                required
              />
            </InputWrapper> */}
            <InputWrapper>
              Criticality: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={criticality}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setCriticality(value);
                }}
              >
                {getOptions([
                  "Low",
                  "Moderate",
                  "High",
                  "Significant",
                  "Critical",
                ])}
              </Select>
              {/* <StyledInput
                value={criticality}
                onChange={(e) => setCriticality(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Cisco Domain: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={ciscoDomain}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setCiscoDomain(value);
                }}
                required
              >
                {getOptions([
                  "EDN-NET",
                  "EDN-IPT",
                  "EDN-SYS",
                  "IGW-NET",
                  "IGW-SYS",
                  "POS",
                  "SOC",
                  "REBD",
                ])}
              </Select>
              {/* <StyledInput
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Patch Version:&nbsp;&nbsp;
              <StyledInput
                value={patchVersion}
                onChange={(e) => setPatchVersion(e.target.value)}
              />
            </InputWrapper>{" "}
            {/* <InputWrapper>
              Section: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={section}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setSection(value);
                }}
              >
                {getOptions([
                  "Cloud & Virtualization Systems",
                  "End point Protection",
                  "Security Infrastructure Management",
                ])}
              </Select>
            </InputWrapper> */}
          </Col>
          <Col span={8}>
            <InputWrapper>
              Status:&nbsp;&nbsp;
              <Select
                value={status}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setStatus(value);
                }}
              >
                <Option value="Production">Production</Option>
                {/* <Option value="Dismantle">Dismantle</Option>
                <Option value="Offloaded">Offloaded</Option>
                <Option value="Powered Off">Powered Off</Option> */}
                <Option value="Excluded">Excluded</Option>
              </Select>
              {/* <StyledInput
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Parent: &nbsp;&nbsp;
              <StyledInput
                value={parent}
                onChange={(e) => setParent(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              VULN Fix Plan Status: &nbsp;
              <span style={{ color: "red" }}>*</span>
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
              VULN OPS Severity: &nbsp;
              <span style={{ color: "red" }}>*</span>
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
            {/* <InputWrapper>
              Department: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={department}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setDepartment(value);
                }}
              >
                {getOptions([
                  "Network Operations Center",
                  "Security Operations Center",
                ])}
              </Select>
            </InputWrapper> */}
            <InputWrapper>
              Serial Number:&nbsp;&nbsp;
              <StyledInput
                value={serialNumber}
                onChange={(e) => setSerialNumber(e.target.value)}
              />
            </InputWrapper>{" "}
            <InputWrapper>
              Pn Code:&nbsp;&nbsp;
              <StyledInput
                value={pnCode}
                onChange={(e) => setPnCode(e.target.value)}
              />
            </InputWrapper>{" "}
            <InputWrapper>
              Max Power:&nbsp;&nbsp;
              <StyledInput
                value={maxPower}
                onChange={(e) => setMaxPower(e.target.value)}
              />
            </InputWrapper>{" "}
            <InputWrapper>
              Device Ru:&nbsp;&nbsp;
              <StyledInput
                value={deviceRu}
                onChange={(e) => setDeviceRu(e.target.value)}
              />
            </InputWrapper>{" "}
            <InputWrapper>
              Manufacturer:&nbsp;&nbsp;
              <StyledInput
                value={manufacturer}
                onChange={(e) => setManufacturer(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Stack:&nbsp;&nbsp;
              <StyledInput
                value={stack}
                onChange={(e) => setStack(e.target.value)}
              />
            </InputWrapper>{" "}
            <InputWrapper>
              Source:&nbsp;&nbsp;
              <StyledInput
                value={source}
                onChange={(e) => setSource(e.target.value)}
              />
            </InputWrapper>{" "}
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
              {/* <StyledInput
                value={siteType}
                onChange={(e) => setSiteType(e.target.value)}
              /> */}
            </InputWrapper>
            <InputWrapper>
              Contract Number:&nbsp;&nbsp;
              <StyledInput
                value={contractNumber}
                onChange={(e) => setContractNumber(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Contract Expiry:&nbsp;&nbsp;
              <StyledInput
                value={contractExpiry}
                onChange={(e) => setContractExpiry(e.target.value)}
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
