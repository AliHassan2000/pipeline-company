import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import {
  Table,
  Button,
  Space,
  notification,
  Spin,
  Input,
  Select,
  Menu,
  Dropdown,
} from "antd";
import Modal from "./modal";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../utils/axios";
import Search from "../../../components/search";
import { StyledTable } from "../../../components/table/main.styles";
import { StyledButton } from "../../../components/button/main.styles";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../components/input/main.styles";
import {
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import Swal from "sweetalert2";
import { Link, useHistory } from "react-router-dom";
// import { SEED_API } from "../../GlobalVar";
// import ShowSeedDevice from "../../seed/ShowSeedDevice";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { roles } from "../../../utils/constants.js";
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
          .get(baseUrl + "/getAllEdnDcCapacityDates")
          .then((response) => {
            setDates(response.data);
            console.log(response);
          });

        const status = await axios.get(
          baseUrl + "/getEdnDcCapacityFetchStatus"
        );
        console.log("popo");
        console.log(status);
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

        const res = await axios.get(baseUrl + "/getAllEdnDcCapacity");
        excelData = res.data;
        setDataSource(excelData);
        setRowCount(excelData.length);
        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

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

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "edndccapacity");
    XLSX.writeFile(wb, "edndccapacity.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
    // await axios
    //   .get(baseUrl + "/exportEdnCdpLegacy")
    //   .then((response) => {
    //     openNotification();
    //     jsonToExcel(response.data);
    //     console.log(response);
    //     setExportLoading(false);
    //   })
    //   .catch((error) => {
    //     setExportLoading(false);
    //     console.log(error);
    //   });
  };

  let seedTemp = [
    {
      site_id: "",
      device_id: "",
      device_ip: "",

      total_1g_ports: "",
      total_10g_ports: "",
      total_25g_ports: "",
      total_40g_ports: "",
      total_100g_ports: "",
      total_fast_ethernet_ports: "",

      connected_1g: "",
      connected_10g: "",
      connected_25g: "",
      connected_40g: "",
      connected_100g: "",
      connected_fast_ethernet: "",

      not_connected_1g: "",
      not_connected_10g: "",
      not_connected_25g: "",
      not_connected_40g: "",
      not_connected_100g: "",
      not_connected_fast_ethernet: "",

      unused_sfps_1g: "",
      unused_sfps_10g: "",
      unused_sfps_10g: "",
      unused_sfps_25g: "",
      unused_sfps_40g: "",
      unused_sfps_100g: "",
    },
  ];

  const fetch = async () => {
    setFetchLoading("true");
    setFetchDate(new Date().toLocaleString());
    setBackgroundColor("red");
    await axios
      .get(baseUrl + "/fetchEdnDcCapacity")
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
    // {
    //   title: "",
    //   key: "edit",
    //   width: "1%",

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
    // {
    //   title: "Region",
    //   dataIndex: "region",
    //   key: "region",
    //   // ...getColumnSearchProps("edn_cdp_legacy_id"),
    //   ...getColumnSearchProps(
    //     "region",
    //     "Region",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.edn_cdp_legacy_id.length - b.edn_cdp_legacy_id.length,
    //   // sortOrder:
    //   //   sortedInfo.columnKey === "edn_cdp_legacy_id" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      title: "Site Id",
      dataIndex: "site_id",
      key: "site_id",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "site_id",
        "Site Id",
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
      dataIndex: "device_id",
      key: "device_id",
      // ...getColumnSearchProps("device_a_interface"),
      ...getColumnSearchProps(
        "device_id",
        "Device Id",
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
      dataIndex: "device_ip",
      key: "device_ip",
      // ...getColumnSearchProps("device_a_trunk_name"),
      ...getColumnSearchProps(
        "device_ip",
        "Device Ip",
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
      dataIndex: "os_version",
      key: "os_version",
      // ...getColumnSearchProps("device_a_trunk_name"),
      ...getColumnSearchProps(
        "os_version",
        "OS Version",
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
      dataIndex: "total_1g_ports",
      key: "total_1g_ports",
      // ...getColumnSearchProps("device_a_ip"),
      ...getColumnSearchProps(
        "total_1g_ports",
        "Total 1G Ports",
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
      dataIndex: "total_10g_ports",
      key: "total_10g_ports",
      // ...getColumnSearchProps("device_a_port_desc"),
      ...getColumnSearchProps(
        "total_10g_ports",
        "Total 10G Ports",
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
      dataIndex: "total_25g_ports",
      key: "total_25g_ports",
      // ...getColumnSearchProps("device_a_port_desc"),
      ...getColumnSearchProps(
        "total_25g_ports",
        "Total 25G Ports",
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
      dataIndex: "total_40g_ports",
      key: "total_40g_ports",
      // ...getColumnSearchProps("device_b_system_name"),
      ...getColumnSearchProps(
        "total_40g_ports",
        "Total 40G Ports",
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
      dataIndex: "total_100g_ports",
      key: "total_100g_ports",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "total_100g_ports",
        "Total 100G Ports",
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
      dataIndex: "total_fast_ethernet_ports",
      key: "total_fast_ethernet_ports",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "total_fast_ethernet_ports",
        "Total Fast Ethernet Ports",
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
      dataIndex: "connected_1g",
      key: "connected_1g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "connected_1g",
        "Connected 1G",
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
      dataIndex: "connected_10g",
      key: "connected_10g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "connected_10g",
        "Connected 10G",
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
      dataIndex: "connected_25g",
      key: "connected_25g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "connected_25g",
        "Connected 25G",
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
      dataIndex: "connected_40g",
      key: "connected_40g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "connected_40g",
        "Connected 40G",
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
      dataIndex: "connected_100g",
      key: "connected_100g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "connected_100g",
        "Connected 100G",
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
      dataIndex: "connected_fast_ethernet",
      key: "connected_fast_ethernet",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "connected_fast_ethernet",
        "Connected Fast Ethernet",
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
      dataIndex: "not_connected_1g",
      key: "not_connected_1g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "not_connected_1g",
        "Not Connected 1G",
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
      dataIndex: "not_connected_10g",
      key: "not_connected_10g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "not_connected_10g",
        "Not Connected 10G",
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
      dataIndex: "not_connected_25g",
      key: "not_connected_25g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "not_connected_25g",
        "Not Connected 25G",
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
      dataIndex: "not_connected_40g",
      key: "not_connected_40g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "not_connected_40g",
        "Not Connected 40G",
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
      dataIndex: "not_connected_100g",
      key: "not_connected_100g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "not_connected_100g",
        "Not Connected 100G",
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
      dataIndex: "not_connected_fast_ethernet",
      key: "not_connected_fast_ethernet",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "not_connected_fast_ethernet",
        "Not Connected Fast Ethernet",
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
      dataIndex: "unused_sfps_1g",
      key: "unused_sfps_1g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "unused_sfps_1g",
        "Unused SFPs 1G",
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
      dataIndex: "unused_sfps_10g",
      key: "unused_sfps_10g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "unused_sfps_10g",
        "Unused SFPs 10G",
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
      dataIndex: "unused_sfps_25g",
      key: "unused_sfps_25g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "unused_sfps_25g",
        "Unused SFPs 25G",
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
      dataIndex: "unused_sfps_40g",
      key: "unused_sfps_40g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "unused_sfps_40g",
        "Unused SFPs 40G",
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
      dataIndex: "unused_sfps_100g",
      key: "unused_sfps_100g",
      // ...getColumnSearchProps("device_b_ip"),
      ...getColumnSearchProps(
        "unused_sfps_100g",
        "Unused SFPs 100G",
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
      dataIndex: "created_by",
      key: "created_by",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "created_by",
        "Created By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
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
      hidden: user?.user_role !== roles.admin,
    },
  ].filter((item) => !item.hidden);

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
      .post(baseUrl + "/getAllEdnDcCapacityByDate", { date: value })
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

  const exportFiltered = async () => {
    setExportLoading(true);
    jsonToExcel(dataSource, "filteredednmaclegacy.xlsx");
    setExportLoading(false);
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

        <StyledHeading>
          EDN DC Capacity
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length}
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
          <div>
            Select Date: &nbsp;&nbsp;
            <Select
              // defaultValue={dates.length > 0 ? dates[0] : null}
              style={{ width: 200 }}
              onChange={handleSelectChange}
              disabled={user?.user_role === roles.user}
            >
              {getOptions(dates)}
            </Select>
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div style={{ display: "flex" }}>
            <Spin spinning={fetchLoading === "true" ? true : false}>
              <StyledButton
                color={"#009BDB"}
                onClick={fetch}
                disabled={user?.user_role !== roles.admin}
              >
                <RightSquareOutlined /> &nbsp; Fetch
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
                  ? `Fetching Started At: ${fetchDate}`
                  : `Fetching Completed At: ${fetchDate}`}
              </div>
            )}
          </div>
          <Spin spinning={exportLoading}>
            <Dropdown overlay={menu} trigger={["click"]}>
              <StyledButton color={"#3bbdc2"}>
                Export
                <DownOutlined />
              </StyledButton>
            </Dropdown>
          </Spin>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 2px 0",
            // border: "1px solid black",
          }}
        >
          <div style={{ display: "flex" }}>
            {/* <div>
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
            </div> */}
          </div>
          {/* <div style={{ display: "flex" }}>
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
          </div> */}
        </div>
        <StyledTable
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          size="small"
          scroll={{ x: 6000, y: height - 350 }}
          onChange={handleChange}
          // rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="edn_dc_capacity_id"
          style={{ whiteSpace: "pre" }}
        />
      </Spin>
    </>
  );
};

export default Index;
