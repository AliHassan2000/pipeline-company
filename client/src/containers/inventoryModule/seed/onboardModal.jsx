import React, { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import { Row, Col, Input, Button, notification, Select, Modal } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import { StyledButton } from "../../../components/button/main.styles";
import { StyledImportFileInput } from "../../../components/input/main.styles";
import { useLocation, useHistory } from "react-router-dom";
import XLSX from "xlsx";
import Swal from "sweetalert2";
import {
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

const AddDeviceModal = (props) => {
  const { Option } = Select;
  // const regex =
  //   "^[0-9]{4}-(0[1-9]|[1][012])-(0[1-9]|[12][0-9]|3[01]) ([0-1][0-9]|2[0123]):([0-5][0-9]):([0-5][0-9])$";

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

  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  const history = useHistory();
  const location = useLocation();
  let [inputValue, setInputValue] = useState("");
  let [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  let [ip, setIp] = useState("");
  let [deviceName, setDeviceName] = useState("");
  let [rackId, setRackId] = useState("");
  let [siteId, setSiteId] = useState("");
  // let [manufactureDate, setManufactureDate] = useState("");
  let [virtual, setVirtual] = useState("Not Virtual");
  let [authentication, setAuthentication] = useState("AAA");
  let [subrackIdNumber, setSubrackIdNumber] = useState("");
  // let [hwEosDate, setHwEosDate] = useState("");
  // let [hwEolDate, setHwEolDate] = useState("");
  // let [swEosDate, setSwEosDate] = useState("");
  // let [swEolDate, setSwEolDate] = useState("");
  let [criticality, setCriticality] = useState("Low");
  let [dFunction, setDFunction] = useState("SWITCH");
  let [ciscoDomain, setCiscoDomain] = useState("EDN-NET");
  let [vulnFixPlanStatus, setVulnFixPlanStatus] = useState("No Plan");
  let [vulnOpsSeverity, setVulnOpsSeverity] = useState("Low");
  let [patchVersion, setPatchVersion] = useState("");
  let [deviceId, setDeviceId] = useState("");
  // let [section, setSection] = useState("Cloud & Virtualization Systems");
  let [softwareVersion, setSoftwareVersion] = useState("");
  let [hardwareVersion, setHardwareVersion] = useState("");
  // let [department, setDepartment] = useState("Network Operations Center");
  let [serialNumber, setSerialNumber] = useState("");
  let [rfsDate, setRfsDate] = useState("");
  let [pnCode, setPnCode] = useState("");
  let [tagId, setTagId] = useState("");
  let [maxPower, setMaxPower] = useState("");
  let [deviceRu, setDeviceRu] = useState("");
  let [manufacturer, setManufacturer] = useState("");
  let [status, setStatus] = useState("production");
  let [stack, setStack] = useState("1");
  let [contractNumber, setContractNumber] = useState("");
  let [contractExpiry, setContractExpiry] = useState("31-12-2022");
  let [creationDate, setCreationDate] = useState("");
  let [modificationDate, setModificationDate] = useState("");
  let [itemCode, setItemCode] = useState("TBF");
  let [itemDesc, setItemDesc] = useState("TBF");
  let [clei, setClei] = useState("TBF");
  let [siteType, setSiteType] = useState("DC");
  let [parent, setParent] = useState("");

  const [integratedWithAAA, setIntegratedWithAAA] = useState("Yes");
  const [integratedWithPAAM, setIntegratedWithPAAM] = useState("NA");
  const [approvedMBSS, setApprovedMBSS] = useState("Yes");
  const [mbssImplemented, setMBSSImplemented] = useState("Yes");
  const [mbssIntegrationCheck, setMBSSIntegrationCheck] = useState("Yes");
  const [integratedWithSiem, setIntegratedWithSiem] = useState("Yes");
  const [threatCases, setThreatCases] = useState("Yes");
  const [vulnerabilityScanning, setVulnerabilityScanning] = useState("Yes");
  const [vulnerabilitySeverity, setVulnerabilitySeverity] = useState("");

  useEffect(() => {
    // inputRef.current.addEventListener("input", importExcel);
    // if (typeof location.state !== "undefined") {
    //   const record = location.state.detail;
    //   // history.replace({
    //   //   pathname: "/staticonboarding",
    //   //   state: { detail: {} },
    //   // });
    //   updateStates(record);
    // }
    updateStates(props.record);
  }, []);

  const updateStates = (record) => {
    console.log("wowww");
    console.log(record);
    setIp(record.ne_ip_address ? record.ne_ip_address : "");
    setDeviceName(record.hostname ? record.hostname : "");
    setRackId(record.rack_id ? record.rack_id : "");
    setSiteId(record.site_id ? record.site_id : "");
    // setManufactureDate(record.manufactuer_date ? record.manufactuer_date : "");
    setVirtual(record.virtual ? record.virtual : "");
    setAuthentication(record.authentication ? record.authentication : "");
    setSubrackIdNumber(
      record.subrack_id_number ? record.subrack_id_number : ""
    );
    setParent(record.parent ? record.parent : "");
    // setHwEosDate;
    // setHwEolDate;
    // setSwEosDate;
    // setSwEolDate;
    setCriticality(record.criticality ? record.criticality : "");
    setDFunction(record.function ? record.function : "");
    setCiscoDomain(record.cisco_domain ? record.cisco_domain : "");
    setVulnFixPlanStatus(
      record.vuln_fix_plan_status ? record.vuln_fix_plan_status : ""
    );
    setVulnOpsSeverity(
      record.vuln_ops_severity ? record.vuln_ops_severity : ""
    );
    // setPatchVersion;
    setDeviceId(record.device_id ? record.device_id : "");
    // setSection(record.section ? record.section : "");
    // setSoftwareVersion;
    // setHardwareVersion;
    // setDepartment(record.department ? record.department : "");
    setSerialNumber(record.serial_number ? record.serial_number : "");
    setRfsDate(record.rfs_date ? record.rfs_date : "");
    setPnCode(record.pn_code ? record.pn_code : "");
    setTagId(record.tag_id ? record.tag_id : "");
    // setMaxPower;
    setDeviceRu(record.device_ru ? record.device_ru : "");
    // setManufacturer;
    // setStatus;
    // setStack;
    setContractNumber(record.contract_number ? record.contract_number : "");
    setContractExpiry(record.contract_expiry ? record.contract_expiry : "");
    // setCreationDate;
    // setModificationDate;
    // setItemCode(record?.item_code ? record.item_code : "TBF");
    // setItemDesc(record?.item_desc ? record.item_desc : "TBF");
    setClei(record?.clei ? record.clei : "TBF");
    setSiteType(record.site_type ? record.site_type : "");

    setIntegratedWithAAA(
      record.integrated_with_aaa ? record.integrated_with_aaa : "Yes"
    );
    setIntegratedWithPAAM(
      record.integrated_with_paam ? record.integrated_with_paam : "NA"
    );
    setApprovedMBSS(record.approved_mbss ? record.approved_mbss : "Yes");
    setMBSSImplemented(
      record.mbss_implemented ? record.mbss_implemented : "Yes"
    );
    setMBSSIntegrationCheck(
      record.mbss_integration_check ? record.mbss_integration_check : "Yes"
    );
    setIntegratedWithSiem(
      record.integrated_with_siem ? record.integrated_with_siem : "NA"
    );
    setThreatCases(record.threat_cases ? record.threat_cases : "NA");
    setVulnerabilityScanning(
      record.vulnerability_scanning ? record.vulnerability_scanning : "Yes"
    );
    setVulnerabilitySeverity(
      record.vulnerability_severity ? record.vulnerability_severity : ""
    );
  };

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/addUnboardedDevice", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Device Onboarded Successfully", "success");
          }
        })
        .catch((error) => {
          // openSweetAlert("Something Went Wrong!", "danger");
          console.log(error);
        });
    } catch (err) {
      console.log(err);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const device = {
      ne_ip_address: ip,
      device_name: deviceName,
      rack_id: rackId,
      site_id: siteId,
      site_type: siteType,
      // manufactuer_date: manufactureDate,
      virtual,
      // item_code: itemCode,
      // item_desc: itemDesc,
      clei,
      authentication,
      subrack_id_number: subrackIdNumber,
      // hw_eos_date: hwEosDate,
      // hw_eol_date: hwEolDate,
      // sw_eos_date: swEosDate,
      // sw_eol_date: swEolDate,
      criticality,
      function: dFunction,
      cisco_domain: ciscoDomain,
      vuln_fix_plan_status: vulnFixPlanStatus,
      vuln_ops_severity: vulnOpsSeverity,
      patch_version: patchVersion,
      device_id: deviceId,
      // section,
      software_version: softwareVersion,
      hardware_version: hardwareVersion,
      // department,
      parent,
      serial_number: serialNumber,
      rfs_date: rfsDate,
      pn_code: pnCode,
      tag_id: tagId,
      max_power: maxPower,
      device_ru: deviceRu,
      manufacturer,
      status,
      contract_number: contractNumber,
      contract_expiry: contractExpiry,
      stack,
      creation_date: creationDate,
      modification_date: modificationDate,

      integrated_with_aaa: integratedWithAAA,
      integrated_with_paam: integratedWithPAAM,
      approved_mbss: approvedMBSS,
      mbss_implemented: mbssImplemented,
      mbss_integration_check: mbssIntegrationCheck,
      integrated_with_siem: integratedWithSiem,
      threat_cases: threatCases,
      vulnerability_scanning: vulnerabilityScanning,
      vulnerability_severity: vulnerabilitySeverity,
    };

    // props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postSeed = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/addUnboardedDevices", seed)
      .then((response) => {
        openSweetAlert("Devices Onboarded Successfully", "success");
        setLoading(false);
      })
      .catch((err) => {
        openSweetAlert("Something Went Wrong!", "danger");
        console.log(err);
        setLoading(false);
      });
  };

  const convertToJson = (headers, fileData) => {
    let rows = [];
    fileData.forEach((row) => {
      const rowData = {};
      row.forEach((element, index) => {
        rowData[headers[index]] = element;
      });
      rows.push(rowData);
    });
    rows = rows.filter((value) => JSON.stringify(value) !== "{}");
    return rows;
  };

  const importExcel = (e) => {
    console.log("in import excel");
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.readAsBinaryString(file);
    reader.onload = (e) => {
      const bstr = e.target.result;
      const workbook = XLSX.read(bstr, { type: "binary" });
      const workSheetName = workbook.SheetNames[0];
      const workSheet = workbook.Sheets[workSheetName];
      const fileData = XLSX.utils.sheet_to_json(workSheet, {
        header: 1,
        raw: false,
      });
      const headers = fileData[0];
      fileData.splice(0, 1);
      let excelData = convertToJson(headers, fileData);
      console.log(excelData);
      postSeed(excelData);
    };
  };

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
    XLSX.writeFile(wb, "staticonboarding.xlsx");
  };

  let excelTemplate = [
    {
      ne_ip_address: "",
      device_id: "",
      device_name: "",
      // item_code: "",
      // item_desc: "",
      // clei: "",
      rack_id: "",
      site_id: "",
      // manufactuer_date: "",
      hw_eos_date: "",
      hw_eol_date: "",
      sw_eos_date: "",
      sw_eol_date: "",
      virtual: "",
      authentication: "",
      subrack_id_number: "",
      criticality: "",
      parent: "",
      function: "",
      cisco_domain: "",
      patch_version: "",
      // section: "",
      software_version: "",
      hardware_version: "",
      // department: "",
      serial_number: "",
      rfs_date: "",
      pn_code: "",
      tag_id: "",
      max_power: "",
      device_ru: "",
      manufacturer: "",
      status: "",
      creation_date: "",
      modification_date: "",
    },
  ];

  const exportTemplate = async () => {
    jsonToExcel(excelTemplate);
    openNotification();
  };

  const openNotification = () => {
    notification.open({
      message: "File Exported Successfully",
      onClick: () => {
        console.log("Notification Clicked!");
      },
    });
  };

  const getOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  return (
    <Modal
      style={{ marginTop: "-25px", zIndex: "99999" }}
      width="90%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <div
        style={{ display: "flex", justifyContent: "center", marginTop: "0px" }}
      >
        <StyledHeading>Static Onboarding</StyledHeading>
      </div>
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={8}>
            <InputWrapper>
              Ip: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={ip}
                onChange={(e) => setIp(e.target.value)}
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
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Device Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
                required
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Rack Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {/* <Select
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
              </Select> */}
              <StyledInput
                value={rackId}
                onChange={(e) => setRackId(e.target.value)}
                required
                disabled
              />
            </InputWrapper>

            <InputWrapper>
              Site Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
                required
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Parent: &nbsp;&nbsp;
              <StyledInput
                value={parent}
                onChange={(e) => setParent(e.target.value)}
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Cisco Domain: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                disabled
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
              VULN Fix Plan Status: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                disabled
                value={vulnFixPlanStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVulnFixPlanStatus(value);
                }}
                required
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
                disabled
                value={vulnOpsSeverity}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVulnOpsSeverity(value);
                }}
                required
              >
                {getOptions(["Low", "Critical", "High"])}
              </Select>
              {/* <StyledInput
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
              /> */}
            </InputWrapper>
            {/* <InputWrapper>
              Section: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                disabled
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

            {/* <InputWrapper>
              Department: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                disabled
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
              Virtual: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                disabled
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
              Authentication: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                disabled
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
            <InputWrapper>
              Contract Number:&nbsp;&nbsp;
              <StyledInput
                value={contractNumber}
                onChange={(e) => setContractNumber(e.target.value)}
                // required
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Hardware Version:&nbsp;&nbsp;
              <StyledInput
                value={hardwareVersion}
                onChange={(e) => setHardwareVersion(e.target.value)}
                // required
              />
            </InputWrapper>
            {/* <InputWrapper>
              Item Code:&nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={itemCode}
                onChange={(e) => setItemCode(e.target.value)}
                required
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Item Desc: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={itemDesc}
                onChange={(e) => setItemDesc(e.target.value)}
                required
                disabled
              />
            </InputWrapper> */}
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
                disabled
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
                disabled
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
                disabled
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
                disabled
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
                disabled
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
                disabled
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
                disabled
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
                disabled
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
              <StyledInput
                value={vulnerabilitySeverity}
                onChange={(e) => setVulnerabilitySeverity(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Clei:&nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={clei}
                onChange={(e) => setClei(e.target.value)}
                required
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Subrack Id Number:&nbsp;&nbsp;
              <StyledInput
                value={subrackIdNumber}
                onChange={(e) => setSubrackIdNumber(e.target.value)}
                // required
                disabled
              />
            </InputWrapper>
            {/* <InputWrapper>
              Manufacture Date:&nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={manufactureDate}
                onChange={(e) => setManufactureDate(e.target.value)}
                // required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Hw Eos Date:&nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={hwEosDate}
                onChange={(e) => setHwEosDate(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Hw Eol Date:&nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={hwEolDate}
                onChange={(e) => setHwEolDate(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Sw Eos Date:&nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={swEosDate}
                onChange={(e) => setSwEosDate(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Sw Eol Date:&nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={swEolDate}
                onChange={(e) => setSwEolDate(e.target.value)}
                // required
              />
            </InputWrapper> */}
            <InputWrapper>
              RFS: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                required
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={rfsDate}
                onChange={(e) => setRfsDate(e.target.value)}
                disabled
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Software Version:&nbsp;&nbsp;
              <StyledInput
                value={softwareVersion}
                onChange={(e) => setSoftwareVersion(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
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
              Pn Code: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={pnCode}
                onChange={(e) => setPnCode(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Tag Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={tagId}
                onChange={(e) => setTagId(e.target.value)}
                // required
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Max Power:&nbsp;&nbsp;
              <StyledInput
                value={maxPower}
                onChange={(e) => setMaxPower(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Device Ru:&nbsp;&nbsp;
              <StyledInput
                value={deviceRu}
                onChange={(e) => setDeviceRu(e.target.value)}
                // required
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Site Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                disabled
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
              Manufacturer: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={manufacturer}
                onChange={(e) => setManufacturer(e.target.value)}
                required
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
                disabled
              >
                <Option value="Production">Production</Option>
                <Option value="Not Handedover">Not Handedover</Option>
                <Option value="Shut Down">Shut Down</Option>
                <Option value="Dismantle">Dismantle</Option>
                <Option value="Offloaded">Offloaded</Option>
              </Select>
              {/* <StyledInput
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  required
                /> */}
            </InputWrapper>
            <InputWrapper>
              Stack:&nbsp;&nbsp;
              <StyledInput
                value={stack}
                onChange={(e) => setStack(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Contract Expiry: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={contractExpiry}
                onChange={(e) => setContractExpiry(e.target.value)}
                required
                disabled
              />
            </InputWrapper>
            {/* <InputWrapper>
                Creation Date:&nbsp;&nbsp;
                <StyledInput
                  pattern={regex}
                  placeholder="dd-mm-yyyy"
                  value={creationDate}
                  onChange={(e) => setCreationDate(e.target.value)}
                  // required
                />
              </InputWrapper>
              <InputWrapper>
                Modification Date:&nbsp;&nbsp;
                <StyledInput
                  pattern={regex}
                  placeholder="dd-mm-yyyy"
                  value={modificationDate}
                  onChange={(e) => setModificationDate(e.target.value)}
                  // required
                />
              </InputWrapper> */}
            {/* <br /> */}
            <InputWrapper>
              Criticality: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                disabled
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
              Function: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={dFunction}
                onChange={(e) => setDFunction(e.target.value)}
                required
                disabled
              />
            </InputWrapper>
            <InputWrapper>
              Patch Version:&nbsp;&nbsp;
              <StyledInput
                value={patchVersion}
                onChange={(e) => setPatchVersion(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center" }}>
            <StyledButton
              color={"red"}
              onClick={handleCancel}
              style={{
                width: "15%",
              }}
            >
              Cancel
            </StyledButton>
            &nbsp; &nbsp;{" "}
            <StyledSubmitButton
              color={"green"}
              type="submit"
              value="Onboard"
              style={{ marginTop: "10px" }}
            />
          </Col>
        </Row>
      </form>
    </Modal>
  );
};

const StyledCard = styled.div`
  height: 100%;
  background-color: white;
  border-radius: 10px;
  padding: 0px 20px 5px 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;

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

const StyledHeading = styled.p`
  font-size: 20px;
  font-family: Montserrat-Regular;
`;

export default AddDeviceModal;
