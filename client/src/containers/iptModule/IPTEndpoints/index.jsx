import React, { useState, useRef, useEffect } from "react";
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
// import Modal from "./modals/cdpLegacy";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../utils/axios";
import Search from "../../../components/search";
import { StyledTable } from "../../../components/table/main.styles";
import { StyledButton } from "../../../components/button/main.styles";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import Modal from "./modal.jsx";
import {
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import Swal from "sweetalert2";
import { Link, useLocation, useHistory } from "react-router-dom";
import { roles } from "../../../utils/constants.js";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
let columnFilters = {};
let excelData = [];

const Index = (props) => {
  const { height, width } = useWindowDimensions();
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
      try {
        const status = await axios.get(baseUrl + "/getIptEndpointsFetchStatus");
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
        setUser(JSON.parse(localStorage.getItem("user")));
        let filter = searchParams.get("filter");
        let res = null;
        if (filter) {
          let query = `?filter=${filter}`;
          res = await axios.get(baseUrl + "/getIptEndpoints" + query);
        } else {
          res = await axios.get(baseUrl + "/getAllIPTEndpoints");
        }
        excelData = res?.data;
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
    XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
    XLSX.writeFile(wb, "iptEndpoints.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    // await axios
    //   .get(baseUrl + "/exportIPTEndpoints ")
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
    setExportLoading(false);
  };

  let seedTemp = [
    {
      edn_cdp_legacy_id: "",
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
      device_a_port_desc: "",
      device_a_vlan: "",
      creation_date: "",
      modification_date: "",
    },
  ];

  const fetch = async () => {
    setFetchLoading("true");
    setFetchDate(new Date().toLocaleString());
    setBackgroundColor("red");
    await axios
      .get(baseUrl + "/fetchIPTEndpoints")
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
    setIsModalVisible(true);
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
      width: "1%",

      render: (text, record) => (
        <a disabled={user?.user_role === roles.user}>
          <EditOutlined
            style={{ paddingLeft: "30%" }}
            onClick={() => {
              if (user?.user_role !== roles.user) {
                edit(record);
              }
            }}
          />
        </a>
      ),
    },
    {
      dataIndex: "hostname",
      key: "hostname",
      // ...getColumnSearchProps("edn_cdp_legacy_id"),
      ...getColumnSearchProps(
        "hostname",
        "Host Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.edn_cdp_legacy_id.length - b.edn_cdp_legacy_id.length,
      // sortOrder:
      //   sortedInfo.columnKey === "edn_cdp_legacy_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "ip_address",
      key: "ip_address",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "ip_address",
        "IP Address",
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
      dataIndex: "mac_address",
      key: "mac_address",
      // ...getColumnSearchProps("device_a_interface"),
      ...getColumnSearchProps(
        "mac_address",
        "MAC Address",
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
      dataIndex: "serial_number",
      key: "serial_number",
      // ...getColumnSearchProps("device_a_trunk_name"),
      ...getColumnSearchProps(
        "serial_number",
        "Serial Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "rfs_date",
      key: "rfs_date",
      // ...getColumnSearchProps("device_a_trunk_name"),
      ...getColumnSearchProps(
        "rfs_date",
        "RFS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "tag_id",
      key: "tag_id",
      // ...getColumnSearchProps("device_a_trunk_name"),
      ...getColumnSearchProps(
        "tag_id",
        "Tag Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "user",
      key: "user",
      // ...getColumnSearchProps("device_a_trunk_name"),
      ...getColumnSearchProps(
        "user",
        "User",
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
      dataIndex: "product_id",
      key: "product_id",
      // ...getColumnSearchProps("device_a_ip"),
      ...getColumnSearchProps(
        "product_id",
        "Product Id",
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
      dataIndex: "description",
      key: "description",
      // ...getColumnSearchProps("device_b_system_name"),
      ...getColumnSearchProps(
        "description",
        "Description",
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
      dataIndex: "firmware",
      key: "firmware",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "firmware",
        "Firmware",
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
      dataIndex: "protocol",
      key: "protocol",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "protocol",
        "Protocol",
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
      dataIndex: "calling_search_space",
      key: "calling_search_space",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "calling_search_space",
        "Calling Search Space",
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
      dataIndex: "device_pool_name",
      key: "device_pool_name",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "device_pool_name",
        "Device Pool Name",
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
      dataIndex: "location_name",
      key: "location_name",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "location_name",
        "Location Name",
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
      dataIndex: "resource_list_name",
      key: "resource_list_name",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "resource_list_name",
        "Resource List Name",
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
      dataIndex: "extensions",
      key: "extensions",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "extensions",
        "Extensions",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "status",
      key: "status",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "status",
        "Status",
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
    jsonToExcel(dataSource);
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
          IPT Endpoints
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
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div style={{ display: "flex" }}>
            {/* <Spin spinning={fetchLoading === "true" ? true : false}> */}
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
            {/* </Spin> */}
            {/* &nbsp;
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
            )} */}
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
          scroll={{ x: 5000, y: height - 350 }}
          onChange={handleChange}
          // rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="edn_cdp_legacy_id"
          style={{ whiteSpace: "pre" }}
        />
      </Spin>
    </>
  );
};

export default Index;
