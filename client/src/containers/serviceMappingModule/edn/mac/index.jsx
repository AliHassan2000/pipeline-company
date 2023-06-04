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
} from "antd";
import Modal from "./modal";
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
import { Link, useHistory, useLocation } from "react-router-dom";
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
  let [fetchLoading, setFetchLoading] = useState("empty");
  let [fetchDate, setFetchDate] = useState("");
  const [backgroundColor, setBackgroundColor] = useState("green");
  let [syncFromLoading, setSyncFromLoading] = useState("empty");
  let [syncFromDate, setSyncFromDate] = useState("");
  const [syncFromBackgroundColor, setSyncFromBackgroundColor] =
    useState("green");

  let [syncEDNServicesFromLoading, setSyncEDNServicesFromLoading] =
    useState("empty");
  let [syncESFromDate, setSyncESFromDate] = useState("");
  const [syncESFromBackgroundColor, setSyncESFromBackgroundColor] =
    useState("green");

  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [dataSource, setDataSource] = useState(excelData);
  let [searchValue, setSearchValue] = useState(null);
  let [inputValue, setInputValue] = useState("");
  let [editRecord, setEditRecord] = useState(null);
  const [togleCheck, setTogleCheck] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  let selectedDevices = [];
  const [isModalVisible, setIsModalVisible] = useState(false);
  const inputRef = useRef(null);
  const history = useHistory();
  const [showSeed, setShowSeed] = useState(false);
  const [seedRecord, setSeedRecord] = useState(null);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  const [isFModalVisible, setIsFModalVisible] = useState(false);
  let [fDataSource, setFDataSource] = useState(null);

  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      setUser(JSON.parse(localStorage.getItem("user")));
      try {
        await axios
          .get(baseUrl + "/getAllEdnMacLegacyDates")
          .then((response) => {
            setDates(response.data);
            console.log(response);
          });
        /////////////////////////////////////////////////////
        let filter = searchParams.get("filter");
        let res = null;
        if (filter) {
          let query = `?filter=${filter}`;
          res = await axios.get(baseUrl + "/getEdnMacLegacy" + query);
        } else {
          res = await axios.get(baseUrl + "/getAllEdnMacLegacy");
        }
        excelData = res?.data;
        setDataSource(excelData);
        setRowCount(excelData.length);
        setLoading(false);
        /////////////////////////////////////////////////////
        const status = await axios.get(baseUrl + "/getEdnMacLegacyFetchStatus");
        if (status.data.fetch_status === "Running") {
          setFetchLoading("true");
          setBackgroundColor("red");
        } else if (status.data.fetch_status === "Completed") {
          setFetchLoading("false");
          setBackgroundColor("green");
        } else {
          setFetchLoading("empty");
        }
        setFetchDate(status.data.fetch_date);
        /////////////////////////////////////////////////////
        const status1 = await axios.get(
          baseUrl + "/getEdnMacLegacySyncFirewallStatus"
        );
        if (status1.data.fetch_status === "Running") {
          setSyncFromLoading("true");
          setSyncFromBackgroundColor("red");
        } else if (status1.data.fetch_status === "Completed") {
          setSyncFromLoading("false");
          setSyncFromBackgroundColor("green");
        } else {
          setSyncFromLoading("empty");
        }
        setSyncFromDate(status1.data.fetch_date);
        /////////////////////////////////////////////////////
        const status2 = await axios.get(
          baseUrl + "/getEdnMacLegacySyncEDNServicesStatus"
        );
        if (status2.data.fetch_status === "Running") {
          setSyncEDNServicesFromLoading("true");
          setSyncESFromBackgroundColor("red");
        } else if (status2.data.fetch_status === "Completed") {
          setSyncEDNServicesFromLoading("false");
          setSyncESFromBackgroundColor("green");
        } else {
          setSyncEDNServicesFromLoading("empty");
        }
        setSyncESFromDate(status2.data.fetch_date);
        /////////////////////////////////////////////////////
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const syncFrom = async () => {
    setSyncFromLoading("true");
    setSyncFromDate(new Date().toLocaleString());
    setSyncFromBackgroundColor("red");
    await axios
      .get(baseUrl + "/syncMacAddressInEDNMAC")
      .then((response) => {
        const promises = [];
        promises.push(
          axios.get(baseUrl + "/getAllEdnMacLegacy").then((response) => {
            console.log(response.data);
            setRowCount(response.data.length);
            setDataSource(response.data);
            excelData = response.data;
            setSyncFromLoading("false");
          })
        );
        return Promise.all(promises);
      })
      .catch((err) => {
        console.log(err);
        setSyncFromLoading("false");
      });

    // await getSNTC();
  };
  const EDNServicesSyncFrom = async () => {
    setSyncEDNServicesFromLoading("true");
    setSyncESFromDate(new Date().toLocaleString());
    setSyncESFromBackgroundColor("red");
    await axios
      .get(baseUrl + "/syncFromEdnServices")
      .then((response) => {
        const promises = [];
        promises.push(
          axios.get(baseUrl + "/getAllEdnMacLegacy").then((response) => {
            console.log(response.data);
            setRowCount(response.data.length);
            setDataSource(response.data);
            excelData = response.data;
            setSyncEDNServicesFromLoading("false");
          })
        );
        return Promise.all(promises);
      })
      .catch((err) => {
        console.log(err);
        setSyncEDNServicesFromLoading("false");
      });

    // await getSNTC();
  };
  const openNotification = () => {
    notification.open({
      message: "File Exported Successfully",
      onClick: () => {
        console.log("Notification Clicked!");
      },
    });
  };

  const openFetchNotification = () => {
    notification.open({
      message: "Fetched Successfully",
      onClick: () => {
        console.log("Notification Clicked!");
      },
    });
  };

  const jsonToExcel = (seedData, fileName) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
    XLSX.writeFile(wb, fileName);
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData, "ednmaclegacy.xlsx");
    setExportLoading(false);
    // await axios
    //   .get(baseUrl + "/exportEdnMacLegacy")
    //   .then((response) => {
    //     // openNotification();
    //     jsonToExcel(response.data);
    //     console.log(response);
    //     setExportLoading(false);
    //   })
    //   .catch((error) => {
    //     setExportLoading(false);
    //     console.log(error);
    //   });
  };

  const exportFiltered = async () => {
    setExportLoading(true);
    jsonToExcel(dataSource, "filteredednmaclegacy.xlsx");
    setExportLoading(false);
  };

  let seedTemp = [
    {
      edn_mac_legacy_id: "",
      device_a_name: "",
      device_a_interface: "",
      device_a_trunk_name: "",
      device_a_ip: "",
      device_b_system_name: "",
      device_b_interface: "",
      device_b_ip: "",
      device_b_type: "",
      device_b_port_desc: "",
      device_a_mac: "",
      device_b_mac: "",
      device_b_mac_vendor: "",
      device_a_port_desc: "",
      device_a_vlan: "",
      device_a_vlan_name: "",
      service_vendor: "",
      creation_date: "",
      modification_date: "",
    },
  ];

  const fetch = async () => {
    setFetchLoading("true");
    setFetchDate(new Date().toLocaleString());
    setBackgroundColor("red");
    await axios
      .get(baseUrl + "/fetchEdnMacLegacy")
      .then((response) => {
        // openFetchNotification();
        console.log(response);
      })
      .catch((error) => console.log(error));
  };

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };

  const showEditModal = () => {
    setIsModalVisible(true);
  };

  //---------------------------------------

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const clearAll = () => {
    setDataSource(excelData);
    setSortedInfo(null);
  };

  const opensweetalertdanger = (title) => {
    Swal.fire({
      title,
      type: "warning",
    });
  };

  const handleOnboard = () => {
    // history.push('/onboard')
    if (selectedRowKeys.length > 0) {
      let filterRes = dataSource.filter((item) =>
        selectedRowKeys.includes(item.ne_ip_address)
      );

      history.push({
        pathname: "/onboard",
        state: { detail: filterRes },
      });
    } else {
      opensweetalertdanger("No device is selected to onboard.");
      // alert("No device is selected to onboard.");
    }

    // setDataSource(
    //   dataSource.filter((item) => selectedDevices.includes(item.ne_ip_address))
    // );
  };

  const remove = (item) => {
    console.log(selectedDevices);
    console.log(item);
    var index = selectedDevices.indexOf(item);
    if (index !== -1) {
      selectedDevices.splice(index, 1);
    }
    console.log("selectedDevices===>", selectedDevices);
  };

  const handleSeedInput = (e) => {
    setSearchValue(e.target.value);
    console.log(e.target);
    let filteredSuggestions = excelData.filter(
      (d) =>
        JSON.stringify(d)
          .replace(" ", "")
          .toLowerCase()
          .indexOf(e.target.value.toLowerCase()) > -1
    );
    setRowCount(filteredSuggestions.length);
    setDataSource(filteredSuggestions);
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

  const postSeed = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/addEdnMlpsDevices", seed)
      .then((response) => {
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/getAllEdnMpls")
            .then((response) => {
              console.log("response===>", response);
              excelData = response.data;
              setDataSource(excelData);
              setLoading(false);
            })
            .catch((error) => {
              console.log(error);
              setLoading(false);
            })
        );
        setLoading(false);
        return Promise.all(promises);
      })
      .catch((err) => {
        console.log(err);
        setLoading(false);
      });
  };

  const importExcel = (e) => {
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
      // const heads = headers.map((head) => ({ title: head, field: head }));
      fileData.splice(0, 1);
      excelData = convertToJson(headers, fileData);
      // console.log(excelData);
      postSeed(excelData);
      setRowCount(excelData.length);
      setDataSource(excelData);
    };
  };

  const CheckBoxData = (ev) => {
    // e.target.checked
    // ? selectedDevices.push(ev.ne_ip_address)
    // : remove(ev.ne_ip_address)
    console.log("working CheckBoxData", ev);
  };

  const edit = (record) => {
    setEditRecord(record);
    showEditModal();
  };
  const showSeedDev = (record) => {
    setShowSeed(true);
    setSeedRecord(record);
  };

  useEffect(() => {
    // inputRef.current.addEventListener("input", importExcel);
  }, []);

  sortedInfo = sortedInfo || {};
  filteredInfo = filteredInfo || {};

  const columns = [
    {
      title: "",
      key: "edit",
      width: "35px",

      render: (text, record) => (
        <a>
          <EditOutlined
            onClick={() => {
              edit(record);
            }}
          />
        </a>
      ),
    },
    {
      title: "EDN MAC Id",
      dataIndex: "edn_mac_legacy_id",
      key: "edn_mac_legacy_id",
      // ...getColumnSearchProps("edn_mac_legacy_id"),
      ...getColumnSearchProps(
        "edn_mac_legacy_id",
        "EDN MAC Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.edn_mac_legacy_id.length - b.edn_mac_legacy_id.length,
      // sortOrder:
      //   sortedInfo.columnKey === "edn_mac_legacy_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Name",
      dataIndex: "device_a_name",
      key: "device_a_name",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "device_a_name",
        "Device A Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Interface",
      dataIndex: "device_a_interface",
      key: "device_a_interface",
      // ...getColumnSearchProps("device_a_interface"),
      ...getColumnSearchProps(
        "device_a_interface",
        "Device A Interface",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      // ...getColumnSearchProps("device_a_interface"),
      ...getColumnSearchProps(
        "device_a_tx",
        "Device A TX",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      // ...getColumnSearchProps("device_a_interface"),
      ...getColumnSearchProps(
        "device_a_rx",
        "Device A RX",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      // ...getColumnSearchProps("device_a_trunk_name"),
      ...getColumnSearchProps(
        "device_a_trunk_name",
        "Device A Trunk Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      // ...getColumnSearchProps("device_a_ip"),
      ...getColumnSearchProps(
        "device_a_ip",
        "Device A Ip",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_ip.length - b.device_a_ip.length,
      // sortOrder: sortedInfo.columnKey === "device_a_ip" && sortedInfo.order,
      ellipsis: true,
    },

    {
      title: "Device B System Name",
      dataIndex: "device_b_system_name",
      key: "device_b_system_name",
      // ...getColumnSearchProps("device_b_system_name"),
      ...getColumnSearchProps(
        "device_b_system_name",
        "Device B System Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "device_b_interface",
        "Device B Interface",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "device_b_ip",
        "Device B Ip",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_b_ip.length - b.device_b_ip.length,
      // sortOrder: sortedInfo.columnKey === "device_b_ip" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Type",
      dataIndex: "device_b_type",
      key: "device_b_type",
      // ...getColumnSearchProps("device_b_type"),
      ...getColumnSearchProps(
        "device_b_type",
        "Device B Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_b_type.length - b.device_b_type.length,
      // sortOrder: sortedInfo.columnKey === "device_b_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Port Desc",
      dataIndex: "device_b_port_desc",
      key: "device_b_port_desc",
      // ...getColumnSearchProps("device_b_port_desc"),
      ...getColumnSearchProps(
        "device_b_port_desc",
        "Device B Port Desc",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      // ...getColumnSearchProps("device_a_mac"),
      ...getColumnSearchProps(
        "device_a_mac",
        "Device A Mac",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_mac.length - b.device_a_mac.length,
      // sortOrder: sortedInfo.columnKey === "device_a_mac" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device B Mac",
      dataIndex: "device_b_mac",
      key: "device_b_mac",
      ...getColumnSearchProps(
        "device_b_mac",
        "Device B Mac",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // ...getColumnSearchProps("device_b_mac"),
      // sorter: (a, b) => a.device_b_mac.length - b.device_b_mac.length,
      // sortOrder: sortedInfo.columnKey === "device_b_mac" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "device_b_mac_vendor",
      key: "device_b_mac_vendor",
      ...getColumnSearchProps(
        "device_b_mac_vendor",
        "Device B Mac Vendor",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // ...getColumnSearchProps("device_b_mac"),
      // sorter: (a, b) => a.device_b_mac.length - b.device_b_mac.length,
      // sortOrder: sortedInfo.columnKey === "device_b_mac" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Port Desc",
      dataIndex: "device_a_port_desc",
      key: "device_a_port_desc",
      // ...getColumnSearchProps("device_a_port_desc"),
      ...getColumnSearchProps(
        "device_a_port_desc",
        "Device A Port Desc",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "device_a_vlan",
        "Device A Vlan",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device A Vlan Name",
      dataIndex: "device_a_vlan_name",
      key: "device_a_vlan_name",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "device_a_vlan_name",
        "Device A Vlan Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "F5 LB",
      dataIndex: "f5_lb",
      key: "f5_lb",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "f5_lb",
        "F5 LB",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "F5 VIP",
      dataIndex: "f5_vip",
      key: "f5_vip",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "f5_vip",
        "F5 VIP",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "F5 VIP",
      dataIndex: "f5_node_status",
      key: "f5_node_status",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "f5_node_status",
        "F5 Node Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "arp_source_name",
      key: "arp_source_name",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "arp_source_name",
        "Arp Source Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "arp_source_type",
      key: "arp_source_type",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "arp_source_type",
        "Arp Source Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Server Name",
      dataIndex: "server_name",
      key: "server_name",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "server_name",
        "Server Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "server_os",
      key: "server_os",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "server_os",
        "Server OS",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "app_name",
      key: "app_name",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "app_name",
        "App Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Owner Name",
      dataIndex: "owner_name",
      key: "owner_name",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "owner_name",
        "Owner Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Owner Email",
      dataIndex: "owner_email",
      key: "owner_email",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "owner_email",
        "Owner Email",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Owner Contact",
      dataIndex: "owner_contact",
      key: "owner_contact",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "owner_contact",
        "Owner Contact",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "service_matched_by",
      key: "service_matched_by",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "service_matched_by",
        "Service Matched By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "modified_by",
      key: "modified_by",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modified_by",
        "Modified By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "service_vendor",
      key: "service_vendor",
      // ...getColumnSearchProps("device_a_vlan"),
      ...getColumnSearchProps(
        "service_vendor",
        "Service Vendor",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_vlan.length - b.device_a_vlan.length,
      // sortOrder: sortedInfo.columnKey === "device_a_vlan" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      // ...getColumnSearchProps("creation_date"),
      ...getColumnSearchProps(
        "creation_date",
        "Creation Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.creation_date.length - b.creation_date.length,
      // sortOrder: sortedInfo.columnKey === "creation_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Modification Date",
      dataIndex: "modification_date",
      key: "modification_date",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modification_date",
        "Modification Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
    },
  ];

  const getOptions = (dates = []) => {
    let options = [];
    dates.forEach((date) => {
      options.push(<Option value={date}>{date}</Option>);
    });
    return options;
  };

  const handleSelectChange = async (value) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/getAllEdnMacLegacyByDate", { date: value })
      .then((response) => {
        excelData = response.data;
        setDataSource(response.data);
        setRowCount(response.data.length);
        setLoading(false);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
      });
    setLoading(false);
    console.log(`selected ${value}`);
  };

  const fColumns = [
    {
      title: "Ip Address",
      dataIndex: "ip_address",
      key: "ip_address",
      ...getColumnSearchProps("ip_address"),
      sorter: (a, b) => a.ip_address - b.ip_address,
      sortOrder: sortedInfo.columnKey === "ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Date",
      dataIndex: "date",
      key: "date",
      ...getColumnSearchProps("date"),
      sorter: (a, b) => a.date - b.date,
      sortOrder: sortedInfo.columnKey === "date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Time",
      dataIndex: "time",
      key: "time",
      ...getColumnSearchProps("time"),
      sorter: (a, b) => a.time - b.time,
      sortOrder: sortedInfo.columnKey === "time" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Reason",
      dataIndex: "reason",
      key: "reason",
      ...getColumnSearchProps("reason"),
      sorter: (a, b) => a.reason - b.reason,
      sortOrder: sortedInfo.columnKey === "reason" && sortedInfo.order,
      ellipsis: true,
    },
  ];

  const handleClose = () => {
    // setDataSource(null);
    setIsFModalVisible(false);
  };

  const menu = (
    <Menu style={{ marginTop: "-220px", height: "90px" }}>
      <Menu.Item
        key="0"
        style={{ backgroundColor: "transparent", padding: "0px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportSeed}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export All
        </StyledButton>
      </Menu.Item>
      <Menu.Item
        key="1"
        style={{ backgroundColor: "transparent", padding: "5px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportFiltered}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export Filtered
        </StyledButton>
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      <Spin tip="Loading..." spinning={loading}>
        {/* <ShowSeedDevice
          showSeed={showSeed}
          setShowSeed={setShowSeed}
          seedRecord={seedRecord}
        /> */}

        {isModalVisible && (
          <Modal
            isModalVisible={isModalVisible}
            setIsModalVisible={setIsModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            editRecord={editRecord}
          />
        )}

        <Modal
          style={{ zIndex: "99999" }}
          width="80%"
          title=""
          closable={false}
          visible={isFModalVisible}
          footer=""
        >
          <div
            style={{
              textAlign: "center",
              fontSize: "15px",
              fontWeight: "bolder",
            }}
          >
            Failed Onboarded Devices
          </div>
          <br />
          {fDataSource ? (
            <StyledTable
              pagination={{
                defaultPageSize: 50,
                pageSizeOptions: [50, 100, 500, 1000],
              }}
              scroll={{ x: 1000 }}
              // pagination={{
              //   defaultPageSize: 50,
              //   defaultPageSize: 8,
              // }}
              columns={fColumns}
              dataSource={fDataSource}
              rowKey="ne_ip_address"
            />
          ) : (
            <div
              style={{
                textAlign: "center",
                height: "100%",
                paddingBottom: "30px",
              }}
            >
              <Spin tip="Loading Data ..." spinning={true} />
            </div>
          )}
          <div
            style={{
              display: "flex",
              justifyContent: "right",
              paddingTop: "20px",
            }}
          >
            <StyledButton color={"red"} onClick={handleClose}>
              Close
            </StyledButton>
          </div>
        </Modal>

        <StyledHeading>
          EDN MAC
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length - 1}
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
          <Search searchValue={searchValue} handleSeedInput={handleSeedInput} />
          {/* <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; Fetch
          </StyledButton> */}
          <div style={{ display: "flex" }}>
            <div>
              Select Date: &nbsp;&nbsp;
              <Select
                defaultValue={dates?.length > 0 ? dates[0] : null}
                style={{ width: 200 }}
                onChange={handleSelectChange}
                disabled={user?.user_role === roles.user}
              >
                {getOptions(dates)}
              </Select>
            </div>
            &nbsp;&nbsp;
            {/* <StyledButton
              color={"#bb0a1e"}
              onClick={() => {
                getFailedDevice();
                setIsFModalVisible(true);
              }}
              disabled={user?.user_role === roles.user}
            >
              <RightSquareOutlined /> &nbsp; Show Failed devices
            </StyledButton>
            &nbsp;&nbsp; */}
            <Spin spinning={exportLoading}>
              <Dropdown overlay={menu} trigger={["click"]}>
                <StyledButton color={"#3bbdc2"}>
                  Export
                  <DownOutlined />
                </StyledButton>
                {/* <a onClick={(e) => e.preventDefault()}>
                  <Space>
                    Export
                    <DownOutlined />
                  </Space>
                </a> */}
              </Dropdown>
            </Spin>
          </div>
        </div>
        <div style={{ display: "flex" }}>
          <div style={{ display: "flex" }}>
            <Spin spinning={fetchLoading === "true" ? true : false}>
              <StyledButton
                color={"#009BDB"}
                onClick={fetch}
                disabled={
                  user?.user_role !== roles.admin ||
                  syncFromLoading === "true" ||
                  syncEDNServicesFromLoading === "true"
                }
              >
                <RightSquareOutlined />
                Fetch
              </StyledButton>
            </Spin>
            &nbsp;
            {fetchLoading === "empty" ? null : (
              <div
                style={{
                  backgroundColor,
                  padding: "0 10px 0 10px",
                  color: "white",
                  borderRadius: "5px",
                  fontWeight: "500",
                  fontSize: "12px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                }}
              >
                {fetchLoading === "true"
                  ? `Fetch Started At: ${fetchDate}`
                  : `Fetch Completed At: ${fetchDate}`}
              </div>
            )}
            &nbsp;
            <Spin spinning={syncFromLoading === "true" ? true : false}>
              <StyledButton
                color={"#3bbdc2"}
                onClick={syncFrom}
                disabled={
                  user?.user_role === roles.ednSM ||
                  fetchLoading === "true" ||
                  syncEDNServicesFromLoading === "true"
                }
              >
                <RightSquareOutlined />
                Sync From Firewall ARP
              </StyledButton>
            </Spin>
            &nbsp;
            {syncFromLoading === "empty" ? null : (
              <div
                style={{
                  backgroundColor: syncFromBackgroundColor,
                  padding: "0 10px 0 10px",
                  color: "white",
                  borderRadius: "5px",
                  fontWeight: "500",
                  fontSize: "12px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                }}
              >
                {syncFromLoading === "true"
                  ? `Sync Started At: ${syncFromDate}`
                  : `Sync Completed At: ${syncFromDate}`}
              </div>
            )}
            &nbsp;
            <Spin
              spinning={syncEDNServicesFromLoading === "true" ? true : false}
            >
              <StyledButton
                color={"#3bbdc2"}
                onClick={EDNServicesSyncFrom}
                disabled={
                  user?.user_role === roles.ednSM ||
                  fetchLoading === "true" ||
                  syncFromLoading === "true"
                }
              >
                <RightSquareOutlined />
                Sync From EDN Services
              </StyledButton>
            </Spin>
          </div>
          &nbsp;
          {syncEDNServicesFromLoading === "empty" ? null : (
            <div
              style={{
                backgroundColor: syncESFromBackgroundColor,
                padding: "0 10px 0 10px",
                color: "white",
                borderRadius: "5px",
                fontWeight: "500",
                fontSize: "12px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              {syncEDNServicesFromLoading === "true"
                ? `Sync Started At: ${syncESFromDate}`
                : `Sync Completed At: ${syncESFromDate}`}
            </div>
          )}
        </div>
        {/* <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 2px 0",
            // border: "1px solid black",
          }}
        >
          <div style={{ display: "flex" }}>
            <div>
              <Button
                style={{
                  border: "none",
                  backgroundColor: "transparent",
                  marginTop: "-4px",
                }}
                onClick={clearAll}
              >
                <ReloadOutlined
                  style={{
                    color: "#009BDB",
                    fontSize: "20px",
                    padding: "0px",
                    margin: "0px",
                  }}
                />
              </Button>
            </div>
          </div>
          <div style={{ display: "flex" }}>
            <StyledButton color={"#3bbdc2"} onClick={exportSeed}>
              <RightSquareOutlined /> &nbsp; Export
            </StyledButton>
            &nbsp;
            <StyledButton color={"#009BDB"} onClick={fetch}>
              <RightSquareOutlined /> &nbsp; Fetch
            </StyledButton>
            &nbsp;
            <div>
              <StyledImportFileInput
                type="file"
                value={inputValue}
                onChange={() => importExcel}
                ref={inputRef}
              />
            </div>
          </div>
        </div> */}
        <StyledTable
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          size="small"
          scroll={{ x: 8000, y: height - 350 }}
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
