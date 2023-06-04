import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import Swal from "sweetalert2";
import MultiSelect from "react-select";

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

  // const regex =
  //   "^[0-9]{4}-(0[1-9]|[1][012])-(0[1-9]|[12][0-9]|3[01]) ([0-1][0-9]|2[0123]):([0-5][0-9]):([0-5][0-9])$";
  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////
  let [ip, setIp] = useState(device ? getString(device.ne_ip_address) : "");
  let [deviceId, setDeviceId] = useState(
    device ? getString(device.device_id) : ""
  );

  let [deviceRu, setDeviceRu] = useState(
    device ? getString(device.device_ru) : "1"
  );
  // let [department, setDepartment] = useState(
  //   device ? getString(device.department) : "Network Operations Center"
  // );
  // let [section, setSection] = useState(
  //   device ? getString(device.section) : "Cloud & Virtualization Systems"
  // );
  // let [vulnFixPlanStatus, setVulnFixPlanStatus] = useState(
  //   device ? getString(device.vuln_fix_plan_status) : "No Plan"
  // );
  // let [vlanOpsSeverity, setVlanOpsSeverity] = useState(
  //   device ? getString(device.vuln_ops_severity) : "Low"
  // );
  let [criticality, setCriticality] = useState(
    device ? getString(device.criticality) : "Low"
  );
  let [dFunction, setDFunction] = useState(
    device ? getString(device.function) : "SWITCH"
  );
  let [ciscoDomain, setCiscoDomain] = useState(
    device ? getString(device.cisco_domain) : "EDN-NET"
  );
  let [parent, setParent] = useState(device ? getString(device.parent) : "");
  let [virtual, setVirtual] = useState(
    device ? getString(device.virtual) : "Not Virtual"
  );
  // const [dropDowns, setDropDowns] = useState({
  //   virtual: `${device ? getString(device.virtual) : ""}`,
  // });
  let [authentication, setAuthentication] = useState(
    device ? getString(device.authentication) : "AAA"
  );

  let [subrackIdNumber, setSubrackIdNumber] = useState(
    device ? getString(device.subrack_id_number) : ""
  );
  let [hostName, setHostName] = useState(
    device ? getString(device.hostname) : ""
  );
  // let [swVersion, setSWVersion] = useState(
  //   device ? getString(device.sw_version) : ""
  // );
  let [siteType, setSiteType] = useState(
    device ? getString(device.site_type) : "DC"
  );
  let [swType, setSwType] = useState(
    device ? getString(device.sw_type) : "IOS"
  );
  let [vendor, setVendor] = useState(
    device ? getString(device.vendor) : "Cisco"
  );
  let [assetType, setAssetType] = useState(
    device ? getString(device.asset_type) : "EDN"
  );
  let [operationStatus, setOperationStatus] = useState(
    device ? getString(device.operation_status) : "production"
  );
  let [siteId, setSiteId] = useState(device ? getString(device.site_id) : "");
  let [rackId, setRackId] = useState(device ? getString(device.rack_id) : "");

  let [region, setRegion] = useState(
    device ? getString(device.region) : "CENTRAL"
  );
  let [siteName, setSiteName] = useState(
    device ? getString(device.site_name) : ""
  );
  let [latitude, setLatitude] = useState(
    device ? getString(device.latitude) : ""
  );
  let [longitude, setLongitude] = useState(
    device ? getString(device.longitude) : ""
  );
  let [city, setCity] = useState(device ? getString(device.city) : "");
  let [datacenterStatus, setDatacenterStatus] = useState(
    device ? getString(device.datacentre_status) : "production"
  );
  let [floor, setFloor] = useState(device ? getString(device.floor) : "");
  let [rackName, setRackName] = useState(
    device ? getString(device.rack_name) : ""
  );
  let [serialNumber, setSerialNumber] = useState(
    device ? getString(device.serial_number) : ""
  );
  // let [manufactureDate, setManufactureDate] = useState(
  //   device ? getDateString(device.manufactuer_date) : ""
  // );
  let [unitPosition, setUnitPosition] = useState(
    device ? getString(device.unit_position) : ""
  );
  let [rackStatus, setRackStatus] = useState(
    device ? getString(device.rack_status) : ""
  );
  let [rfsDate, setRfsDate] = useState(
    device ? getDateString(device.rfs_date) : ""
  );
  let [height, setHeight] = useState(device ? getString(device.height) : "");
  let [width, setWidth] = useState(device ? getString(device.width) : "");
  let [depth, setDepth] = useState(device ? getString(device.depth) : "");
  // let [pnCode, setPnCode] = useState(device ? getString(device.pn_code) : "");
  let [tagId, setTagId] = useState(device ? getString(device.tag_id) : "TBF");

  let [rackModel, setRackModel] = useState(
    device ? getString(device.rack_model) : ""
  );

  let [contractNumber, setContractNumber] = useState(
    device ? getString(device.contract_number) : ""
  );

  let [contractExpiry, setContractExpiry] = useState(
    device ? getString(device.contract_expiry) : ""
  );

  // let [itemCode, setItemCode] = useState(
  //   device?.item_code ? device.item_code : "TBF"
  // );
  // let [itemDesc, setItemDesc] = useState(
  //   device?.item_desc ? device.item_desc : "TBF"
  // );
  let [clei, setClei] = useState(device?.clei ? device.clei : "TBF");

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
        .post(baseUrl + "/addDevice", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert(
              `Device ${device ? "Updated" : "Added"} Successfully`,
              "success"
            );
            const promises = [];
            promises.push(
              axios
                .get(baseUrl + "/getSeeds")
                .then((response) => {
                  console.log(response.data);
                  props.setDataSource(response.data);
                  props.excelData = response.data;
                  props.setRowCount(response.data.length);
                  props.excelData = response.data;
                })
                .catch((error) => {
                  console.log(error);
                  //  openSweetAlert("Something Went Wrong!", "error");
                })
            );
            return Promise.all(promises);
          }
        })
        .catch((error) => {
          console.log("in add seed device catch ==> " + error);
          // openSweetAlert("Something Went Wrong!", "error");
        });
    } catch (err) {
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
      ne_ip_address: ip,
      device_id: deviceId,
      device_ru: deviceRu,
      // department,
      // section,
      criticality,
      function: dFunction,
      cisco_domain: ciscoDomain,
      // item_code: itemCode,
      // item_desc: itemDesc,

      clei,
      parent,
      // vuln_fix_plan_status: vulnFixPlanStatus,
      // vuln_ops_severity: vlanOpsSeverity,
      virtual,
      authentication,
      subrack_id_number: subrackIdNumber,
      hostname: hostName,
      site_type: siteType,
      // sw_version: swVersion,
      sw_type: swType,
      vendor,
      asset_type: assetType,
      operation_status: operationStatus,
      site_id: siteId,
      rack_id: rackId,
      region,
      site_name: siteName,
      latitude,
      longitude,
      city,
      datacentre_status: datacenterStatus,
      floor,
      rack_name: rackName,
      serial_number: serialNumber,
      // manufactuer_date: manufactureDate,
      unit_position: unitPosition,
      rack_status: rackStatus,
      rfs_date: rfsDate,
      height,
      width,
      depth,
      // pn_code: pnCode,
      tag_id: tagId,
      rack_model: rackModel,
      contract_number: contractNumber,
      contract_expiry: contractExpiry,

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
      style={{ marginTop: "-20px", zIndex: "99999" }}
      width="90%"
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
              Ip: &nbsp;<span style={{ color: "red" }}>*</span>
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
              Device Id: &nbsp;<span style={{ color: "red" }}>*</span>
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
            </InputWrapper>
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
            <InputWrapper>
              Rack Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
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
                {/* <Option value="jack">Jack</Option>
                <Option value="lucy">Lucy</Option>
                <Option value="tom">Tom</Option> */}
              </Select>
              {/* <StyledInput
                value={rackId}
                onChange={(e) => setRackId(e.target.value)}
                required
              /> */}
            </InputWrapper>
            {/* <InputWrapper>
              Rack Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={rackName}
                onChange={(e) => setRackName(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Site Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={siteName}
                onChange={(e) => setSiteName(e.target.value)}
                required
              />
            </InputWrapper> */}
            <InputWrapper>
              RFS: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={rfsDate}
                onChange={(e) => setRfsDate(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              SW Type: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={swType}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setSwType(value);
                }}
              >
                {getOptions([
                  "IOS",
                  "A10",
                  "ACI-LEAF",
                  "ACI-SPINE",
                  "AP",
                  "APIC",
                  "Arbor",
                  "Arbor-Sec",
                  "Arista",
                  "ASA96",
                  "ASA-SOC",
                  "BeyondTrust",
                  "DNS Filtering",
                  "F5",
                  "FireEye",
                  "FirepowerServer",
                  "Firepower-SSH",
                  "Fortinet-Sec",
                  "Greatbay",
                  "HPAruba",
                  "Infoblox",
                  "IOS-XE",
                  "IOS-XR",
                  "IPT",
                  "Juniper-Screenos",
                  "Juniper-Sec",
                  "Linux",
                  "Microsoft",
                  "MobileIron",
                  "Nutanix",
                  "NX-OS",
                  "Ookla",
                  "oscilloquartz",
                  "PaloAlto",
                  "PRIME",
                  "PulseSecure",
                  "Qualys",
                  "SolarWind",
                  "SolarWinds",
                  "StorMagic",
                  "Symantec",
                  "UCS",
                  "UCS-CIMC",
                  "UCS-SYS",
                  "vcenter",
                  "WireFilter",
                  "WLC",
                ])}
              </Select>
              {/* <StyledInput
                value={swType}
                onChange={(e) => setSwType(e.target.value)}
              /> */}
            </InputWrapper>
            {/* <InputWrapper>
              City: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={city}
                onChange={(e) => setCity(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Region: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={region}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setRegion(value);
                }}
                required
              >
                {getOptions([
                  "CENTRAL",
                  "EASTERN",
                  "INTERNATIONAL",
                  "SOUTHERN",
                  "WESTERN",
                ])}
              </Select>
            </InputWrapper> */}
            <InputWrapper>
              Subrack Id Number: &nbsp;&nbsp;
              <StyledInput
                value={subrackIdNumber}
                onChange={(e) => setSubrackIdNumber(e.target.value)}
              />
            </InputWrapper>
            {/* <InputWrapper>
              Latitude: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Longitude: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Datacenter Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={datacenterStatus}
                onChange={(e) => setDatacenterStatus(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Floor: &nbsp;&nbsp;
              <StyledInput
                value={floor}
                onChange={(e) => setFloor(e.target.value)}
              />
            </InputWrapper> */}
            <InputWrapper>
              Contract Number:&nbsp;&nbsp;
              <StyledInput
                value={contractNumber}
                onChange={(e) => setContractNumber(e.target.value)}
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
              />
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
              {/* <StyledInput
                value={assetType}
                onChange={(e) => setAssetType(e.target.value)}
              /> */}
            </InputWrapper>
            {/* <InputWrapper>
              Device Ru: &nbsp;&nbsp;
              <StyledInput value={deviceRu} onChange={(e) => setDeviceRu(e.target.value)} />
            </InputWrapper> */}
            {/* <InputWrapper>
              Height: &nbsp;&nbsp;
              <StyledInput
                value={height}
                onChange={(e) => setHeight(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Width: &nbsp;&nbsp;
              <StyledInput
                value={width}
                onChange={(e) => setWidth(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Depth: &nbsp;&nbsp;
              <StyledInput
                value={depth}
                onChange={(e) => setDepth(e.target.value)}
              />
            </InputWrapper>

            <InputWrapper>
              Pn Code: &nbsp;&nbsp;
              <StyledInput
                value={pnCode}
                onChange={(e) => setPnCode(e.target.value)}
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              Item Code:&nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={itemCode}
                onChange={(e) => setItemCode(e.target.value)}
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
            {/* -------------------------------------------------------------------- */}
            <InputWrapper>
              Host Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={hostName}
                onChange={(e) => setHostName(e.target.value)}
                required
              />
            </InputWrapper>
            {/* <InputWrapper>
              SW Version: &nbsp;&nbsp;
              <StyledInput
                value={swVersion}
                onChange={(e) => setSWVersion(e.target.value)}
              />
            </InputWrapper> */}

            {/* <InputWrapper>
              Manufacture Date: &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={manufactureDate}
                onChange={(e) => setManufactureDate(e.target.value)}
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
          </Col>
          <Col span={8}>
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
            {/* <InputWrapper>
              Rack Serial Number: &nbsp;&nbsp;
              <StyledInput
                value={serialNumber}
                onChange={(e) => setSerialNumber(e.target.value)}
              />
            </InputWrapper> */}
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
              Rack Model: &nbsp;&nbsp;
              <StyledInput
                value={rackModel}
                onChange={(e) => setRackModel(e.target.value)}
              />
            </InputWrapper> */}
            <InputWrapper>
              Device Ru: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deviceRu}
                onChange={(e) => setDeviceRu(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Parent: &nbsp;&nbsp;
              <StyledInput
                value={parent}
                onChange={(e) => setParent(e.target.value)}
              />
            </InputWrapper>

            {/* <InputWrapper>
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
            </InputWrapper> */}
            {/* <InputWrapper>
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
            </InputWrapper> */}

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
              Vendor: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={vendor}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setVendor(value);
                }}
              >
                <Option value="Cisco">Cisco</Option>
                <Option value="A10">A10</Option>
                <Option value="Arbor">Arbor</Option>
                <Option value="Arista">Arista</Option>
                <Option value="Aruba Networks">Aruba Networks</Option>
                <Option value="BeyondTrust">BeyondTrust</Option>
                <Option value="Dell">Dell</Option>
                <Option value="F5">F5</Option>
                <Option value="FireEye">FireEye</Option>
                <Option value="Fortinet">Fortinet</Option>
                <Option value="Greatbay">Greatbay</Option>
                <Option value="HP">HP</Option>
                <Option value="HPAruba">HPAruba</Option>
                <Option value="Infoblox">Infoblox</Option>
                <Option value="Juniper">Juniper</Option>
                <Option value="Microsoft">Microsoft</Option>
                <Option value="MobileIron">MobileIron</Option>
                <Option value="Newnet">Newnet</Option>
                <Option value="Nutanix">Nutanix</Option>
                <Option value="Ookla">Ookla</Option>
                <Option value="oscilloquartz">oscilloquartz</Option>
                <Option value="Others">Others</Option>
                <Option value="PaloAlto">PaloAlto</Option>
                <Option value="PulseSecure">PulseSecure</Option>
                <Option value="Qualys">Qualys</Option>
                <Option value="SolarWinds">SolarWinds</Option>
                <Option value="StorMagic">StorMagic</Option>
                <Option value="SUN">SUN</Option>
                <Option value="Symantec">Symantec</Option>
                <Option value="Virtual">Virtual</Option>
                <Option value="Vmware">Vmware</Option>
                <Option value="WireFilter">WireFilter</Option>
              </Select>
              {/* <StyledInput
                value={vendor}
                onChange={(e) => setVendor(e.target.value)}
              /> */}
            </InputWrapper>
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
              Function: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={dFunction}
                onChange={(e) => setDFunction(e.target.value)}
                required
              />
            </InputWrapper>

            {/* <InputWrapper>
              Unit Position: &nbsp;&nbsp;
              <StyledInput
                value={unitPosition}
                onChange={(e) => setUnitPosition(e.target.value)}
              />
            </InputWrapper> */}

            {/* <InputWrapper>
              Rack Status: &nbsp;&nbsp;
              <StyledInput
                value={rackStatus}
                onChange={(e) => setRackStatus(e.target.value)}
              />
            </InputWrapper> */}

            <InputWrapper>
              Contract Expiry:&nbsp;&nbsp;
              <StyledInput
                value={contractExpiry}
                onChange={(e) => setContractExpiry(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Operation Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={operationStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setOperationStatus(value);
                }}
              >
                <Option value="Production">Production</Option>
                <Option value="Not Handedover">Not Handedover</Option>
                {/* <Option value="Dismantle">Dismantle</Option>
                <Option value="Offloaded">Offloaded</Option> */}
              </Select>
              {/* <StyledInput
                value={operationStatus}
                onChange={(e) => setOperationStatus(e.target.value)}
              /> */}
            </InputWrapper>
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
          </Col>
          <Col
            span={24}
            style={{
              textAlign: "center",
              marginTop: "15px",
              marginBottom: "10px",
            }}
          >
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
