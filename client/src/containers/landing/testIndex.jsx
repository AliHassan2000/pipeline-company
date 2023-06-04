// import React, { useEffect, useState, useRef } from "react";
// import axios, { baseUrl } from "../../utils/axios";
// import { Menu, Row, Col, Dropdown } from "antd";
// import { Route, Switch, useLocation, useHistory } from "react-router-dom";
// import {
//   HomeOutlined,
//   CalendarOutlined,
//   DatabaseOutlined,
//   ToolOutlined,
//   WalletOutlined,
//   FolderAddOutlined,
//   TeamOutlined,
//   UserOutlined,
// } from "@ant-design/icons";
// import Home from "../home";
// import Seed from "../seed";
// import Onboard from "../onBoard";
// import DataCenters from "../Inventory/dataCenters";
// import Racks from "../Inventory/racks";
// import Devices from "../Inventory/devices";
// import Boards from "../Inventory/boards";
// import SubBoards from "../Inventory/subBoards";
// import SFPs from "../Inventory/sfps";
// import Licenses from "../Inventory/licenses";
// import Operations from "../operations";
// import EdnServiceMapping from "../ednServiceMapping";
// import EdnNeList from "../ednNodeList/ednNeList";
// import EdnSecList from "../ednNodeList/ednSecList";
// import EdnItList from "../ednNodeList/ednItList";
// import SNTC from "../sntc";
// import StaticOnboarding from "../staticOnboarding";
// import EDNToMPLS from "../physicalMapping/EDNMPLS";
// import EDNIPT from "../physicalMapping/EDNIPT";
// import EDNSystems from "../physicalMapping/EDNSystems";
// import IGWSystems from "../physicalMapping/IGWSystems";
// import Security from "../physicalMapping/EDNSecurity";
// import EDNCDPLegacy from "../physicalMapping/EDN/cdpLegacy";
// import EDNLLDPLegacy from "../physicalMapping/EDN/lldpLegacy";
// import EDNMACLegacy from "../physicalMapping/EDN/macLegacy";
// import EDNMACLegacySearch from "../physicalMapping/EDN/macLegacySearch";
// import EDNLLDPACI from "../physicalMapping/EDN/lldpAci";
// import EDNARP from "../physicalMapping/EDN/firewallARP";
// import EDNServices from "../physicalMapping/EDNServices";
// import IGWServices from "../physicalMapping/IGWServices";
// import IGWLinks from "../physicalMapping/IGWLinks";
// import IGWACI from "../physicalMapping/IGW/lldpAci";
// import IGWCDPLegacy from "../physicalMapping/IGW/cdpLegacy";
// import IGWLLDPLegacy from "../physicalMapping/IGW/lldpLegacy";
// import IGWMACLegacy from "../physicalMapping/IGW/macLegacy";
// import EDNMaster from "../physicalMapping/EDNMaster";
// import IGWMaster from "../physicalMapping/IGWMaster";
// import EDNIPAM from "../IPAM/EDNIPAM";
// import EDNIPAMDashboard from "../IPAM/EDNDashboard";
// import IGWIPAMDashboard from "../IPAM/IGWDashboard";
// import IGWIPAM from "../IPAM/IGWIPAM";
// import PNCodeStats from "../pnCodeStats";
// import AddMember from "../admin/addMember";
// import IPTDashboard from "../IPT/IPTDashboard";
// import IPTEndpoints from "../IPT/IPTEndpoints";
// import AccessPoints from "../accessPoints";
// import EDNNetDashboard from "../dashboards/ednNet";
// import IGWNETDashboard from "../dashboards/igwNet";
// import EDNSYSDashboard from "../dashboards/ednSys";
// import IGWSysDashboard from "../dashboards/igwSys";
// import SOCDashboard from "../dashboards/soc";
// import IPTExec from "../physicalMapping/IPTExec";
// import DCEDN from "../dcCapacity/EDN";
// import DCIGW from "../dcCapacity/IGW";
// import DCEDNDashboard from "../dcCapacity/EDNDashboard";
// import DCIGWDashboard from "../dcCapacity/IGWDashboard";
// import REBD from "../Inventory/rebd";
// import IOSTRACKER from "../Inventory/Tracker/EDN/iosTracker/iosTracker.jsx";
// import POS from "../Inventory/pos";
// import FUNCTION from "../Inventory/functions";
// import Domains from "../Inventory/domains";
// import CDN from "../cdn";
// import Power from "../powerfeeds";
// import UpdatePanel from "../admin/updatePanel";
// import DeletePanel from "../admin/deletePanel";
// import EDNIPAMFailedDevices from "../admin/failedDevices/ipam/edn";
// import IGWIPAMFailedDevices from "../admin/failedDevices/ipam/igw";
// import AccessPointsFailedDevices from "../admin/failedDevices/accessPoints";
// import EDNDCCapacityFailedDevices from "../admin/failedDevices/dcCapacity/edn";
// import IGWDCCapacityFailedDevices from "../admin/failedDevices/dcCapacity/igw";
// import EDNExchangeFailedDevices from "../admin/failedDevices/ednExchange";
// import InventoryFailedDevices from "../admin/failedDevices/inventory";
// import IPTEndpointsFailedDevices from "../admin/failedDevices/iptEndpoints";
// import EDNPhysicalMappingFailedDevices from "../admin/failedDevices/physicalMapping/edn";
// import IGWPhysicalMappingFailedDevices from "../admin/failedDevices/physicalMapping/igw";
// import EDNPhysicalMappingCDPLegacyFailedDevices from "../admin/failedDevices/physicalMapping/edn/cdpLegacy";
// import EDNPhysicalMappingFirewallARPFailedDevices from "../admin/failedDevices/physicalMapping/edn/firewallARP";
// import EDNPhysicalMappingLLDPFailedDevices from "../admin/failedDevices/physicalMapping/edn/lldp";
// import EDNPhysicalMappingMACFailedDevices from "../admin/failedDevices/physicalMapping/edn/mac";

// import IGWPhysicalMappingCDPLegacyFailedDevices from "../admin/failedDevices/physicalMapping/igw/cdpLegacy";
// import IGWPhysicalMappingLLDPFailedDevices from "../admin/failedDevices/physicalMapping/igw/lldp";
// import IGWPhysicalMappingMACFailedDevices from "../admin/failedDevices/physicalMapping/igw/mac";
// import F5FailedDevices from "../admin/failedDevices/f5";

// import EDNVulnerabilityDashboard from "../vulnerability/edn/dashboard";
// import EDNVulnerabilityMaster from "../vulnerability/edn/master";
// import EDNVulnerabilityClosed from "../vulnerability/edn/closed";
// import EDNVulnerabilityNotFoundDevices from "../vulnerability/edn/notFoundDevices";
// import EDNVulnerabilityNoPlanDevices from "../vulnerability/edn/noPlanDevices";
// import EDNVulnerabilityInProgress from "../vulnerability/edn/inprogress";
// import EDNVulnerabilityManagedBy from "../vulnerability/edn/managedby";
// import EDNVulnerabilityOpen from "../vulnerability/edn/open";
// import EDNVulnerabilityOverdue from "../vulnerability/edn/overdue";

// import IGWVulnerabilityDashboard from "../vulnerability/igw/dashboard";
// import IGWVulnerabilityMaster from "../vulnerability/igw/master";
// import IGWVulnerabilityArcher from "../vulnerability/igw/archer";
// import IGWVulnerabilityNotFoundDevices from "../vulnerability/igw/notFoundDevices";
// import IGWVulnerabilityNoPlanDevices from "../vulnerability/igw/noPlanDevices";

// import { NavIcons } from "../navIcons";
// import { StyledImage } from "../../components/image/main.styles";
// import Logo from "../../resources/img2.png";
// import ServiceMappingLogo from "../../resources/serviceMappingLogo.png";
// import {
//   StyledBar,
//   StyledLogoLink,
//   StyledBodyCol,
//   StyledLink,
//   StyledMenuColumn,
//   StyledSubMenu,
//   StyledMenuItem,
//   StyledUserNameContainer,
//   StyledMenu,
//   StyledLogoutMenuItem,
// } from "../landing/styles/main.styles";
// import { roles } from "../../utils/constants.js";
// import CPModal from "./cPModal";
// import EDNExchangeDashboard from "../ednExchanges/dashboard";
// import EDNExchange from "../ednExchanges/exchange";
// import VRFOwners from "../ednExchanges/vrfOwners";
// import ReceivedRoutes from "../ednExchanges/receivedRoutes";
// import ServiceMappingDashboard from "../physicalMapping/dashboards/serviceMapping";
// import PhysicalServers from "../itServiceMapping/physicalServers";
// import App from "../itServiceMapping/app";
// import Os from "../itServiceMapping/os";
// import Mac from "../itServiceMapping/mac";
// import Ip from "../itServiceMapping/ip";
// import Owner from "../itServiceMapping/owner";
// import IPTAssignmentTracker from "../trackers/iptAssignmentTracker";
// import IPTClearanceTracker from "../trackers/iptClearanceTracker";
// import EDNPowerOffTracker from "../trackers/ednPowerOffTracker";
// import EDNHandbackTracker from "../trackers/ednHandbackTracker";
// import EDNHandoverTracker from "../trackers/ednHandoverTracker";
// import PMRTracker from "../trackers/pmrTracker";
// import IPTRMATracker from "../IPT/RMATracker";
// import Snags from "../trackers/snags";
// import F5 from "../f5";
// import F5Dashboard from "../f5/dashboard";

// let userInfo = JSON.parse(localStorage.getItem("user"));

// const Index = (props) => {
//   useEffect(() => {
//     setUser(JSON.parse(localStorage.getItem("user")));
//   }, []);

//   console.log("ye cheez", userInfo);
//   const location = useLocation();
//   const history = useHistory();
//   const [user, setUser] = useState();
//   const [showCPModal, setShowCPModal] = useState(false);
//   const [module, setModule] = useState(
//     localStorage.getItem("module")
//       ? localStorage.getItem("module")
//       : userInfo?.user_role === roles?.ednSM
//       ? "physicalmapping"
//       : "inventorymodule"
//   );

//   let barColor =
//     baseUrl === "https://localhost:5000"
//       ? "orange"
//       : userInfo?.user_role === roles?.ednSM
//       ? "#2d5918"
//       : "#009bdb";

//   return (
//     <>
//       <StyledBar
//         style={{ position: "fixed", zIndex: "999", backgroundColor: barColor }}
//       >
//         <StyledLogoLink to="/">
//           <StyledImage
//             src={user?.user_role === roles.ednSM ? ServiceMappingLogo : Logo}
//           ></StyledImage>
//         </StyledLogoLink>
//         <div
//           style={{
//             display: "flex",
//             justifyContent: "center",
//             // border: "1px solid black",
//             width: "55%",
//           }}
//         >
//           <StyledMenu
//             user={user?.user_role}
//             // style={{ float: "center" }}
//             selectedKeys={[`${module}`]}
//             mode="horizontal"
//             inlineCollapsed={false}
//           >
//             {user?.user_role !== roles.ednSM ? (
//               <>
//                 <StyledMenuItem
//                   key="inventorymodule"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("inventorymodule");
//                     localStorage.setItem("module", "inventorymodule");
//                     history.push("/");
//                   }}
//                 >
//                   Inventory
//                 </StyledMenuItem>
//                 <StyledMenuItem
//                   key="dccapacity"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("dccapacity");
//                     localStorage.setItem("module", "dccapacity");
//                     history.push("/dccapacityedndashboard");
//                   }}
//                 >
//                   DC Capacity
//                 </StyledMenuItem>
//                 <StyledMenuItem
//                   key="ipam"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("ipam");
//                     localStorage.setItem("module", "ipam");
//                     history.push("/ednipamdashboard");
//                   }}
//                 >
//                   IPAM
//                 </StyledMenuItem>
//                 <StyledMenuItem
//                   key="ednexchanges"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("ednexchanges");
//                     localStorage.setItem("module", "ednexchanges");
//                     history.push("/ednexchangedashboard");
//                   }}
//                 >
//                   EDN Exchange
//                 </StyledMenuItem>
//                 <StyledMenuItem
//                   key="physicalmapping"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("physicalmapping");
//                     localStorage.setItem("module", "physicalmapping");
//                     console.log("edn sm tag ===>");
//                     console.log(user, roles);
//                     history.push("/ednmaster");
//                   }}
//                 >
//                   Physical Mapping
//                 </StyledMenuItem>
//                 <StyledMenuItem
//                   key="f5"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("f5");
//                     localStorage.setItem("module", "f5");
//                     console.log("edn sm tag ===>");
//                     console.log(user, roles);
//                     history.push("/f5dashboard");
//                   }}
//                 >
//                   F5
//                 </StyledMenuItem>
//               </>
//             ) : null}

//             {user?.user_role === roles.ednSM ? (
//               <>
//                 <StyledMenuItem
//                   key="physicalmapping"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("physicalmapping");
//                     localStorage.setItem("module", "physicalmapping");
//                     history.push("/");
//                   }}
//                 >
//                   EDN
//                 </StyledMenuItem>
//                 <StyledMenuItem
//                   key="igwsm"
//                   // icon={<HomeOutlined />}
//                   // onClick={() => {
//                   //   setModule("igwsm");
//                   //   localStorage.setItem("module", "igwsm");
//                   //   history.push("/ednmaclegacy");
//                   // }}
//                 >
//                   IGW
//                 </StyledMenuItem>
//               </>
//             ) : null}
//             {user?.user_role !== roles.ednSM ? (
//               <>
//                 <StyledMenuItem
//                   key="ipt"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("ipt");
//                     localStorage.setItem("module", "ipt");
//                     history.push("/iptdashboard");
//                   }}
//                 >
//                   IPT Endpoints
//                 </StyledMenuItem>
//                 <StyledMenuItem
//                   key="accesspointsmodule"
//                   // icon={<HomeOutlined />}
//                   onClick={() => {
//                     setModule("accesspointsmodule");
//                     localStorage.setItem("module", "accesspointsmodule");
//                     history.push("/accesspoints");
//                   }}
//                 >
//                   Access Points
//                 </StyledMenuItem>
//                 {user?.user_role === roles.admin ? (
//                   <StyledMenuItem
//                     key="admin"
//                     // icon={<HomeOutlined />}
//                     onClick={() => {
//                       setModule("admin");
//                       localStorage.setItem("module", "admin");
//                       history.push("/addmember");
//                     }}
//                   >
//                     Admin
//                   </StyledMenuItem>
//                 ) : null}
//               </>
//             ) : null}
//           </StyledMenu>
//         </div>
//         <NavIcons setShowCPModal={setShowCPModal} />
//       </StyledBar>
//       <StyledBar />
//       <Row>
//         <StyledMenuColumn
//           xs={{ span: 4 }}
//           md={{ span: 4 }}
//           lg={{ span: 4 }}
//           xl={{ span: 4 }}
//         >
//           <StyledMenu
//             user={user?.user_role}
//             defaultSelectedKeys={["/"]}
//             selectedKeys={[`/${location.pathname.split("/")[1]}`]}
//             mode="inline"
//             inlineCollapsed={false}
//           >
//             {module === "inventorymodule" ? (
//               <>
//                 <StyledMenuItem
//                   key="/"
//                   icon={<HomeOutlined />}
//                   onClick={() => history.push("/")}
//                 >
//                   Home
//                 </StyledMenuItem>
//                 {user?.user_role !== roles.executive ? (
//                   <>
//                     {user?.user_role !== roles.user ? (
//                       <>
//                         <StyledMenuItem
//                           key="/seed"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/seed")}
//                         >
//                           Seed Devices
//                         </StyledMenuItem>
//                         {/* <StyledMenuItem
//                       key="/staticonboarding"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/staticonboarding")}
//                     >
//                       Static Onboarding
//                     </StyledMenuItem> */}
//                       </>
//                     ) : null}

//                     <StyledSubMenu
//                       user={user?.user_role}
//                       style={{ color: "white" }}
//                       key="sub1"
//                       icon={<DatabaseOutlined />}
//                       title="Inventory"
//                     >
//                       <StyledMenuItem
//                         key="/powerfeeds"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/powerfeeds")}
//                       >
//                         Power Feeds
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/sntc"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/sntc")}
//                       >
//                         SNTC
//                       </StyledMenuItem>
//                       {/* <StyledMenuItem
//                         key="/iptendpoints"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/iptendpoints")}
//                       >
//                         IPT Endpoints
//                       </StyledMenuItem> */}
//                       <StyledMenuItem
//                         key="/cdn"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/cdn")}
//                       >
//                         CDN
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/sites"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/sites")}
//                       >
//                         Sites
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/racks"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/racks")}
//                       >
//                         Racks
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/devices"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/devices")}
//                       >
//                         Devices
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/boards"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/boards")}
//                       >
//                         Boards
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/subboards"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/subboards")}
//                       >
//                         SubBoards
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/sfps"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/sfps")}
//                       >
//                         SFPs
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/licenses"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/licenses")}
//                       >
//                         Licenses
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/rebd"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/rebd")}
//                       >
//                         REBD
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/pos"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/pos")}
//                       >
//                         POS
//                       </StyledMenuItem>
//                       {user?.user_role === roles.admin ? (
//                         <>
//                           <StyledMenuItem
//                             key="/functions"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/functions")}
//                           >
//                             Functions
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/domains"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/domains")}
//                           >
//                             Domains
//                           </StyledMenuItem>
//                         </>
//                       ) : null}
//                     </StyledSubMenu>

//                     <StyledSubMenu
//                       user={user?.user_role}
//                       style={{ color: "white" }}
//                       key="sub3-2"
//                       icon={<DatabaseOutlined />}
//                       title="Trackers"
//                     >
//                       <StyledSubMenu
//                         style={{ color: "white" }}
//                         key="itservicemapping"
//                         icon={<DatabaseOutlined />}
//                         title="EDN"
//                       >
//                         <StyledMenuItem
//                           key="/iostracker"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/iostracker")}
//                         >
//                           IOS Tracker
//                         </StyledMenuItem>
//                         <StyledMenuItem
//                           key="/ednpowerofftracker"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/ednpowerofftracker")}
//                         >
//                           Power Off Tracker
//                         </StyledMenuItem>
//                         <StyledMenuItem
//                           key="/ednhandbacktracker"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/ednhandbacktracker")}
//                         >
//                           Handback Tracker
//                         </StyledMenuItem>
//                         <StyledMenuItem
//                           key="/ednhandovertracker"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/ednhandovertracker")}
//                         >
//                           Handover Tracker
//                         </StyledMenuItem>
//                         <StyledMenuItem
//                           key="/pmrtracker"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/pmrtracker")}
//                         >
//                           PMR Tracker
//                         </StyledMenuItem>
//                         <StyledMenuItem
//                           key="/snags"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/snags")}
//                         >
//                           Snags
//                         </StyledMenuItem>
//                       </StyledSubMenu>
//                     </StyledSubMenu>

//                     <StyledMenuItem
//                       key="/onboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/onboard")}
//                     >
//                       OnBoarded Devices
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/pncodestats"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/pncodestats")}
//                     >
//                       PN Code Stats
//                     </StyledMenuItem>
//                   </>
//                 ) : null}
//                 {/* //----------------------------------------------------------------------- */}

//                 <StyledSubMenu
//                   style={{ color: "white" }}
//                   key="dashboards"
//                   icon={<DatabaseOutlined />}
//                   title="Dashboards"
//                 >
//                   <StyledMenuItem
//                     key="/ednnetdashboard"
//                     icon={<WalletOutlined />}
//                     onClick={() => history.push("/ednnetdashboard")}
//                   >
//                     EDN Net
//                   </StyledMenuItem>
//                   <StyledMenuItem
//                     key="/igwnetdashboard"
//                     icon={<WalletOutlined />}
//                     onClick={() => history.push("/igwnetdashboard")}
//                   >
//                     IGW Net
//                   </StyledMenuItem>
//                   <StyledMenuItem
//                     key="/ednsysdashboard"
//                     icon={<WalletOutlined />}
//                     onClick={() => history.push("/ednsysdashboard")}
//                   >
//                     EDN Sys
//                   </StyledMenuItem>
//                   <StyledMenuItem
//                     key="/igwsysdashboard"
//                     icon={<WalletOutlined />}
//                     onClick={() => history.push("/igwsysdashboard")}
//                   >
//                     IGW Sys
//                   </StyledMenuItem>
//                   <StyledMenuItem
//                     key="/socdashboard"
//                     icon={<WalletOutlined />}
//                     onClick={() => history.push("/socdashboard")}
//                   >
//                     SOC
//                   </StyledMenuItem>
//                 </StyledSubMenu>
//                 <StyledSubMenu
//                   style={{ color: "white" }}
//                   key="vulnerability"
//                   icon={<DatabaseOutlined />}
//                   title="Vulnerability"
//                 >
//                   <StyledSubMenu
//                     style={{ color: "white" }}
//                     key="ednvulnerability"
//                     icon={<DatabaseOutlined />}
//                     title="EDN"
//                   >
//                     <StyledMenuItem
//                       key="/ednvulnerabilitydashboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednvulnerabilitydashboard")}
//                     >
//                       Dashboard
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/ednvulnerabilitymaster"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednvulnerabilitymaster")}
//                     >
//                       Master
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/ednvulnerabilityarcher"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednvulnerabilityarcher")}
//                     >
//                       Archer
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/ednvulnerabilitynotfounddevices"
//                       icon={<WalletOutlined />}
//                       onClick={() =>
//                         history.push("/ednvulnerabilitynotfounddevices")
//                       }
//                     >
//                       Not Found Devices
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/ednvulnerabilitynoplandevices"
//                       icon={<WalletOutlined />}
//                       onClick={() =>
//                         history.push("/ednvulnerabilitynoplandevices")
//                       }
//                     >
//                       No Plan Devices
//                     </StyledMenuItem>
//                     {/* <StyledMenuItem
//                       key="/ednvulnerabilityinprogress"
//                       icon={<WalletOutlined />}
//                       onClick={() =>
//                         history.push("/ednvulnerabilityinprogress")
//                       }
//                     >
//                       Inprogress
//                     </StyledMenuItem>
//                      <StyledMenuItem
//                       key="/ednvulnerabilitymanagedby"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednvulnerabilitymanagedby")}
//                     >
//                       Managedby
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/ednvulnerabilityopen"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednvulnerabilityopen")}
//                     >
//                       Open
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/ednvulnerabilityoverdue"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednvulnerabilityoverdue")}
//                     >
//                       Overdue
//                     </StyledMenuItem> */}
//                   </StyledSubMenu>
//                   <StyledSubMenu
//                     style={{ color: "white", paddingBottom: "500px" }}
//                     key="igwvulnerability"
//                     icon={<DatabaseOutlined />}
//                     title="IGW"
//                   >
//                     <StyledMenuItem
//                       key="/igwvulnerabilitydashboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/igwvulnerabilitydashboard")}
//                     >
//                       Dashboard
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/igwvulnerabilitymaster"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/igwvulnerabilitymaster")}
//                     >
//                       Master
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/igwvulnerabilityarcher"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/igwvulnerabilityarcher")}
//                     >
//                       Archer
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/igwvulnerabilitynotfounddevices"
//                       icon={<WalletOutlined />}
//                       onClick={() =>
//                         history.push("/igwvulnerabilitynotfounddevices")
//                       }
//                     >
//                       Not Found Devices
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/igwvulnerabilitynoplandevices"
//                       icon={<WalletOutlined />}
//                       onClick={() =>
//                         history.push("/igwvulnerabilitynoplandevices")
//                       }
//                     >
//                       No Plan Devices
//                     </StyledMenuItem>
//                   </StyledSubMenu>
//                 </StyledSubMenu>
//               </>
//             ) : null}

//             {module === "accesspointsmodule" ? (
//               <>
//                 <StyledMenuItem
//                   key="/accesspoints"
//                   icon={<WalletOutlined />}
//                   onClick={() => history.push("/accesspoints")}
//                 >
//                   Access Points
//                 </StyledMenuItem>
//               </>
//             ) : null}

//             {module === "f5" ? (
//               <>
//                 <StyledMenuItem
//                   key="/f5dashboard"
//                   icon={<WalletOutlined />}
//                   onClick={() => history.push("/f5dashboard")}
//                 >
//                   F5 Dashboard
//                 </StyledMenuItem>
//                 <StyledMenuItem
//                   key="/f5"
//                   icon={<WalletOutlined />}
//                   onClick={() => history.push("/f5")}
//                 >
//                   F5
//                 </StyledMenuItem>
//               </>
//             ) : null}

//             {module === "ipt" ? (
//               <>
//                 {user?.user_role !== roles.executive ? (
//                   <>
//                     <StyledMenuItem
//                       key="/iptdashboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/iptdashboard")}
//                     >
//                       IPT Dashboard
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/iptendpoints"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/iptendpoints")}
//                     >
//                       IPT Endpoints
//                     </StyledMenuItem>
//                     <StyledSubMenu
//                       style={{ color: "white" }}
//                       key="trackers"
//                       icon={<DatabaseOutlined />}
//                       title="Trackers"
//                     >
//                       <StyledMenuItem
//                         key="/iptassignmenttracker"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/iptassignmenttracker")}
//                       >
//                         IPT Assignment Tracker
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/iptclearancetracker"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/iptclearancetracker")}
//                       >
//                         IPT Clearance Tracker
//                       </StyledMenuItem>
//                       <StyledMenuItem
//                         key="/iptrmatracker"
//                         icon={<WalletOutlined />}
//                         onClick={() => history.push("/iptrmatracker")}
//                       >
//                         IPT RMA Tracker
//                       </StyledMenuItem>
//                     </StyledSubMenu>
//                   </>
//                 ) : null}
//               </>
//             ) : null}

//             {/* ---------------------------------------------------------------- */}
//             {module === "dccapacity" ? (
//               <>
//                 {!(user?.user_role === roles.executive) ? (
//                   <>
//                     {/* <StyledSubMenu
//                       style={{ color: "white" }}
//                       key="subDcCapacity"
//                       icon={<DatabaseOutlined />}
//                       title="DC Capacity"
//                     > */}
//                     <StyledMenuItem
//                       key="/dccapacityedndashboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/dccapacityedndashboard")}
//                     >
//                       EDN Dashboard
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/dccapacityigwdashboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/dccapacityigwdashboard")}
//                     >
//                       IGW Dashboard
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/dccapacityedn"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/dccapacityedn")}
//                     >
//                       EDN
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/dccapacityigw"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/dccapacityigw")}
//                     >
//                       IGW
//                     </StyledMenuItem>
//                     {/* </StyledSubMenu> */}
//                   </>
//                 ) : null}
//               </>
//             ) : null}
//             {module === "ipam" ? (
//               <>
//                 {!(user?.user_role === roles.executive) ? (
//                   <>
//                     {/* <StyledSubMenu
//                       style={{ color: "white" }}
//                       key="subIpam"
//                       icon={<DatabaseOutlined />}
//                       title="IPAM"
//                     > */}
//                     <StyledMenuItem
//                       key="/ednipamdashboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednipamdashboard")}
//                     >
//                       EDN Dashboard
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/igwipamdashboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/igwipamdashboard")}
//                     >
//                       IGW Dashboard
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/ednipam"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednipam")}
//                     >
//                       EDN
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/igwipam"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/igwipam")}
//                     >
//                       IGW
//                     </StyledMenuItem>
//                     {/* </StyledSubMenu> */}
//                   </>
//                 ) : null}
//               </>
//             ) : null}

//             {module === "ednexchanges" ? (
//               <>
//                 {!(user?.user_role === roles.executive) ? (
//                   <>
//                     <StyledMenuItem
//                       key="/ednexchangedashboard"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednexchangedashboard")}
//                     >
//                       EDN Exchange Dashboard
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/ednexchange"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/ednexchange")}
//                     >
//                       EDN Exchange
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/vrfowners"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/vrfowners")}
//                     >
//                       VRF Owners
//                     </StyledMenuItem>
//                     <StyledMenuItem
//                       key="/received-routes"
//                       icon={<WalletOutlined />}
//                       onClick={() => history.push("/received-routes")}
//                     >
//                       Received Routes
//                     </StyledMenuItem>
//                   </>
//                 ) : null}
//               </>
//             ) : null}

//             {module === "physicalmapping" ? (
//               <>
//                 {user?.user_role !== roles.executive ? (
//                   <>
//                     {user?.user_role !== roles.ednSM ? (
//                       <>
//                         <StyledMenuItem
//                           key="/ednmaster"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/ednmaster")}
//                         >
//                           EDN Mapping
//                         </StyledMenuItem>
//                         <StyledMenuItem
//                           key="/igwmaster"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/igwmaster")}
//                         >
//                           IGW Mapping
//                         </StyledMenuItem>
//                       </>
//                     ) : null}
//                     <>
//                       {user?.user_role !== roles.user &&
//                       user?.user_role !== roles.ednSM ? (
//                         <>
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="sub2"
//                             icon={<DatabaseOutlined />}
//                             title="EDN Node List"
//                           >
//                             <StyledMenuItem
//                               key="/nelist"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/nelist")}
//                             >
//                               EDN NE List
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/seclist"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/seclist")}
//                             >
//                               EDN SEC List
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                         </>
//                       ) : null}
//                     </>

//                     {user?.user_role !== roles.user &&
//                     user?.user_role !== roles.ednSM ? (
//                       <>
//                         <StyledSubMenu
//                           style={{ color: "white" }}
//                           key="sub3-1"
//                           icon={<DatabaseOutlined />}
//                           title="IGW"
//                         >
//                           <StyledMenuItem
//                             key="/igwsystems"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/igwsystems")}
//                           >
//                             IGW Systems
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/igwservices"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/igwservices")}
//                           >
//                             IGW Services
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/igwlinks"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/igwlinks")}
//                           >
//                             IGW Services DB
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/igwcdplegacy"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/igwcdplegacy")}
//                           >
//                             CDP Legacy
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/igwlldplegacy"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/igwlldplegacy")}
//                           >
//                             LLDP
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/igwmaclegacy"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/igwmaclegacy")}
//                           >
//                             MAC
//                           </StyledMenuItem>
//                         </StyledSubMenu>
//                       </>
//                     ) : null}

//                     {user?.user_role !== roles.user &&
//                     user?.user_role !== roles.ednSM ? (
//                       <>
//                         <StyledSubMenu
//                           user={user?.user_role}
//                           style={{ color: "white" }}
//                           key="sub3-2"
//                           icon={<DatabaseOutlined />}
//                           title="EDN"
//                         >
//                           <StyledSubMenu
//                             user={user?.user_role}
//                             style={{ color: "white" }}
//                             key="dashboards"
//                             icon={<DatabaseOutlined />}
//                             title="Dashboards"
//                           >
//                             <StyledMenuItem
//                               key="/servicemappingdashboard"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/servicemappingdashboard")
//                               }
//                             >
//                               Service Mapping
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                           <StyledSubMenu
//                             user={user?.user_role}
//                             style={{ color: "white" }}
//                             key="itservicemapping"
//                             icon={<DatabaseOutlined />}
//                             title="IT Service Mapping"
//                           >
//                             <StyledMenuItem
//                               key="/physicalservers"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/physicalservers")}
//                             >
//                               Physical Servers
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/app"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/app")}
//                             >
//                               App
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/os"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/os")}
//                             >
//                               Os
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/mac"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/mac")}
//                             >
//                               Mac
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/ip"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/ip")}
//                             >
//                               Ip
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/owner"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/owner")}
//                             >
//                               Owner
//                             </StyledMenuItem>
//                           </StyledSubMenu>

//                           <StyledMenuItem
//                             key="/edncdplegacy"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/edncdplegacy")}
//                           >
//                             CDP Legacy
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/ednlldplegacy"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/ednlldplegacy")}
//                           >
//                             LLDP
//                           </StyledMenuItem>

//                           <StyledMenuItem
//                             key="/ednmaclegacy"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/ednmaclegacy")}
//                           >
//                             MAC
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/ednmaclegacysearch"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/ednmaclegacysearch")}
//                           >
//                             Service Mapping Search
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/ednarp"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/ednarp")}
//                           >
//                             Firewall ARP
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/edntompls"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/edntompls")}
//                           >
//                             EDN MPLS
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/ednipt"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/ednipt")}
//                           >
//                             EDN IPT
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/ednsystems"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/ednsystems")}
//                           >
//                             EDN Systems
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             key="/security"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/security")}
//                           >
//                             EDN Security
//                           </StyledMenuItem>
//                           <StyledMenuItem
//                             style={{ marginBottom: "100px" }}
//                             key="/ednservices"
//                             icon={<WalletOutlined />}
//                             onClick={() => history.push("/ednservices")}
//                           >
//                             EDN Services
//                           </StyledMenuItem>
//                         </StyledSubMenu>
//                       </>
//                     ) : (
//                       <>
//                         {user?.user_role === roles.user ? (
//                           <>
//                             <StyledMenuItem
//                               key="/edndashboard"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/edndashboard")}
//                             >
//                               EDN Dashboard
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/ednmaclegacy"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/ednmaclegacy")}
//                             >
//                               Edn Service Mapping
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/ednmaclegacyseacrh"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/ednmaclegacysearch")
//                               }
//                             >
//                               Edn Service Mapping Search
//                             </StyledMenuItem>
//                             <StyledSubMenu
//                               user={user?.user_role}
//                               style={{ color: "white" }}
//                               key="itservicemapping"
//                               icon={<DatabaseOutlined />}
//                               title="IT Service Mapping"
//                             >
//                               <StyledMenuItem
//                                 key="/physicalservers"
//                                 icon={<WalletOutlined />}
//                                 onClick={() => history.push("/physicalservers")}
//                               >
//                                 Physical Servers
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/app"
//                                 icon={<WalletOutlined />}
//                                 onClick={() => history.push("/app")}
//                               >
//                                 App
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/os"
//                                 icon={<WalletOutlined />}
//                                 onClick={() => history.push("/os")}
//                               >
//                                 Os
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/mac"
//                                 icon={<WalletOutlined />}
//                                 onClick={() => history.push("/mac")}
//                               >
//                                 Mac
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/ip"
//                                 icon={<WalletOutlined />}
//                                 onClick={() => history.push("/ip")}
//                               >
//                                 Ip
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/owner"
//                                 icon={<WalletOutlined />}
//                                 onClick={() => history.push("/owner")}
//                               >
//                                 Owner
//                               </StyledMenuItem>
//                             </StyledSubMenu>
//                           </>
//                         ) : (
//                           <>
//                             <StyledMenuItem
//                               key="/"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/")}
//                             >
//                               EDN Dashboard
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/ednmaclegacy"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/ednmaclegacy")}
//                             >
//                               Edn Service Mapping
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/ednmaclegacysearch"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/ednmaclegacysearch")
//                               }
//                             >
//                               Edn Service Mapping Search
//                             </StyledMenuItem>
//                           </>
//                         )}
//                       </>
//                     )}
//                   </>
//                 ) : null}
//               </>
//             ) : null}

//             {module === "admin" ? (
//               <>
//                 {!(user?.user_role === roles.executive) ? (
//                   <>
//                     {user?.user_role !== roles.engineer &&
//                     user?.user_role !== roles.user ? (
//                       // <StyledSubMenu
//                       //   style={{ color: "white" }}
//                       //   key="admin"
//                       //   icon={<DatabaseOutlined />}
//                       //   title="Admin"
//                       // >
//                       <>
//                         <StyledMenuItem
//                           style={{ marginBottom: "0px" }}
//                           key="/addmember"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/addmember")}
//                         >
//                           Users
//                         </StyledMenuItem>
//                         <StyledMenuItem
//                           key="/updatepanel"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/updatepanel")}
//                         >
//                           Update Panel
//                         </StyledMenuItem>
//                         <StyledMenuItem
//                           key="/deletepanel"
//                           icon={<WalletOutlined />}
//                           onClick={() => history.push("/deletepanel")}
//                         >
//                           Delete Panel
//                         </StyledMenuItem>
//                         <StyledSubMenu
//                           style={{ color: "white" }}
//                           key="faileddevices"
//                           icon={<DatabaseOutlined />}
//                           title="Failed Devices"
//                         >
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="inventoryfaileddevices"
//                             icon={<DatabaseOutlined />}
//                             title="Inventory"
//                           >
//                             <StyledMenuItem
//                               key="/inventoryfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/inventoryfaileddevices")
//                               }
//                             >
//                               Inventory
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="dccapacityfaileddevices"
//                             icon={<DatabaseOutlined />}
//                             title="DC Capacity"
//                           >
//                             <StyledMenuItem
//                               key="/edndccapacityfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/edndccapacityfaileddevices")
//                               }
//                             >
//                               EDN
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/igwdccapacityfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/igwdccapacityfaileddevices")
//                               }
//                             >
//                               IGW
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="ipamfaileddevices"
//                             icon={<DatabaseOutlined />}
//                             title="IPAM"
//                           >
//                             <StyledMenuItem
//                               key="/ednipamfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/ednipamfaileddevices")
//                               }
//                             >
//                               EDN
//                             </StyledMenuItem>
//                             <StyledMenuItem
//                               key="/igwipamfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/igwipamfaileddevices")
//                               }
//                             >
//                               IGW
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="ednexchangefaileddevices"
//                             icon={<DatabaseOutlined />}
//                             title="EDN Exchange"
//                           >
//                             <StyledMenuItem
//                               key="/ednexchangefaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/ednexchangefaileddevices")
//                               }
//                             >
//                               EDN Exchange
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="physicalmappingfaileddevices"
//                             icon={<DatabaseOutlined />}
//                             title="Physical Mapping"
//                           >
//                             {/* <StyledMenuItem
//                               key="/ednphysicalmappingfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/ednphysicalmappingfaileddevices")
//                               }
//                             >
//                               EDN
//                             </StyledMenuItem> */}
//                             <StyledSubMenu
//                               style={{ color: "white" }}
//                               key="ednphysicalmappingfaileddevices"
//                               icon={<DatabaseOutlined />}
//                               title="EDN"
//                             >
//                               <StyledMenuItem
//                                 key="/ednphysicalmappingcdplegacyfaileddevices"
//                                 icon={<WalletOutlined />}
//                                 onClick={() =>
//                                   history.push(
//                                     "/ednphysicalmappingcdplegacyfaileddevices"
//                                   )
//                                 }
//                               >
//                                 CDP Legacy
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/ednphysicalmappingfirewallarpfaileddevices"
//                                 icon={<WalletOutlined />}
//                                 onClick={() =>
//                                   history.push(
//                                     "/ednphysicalmappingfirewallarpfaileddevices"
//                                   )
//                                 }
//                               >
//                                 Firewall ARP
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/ednphysicalmappinglldpfaileddevices"
//                                 icon={<WalletOutlined />}
//                                 onClick={() =>
//                                   history.push(
//                                     "/ednphysicalmappinglldpfaileddevices"
//                                   )
//                                 }
//                               >
//                                 LLDP
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/ednphysicalmappingmacfaileddevices"
//                                 icon={<WalletOutlined />}
//                                 onClick={() =>
//                                   history.push(
//                                     "/ednphysicalmappingmacfaileddevices"
//                                   )
//                                 }
//                               >
//                                 MAC
//                               </StyledMenuItem>
//                             </StyledSubMenu>

//                             {/* <StyledMenuItem
//                               key="/igwphysicalmappingfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/igwphysicalmappingfaileddevices")
//                               }
//                             >
//                               IGW
//                             </StyledMenuItem> */}
//                             <StyledSubMenu
//                               style={{ color: "white" }}
//                               key="igwphysicalmappingfaileddevices"
//                               icon={<DatabaseOutlined />}
//                               title="IGW"
//                             >
//                               <StyledMenuItem
//                                 key="/igwphysicalmappingcdplegacyfaileddevices"
//                                 icon={<WalletOutlined />}
//                                 onClick={() =>
//                                   history.push(
//                                     "/igwphysicalmappingcdplegacyfaileddevices"
//                                   )
//                                 }
//                               >
//                                 CDP Legacy
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/igwphysicalmappinglldpfaileddevices"
//                                 icon={<WalletOutlined />}
//                                 onClick={() =>
//                                   history.push(
//                                     "/igwphysicalmappinglldpfaileddevices"
//                                   )
//                                 }
//                               >
//                                 LLDP
//                               </StyledMenuItem>
//                               <StyledMenuItem
//                                 key="/igwphysicalmappingmacfaileddevices"
//                                 icon={<WalletOutlined />}
//                                 onClick={() =>
//                                   history.push(
//                                     "/igwphysicalmappingmacfaileddevices"
//                                   )
//                                 }
//                               >
//                                 MAC
//                               </StyledMenuItem>
//                             </StyledSubMenu>
//                           </StyledSubMenu>
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="iptendpointsfaileddevices"
//                             icon={<DatabaseOutlined />}
//                             title="IPT Endpoints"
//                           >
//                             <StyledMenuItem
//                               key="/iptendpointsfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/iptendpointsfaileddevices")
//                               }
//                             >
//                               IPT Endpoints
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="f5faileddevices"
//                             icon={<DatabaseOutlined />}
//                             title="F5"
//                           >
//                             <StyledMenuItem
//                               key="/f5faileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() => history.push("/f5faileddevices")}
//                             >
//                               F5
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                           <StyledSubMenu
//                             style={{ color: "white" }}
//                             key="accesspointsfaileddevices"
//                             icon={<DatabaseOutlined />}
//                             title="Access Points"
//                           >
//                             <StyledMenuItem
//                               key="/accesspointsfaileddevices"
//                               icon={<WalletOutlined />}
//                               onClick={() =>
//                                 history.push("/accesspointsfaileddevices")
//                               }
//                             >
//                               Access Points
//                             </StyledMenuItem>
//                           </StyledSubMenu>
//                         </StyledSubMenu>
//                       </>
//                     ) : // </StyledSubMenu>
//                     null}
//                   </>
//                 ) : null}
//               </>
//             ) : null}
//           </StyledMenu>
//         </StyledMenuColumn>
//         <Col
//           xs={{ span: 4 }}
//           md={{ span: 4 }}
//           lg={{ span: 4 }}
//           xl={{ span: 4 }}
//         ></Col>
//         <StyledBodyCol
//           xs={{ span: 20 }}
//           md={{ span: 20 }}
//           lg={{ span: 20 }}
//           xl={{ span: 20 }}
//         >
//           {showCPModal ? (
//             <CPModal
//               showCPModal={showCPModal}
//               setShowCPModal={setShowCPModal}
//             />
//           ) : null}
//           {user?.user_role !== roles.ednSM ? (
//             <>
//               <Route exact path="/" component={Home} />
//               {user?.user_role !== roles.executive ? (
//                 <>
//                   <Route
//                     exact
//                     path="/physicalservers"
//                     component={PhysicalServers}
//                   />
//                   <Route exact path="/app" component={App} />
//                   <Route exact path="/os" component={Os} />
//                   <Route exact path="/mac" component={Mac} />
//                   <Route exact path="/ip" component={Ip} />
//                   <Route exact path="/owner" component={Owner} />
//                   <Route exact path="/f5" component={F5} />
//                   <Route exact path="/f5dashboard" component={F5Dashboard} />
//                   {user?.user_role !== roles.user ? (
//                     <>
//                       <Route exact path="/seed" component={Seed} />
//                       <Route
//                         exact
//                         path="/staticonboarding"
//                         component={StaticOnboarding}
//                       />
//                       <Route
//                         exact
//                         path="/servicemappingdashboard"
//                         component={ServiceMappingDashboard}
//                       />

//                       <Route exact path="/nelist" component={EdnNeList} />
//                       <Route exact path="/seclist" component={EdnSecList} />
//                       <Route exact path="/itlist" component={EdnItList} />
//                       <Route exact path="/edntompls" component={EDNToMPLS} />
//                       {/* <Route exact path="/iptexeceps" component={IPTExec} /> */}
//                       <Route exact path="/ednipt" component={EDNIPT} />
//                       <Route exact path="/igwsystems" component={IGWSystems} />
//                       <Route exact path="/ednsystems" component={EDNSystems} />
//                       <Route exact path="/security" component={Security} />
//                       <Route
//                         exact
//                         path="/edncdplegacy"
//                         component={EDNCDPLegacy}
//                       />
//                       <Route
//                         exact
//                         path="/ednlldplegacy"
//                         component={EDNLLDPLegacy}
//                       />
//                       <Route
//                         exact
//                         path="/igwlldplegacy"
//                         component={IGWLLDPLegacy}
//                       />

//                       {/* <Route
//                         exact
//                         path="/ednmaclegacy"
//                         component={EDNMACLegacy}
//                       /> */}
//                       {/* <Route exact path="/ednlldpaci" component={EDNLLDPACI} /> */}
//                       <Route exact path="/ednarp" component={EDNARP} />
//                       {/* <Route exact path="/igwaci" component={IGWACI} /> */}
//                       <Route
//                         exact
//                         path="/igwcdplegacy"
//                         component={IGWCDPLegacy}
//                       />
//                       <Route
//                         exact
//                         path="/igwmaclegacy"
//                         component={IGWMACLegacy}
//                       />

//                       <Route
//                         exact
//                         path="/ednservices"
//                         component={EDNServices}
//                       />
//                       <Route
//                         exact
//                         path="/igwservices"
//                         component={IGWServices}
//                       />
//                       <Route exact path="/igwlinks" component={IGWLinks} />
//                       {/* //////////////////// */}
//                       <Route
//                         exact
//                         path="/ednvulnerabilitydashboard"
//                         component={EDNVulnerabilityDashboard}
//                       />
//                       <Route
//                         exact
//                         path="/ednvulnerabilitymaster"
//                         component={EDNVulnerabilityMaster}
//                       />
//                       <Route
//                         exact
//                         path="/ednvulnerabilityarcher"
//                         component={EDNVulnerabilityClosed}
//                       />
//                       <Route
//                         exact
//                         path="/ednvulnerabilitynotfounddevices"
//                         component={EDNVulnerabilityNotFoundDevices}
//                       />
//                       <Route
//                         exact
//                         path="/ednvulnerabilitynoplandevices"
//                         component={EDNVulnerabilityNoPlanDevices}
//                       />
//                       <Route
//                         exact
//                         path="/ednvulnerabilityinprogress"
//                         component={EDNVulnerabilityInProgress}
//                       />
//                       <Route
//                         exact
//                         path="/ednvulnerabilitymanagedby"
//                         component={EDNVulnerabilityManagedBy}
//                       />
//                       <Route
//                         exact
//                         path="/ednvulnerabilityopen"
//                         component={EDNVulnerabilityOpen}
//                       />
//                       <Route
//                         exact
//                         path="/ednvulnerabilityoverdue"
//                         component={EDNVulnerabilityOverdue}
//                       />
//                       {/* ////////////////////////////// */}
//                       <Route
//                         exact
//                         path="/igwvulnerabilitydashboard"
//                         component={IGWVulnerabilityDashboard}
//                       />
//                       <Route
//                         exact
//                         path="/igwvulnerabilitymaster"
//                         component={IGWVulnerabilityMaster}
//                       />
//                       <Route
//                         exact
//                         path="/igwvulnerabilityarcher"
//                         component={IGWVulnerabilityArcher}
//                       />
//                       <Route
//                         exact
//                         path="/igwvulnerabilitynotfounddevices"
//                         component={IGWVulnerabilityNotFoundDevices}
//                       />
//                       <Route
//                         exact
//                         path="/igwvulnerabilitynoplandevices"
//                         component={IGWVulnerabilityNoPlanDevices}
//                       />
//                       {/* //////////////////// */}
//                     </>
//                   ) : null}
//                   {user?.user_role !== roles.executive ? (
//                     <>
//                       <Route exact path="/dccapacityigw" component={DCIGW} />
//                       <Route exact path="/dccapacityedn" component={DCEDN} />
//                       <Route
//                         exact
//                         path="/dccapacityedndashboard"
//                         component={DCEDNDashboard}
//                       />
//                       <Route
//                         exact
//                         path="/dccapacityigwdashboard"
//                         component={DCIGWDashboard}
//                       />
//                       <Route exact path="/ednipam" component={EDNIPAM} />
//                       <Route
//                         exact
//                         path="/ednipamdashboard"
//                         component={EDNIPAMDashboard}
//                       />
//                       <Route exact path="/igwipam" component={IGWIPAM} />
//                       <Route
//                         exact
//                         path="/igwipamdashboard"
//                         component={IGWIPAMDashboard}
//                       />
//                     </>
//                   ) : null}
//                   <Route exact path="/ednmaster" component={EDNMaster} />
//                   <Route exact path="/igwmaster" component={IGWMaster} />

//                   <Route exact path="/onboard" component={Onboard} />
//                   <Route exact path="/sites" component={DataCenters} />
//                   <Route exact path="/sntc" component={SNTC} />
//                   <Route exact path="/racks" component={Racks} />
//                   <Route exact path="/rebd" component={REBD} />
//                   <Route exact path="/iostracker" component={IOSTRACKER} />
//                   <Route exact path="/pos" component={POS} />
//                   {user?.user_role === roles.admin ? (
//                     <>
//                       <Route exact path="/functions" component={FUNCTION} />
//                       <Route exact path="/domains" component={Domains} />
//                     </>
//                   ) : null}
//                   <Route exact path="/devices" component={Devices} />
//                   <Route exact path="/boards" component={Boards} />
//                   <Route exact path="/subboards" component={SubBoards} />
//                   <Route exact path="/sfps" component={SFPs} />
//                   <Route exact path="/licenses" component={Licenses} />
//                   <Route exact path="/edn" component={EdnServiceMapping} />
//                   <Route exact path="/pncodestats" component={PNCodeStats} />
//                   <Route exact path="/iptdashboard" component={IPTDashboard} />
//                   <Route exact path="/iptendpoints" component={IPTEndpoints} />
//                   <Route exact path="/cdn" component={CDN} />
//                   <Route exact path="/powerfeeds" component={Power} />
//                   <Route exact path="/accesspoints" component={AccessPoints} />
//                   <Route
//                     exact
//                     path="/iptassignmenttracker"
//                     component={IPTAssignmentTracker}
//                   />
//                   <Route
//                     exact
//                     path="/iptrmatracker"
//                     component={IPTRMATracker}
//                   />
//                   <Route
//                     exact
//                     path="/iptclearancetracker"
//                     component={IPTClearanceTracker}
//                   />
//                   <Route
//                     exact
//                     path="/ednpowerofftracker"
//                     component={EDNPowerOffTracker}
//                   />
//                   <Route
//                     exact
//                     path="/ednhandbacktracker"
//                     component={EDNHandbackTracker}
//                   />
//                   <Route
//                     exact
//                     path="/ednhandovertracker"
//                     component={EDNHandoverTracker}
//                   />
//                   <Route exact path="/pmrtracker" component={PMRTracker} />
//                   <Route exact path="/snags" component={Snags} />
//                   {user?.user_role !== roles.engineer &&
//                   user?.user_role !== roles.user ? (
//                     <>
//                       <Route exact path="/addmember" component={AddMember} />
//                       <Route
//                         exact
//                         path="/updatepanel"
//                         component={UpdatePanel}
//                       />
//                       <Route
//                         exact
//                         path="/deletepanel"
//                         component={DeletePanel}
//                       />
//                       <Route
//                         exact
//                         path="/ednipamfaileddevices"
//                         component={EDNIPAMFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/igwipamfaileddevices"
//                         component={IGWIPAMFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/accesspointsfaileddevices"
//                         component={AccessPointsFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/edndccapacityfaileddevices"
//                         component={EDNDCCapacityFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/igwdccapacityfaileddevices"
//                         component={IGWDCCapacityFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/ednexchangefaileddevices"
//                         component={EDNExchangeFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/inventoryfaileddevices"
//                         component={InventoryFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/iptendpointsfaileddevices"
//                         component={IPTEndpointsFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/ednphysicalmappingfaileddevices"
//                         component={EDNPhysicalMappingFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/ednphysicalmappingcdplegacyfaileddevices"
//                         component={EDNPhysicalMappingCDPLegacyFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/ednphysicalmappingfirewallarpfaileddevices"
//                         component={EDNPhysicalMappingFirewallARPFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/ednphysicalmappinglldpfaileddevices"
//                         component={EDNPhysicalMappingLLDPFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/ednphysicalmappingmacfaileddevices"
//                         component={EDNPhysicalMappingMACFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/igwphysicalmappingfaileddevices"
//                         component={IGWPhysicalMappingFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/igwphysicalmappingcdplegacyfaileddevices"
//                         component={IGWPhysicalMappingCDPLegacyFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/igwphysicalmappinglldpfaileddevices"
//                         component={IGWPhysicalMappingLLDPFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/igwphysicalmappingmacfaileddevices"
//                         component={IGWPhysicalMappingMACFailedDevices}
//                       />
//                       <Route
//                         exact
//                         path="/f5faileddevices"
//                         component={F5FailedDevices}
//                       />
//                     </>
//                   ) : null}
//                 </>
//               ) : null}
//               <Route
//                 exact
//                 path="/ednnetdashboard"
//                 component={EDNNetDashboard}
//               />
//               <Route
//                 exact
//                 path="/igwnetdashboard"
//                 component={IGWNETDashboard}
//               />
//               <Route
//                 exact
//                 path="/ednsysdashboard"
//                 component={EDNSYSDashboard}
//               />
//               <Route
//                 exact
//                 path="/igwsysdashboard"
//                 component={IGWSysDashboard}
//               />
//               <Route exact path="/socdashboard" component={SOCDashboard} />

//               <Route exact path="/ednexchange" component={EDNExchange} />
//               <Route exact path="/vrfowners" component={VRFOwners} />
//               <Route exact path="/received-routes" component={ReceivedRoutes} />
//               <Route
//                 exact
//                 path="/ednexchangedashboard"
//                 component={EDNExchangeDashboard}
//               />
//             </>
//           ) : null}

//           {user?.user_role !== roles.executive ? (
//             // && user?.user_role !== roles.user
//             <>
//               <Route exact path="/ednmaclegacy" component={EDNMACLegacy} />
//               <Route
//                 exact
//                 path="/ednmaclegacysearch"
//                 component={EDNMACLegacySearch}
//               />

//               {user?.user_role !== roles.ednSM ? (
//                 <Route
//                   exact
//                   path="/edndashboard"
//                   component={ServiceMappingDashboard}
//                 />
//               ) : (
//                 <Route exact path="/" component={ServiceMappingDashboard} />
//               )}
//             </>
//           ) : null}
//         </StyledBodyCol>
//       </Row>
//     </>
//   );
// };

// export default Index;
