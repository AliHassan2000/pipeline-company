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
        // await axios.get(baseUrl + "/getAllIgwServiceDates").then((response) => {
        //   setDates(response.data);
        //   console.log(response);
        // });

        const res = await axios.get(baseUrl + "/getAllIgwServices");
        excelData = res.data;
        // console.log("papi");
        // console.log(res);
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
    XLSX.utils.book_append_sheet(wb, binarySeedData, "igwservices");
    XLSX.writeFile(wb, "igwservices.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);

    // await axios
    //   .get(baseUrl + "/exportEdnSystem")
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

  let seedTemp = [
    {
      device_a_name: "",
      device_a_interface: "",
      device_b_ip: "",
      device_b_mac: "",
      device_b_system_name: "",
      device_b_type: "",
      server_name: "",
      server_os: "",
      app_name: "",
      owner_name: "",
      owner_email: "",
      owner_contact: "",
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
      .post(baseUrl + "/addIgwServices", seed)
      .then((response) => {
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/getAllIgwServices")
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
    inputRef.current.addEventListener("input", importExcel);
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

    // {
    //   title: "EDN MPLS Id",
    //   dataIndex: "edn_mlps_id",
    //   key: "edn_mlps_id",
    //   ...getColumnSearchProps("edn_mlps_id"),
    //   render: (text, record) => (
    //     <a
    //       onClick={() => {
    //         showSeedDev(record);
    //       }}
    //     >
    //       {text}
    //     </a>
    //   ),
    //   sorter: (a, b) => a.edn_mlps_id.length - b.edn_mlps_id.length,
    //   sortOrder: sortedInfo.columnKey === "edn_mlps_id" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      dataIndex: "igw_service_mapping_id",
      key: "igw_service_mapping_id",
      // ...getColumnSearchProps("edn_system_id"),
      ...getColumnSearchProps(
        "igw_service_mapping_id",
        "Igw Service Mapping Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.edn_system_id.length - b.edn_system_id.length,
      // sortOrder: sortedInfo.columnKey === "edn_system_id" && sortedInfo.order,
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
      dataIndex: "server_name",
      key: "server_name",
      // ...getColumnSearchProps("device_a_ip"),
      ...getColumnSearchProps(
        "server_name",
        "Server Name",
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
      dataIndex: "owner_name",
      key: "owner_name",
      // ...getColumnSearchProps("device_a_ip"),
      ...getColumnSearchProps(
        "owner_name",
        "Owner Name",
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
      dataIndex: "owner_email",
      key: "owner_email",
      // ...getColumnSearchProps("device_a_ip"),
      ...getColumnSearchProps(
        "owner_email",
        "Owner Email",
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
      dataIndex: "owner_contact",
      key: "owner_contact",
      // ...getColumnSearchProps("device_b_interface"),
      ...getColumnSearchProps(
        "owner_contact",
        "Owner Contact",
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
  ];

  const handleDelete = () => {
    if (selectedRowKeys.length > 0) {
      axios
        .post(baseUrl + "/deleteIgwServiceDevice", {
          ips: selectedRowKeys,
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllIgwServices")
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
      .post(baseUrl + "/getAllIgwServicebyDate", { date: value })
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
          IGW Services
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
          {/* <div>
            Select Date: &nbsp;&nbsp;
            <Select
              defaultValue={dates ? dates[0] : null}
              style={{ width: 200 }}
              onChange={handleSelectChange}
              disabled={user?.user_role === roles.user}
            >
              {getOptions(dates)}
            </Select>
          </div> */}
          <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; Add Record
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
            <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
              <RightSquareOutlined /> &nbsp; Delete
            </StyledButton>
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
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          size="small"
          scroll={{ x: 4000, y: height - 350 }}
          onChange={handleChange}
          rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="igw_service_mapping_id"
          style={{ whiteSpace: "pre" }}
        />
      </Spin>
    </>
  );
};

export default Index;
