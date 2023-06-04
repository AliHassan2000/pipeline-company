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
// import { SEED_API } from "../../../GlobalVar";
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
  const [isFModalVisible, setIsFModalVisible] = useState(false);
  let [fDataSource, setFDataSource] = useState(null);
  const getFailedDevice = async () => {
    let date = new Date();
    let month = date.getMonth() + 1;
    let dateString = `${date.getDate()}-${
      month < 10 ? "0" + month : month
    }-${date.getFullYear()}`;
    console.log(date.getFullYear());
    try {
      await axios
        .post(baseUrl + "/getFailedDevices", { date: dateString })
        .then((res) => {
          setFDataSource(res.data);
          console.log(res);
        })
        .catch((err) => {
          console.log(err);
        });
    } catch (err) {
      console.log(err);
    }
  };

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
        await axios.get(baseUrl + "/getAllF5Dates").then((response) => {
          setDates(response.data);
          console.log(response);
        });

        const status = await axios.get(baseUrl + "/getF5FetchStatus");
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

        const res = await axios.get(baseUrl + "/getAllF5");
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
    XLSX.utils.book_append_sheet(wb, binarySeedData, "f5");
    XLSX.writeFile(wb, "f5.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
    // await axios
    //   .get(baseUrl + "/exportEdnLldpLegacy")
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
      edn_lldp_legacy_id: "",
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
      device_a_vlan_name: "",
      creation_date: "",
      modification_date: "",
    },
  ];

  const fetch = async () => {
    setFetchLoading("true");
    setFetchDate(new Date().toLocaleString());
    setBackgroundColor("red");
    await axios
      .get(baseUrl + "/fetchF5")
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
      dataIndex: "site_id",
      key: "site_id",
      ...getColumnSearchProps(
        "site_id",
        "Site Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
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
      ellipsis: true,
    },
    {
      dataIndex: "ip_address",
      key: "ip_address",
      ...getColumnSearchProps(
        "ip_address",
        "Ip Address",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "vserver_name",
      key: "vserver_name",
      ...getColumnSearchProps(
        "vserver_name",
        "Vserver Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "vip",
      key: "vip",
      ...getColumnSearchProps(
        "vip",
        "VIP",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "description",
      key: "description",
      ...getColumnSearchProps(
        "description",
        "Description",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "pool_name",
      key: "pool_name",
      ...getColumnSearchProps(
        "pool_name",
        "Pool Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "monitor_name",
      key: "monitor_name",
      ...getColumnSearchProps(
        "monitor_name",
        "Monitor Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "monitor_value",
      key: "monitor_value",
      ...getColumnSearchProps(
        "monitor_value",
        "Monitor Value",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "ssl_profile",
      key: "ssl_profile",
      ...getColumnSearchProps(
        "ssl_profile",
        "SSL Profile",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "pool_member",
      key: "pool_member",
      ...getColumnSearchProps(
        "pool_member",
        "Pool Member",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "node",
      key: "node",
      ...getColumnSearchProps(
        "node",
        "Node",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "service_port",
      key: "service_port",
      ...getColumnSearchProps(
        "service_port",
        "Service Port",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "monitor_status",
      key: "monitor_status",
      ...getColumnSearchProps(
        "monitor_status",
        "Monitor status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "lb_method",
      key: "lb_method",
      ...getColumnSearchProps(
        "lb_method",
        "LB Method",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
      .post(baseUrl + "/getAllF5ByDate", { date: value })
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
          F5
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
          <div>
            Select Date: &nbsp;&nbsp;
            <Select
              defaultValue={dates ? dates[0] : null}
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
          <div style={{ display: "flex" }}>
            {/* <StyledButton
              color={"#bb0a1e"}
              onClick={() => {
                getFailedDevice();
                setIsFModalVisible(true);
              }}
              disabled={user?.user_role === roles.user}
            >
              <RightSquareOutlined /> &nbsp; Show Failed devices
            </StyledButton> */}
            &nbsp;&nbsp;
            <Spin spinning={exportLoading}>
              <Dropdown overlay={menu} trigger={["click"]}>
                <StyledButton color={"#3bbdc2"}>
                  Export
                  <DownOutlined />
                </StyledButton>
              </Dropdown>
            </Spin>
          </div>
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
          scroll={{ x: 3500, y: height - 350 }}
          onChange={handleChange}
          // rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="f5_id"
          style={{ whiteSpace: "pre" }}
        />
      </Spin>
    </>
  );
};

export default Index;
