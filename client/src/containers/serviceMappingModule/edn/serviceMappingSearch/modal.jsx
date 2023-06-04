// import React, {
//   useEffect,
//   useState,
//   forwardRef,
//   useImperativeHandle,
// } from "react";
// import styled from "styled-components";
// import { Row, Col, Modal, Input, Button, DatePicker, Select, Spin } from "antd";
// import axios, { baseUrl } from "../../../../utils/axios";
// import moment from "moment";
// import { RightSquareOutlined } from "@ant-design/icons";
// import XLSX from "xlsx";

// const AddDeviceModal = forwardRef((props, ref) => {
//   const { Option } = Select;
//   let [exportLoading, setExportLoading] = useState(false);
//   let [deviceAName, setDeviceAName] = useState("");
//   //   let [deviceAInterface, setDeviceAInterface] = useState("");
//   //   let [deviceATrunkName, setDeviceATrunkName] = useState("");
//   let [deviceAIp, setDeviceAIp] = useState("");
//   let [deviceBSystemName, setDeviceBSystemName] = useState("");
//   //   let [deviceBInterface, setDeviceBInterface] = useState("");
//   let [deviceBIp, setDeviceBIp] = useState("");
//   //   let [deviceBType, setDeviceBType] = useState("");
//   //   let [deviceBPortDesc, setDeviceBPortDesc] = useState("");
//   //   let [deviceAMac, setDeviceAMac] = useState("");
//   let [deviceBMac, setDeviceBMac] = useState("");
//   //   let [deviceAPortDesc, setDeviceAPortDesc] = useState("");
//   let [deviceAVlan, setDeviceAVlan] = useState("");
//   //   let [deviceAVlanName, setDeviceAVlanName] = useState("");
//   let [serverName, setServerName] = useState("");
//   //   let [serverOS, setServerOS] = useState("");
//   let [appName, setAppName] = useState("");
//   //   let [ownerName, setOwnerName] = useState("");
//   //   let [ownerEmail, setOwnerEmail] = useState("");
//   //   let [ownerContact, setOwnerContact] = useState("");
//   let [serviceVendor, setServiceVendor] = useState("");
//   let [fetchDate, setFetchDate] = useState(
//     props.dates?.length > 0 ? props.dates[0] : null
//   );

//   let [deviceANames, setDeviceANames] = useState([]);
//   let [deviceANameOptions, setDeviceANameOptions] = useState([]);

//   useEffect(() => {
//     (async () => {
//       try {
//         const res = await axios.get(baseUrl + "/getDeviceANames");
//         setDeviceANames(res.data);
//       } catch (err) {
//         console.log(err.response);
//       }
//     })();
//   }, []);

//   useEffect(() => {
//     let options = getOptions(deviceANames);
//     setDeviceANameOptions(options);
//   }, [deviceANames]);

//   const getOptions = (values = []) => {
//     let options = [];
//     values.map((value) => {
//       options.push(<Option value={value}>{value}</Option>);
//     });
//     return options;
//   };

//   const getEdnMacLegacyBySearchFilters = async (filters) => {
//     props.setLoading(true);
//     await axios
//       .post(
//         baseUrl +
//           `/getEdnMacLegacyBySearchFilters?limit=${props.pageSize}&offset=${
//             props.pageSize * (props.currentPage - 1)
//           }`,
//         filters
//       )
//       .then((response) => {
//         props.setDataSource(response.data.data);
//         props.setTotal(response.data.total);
//         props.setLoading(false);
//       })
//       .catch((error) => {
//         console.log(error);
//         props.setLoading(false);
//       });
//   };

//   const handleSubmit = (e) => {
//     e?.preventDefault();
//     const filters = {
//       device_a_name: deviceAName,
//       //   device_a_interface: deviceAInterface,
//       //   device_a_trunk_name: deviceATrunkName,
//       device_a_ip: deviceAIp,
//       device_b_ip: deviceBIp,
//       //   device_a_mac: deviceAMac,
//       device_b_mac: deviceBMac,
//       //   device_a_port_desc: deviceAPortDesc,
//       device_a_vlan: deviceAVlan,
//       device_b_system_name: deviceBSystemName,
//       //   device_b_interface: deviceBInterface,
//       //   device_b_type: deviceBType,
//       //   device_b_port_desc: deviceBPortDesc,
//       server_name: serverName,
//       //   server_os: serverOS,
//       app_name: appName,
//       //   owner_name: ownerName,
//       //   owner_email: ownerEmail,
//       //   owner_contact: ownerContact,
//       service_vendor: serviceVendor,
//       fetch_date: fetchDate,
//     };

//     getEdnMacLegacyBySearchFilters(filters);

//     // if (checkProperties(filters)) {
//     //   getEdnMacLegacyBySearchFilters(filters);
//     // } else {
//     //   alert("No filter is selected! Atleast 1 filter is a must to search :)");
//     // }
//   };

//   useImperativeHandle(ref, () => ({ handleSubmit }), [
//     deviceAName,
//     deviceAIp,
//     deviceBIp,
//     deviceBMac,
//     deviceAVlan,
//     deviceBSystemName,
//     serverName,
//     appName,
//     serviceVendor,
//     fetchDate,
//     props.pageSize,
//     props.currentPage,
//   ]);

//   const checkProperties = (obj) => {
//     for (let key in obj) {
//       if (obj[key] !== null && obj[key] != "") return true;
//     }
//     return false;
//   };

//   const handleCancel = async () => {
//     setDeviceAName("");
//     setDeviceAIp("");
//     setDeviceBSystemName("");
//     setDeviceBIp("");
//     setDeviceBMac("");
//     setDeviceAVlan("");
//     setServerName("");
//     setAppName("");
//     setServiceVendor("");
//     setFetchDate("");

//     props.setDataSource([]);
//   };

//   const handleSelectChange = (value) => {
//     setFetchDate(value);
//   };

//   const exportSeed = async () => {
//     // setExportLoading(true);
//     // jsonToExcel(dataSource, "ednmaclegacySearched.xlsx");
//     // setExportLoading(false);
//     const filters = {
//       device_a_name: deviceAName,
//       device_a_ip: deviceAIp,
//       device_b_ip: deviceBIp,
//       device_b_mac: deviceBMac,
//       device_a_vlan: deviceAVlan,
//       device_b_system_name: deviceBSystemName,
//       server_name: serverName,
//       app_name: appName,
//       service_vendor: serviceVendor,
//       fetch_date: fetchDate,
//     };

//     await axios
//       .post(baseUrl + "/exportEdnMacLegacySearched", filters)
//       .then((response) => {
//         jsonToExcel(response.data, "ednmaclegacySearched.xlsx");
//         console.log(response);
//         setExportLoading(false);
//       })
//       .catch((error) => {
//         setExportLoading(false);
//         console.log(error);
//       });
//   };

//   const jsonToExcel = (seedData, fileName) => {
//     let wb = XLSX.utils.book_new();
//     let binarySeedData = XLSX.utils.json_to_sheet(seedData);
//     XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
//     XLSX.writeFile(wb, fileName);
//     setExportLoading(false);
//   };

//   return (
//     <>
//       <form onSubmit={handleSubmit}>
//         <Row gutter={30}>
//           <Col span={12}>
//             <InputWrapper>
//               Device A Name:
//               {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
//               &nbsp;&nbsp;
//               <StyledInput
//                 value={deviceAName}
//                 onChange={(e) => setDeviceAName(e.target.value)}
//                 // required
//               />
//             </InputWrapper>
//             <InputWrapper>
//               Device A Ip:
//               {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
//               &nbsp;&nbsp;
//               <StyledInput
//                 value={deviceAIp}
//                 onChange={(e) => setDeviceAIp(e.target.value)}
//                 // required
//               />
//             </InputWrapper>
//             <InputWrapper>
//               Device B System Name: &nbsp;&nbsp;
//               <StyledInput
//                 value={deviceBSystemName}
//                 onChange={(e) => setDeviceBSystemName(e.target.value)}
//               />
//             </InputWrapper>
//             <InputWrapper>
//               Device B Ip: &nbsp;&nbsp;
//               <StyledInput
//                 value={deviceBIp}
//                 onChange={(e) => setDeviceBIp(e.target.value)}
//                 // required
//               />
//             </InputWrapper>
//             <InputWrapper>
//               Device B Mac: &nbsp;&nbsp;
//               <StyledInput
//                 value={deviceBMac}
//                 onChange={(e) => setDeviceBMac(e.target.value)}
//               />
//             </InputWrapper>
//           </Col>
//           <Col span={12}>
//             <InputWrapper>
//               Device A Vlan:&nbsp;&nbsp;
//               <StyledInput
//                 value={deviceAVlan}
//                 onChange={(e) => setDeviceAVlan(e.target.value)}
//                 // required
//               />
//             </InputWrapper>
//             <InputWrapper>
//               Server Name: &nbsp;&nbsp;
//               <StyledInput
//                 value={serverName}
//                 onChange={(e) => setServerName(e.target.value)}
//               />
//             </InputWrapper>
//             <InputWrapper>
//               App Name: &nbsp;&nbsp;
//               <StyledInput
//                 value={appName}
//                 onChange={(e) => setAppName(e.target.value)}
//               />
//             </InputWrapper>
//             <InputWrapper>
//               Service Vendor: &nbsp;&nbsp;
//               <StyledInput
//                 value={serviceVendor}
//                 onChange={(e) => setServiceVendor(e.target.value)}
//               />
//             </InputWrapper>
//             <InputWrapper>
//               Fetch Date: &nbsp;&nbsp;
//               <Select
//                 defaultValue={props.dates?.length > 0 ? props.dates[0] : null}
//                 style={{ width: "100%" }}
//                 onChange={handleSelectChange}
//                 // value={fetchDate}
//                 // disabled={user?.user_role === roles.user}
//               >
//                 {getOptions(props.dates)}
//               </Select>
//             </InputWrapper>
//           </Col>
//           <Col span={24} style={{ textAlign: "center" }}>
//             <StyledButton color={"red"} onClick={handleCancel}>
//               Clear
//             </StyledButton>
//             &nbsp; &nbsp;{" "}
//             <StyledSubmitButton color={"green"} type="submit" value="Search" />
//           </Col>
//         </Row>
//       </form>
//     </>
//   );
// });

// const StyledInput = styled(Input)`
//   height: 1.6rem;
// `;

// const InputWrapper = styled.div`
//   font-size: 12px;
//   white-space: nowrap;
//   display: flex;
//   justify-content: space-between;
//   padding-bottom: 10px;
// `;

// const StyledSubmitButton = styled(Input)`
//   font-size: 11px;
//   font-weight: bolder;
//   width: 15%;
//   font-family: Montserrat-Regular;
//   box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
//   background-color: ${(props) => props.color};
//   border-color: ${(props) => props.color};
//   color: white;
//   border-radius: 5px;
//   &:focus,
//   &:hover {
//     background-color: ${(props) => props.color};
//     border-color: ${(props) => props.color};
//     color: white;
//     opacity: 0.8;
//   }
// `;

// const StyledButton = styled(Button)`
//   height: 27px;
//   font-size: 11px;
//   font-weight: bolder;
//   width: 15%;
//   font-family: Montserrat-Regular;
//   box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
//   background-color: ${(props) => props.color};
//   border-color: ${(props) => props.color};
//   color: white;
//   border-radius: 5px;
//   &:focus,
//   &:hover {
//     background-color: ${(props) => props.color};
//     border-color: ${(props) => props.color};
//     color: white;
//     opacity: 0.8;
//   }
// `;

// export default AddDeviceModal;
