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
import OnboardModal from "./onboardModal";
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
import ShowSeedDevice from "./ShowSeedDevice";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { Context } from "../../../context";
import { roles } from "../../../utils/constants";

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
      // try {
      //   if (seedDevices.length === 0) {
      //     let data = await getSeedDevices();
      //     console.log(data);
      //     setRowCount(data.length);
      //     setDataSource(data);
      //   } else {
      //     setRowCount(seedDevices.length);
      //     setDataSource(seedDevices);
      //   }
      //   setLoading(false);
      // } catch (err) {
      //   console.log(err);
      //   setLoading(false);
      // }
      try {
        const res = await axios.get(baseUrl + "/getSeeds");
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
    XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
    XLSX.writeFile(wb, "seeddevices.xlsx");
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
      ne_ip_address: "",
      device_id: "",
      device_ru: "",
      parent: "",
      // item_code: "",
      // item_desc: "",
      clei: "",
      // department: "",
      // section: "",
      criticality: "",
      function: "",
      // vuln_fix_plan_status: "",
      // vuln_ops_severity: "",
      cisco_domain: "",
      virtual: "",
      authentication: "",
      subrack_id_number: "",
      hostname: "",
      // sw_version: "",
      sw_type: "",
      vendor: "",
      asset_type: "",
      operation_status: "",
      site_id: "",
      site_type: "",
      rack_id: "",
      contract_number: "",
      contract_expiry: "",
      // region: "",
      // site_name: "",
      // latitude: "",
      // longitude: "",
      // city: "",
      // datacentre_status: "",

      // floor: "",
      // rack_name: "",
      // serial_number: "",
      // manufactuer_date: "",
      // unit_position: "",
      // rack_status: "",
      // device_ru: "",
      rfs_date: "",
      // height: "",
      // width: "",
      // depth: "",
      // pn_code: "",
      tag_id: "",
      // rack_model: "",
      integrated_with_aaa: "",
      integrated_with_paam: "",
      approved_mbss: "",
      mbss_implemented: "",
      mbss_integration_check: "",
      integrated_with_siem: "",
      threat_cases: "",
      vulnerability_scanning: "",
      vulnerability_severity: "",
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

  // const handleColumnInput = (e) => {
  //   setSearchText(e.target.value);
  //   console.log("hello");
  //   // console.log(column);
  //   console.log(e.target.value);
  //   let filteredSuggestions = excelData.filter(
  //     (d) =>
  //       JSON.stringify(d["ne_ip_address"])
  //         .replace(" ", "")
  //         .toLowerCase()
  //         .indexOf(e.target.value.toLowerCase()) > -1
  //   );
  //   setRowCount(filteredSuggestions.length);
  //   setDataSource(filteredSuggestions);
  // };

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
      .post(baseUrl + "/addSeed", seed)
      .then((response) => {
        console.log("hahahehehoho");
        console.log(response.status);
        if (response?.response?.status == 500) {
          openSweetAlert(response?.response?.data?.response, "error");
          setLoading(false);
        } else {
          openSweetAlert("Seed Added Successfully", "success");
        }
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/getSeeds")
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
    console.log(file);
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

    {
      title: "",
      key: "static",
      width: "35px",

      render: (text, record) => (
        <a>
          <span
            style={{ fontWeight: "600" }}
            onClick={() => {
              // staticOnboard(record);
              showOnboardModal(record);
            }}
          >
            S
          </span>
        </a>
      ),
    },

    {
      title: "Ip Address",
      dataIndex: "ne_ip_address",
      key: "ne_ip_address",
      // ...getColumnSearchProps("ne_ip_address"),
      ...getColumnSearchProps(
        "ne_ip_address",
        "Ip Address",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      render: (text, record) => (
        <a
          onClick={() => {
            showSeedDev(record);
          }}
        >
          {text}
        </a>
      ),
      // sorter: (a, b) => a.ne_ip_address.length - b.ne_ip_address.length,
      // sortOrder: sortedInfo.columnKey === "ne_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Host Name",
      dataIndex: "hostname",
      key: "hostname",
      ...getColumnSearchProps(
        "hostname",
        "Host Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hostname.length - b.hostname.length,
      // sortOrder: sortedInfo.columnKey === "hostname" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Site Id",
      dataIndex: "site_id",
      key: "site_id",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "site_id",
        "Site Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_id.length - b.site_id.length,
      // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Rack Id",
      dataIndex: "rack_id",
      key: "rack_id",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "rack_id",
        "Rack Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_id.length - b.site_id.length,
      // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Sw Type",
      dataIndex: "sw_type",
      key: "sw_type",
      // ...getColumnSearchProps("sw_type"),
      ...getColumnSearchProps(
        "sw_type",
        "SW Type",
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
      title: "Onboard Status",
      dataIndex: "onboard_status",
      key: "onboard_status",
      // ...getColumnSearchProps("onboard_status"),
      ...getColumnSearchProps(
        "onboard_status",
        "Onboard Status",
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
      title: "Device Id",
      dataIndex: "device_id",
      key: "device_id",
      // ...getColumnSearchProps("device_id"),
      ...getColumnSearchProps(
        "device_id",
        "Device Id",
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
      title: "Device Ru",
      dataIndex: "device_ru",
      key: "device_ru",
      // ...getColumnSearchProps("device_ru"),
      ...getColumnSearchProps(
        "device_ru",
        "Device Ru",
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
      title: "Parent",
      dataIndex: "parent",
      key: "parent",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "parent",
        "Parent",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "VULN Fix Plan Status",
      dataIndex: "vuln_fix_plan_status",
      key: "vuln_fix_plan_status",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "vuln_fix_plan_status",
        "VULN Fix Plan Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "vuln_ops_severity",
      key: "vuln_ops_severity",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "vuln_ops_severity",
        "VULN OPS Severity",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   dataIndex: "item_code",
    //   key: "item_code",
    //   // ...getColumnSearchProps("authentication"),
    //   ...getColumnSearchProps(
    //     "item_code",
    //     "Item Code",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.authentication.length - b.authentication.length,
    //   // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   dataIndex: "item_desc",
    //   key: "item_desc",
    //   // ...getColumnSearchProps("authentication"),
    //   ...getColumnSearchProps(
    //     "item_desc",
    //     "Item Desc",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.authentication.length - b.authentication.length,
    //   // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      dataIndex: "clei",
      key: "clei",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "clei",
        "Clei",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "Department",
    //   dataIndex: "department",
    //   key: "department",
    //   width: "3.5%",
    //   // ...getColumnSearchProps("department"),
    //   ...getColumnSearchProps(
    //     "department",
    //     "Department",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.department.length - b.department.length,
    //   // sortOrder: sortedInfo.columnKey === "department" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Section",
    //   dataIndex: "section",
    //   key: "section",
    //   width: "3.5%",
    //   // ...getColumnSearchProps("section"),
    //   ...getColumnSearchProps(
    //     "section",
    //     "Section",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.section.length - b.section.length,
    //   // sortOrder: sortedInfo.columnKey === "section" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      title: "Criticality",
      dataIndex: "criticality",
      key: "criticality",
      // ...getColumnSearchProps("criticality"),
      ...getColumnSearchProps(
        "criticality",
        "Criticality",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.criticality.length - b.criticality.length,
      // sortOrder: sortedInfo.columnKey === "criticality" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "function",
      key: "function",
      // ...getColumnSearchProps("function"),
      ...getColumnSearchProps(
        "function",
        "Function",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.function.length - b.function.length,
      // sortOrder: sortedInfo.columnKey === "function" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "cisco_domain",
      key: "cisco_domain",
      // ...getColumnSearchProps("domain"),
      ...getColumnSearchProps(
        "cisco_domain",
        "Cisco Domain",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.domain.length - b.domain.length,
      // sortOrder: sortedInfo.columnKey === "domain" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Virtual",
      dataIndex: "virtual",
      key: "virtual",
      // ...getColumnSearchProps("virtual"),
      ...getColumnSearchProps(
        "virtual",
        "Virtual",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.virtual.length - b.virtual.length,
      // sortOrder: sortedInfo.columnKey === "virtual" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Authentication",
      dataIndex: "authentication",
      key: "authentication",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "authentication",
        "Authentication",
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
      title: "Subrack Id Number",
      dataIndex: "subrack_id_number",
      key: "subrack_id_number",
      // ...getColumnSearchProps("subrack_id_number"),
      ...getColumnSearchProps(
        "subrack_id_number",
        "Subrack Id Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.subrack_id_number.length - b.subrack_id_number.length,
      // sortOrder:
      //   sortedInfo.columnKey === "subrack_id_number" && sortedInfo.order,
      ellipsis: true,
    },

    // {
    //   title: "Sw Version",
    //   dataIndex: "sw_version",
    //   key: "sw_version",
    //   ...getColumnSearchProps("sw_version"),
    //   sorter: (a, b) => a.sw_version.length - b.sw_version.length,
    //   sortOrder: sortedInfo.columnKey === "sw_version" && sortedInfo.order,
    //   ellipsis: true,
    // },

    {
      title: "Site Type",
      dataIndex: "site_type",
      key: "site_type",
      // ...getColumnSearchProps("site_type"),
      ...getColumnSearchProps(
        "site_type",
        "Site Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_type.length - b.site_type.length,
      // sortOrder: sortedInfo.columnKey === "site_type" && sortedInfo.order,
      ellipsis: true,
    },

    {
      title: "Vendor",
      dataIndex: "vendor",
      key: "vendor",
      // ...getColumnSearchProps("vendor"),
      ...getColumnSearchProps(
        "vendor",
        "Vendor",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.vendor.length - b.vendor.length,
      // sortOrder: sortedInfo.columnKey === "vendor" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Asset Type",
      dataIndex: "asset_type",
      key: "asset_type",
      // ...getColumnSearchProps("asset_type"),
      ...getColumnSearchProps(
        "asset_type",
        "Asset Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.asset_type.length - b.asset_type.length,
      // sortOrder: sortedInfo.columnKey === "asset_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Operation Status",
      dataIndex: "operation_status",
      key: "operation_status",
      // ...getColumnSearchProps("operation_status"),
      ...getColumnSearchProps(
        "operation_status",
        "Operation Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.operation_status.length - b.operation_status.length,
      // sortOrder:
      //   sortedInfo.columnKey === "operation_status" && sortedInfo.order,
      ellipsis: true,
    },
    //////////////////////////////////////////////
    // {
    //   title: "Region",
    //   dataIndex: "region",
    //   key: "region",
    //   // ...getColumnSearchProps("region"),
    //   ...getColumnSearchProps(
    //     "region",
    //     "Region",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.rack_name.length - b.rack_name.length,
    //   // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Site Name",
    //   dataIndex: "site_name",
    //   key: "site_name",
    //   // ...getColumnSearchProps("site_name"),
    //   ...getColumnSearchProps(
    //     "site_name",
    //     "Site Name",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.site_name.length - b.site_name.length,
    //   // sortOrder: sortedInfo.columnKey === "site_name" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Latitude",
    //   dataIndex: "latitude",
    //   key: "latitude",
    //   // ...getColumnSearchProps("latitude"),
    //   ...getColumnSearchProps(
    //     "latitude",
    //     "Latitude",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.region.length - b.region.length,
    //   // sortOrder: sortedInfo.columnKey === "latitude" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Longtitude",
    //   dataIndex: "longitude",
    //   key: "longitude",
    //   // ...getColumnSearchProps("status"),
    //   ...getColumnSearchProps(
    //     "longitude",
    //     "Longitude",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.region.length - b.region.length,
    //   // sortOrder: sortedInfo.columnKey === "longtitude" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "City",
    //   dataIndex: "city",
    //   key: "city",
    //   // ...getColumnSearchProps("city"),
    //   ...getColumnSearchProps(
    //     "city",
    //     "City",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.city.length - b.city.length,
    //   // sortOrder: sortedInfo.columnKey === "city" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Datacentre Status",
    //   dataIndex: "datacentre_status",
    //   key: "datacentre_status",
    //   // ...getColumnSearchProps("datacentre_status"),
    //   ...getColumnSearchProps(
    //     "datacentre_status",
    //     "Datacentre Status",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.datacentre_status.length - b.datacentre_status.length,
    //   // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
    //   ellipsis: true,
    // },

    ////////////////////////////////////////////////////////////////////////////
    // {
    //   title: "Floor",
    //   dataIndex: "floor",
    //   key: "floor",
    //   // ...getColumnSearchProps("floor"),
    //   ...getColumnSearchProps(
    //     "floor",
    //     "Floor",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.floor.length - b.floor.length,
    //   // sortOrder: sortedInfo.columnKey === "floor" && sortedInfo.order,
    //   ellipsis: true,
    // },

    // {
    //   title: "Rack Name",
    //   dataIndex: "rack_name",
    //   key: "rack_name",
    //   // ...getColumnSearchProps("rack_name"),
    //   ...getColumnSearchProps(
    //     "rack_name",
    //     "Rack Name",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.rack_name.length - b.rack_name.length,
    //   // sortOrder: sortedInfo.columnKey === "rack_name" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Serial Number",
    //   dataIndex: "serial_number",
    //   key: "serial_number",
    //   // ...getColumnSearchProps("serial_number"),
    //   ...getColumnSearchProps(
    //     "serial_number",
    //     "Serial Number",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.serial_number.length - b.serial_number.length,
    //   // sortOrder: sortedInfo.columnKey === "serial_number" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Manufacture Date",
    //   dataIndex: "manufactuer_date",
    //   key: "manufactuer_date",
    //   // ...getColumnSearchProps("manufactuer_date"),
    //   ...getColumnSearchProps(
    //     "manufactuer_date",
    //     "Manufacture Date",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.manufactuer_date.length - b.manufactuer_date.length,
    //   // sortOrder:
    //   //   sortedInfo.columnKey === "manufactuer_date" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Unit Position",
    //   dataIndex: "unit_position",
    //   key: "unit_position",
    //   // ...getColumnSearchProps("unit_position"),
    //   ...getColumnSearchProps(
    //     "unit_position",
    //     "Unit Position",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.unit_position.length - b.unit_position.length,
    //   // sortOrder: sortedInfo.columnKey === "unit_position" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Rack Status",
    //   dataIndex: "rack_status",
    //   key: "rack_status",
    //   // ...getColumnSearchProps("rack_status"),
    //   ...getColumnSearchProps(
    //     "rack_status",
    //     "Rack Status",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.rack_status.length - b.rack_status.length,
    //   // sortOrder: sortedInfo.columnKey === "rack_status" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Device Ru",
    //   dataIndex: "device_ru",
    //   key: "device_ru",
    //   // ...getColumnSearchProps("device_ru"),
    //   ...getColumnSearchProps(
    //     "device_ru",
    //     "Device Ru",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.device_ru.length - b.device_ru.length,
    //   // sortOrder: sortedInfo.columnKey === "device_ru" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      dataIndex: "rfs_date",
      key: "rfs_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "rfs_date",
        "RFS",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rfs_date.length - b.rfs_date.length,
      // sortOrder: sortedInfo.columnKey === "rfs_date" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "Height",
    //   dataIndex: "height",
    //   key: "height",
    //   // ...getColumnSearchProps("height"),
    //   ...getColumnSearchProps(
    //     "height",
    //     "Height",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.height.length - b.height.length,
    //   // sortOrder: sortedInfo.columnKey === "height" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Width",
    //   dataIndex: "width",
    //   key: "width",
    //   // ...getColumnSearchProps("width"),
    //   ...getColumnSearchProps(
    //     "width",
    //     "Width",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.width.length - b.width.length,
    //   // sortOrder: sortedInfo.columnKey === "width" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Depth",
    //   dataIndex: "depth",
    //   key: "depth",
    //   // ...getColumnSearchProps("depth"),
    //   ...getColumnSearchProps(
    //     "depth",
    //     "Depth",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.depth.length - b.depth.length,
    //   // sortOrder: sortedInfo.columnKey === "depth" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "PN Code",
    //   dataIndex: "pn_code",
    //   key: "pn_code",
    //   // ...getColumnSearchProps("pn_code"),
    //   ...getColumnSearchProps(
    //     "pn_code",
    //     "PN Code",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.pn_code.length - b.pn_code.length,
    //   // sortOrder: sortedInfo.columnKey === "pn_code" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      title: "Tag Id",
      dataIndex: "tag_id",
      key: "tag_id",
      // ...getColumnSearchProps("tag_id"),
      ...getColumnSearchProps(
        "tag_id",
        "Tag Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.tag_id.length - b.tag_id.length,
      // sortOrder: sortedInfo.columnKey === "tag_id" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "Rack Model",
    //   dataIndex: "rack_model",
    //   key: "rack_model",
    //   // ...getColumnSearchProps("rack_model"),
    //   ...getColumnSearchProps(
    //     "rack_model",
    //     "Rack Model",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.rack_model.length - b.rack_model.length,
    //   // sortOrder: sortedInfo.columnKey === "rack_model" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      title: "Contract Number",
      dataIndex: "contract_number",
      key: "contract_number",
      // ...getColumnSearchProps("contract_number"),
      ...getColumnSearchProps(
        "contract_number",
        "Contract Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.contract_number.length - b.contract_number.length,
      // sortOrder: sortedInfo.columnKey === "contract_number" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "contract_expiry",
      key: "contract_expiry",
      ...getColumnSearchProps(
        "contract_expiry",
        "Contract Expiry",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    ////////////////////////////////////////////////////////////
    {
      dataIndex: "integrated_with_aaa",
      key: "integrated_with_aaa",
      ...getColumnSearchProps(
        "integrated_with_aaa",
        "Integrated with AAA",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "integrated_with_paam",
      key: "integrated_with_paam",
      ...getColumnSearchProps(
        "integrated_with_paam",
        "Integrated with PAAM",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "approved_mbss",
      key: "approved_mbss",
      ...getColumnSearchProps(
        "approved_mbss",
        "Approved MBSS",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "mbss_implemented",
      key: "mbss_implemented",
      ...getColumnSearchProps(
        "mbss_implemented",
        "MBSS Implemented",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "mbss_integration_check",
      key: "mbss_integration_check",
      ...getColumnSearchProps(
        "mbss_integration_check",
        "MBSS Integration Check",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "integrated_with_siem",
      key: "integrated_with_siem",
      ...getColumnSearchProps(
        "integrated_with_siem",
        "Integrated with Siem",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "threat_cases",
      key: "threat_cases",
      ...getColumnSearchProps(
        "threat_cases",
        "Threat Cases",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "vulnerability_scanning",
      key: "vulnerability_scanning",
      ...getColumnSearchProps(
        "vulnerability_scanning",
        "Vulnerability Scanning",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "vulnerability_severity",
      key: "vulnerability_severity",
      ...getColumnSearchProps(
        "vulnerability_severity",
        "Vulnerability Severity",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    // {
    //   title: "",
    //   key: "edit",
    //   width: "0.9%",
    //   fixed: "right",

    //   render: (text, record) => (
    //     <StyledButton
    //       color={"#009BDB"}
    //       style={{
    //         width: "90%",
    //         fontSize: "10px",
    //         height: "25px",
    //         margin: "0px",
    //       }}
    //       onClick={() => {
    //         edit(record);
    //       }}
    //     >
    //       Edit
    //     </StyledButton>
    //   ),
    // },
    // {
    //   title: "",
    //   key: "edit",
    //   width: "1%",
    //   fixed: "right",
    //   render: (text, record) => (
    //     <StyledButton
    //       color={"#009BDB"}
    //       style={{ width: "90%", fontSize: "10px", height: "25px" }}
    //       onClick={() => {
    //         showSeedDev(record);
    //       }}
    //     >
    //       show
    //     </StyledButton>
    //   ),
    // },
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
        <ShowSeedDevice
          showSeed={showSeed}
          setShowSeed={setShowSeed}
          seedRecord={seedRecord}
        />

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

        {isOnboardModalVisible && (
          <OnboardModal
            isModalVisible={isOnboardModalVisible}
            setIsModalVisible={setIsOnboardModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            excelData={excelData}
            setRowCount={setRowCount}
            record={onboardRecord}
          />
        )}

        <StyledHeading>
          Devices Seed Portal
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length - 2}
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
          <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; Add Device
          </StyledButton>
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
            <StyledButton
              onClick={handleOnboard}
              color={"#009BDB"}
              // style={{ paddingTop: "0px" }}
            >
              <PlusOutlined /> &nbsp; On Board
            </StyledButton>
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
          scroll={{ x: 8000, y: height - 350 }}
          onChange={handleChange}
          rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="ne_ip_address"
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
