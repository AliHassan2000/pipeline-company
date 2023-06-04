import React, { useState, useRef, useEffect, useContext } from "react";
import styled from "styled-components";
import {
  Table,
  Button,
  Space,
  notification,
  Spin,
  Input,
  Menu,
  Dropdown,
} from "antd";
import Modal from "./modal";
// import OnboardModal from "./onboardModal";
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
// import { SEED_API } from "../../GlobalVar";
// import ShowSeedDevice from "./ShowSeedDevice";
import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
import { Context } from "../../../../context";
import { roles } from "../../../../utils/constants";

let excelData = [];
let columnFilters = {};
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const [user, setUser] = useState();
  // const { excelData, setExcelData, seedDevices, getSeedDevices } =
  //   useContext(Context);
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [dataSource, setDataSource] = useState(excelData);
  let [searchValue, setSearchValue] = useState(null);
  let [inputValue, setInputValue] = useState("");
  let [editRecord, setEditRecord] = useState(null);
  let [onboardRecord, setOnboardRecord] = useState(null);
  const [togleCheck, setTogleCheck] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  let selectedDevices = [];
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isOnboardModalVisible, setIsOnboardModalVisible] = useState(false);
  const inputRef = useRef(null);
  const searchRef = useRef(null);
  const history = useHistory();
  const [showSeed, setShowSeed] = useState(false);
  const [seedRecord, setSeedRecord] = useState(null);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  let [syncFromLoading, setSyncFromLoading] = useState(false);
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
        const res = await axios.get(baseUrl + "/getPower");
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

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "powerfeeds");
    XLSX.writeFile(wb, "powerfeeds.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
    // await axios
    //   .get(baseUrl + "/exportSeed")
    //   .then((response) => {
    //     openNotification();
    //     jsonToExcel(response.data);
    //     console.log(response);
    //   })
    //   .catch((error) => {
    //     setExportLoading(false);
    //     console.log(error);
    //   });
  };

  let seedTemp = [
    {
      device_id: "",
      // site_id: "",
      // rack_id: "",
      power_source_type: "",
      number_of_power_sources: "",
      psu1_fuse: "",
      psu2_fuse: "",
      psu3_fuse: "",
      psu4_fuse: "",
      psu5_fuse: "",
      psu6_fuse: "",

      psu1_pdu_details: "",
      psu2_pdu_details: "",
      psu3_pdu_details: "",
      psu4_pdu_details: "",
      psu5_pdu_details: "",
      psu6_pdu_details: "",

      psu1_dcdp_details: "",
      psu2_dcdp_details: "",
      psu3_dcdp_details: "",
      psu4_dcdp_details: "",
      psu5_dcdp_details: "",
      psu6_dcdp_details: "",
    },
  ];

  const exportTemplate = async () => {
    jsonToExcel(seedTemp);
    openNotification();
  };

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };

  const showOnboardModal = (record) => {
    setOnboardRecord(record);
    setIsOnboardModalVisible(true);
  };

  const showEditModal = () => {
    setIsModalVisible(true);
  };

  //---------------------------------------
  const syncFrom = async () => {
    setSyncFromLoading(true);
    await axios
      .get(baseUrl + "/syncFromInventory")
      .then((response) => {
        const promises = [];
        promises.push(
          axios.get(baseUrl + "/getPower").then((response) => {
            console.log(response.data);
            setRowCount(response.data.length);
            setDataSource(response.data);
            excelData = response.data;
            setSyncFromLoading(false);
          })
        );
        return Promise.all(promises);
      })
      .catch((err) => {
        console.log(err);
        setSyncFromLoading(false);
      });

    // await getSNTC();
  };
  //---------------------------------------

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const clearAll = () => {
    setSearchValue("");
    setDataSource(excelData);
    setRowCount(excelData.length);
    setSortedInfo(null);
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
      openSweetAlert("No device is selected to onboard.", "danger");
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

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postSeed = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/addPowerData", seed)
      .then((response) => {
        console.log("hahahehehoho");
        console.log(response.status);
        if (response?.response?.status == 500) {
          openSweetAlert(response?.response?.data?.response, "error");
          setLoading(false);
        } else {
          openSweetAlert("All Powers Added Successfully", "success");
        }
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/getPower")
            .then((response) => {
              // console.log("response===>", response);
              // setExcelData(response.data);
              excelData = response?.data;
              setRowCount(response?.data?.length);
              setDataSource(response?.data);
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
        // openSweetAlert("Something Went Wrong!", "danger");
        console.log("error ==> " + err);
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
      let data = convertToJson(headers, fileData);
      // console.log(excelData);
      postSeed(data);
      // setRowCount(data.length);
      // setDataSource(data);
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
    inputRef.current.addEventListener("input", importExcel);
  }, []);

  const staticOnboard = (record) => {
    history.push({
      pathname: "/staticonboarding",
      state: { detail: record },
    });
  };

  sortedInfo = sortedInfo || {};
  filteredInfo = filteredInfo || {};
  const FilterByNameInput = (title) => (
    <Input
      placeholder={title}
      // value={value}
      onChange={(e) => {
        // const currValue = e.target.value;
        // setValue(currValue);
        // const filteredData = data.filter((entry) =>
        //   entry.name.includes(currValue)
        // );
        // setDataSource(filteredData);
      }}
    />
  );
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
    // {
    //   title: "",
    //   key: "static",
    //   width: "1%",

    //   render: (text, record) => (
    //     <a>
    //       <span
    //         style={{ fontWeight: "600" }}
    //         onClick={() => {
    //           // staticOnboard(record);
    //           showOnboardModal(record);
    //         }}
    //       >
    //         S
    //       </span>
    //     </a>
    //   ),
    // },

    // {
    //   dataIndex: "ne_ip_address",
    //   key: "ne_ip_address",
    //   // ...getColumnSearchProps("ne_ip_address"),
    //   ...getColumnSearchProps(
    //     "ne_ip_address",
    //     "Ip Address",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   render: (text, record) => (
    //     <a
    //       onClick={() => {
    //         showSeedDev(record);
    //       }}
    //     >
    //       {text}
    //     </a>
    //   ),
    //   // sorter: (a, b) => a.ne_ip_address.length - b.ne_ip_address.length,
    //   // sortOrder: sortedInfo.columnKey === "ne_ip_address" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      dataIndex: "device_id",
      key: "device_id",
      ...getColumnSearchProps(
        "device_id",
        "Device Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hostname.length - b.hostname.length,
      // sortOrder: sortedInfo.columnKey === "hostname" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "Site Id",
    //   dataIndex: "site_id",
    //   key: "site_id",
    //   // ...getColumnSearchProps("site_id"),
    //   ...getColumnSearchProps(
    //     "site_id",
    //     "Site Id",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.site_id.length - b.site_id.length,
    //   // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Rack Id",
    //   dataIndex: "rack_id",
    //   key: "rack_id",
    //   // ...getColumnSearchProps("site_id"),
    //   ...getColumnSearchProps(
    //     "rack_id",
    //     "Rack Id",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.site_id.length - b.site_id.length,
    //   // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "status",
        "Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "power_source_type",
      key: "power_source_type",
      // ...getColumnSearchProps("sw_type"),
      ...getColumnSearchProps(
        "power_source_type",
        "Power Source Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sw_type.length - b.sw_type.length,
      // sortOrder: sortedInfo.columnKey === "sw_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "number_of_power_sources",
      key: "number_of_power_sources",
      // ...getColumnSearchProps("onboard_status"),
      ...getColumnSearchProps(
        "number_of_power_sources",
        "No. Of Power Sources",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.onboard_status.length - b.onboard_status.length,
      // sortOrder: sortedInfo.columnKey === "onboard_status" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu1_fuse",
      key: "psu1_fuse",
      // ...getColumnSearchProps("device_id"),
      ...getColumnSearchProps(
        "psu1_fuse",
        "PSU1 Fuse",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_id.length - b.device_id.length,
      // sortOrder: sortedInfo.columnKey === "device_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu2_fuse",
      key: "psu2_fuse",
      // ...getColumnSearchProps("device_ru"),
      ...getColumnSearchProps(
        "psu2_fuse",
        "PSU2 Fuse",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_ru.length - b.device_ru.length,
      // sortOrder: sortedInfo.columnKey === "device_ru" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu3_fuse",
      key: "psu3_fuse",
      // ...getColumnSearchProps("device_ru"),
      ...getColumnSearchProps(
        "psu3_fuse",
        "PSU3 Fuse",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_ru.length - b.device_ru.length,
      // sortOrder: sortedInfo.columnKey === "device_ru" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu4_fuse",
      key: "psu4_fuse",
      // ...getColumnSearchProps("device_ru"),
      ...getColumnSearchProps(
        "psu4_fuse",
        "PSU4 Fuse",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_ru.length - b.device_ru.length,
      // sortOrder: sortedInfo.columnKey === "device_ru" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu5_fuse",
      key: "psu5_fuse",
      // ...getColumnSearchProps("device_ru"),
      ...getColumnSearchProps(
        "psu5_fuse",
        "PSU5 Fuse",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_ru.length - b.device_ru.length,
      // sortOrder: sortedInfo.columnKey === "device_ru" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu6_fuse",
      key: "psu6_fuse",
      // ...getColumnSearchProps("device_ru"),
      ...getColumnSearchProps(
        "psu6_fuse",
        "PSU6 Fuse",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_ru.length - b.device_ru.length,
      // sortOrder: sortedInfo.columnKey === "device_ru" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu1_pdu_details",
      key: "psu1_pdu_details",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "psu1_pdu_details",
        "PSU1 PDU Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu2_pdu_details",
      key: "psu2_pdu_details",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "psu2_pdu_details",
        "PSU2 PDU Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu3_pdu_details",
      key: "psu3_pdu_details",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "psu3_pdu_details",
        "PSU3 PDU Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu4_pdu_details",
      key: "psu4_pdu_details",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "psu4_pdu_details",
        "PSU4 PDU Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu5_pdu_details",
      key: "psu5_pdu_details",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "psu5_pdu_details",
        "PSU5 PDU Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu6_pdu_details",
      key: "psu6_pdu_details",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "psu6_pdu_details",
        "PSU6 PDU Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu1_dcdp_details",
      key: "psu1_dcdp_details",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "psu1_dcdp_details",
        "PSU1 DCDP Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu2_dcdp_details",
      key: "psu2_dcdp_details",
      // ...getColumnSearchProps("department"),
      ...getColumnSearchProps(
        "psu2_dcdp_details",
        "PSU2 DCDP Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.department.length - b.department.length,
      // sortOrder: sortedInfo.columnKey === "department" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu3_dcdp_details",
      key: "psu3_dcdp_details",
      // ...getColumnSearchProps("department"),
      ...getColumnSearchProps(
        "psu3_dcdp_details",
        "PSU3 DCDP Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.department.length - b.department.length,
      // sortOrder: sortedInfo.columnKey === "department" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu4_dcdp_details",
      key: "psu4_dcdp_details",
      // ...getColumnSearchProps("department"),
      ...getColumnSearchProps(
        "psu4_dcdp_details",
        "PSU4 DCDP Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.department.length - b.department.length,
      // sortOrder: sortedInfo.columnKey === "department" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu5_dcdp_details",
      key: "psu5_dcdp_details",
      // ...getColumnSearchProps("department"),
      ...getColumnSearchProps(
        "psu5_dcdp_details",
        "PSU5 DCDP Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.department.length - b.department.length,
      // sortOrder: sortedInfo.columnKey === "department" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "psu6_dcdp_details",
      key: "psu6_dcdp_details",
      // ...getColumnSearchProps("department"),
      ...getColumnSearchProps(
        "psu6_dcdp_details",
        "PSU6 DCDP Details",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.department.length - b.department.length,
      // sortOrder: sortedInfo.columnKey === "department" && sortedInfo.order,
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

  const opensweetalertdanger = () => {
    Swal.fire({
      title: "No power data selected to delete!",
      // text: "OOPS",
      type: "warning",
    });
  };

  const handleDelete = () => {
    if (selectedRowKeys.length > 0) {
      axios
        .post(baseUrl + "/deletePower", {
          power_ids: selectedRowKeys,
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getPower")
              .then((response) => {
                console.log(response.data);
                setDataSource(response.data);
                excelData = response.data;
                setRowCount(excelData.length);
                setLoading(false);
              })
              .catch((error) => {
                console.log(error);
                setLoading(false);
              })
          );
          return Promise.all(promises);
        })
        .catch((err) => {
          console.log(err);
          setLoading(false);
        });
    } else {
      opensweetalertdanger("No device is selected to delete.");
    }
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
            excelData={excelData}
            setRowCount={setRowCount}
            editRecord={editRecord}
          />
        )}

        <StyledHeading>
          Power Feeds
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns:{columns.length - 1}
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
            <PlusOutlined /> &nbsp; Add Power
          </StyledButton> */}
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
            {/* <Link to="/onboard"> */}
            {/* <StyledButton
              onClick={handleOnboard}
              color={"#009BDB"}
              // style={{ paddingTop: "0px" }}
            >
              <PlusOutlined /> &nbsp; On Board
            </StyledButton> */}

            {/* <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
              <RightSquareOutlined /> &nbsp; Delete
            </StyledButton> */}

            {/* <Spin spinning={syncFromLoading}>
              <StyledButton color={"#3bbdc2"} onClick={syncFrom} >
                <RightSquareOutlined /> &nbsp; Sync From Inventory
              </StyledButton>
            </Spin> */}

            {/* </Link> */}
            {/* &nbsp;&nbsp;&nbsp;&nbsp;
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
            </div> */}
          </div>
          <div style={{ display: "flex" }}>
            <StyledButton color={"#3bbdc2"} onClick={exportTemplate}>
              <RightSquareOutlined /> &nbsp; Export Template
            </StyledButton>
            &nbsp;
            <Spin spinning={exportLoading}>
              <Dropdown overlay={menu} trigger={["click"]}>
                <StyledButton color={"#3bbdc2"}>
                  Export
                  <DownOutlined />
                </StyledButton>
              </Dropdown>
            </Spin>
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
        </div>
        <StyledTable
          size="small"
          scroll={{ x: 6400, y: height - 350 }}
          onChange={handleChange}
          // rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="power_id"
          style={{ whiteSpace: "pre" }}
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
        />
      </Spin>
    </>
  );
};

export default Index;
