import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import {
  Table,
  Button,
  Menu,
  Dropdown,
  Space,
  notification,
  Spin,
  Input,
  Select,
  Row,
  Col,
} from "antd";
// import SearchForm from "./modals/macLegacySearch";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../../utils/axios";
import Search from "../../../../components/search";
import { StyledTable } from "../../../../components/table/main.styles";
import { StyledButton } from "../../../../components/button/main.styles";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../../components/input/main.styles";
import {
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import Swal from "sweetalert2";
import { Link, useHistory } from "react-router-dom";
// import { SEED_API } from "../../../GlobalVar";
// import ShowSeedDevice from "../../../seed/ShowSeedDevice";
import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
import { roles } from "../../../../utils/constants.js";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const { Option } = Select;
  const [dates, setDates] = useState([]);
  const [user, setUser] = useState();
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [total, setTotal] = useState(0);
  let [dataSource, setDataSource] = useState([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  const [pageSize, setPageSize] = useState(50);
  const [currentPage, setCurrentPage] = useState(1);
  const ref = useRef();

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      setUser(JSON.parse(localStorage.getItem("user")));
      try {
        await axios
          .get(baseUrl + "/getAllEdnMacLegacyDates")
          .then((response) => {
            setDates(response.data);
            setFetchDate(response.data?.length > 0 ? response.data[0] : null);
            console.log(response);
          });
        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);
  //////////////////////////////////////////////////////////////////
  let [deviceAName, setDeviceAName] = useState("");
  //   let [deviceAInterface, setDeviceAInterface] = useState("");
  //   let [deviceATrunkName, setDeviceATrunkName] = useState("");
  let [deviceAIp, setDeviceAIp] = useState("");
  let [deviceBSystemName, setDeviceBSystemName] = useState("");
  //   let [deviceBInterface, setDeviceBInterface] = useState("");
  let [deviceBIp, setDeviceBIp] = useState("");
  //   let [deviceBType, setDeviceBType] = useState("");
  //   let [deviceBPortDesc, setDeviceBPortDesc] = useState("");
  //   let [deviceAMac, setDeviceAMac] = useState("");
  let [deviceBMac, setDeviceBMac] = useState("");
  //   let [deviceAPortDesc, setDeviceAPortDesc] = useState("");
  let [deviceAVlan, setDeviceAVlan] = useState("");
  //   let [deviceAVlanName, setDeviceAVlanName] = useState("");
  let [serverName, setServerName] = useState("");
  //   let [serverOS, setServerOS] = useState("");
  let [appName, setAppName] = useState("");
  //   let [ownerName, setOwnerName] = useState("");
  //   let [ownerEmail, setOwnerEmail] = useState("");
  //   let [ownerContact, setOwnerContact] = useState("");
  let [serviceVendor, setServiceVendor] = useState("");
  let [arpSourceName, setArpSourceName] = useState("");
  let [f5LB, setF5LB] = useState("");
  let [fetchDate, setFetchDate] = useState(null);

  // let [deviceANames, setDeviceANames] = useState([]);
  // let [deviceANameOptions, setDeviceANameOptions] = useState([]);

  // useEffect(() => {
  //   (async () => {
  //     try {
  //       const res = await axios.get(baseUrl + "/getDeviceANames");
  //       setDeviceANames(res.data);
  //     } catch (err) {
  //       console.log(err.response);
  //     }
  //   })();
  // }, []);

  // useEffect(() => {
  //   let options = getOptions(deviceANames);
  //   setDeviceANameOptions(options);
  // }, [deviceANames]);

  const getOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  const getEdnMacLegacyBySearchFilters = async (
    filters,
    pageSize,
    currentPage
  ) => {
    setLoading(true);
    await axios
      .post(
        baseUrl +
          `/getEdnMacLegacyBySearchFilters?limit=${pageSize}&offset=${
            pageSize * (currentPage - 1)
          }`,
        filters
      )
      .then((response) => {
        setDataSource(response.data.data);
        setTotal(response.data.total);
        setLoading(false);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
      });
  };

  const handleSubmit = (pageSize, currentPage) => {
    const filters = {
      device_a_name: deviceAName,
      //   device_a_interface: deviceAInterface,
      //   device_a_trunk_name: deviceATrunkName,
      device_a_ip: deviceAIp,
      device_b_ip: deviceBIp,
      //   device_a_mac: deviceAMac,
      device_b_mac: deviceBMac,
      //   device_a_port_desc: deviceAPortDesc,
      device_a_vlan: deviceAVlan,
      device_b_system_name: deviceBSystemName,
      //   device_b_interface: deviceBInterface,
      //   device_b_type: deviceBType,
      //   device_b_port_desc: deviceBPortDesc,
      server_name: serverName,
      //   server_os: serverOS,
      app_name: appName,
      //   owner_name: ownerName,
      //   owner_email: ownerEmail,
      //   owner_contact: ownerContact,
      service_vendor: serviceVendor,
      arp_source_name: arpSourceName,
      f5_lb: f5LB,
      fetch_date: fetchDate,
    };

    getEdnMacLegacyBySearchFilters(filters, pageSize, currentPage);

    // if (checkProperties(filters)) {
    //   getEdnMacLegacyBySearchFilters(filters);
    // } else {
    //   alert("No filter is selected! Atleast 1 filter is a must to search :)");
    // }
  };

  // useImperativeHandle(ref, () => ({ handleSubmit }), [
  //   deviceAName,
  //   deviceAIp,
  //   deviceBIp,
  //   deviceBMac,
  //   deviceAVlan,
  //   deviceBSystemName,
  //   serverName,
  //   appName,
  //   serviceVendor,
  //   fetchDate,
  //   props.pageSize,
  //   props.currentPage,
  // ]);

  const checkProperties = (obj) => {
    for (let key in obj) {
      if (obj[key] !== null && obj[key] != "") return true;
    }
    return false;
  };

  const handleCancel = async () => {
    setDeviceAName("");
    setDeviceAIp("");
    setDeviceBSystemName("");
    setDeviceBIp("");
    setDeviceBMac("");
    setDeviceAVlan("");
    setServerName("");
    setAppName("");
    setServiceVendor("");
    setArpSourceName("");
    setF5LB("");
    setFetchDate(null);
    setDataSource([]);
    setTotal(0);
    setCurrentPage(1);
    setFetchDate(dates?.length > 0 ? dates[0] : null);
  };

  const handleSelectChange = (value) => {
    setFetchDate(value);
  };

  const exportSeed = async () => {
    // setExportLoading(true);
    // jsonToExcel(dataSource, "ednmaclegacySearched.xlsx");
    // setExportLoading(false);
    const filters = {
      device_a_name: deviceAName,
      device_a_ip: deviceAIp,
      device_b_ip: deviceBIp,
      device_b_mac: deviceBMac,
      device_a_vlan: deviceAVlan,
      device_b_system_name: deviceBSystemName,
      server_name: serverName,
      app_name: appName,
      service_vendor: serviceVendor,
      arp_source_name: arpSourceName,
      f5_lb: f5LB,
      fetch_date: fetchDate,
    };

    await axios
      .post(baseUrl + "/exportEdnMacLegacySearched", filters)
      .then((response) => {
        jsonToExcel(response.data, "ednmaclegacySearched.xlsx");
        console.log(response);
        setExportLoading(false);
      })
      .catch((error) => {
        setExportLoading(false);
        console.log(error);
      });
  };

  const jsonToExcel = (seedData, fileName) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
    XLSX.writeFile(wb, fileName);
    setExportLoading(false);
  };

  /////////////////////////////////////////////////////////////////////

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
  };

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
    handleSubmit(pagination.pageSize, pagination.current);
    setPageSize(pagination.pageSize);
    setCurrentPage(pagination.current);
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  sortedInfo = sortedInfo || {};
  filteredInfo = filteredInfo || {};

  const columns = [
    // {
    //   title: "",
    //   key: "edit",
    //   width: "35px",

    //   render: (text, record) => (
    //     <a>
    //       <EditOutlined
    //         onClick={() => {
    //           edit(record);
    //         }}
    //       />
    //     </a>
    //   ),
    // },
    {
      title: "EDN MAC Id",
      dataIndex: "edn_mac_legacy_id",
      key: "edn_mac_legacy_id",
      align: "center",
      // ...getColumnSearchProps("edn_mac_legacy_id"),
      //   ...getColumnSearchProps(
      //     "edn_mac_legacy_id",
      //     "EDN MAC Id",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.edn_mac_legacy_id.length - b.edn_mac_legacy_id.length,
      // sortOrder:
      //   sortedInfo.columnKey === "edn_mac_legacy_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Name",
      dataIndex: "device_a_name",
      key: "device_a_name",
      align: "center",
      // ...getColumnSearchProps("device_a_name"),
      //   ...getColumnSearchProps(
      //     "device_a_name",
      //     "Device A Name",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Interface",
      dataIndex: "device_a_interface",
      key: "device_a_interface",
      align: "center",
      // ...getColumnSearchProps("device_a_interface"),
      //   ...getColumnSearchProps(
      //     "device_a_interface",
      //     "Device A Interface",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) =>
      //   a.device_a_interface.length - b.device_a_interface.length,
      // sortOrder:
      //   sortedInfo.columnKey === "device_a_interface" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A TX",
      dataIndex: "device_a_tx",
      key: "device_a_tx",
      align: "center",
      // ...getColumnSearchProps("device_a_interface"),
      // ...getColumnSearchProps(
      //   "device_a_tx",
      //   "Device A TX",
      //   setRowCount,
      //   setDataSource,
      //   excelData,
      //   columnFilters
      // ),
      // sorter: (a, b) =>
      //   a.device_a_interface.length - b.device_a_interface.length,
      // sortOrder:
      //   sortedInfo.columnKey === "device_a_interface" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A RX",
      dataIndex: "device_a_rx",
      key: "device_a_rx",
      align: "center",
      // ...getColumnSearchProps("device_a_interface"),
      // ...getColumnSearchProps(
      //   "device_a_rx",
      //   "Device A RX",
      //   setRowCount,
      //   setDataSource,
      //   excelData,
      //   columnFilters
      // ),
      // sorter: (a, b) =>
      //   a.device_a_interface.length - b.device_a_interface.length,
      // sortOrder:
      //   sortedInfo.columnKey === "device_a_interface" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Trunk Name",
      dataIndex: "device_a_trunk_name",
      key: "device_a_trunk_name",
      align: "center",
      // ...getColumnSearchProps("device_a_trunk_name"),
      //   ...getColumnSearchProps(
      //     "device_a_trunk_name",
      //     "Device A Trunk Name",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) =>
      //   a.device_a_trunk_name.length - b.device_a_trunk_name.length,
      // sortOrder:
      //   sortedInfo.columnKey === "device_a_trunk_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Ip",
      dataIndex: "device_a_ip",
      key: "device_a_ip",
      align: "center",
      // ...getColumnSearchProps("device_a_ip"),
      //   ...getColumnSearchProps(
      //     "device_a_ip",
      //     "Device A Ip",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_ip.length - b.device_a_ip.length,
      // sortOrder: sortedInfo.columnKey === "device_a_ip" && sortedInfo.order,
      ellipsis: true,
    },

    {
      title: "Device B System Name",
      dataIndex: "device_b_system_name",
      key: "device_b_system_name",
      align: "center",
      // ...getColumnSearchProps("device_b_system_name"),
      //   ...getColumnSearchProps(
      //     "device_b_system_name",
      //     "Device B System Name",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) =>
      //   a.device_b_system_name.length - b.device_b_system_name.length,
      // sortOrder:
      //   sortedInfo.columnKey === "device_b_system_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Interface",
      dataIndex: "device_b_interface",
      key: "device_b_interface",
      align: "center",
      // ...getColumnSearchProps("device_b_interface"),
      //   ...getColumnSearchProps(
      //     "device_b_interface",
      //     "Device B Interface",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) =>
      //   a.device_b_interface.length - b.device_b_interface.length,
      // sortOrder:
      //   sortedInfo.columnKey === "device_b_interface" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Ip",
      dataIndex: "device_b_ip",
      key: "device_b_ip",
      align: "center",
      // ...getColumnSearchProps("device_b_ip"),
      //   ...getColumnSearchProps(
      //     "device_b_ip",
      //     "Device B Ip",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_b_ip.length - b.device_b_ip.length,
      // sortOrder: sortedInfo.columnKey === "device_b_ip" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Type",
      dataIndex: "device_b_type",
      key: "device_b_type",
      align: "center",
      // ...getColumnSearchProps("device_b_type"),
      //   ...getColumnSearchProps(
      //     "device_b_type",
      //     "Device B Type",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_b_type.length - b.device_b_type.length,
      // sortOrder: sortedInfo.columnKey === "device_b_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Port Desc",
      dataIndex: "device_b_port_desc",
      key: "device_b_port_desc",
      align: "center",
      // ...getColumnSearchProps("device_b_port_desc"),
      //   ...getColumnSearchProps(
      //     "device_b_port_desc",
      //     "Device B Port Desc",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) =>
      //   a.device_b_port_desc.length - b.device_b_port_desc.length,
      // sortOrder:
      //   sortedInfo.columnKey === "device_b_port_desc" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Mac",
      dataIndex: "device_a_mac",
      key: "device_a_mac",
      align: "center",
      // ...getColumnSearchProps("device_a_mac"),
      //   ...getColumnSearchProps(
      //     "device_a_mac",
      //     "Device A Mac",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_mac.length - b.device_a_mac.length,
      // sortOrder: sortedInfo.columnKey === "device_a_mac" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Mac",
      dataIndex: "device_b_mac",
      key: "device_b_mac",
      align: "center",
      //   ...getColumnSearchProps(
      //     "device_b_mac",
      //     "Device B Mac",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // ...getColumnSearchProps("device_b_mac"),
      // sorter: (a, b) => a.device_b_mac.length - b.device_b_mac.length,
      // sortOrder: sortedInfo.columnKey === "device_b_mac" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Mac Vendor",
      dataIndex: "device_b_mac_vendor",
      key: "device_b_mac_vendor",
      align: "center",
      //   ...getColumnSearchProps(
      //     "device_b_mac_vendor",
      //     "Device B Mac Vendor",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // ...getColumnSearchProps("device_b_mac"),
      // sorter: (a, b) => a.device_b_mac.length - b.device_b_mac.length,
      // sortOrder: sortedInfo.columnKey === "device_b_mac" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Port Desc",
      dataIndex: "device_a_port_desc",
      key: "device_a_port_desc",
      align: "center",
      // ...getColumnSearchProps("device_a_port_desc"),
      //   ...getColumnSearchProps(
      //     "device_a_port_desc",
      //     "Device A Port Desc",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) =>
      //   a.device_a_port_desc.length - b.device_a_port_desc.length,
      // sortOrder:
      //   sortedInfo.columnKey === "device_a_port_desc" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Vlan",
      dataIndex: "device_a_vlan",
      key: "device_a_vlan",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "device_a_vlan",
      //     "Device A Vlan",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Vlan Name",
      dataIndex: "device_a_vlan_name",
      key: "device_a_vlan_name",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "device_a_vlan_name",
      //     "Device A Vlan Name",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "F5 LB",
      dataIndex: "f5_lb",
      key: "f5_lb",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      // ...getColumnSearchProps(
      //   "f5_lb",
      //   "F5 LB",
      //   setRowCount,
      //   setDataSource,
      //   excelData,
      //   columnFilters
      // ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "F5 VIP",
      dataIndex: "f5_vip",
      key: "f5_vip",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      // ...getColumnSearchProps(
      //   "f5_vip",
      //   "F5 VIP",
      //   setRowCount,
      //   setDataSource,
      //   excelData,
      //   columnFilters
      // ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "F5 Node Status",
      dataIndex: "f5_node_status",
      key: "f5_node_status",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      // ...getColumnSearchProps(
      //   "f5_node_status",
      //   "F5 Node Status",
      //   setRowCount,
      //   setDataSource,
      //   excelData,
      //   columnFilters
      // ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Arp Source Name",
      dataIndex: "arp_source_name",
      key: "arp_source_name",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "arp_source_name",
      //     "Arp Source Name",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Arp Source Type",
      dataIndex: "arp_source_type",
      key: "arp_source_type",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "arp_source_type",
      //     "Arp Source Type",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Server Name",
      dataIndex: "server_name",
      key: "server_name",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "server_name",
      //     "Server Name",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Server OS",
      dataIndex: "server_os",
      key: "server_os",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "server_os",
      //     "Server OS",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "App Name",
      dataIndex: "app_name",
      key: "app_name",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "app_name",
      //     "App Name",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Owner Name",
      dataIndex: "owner_name",
      key: "owner_name",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "owner_name",
      //     "Owner Name",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Owner Email",
      dataIndex: "owner_email",
      key: "owner_email",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "owner_email",
      //     "Owner Email",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Owner Contact",
      dataIndex: "owner_contact",
      key: "owner_contact",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "owner_contact",
      //     "Owner Contact",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Service Matched By",
      dataIndex: "service_matched_by",
      key: "service_matched_by",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "service_matched_by",
      //     "Service Matched By",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Modified By",
      dataIndex: "modified_by",
      key: "modified_by",
      align: "center",
      // ...getColumnSearchProps("modification_date"),
      //   ...getColumnSearchProps(
      //     "modified_by",
      //     "Modified By",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Service Vendor",
      dataIndex: "service_vendor",
      key: "service_vendor",
      align: "center",
      // ...getColumnSearchProps("device_a_vlan"),
      //   ...getColumnSearchProps(
      //     "service_vendor",
      //     "Service Vendor",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      align: "center",
      // ...getColumnSearchProps("creation_date"),
      //   ...getColumnSearchProps(
      //     "creation_date",
      //     "Creation Date",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.creation_date.length - b.creation_date.length,
      // sortOrder: sortedInfo.columnKey === "creation_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Modification Date",
      dataIndex: "modification_date",
      key: "modification_date",
      align: "center",
      // ...getColumnSearchProps("modification_date"),
      //   ...getColumnSearchProps(
      //     "modification_date",
      //     "Modification Date",
      //     setRowCount,
      //     setDataSource,
      //     excelData,
      //     columnFilters
      //   ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
    },
  ];

  return (
    <>
      <Spin tip="Loading..." spinning={loading}>
        <StyledHeading>
          EDN Service Mapping Search
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {total} &nbsp;&nbsp;&nbsp; Columns: {columns.length}
          </span>
        </StyledHeading>

        <div
          style={{
            // border: "1px solid black",
            marginTop: "0px",
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <div></div>
          <div style={{ display: "flex" }}>
            <Spin spinning={exportLoading}>
              <StyledButton
                color={"#3bbdc2"}
                onClick={exportSeed}
                style={{ width: "100%" }}
              >
                <RightSquareOutlined /> Export
              </StyledButton>
            </Spin>
          </div>
        </div>

        {/* <SearchForm
          dates={dates}
          setDataSource={setDataSource}
          pageSize={pageSize}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          setLoading={setLoading}
          setTotal={setTotal}
          ref={ref}
          handleSubmit={handleSubmit}
          deviceAName={deviceAName}
          setDeviceAName={setDeviceAName}
          deviceAIp={deviceAIp}
          setDeviceAIp={setDeviceAIp}
          deviceBSystemName={deviceBSystemName}
          setDeviceBSystemName={setDeviceBSystemName}
          deviceBIp={deviceBIp}
          setDeviceBIp={setDeviceBIp}
          deviceBMac={deviceBMac}
          setDeviceBMac={setDeviceBMac}
        /> */}

        {/* <form onSubmit={handleSubmit}> */}
        <Row gutter={30}>
          <Col span={12}>
            <InputWrapper>
              Device A Name:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={deviceAName}
                onChange={(e) => setDeviceAName(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Device A Ip:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={deviceAIp}
                onChange={(e) => setDeviceAIp(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Device B System Name: &nbsp;&nbsp;
              <StyledInput
                value={deviceBSystemName}
                onChange={(e) => setDeviceBSystemName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Device B Ip: &nbsp;&nbsp;
              <StyledInput
                value={deviceBIp}
                onChange={(e) => setDeviceBIp(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Device B Mac: &nbsp;&nbsp;
              <StyledInput
                value={deviceBMac}
                onChange={(e) => setDeviceBMac(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              F5 LB: &nbsp;&nbsp;
              <StyledInput
                value={f5LB}
                onChange={(e) => setF5LB(e.target.value)}
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Device A Vlan:&nbsp;&nbsp;
              <StyledInput
                value={deviceAVlan}
                onChange={(e) => setDeviceAVlan(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Server Name: &nbsp;&nbsp;
              <StyledInput
                value={serverName}
                onChange={(e) => setServerName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              App Name: &nbsp;&nbsp;
              <StyledInput
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Service Vendor: &nbsp;&nbsp;
              <StyledInput
                value={serviceVendor}
                onChange={(e) => setServiceVendor(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Arp Source Name: &nbsp;&nbsp;
              <StyledInput
                value={arpSourceName}
                onChange={(e) => setArpSourceName(e.target.value)}
              />
            </InputWrapper>
            <InputWrapper>
              Fetch Date: &nbsp;&nbsp;
              <Select
                defaultValue={dates?.length > 0 ? dates[0] : null}
                style={{ width: "100%" }}
                onChange={handleSelectChange}
                value={fetchDate}
                // disabled={user?.user_role === roles.user}
              >
                {getOptions(dates)}
              </Select>
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center" }}>
            <StyledButton2 color={"red"} onClick={handleCancel}>
              Clear
            </StyledButton2>
            &nbsp; &nbsp;
            <StyledButton2
              color={"green"}
              onClick={() => handleSubmit(pageSize, currentPage)}
            >
              Search
            </StyledButton2>
          </Col>
        </Row>
        {/* </form> */}
        <StyledTable
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
            total,
          }}
          size="small"
          scroll={{ x: 7500, y: height - 350 }}
          onChange={handleChange}
          // rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="edn_mac_legacy_id"
          style={{ whiteSpace: "pre" }}
        />
      </Spin>
    </>
  );
};

export default Index;

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

const StyledButton2 = styled(Button)`
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
