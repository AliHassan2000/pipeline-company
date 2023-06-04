import React, { useState, useRef, useEffect, useContext } from "react";
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
// import Modal from "./modal";
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
// import ShowSeedDevice from "./ShowSeedDevice";
import { Context } from "../../../context";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { roles } from "../../../utils/constants.js";
import Modal from "./modal";

let columnFilters = {};
let excelData = [];

const Index = (props) => {
  const { height, width } = useWindowDimensions();
  // const { excelData, setExcelData, pnCodeStats, getPnCodeStats } =
  //   useContext(Context);
  const { Option } = Select;
  const [user, setUser] = useState();
  let [exportLoading, setExportLoading] = useState(false);
  let [fetchLoading, setFetchLoading] = useState(false);
  let [loading, setLoading] = useState(false);
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
  const [isImportModalVisible, setIsImportModalVisible] = useState(false);
  const inputRef = useRef(null);
  const history = useHistory();
  const [showSeed, setShowSeed] = useState(false);
  const [seedRecord, setSeedRecord] = useState(null);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  const [date, setDate] = useState("");
  const [dates, setDates] = useState([]);

  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );

  const handleSelectChange = async (value) => {
    setLoading(true);
    setDate(value);
    await axios
      .post(baseUrl + "/getPnCodeByDate", { date: value })
      .then((response) => {
        // setExcelData(response.data);
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
        await axios.get(baseUrl + "/getAllPNCodeDates").then((response) => {
          setDates(response.data);
          console.log(response);
        });

        //   if (pnCodeStats.length === 0) {
        //     let data = await getPnCodeStats();
        //     console.log(data);
        //     setRowCount(data.length);
        //     setDataSource(data);
        //   } else {
        //     setRowCount(pnCodeStats.length);
        //     setDataSource(pnCodeStats);
        //   }
        //   setLoading(false);
        // } catch (err) {
        //   console.log(err);
        //   setLoading(false);
        // }

        const res = await axios.get(baseUrl + "/getPNCodeStatsPerCiscoDomain");
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
    XLSX.writeFile(wb, "pncodestats.xlsx");
    setExportLoading(false);
  };

  const fetch = async () => {
    setFetchLoading(true);
    await axios
      .get(baseUrl + "/fetchPnCodeSnap")
      .then((response) => {
        setFetchLoading(false);
      })
      .catch((err) => {
        console.log(err);
        setFetchLoading(false);
      });
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);

    // await axios
    //   .get(baseUrl + "/exportPNCodeStats")
    //   .then((response) => {
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
      // pn_code: "",
      "IGW-SYS": "",
      "IGW-NET": "",
      "EDN-SYS": "",
      "EDN-NET": "",
      "EDN-IPT": "",
      "EDN-IPT-Endpoints": "",
      SOC: "",
      CDN: "",
      POS: "",
      REBD: "",
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

  const postSeed = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/addSeed", seed)
      .then((response) => {
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/getSeeds")
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

  const getOptions = (dates = []) => {
    let options = [];
    dates.forEach((date) => {
      options.push(<Option value={date}>{date}</Option>);
    });
    return options;
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

  //   useEffect(() => {
  //     inputRef.current.addEventListener("input", importExcel);
  //   }, []);

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
    // {
    //   title: "",
    //   key: "edit",
    //   width: "0.3%",

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
      title: "PN Code",
      dataIndex: "pn_code",
      key: "pn_code",
      // ...getColumnSearchProps("ne_ip_address"),
      ...getColumnSearchProps(
        "pn_code",
        "PN Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.ne_ip_address.length - b.ne_ip_address.length,
      // sortOrder: sortedInfo.columnKey === "ne_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "IGW System",
      dataIndex: "IGW-SYS",
      key: "IGW-SYS",
      ...getColumnSearchProps(
        "IGW-SYS",
        "IGW System",
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
      title: "IGW NET",
      dataIndex: "IGW-NET",
      key: "IGW-NET",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "IGW-NET",
        "IGW NET",
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
      title: "EDN System",
      dataIndex: "EDN-SYS",
      key: "EDN-SYS",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "EDN-SYS",
        "EDN System",
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
      title: "EDN NET",
      dataIndex: "EDN-NET",
      key: "EDN-NET",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "EDN-NET",
        "EDN NET",
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
      title: "EDN IPT",
      dataIndex: "EDN-IPT",
      key: "EDN-IPT",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "EDN-IPT",
        "EDN IPT",
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
      title: "EDN IPT Endpoints",
      dataIndex: "EDN-IPT-Endpoints",
      key: "EDN-IPT-Endpoints",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "EDN-IPT-Endpoints",
        "EDN IPT Endpoints",
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
      title: "SOC",
      dataIndex: "SOC",
      key: "SOC",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "SOC",
        "SOC",
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
      title: "CDN",
      dataIndex: "CDN",
      key: "CDN",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "CDN",
        "CDN",
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
      title: "POS",
      dataIndex: "POS",
      key: "POS",

      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "POS",
        "POS",
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
      title: "REBD",
      dataIndex: "REBD",
      key: "REBD",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "REBD",
        "REBD",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_id.length - b.site_id.length,
      // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
  ];

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

  const handleDeleteFetchByDate = () => {
    if (date !== "") {
      axios
        .post(baseUrl + "/deleteFetchesByDate", {
          name: "PN Code Stats",
          date,
        })
        .then(() => {})
        .catch((err) => {
          console.log(err);
          setLoading(false);
        });
    } else {
      alert("Please select a date before deleting it's fetch");
    }
  };

  const deleteFetch = () => {
    Swal.fire({
      title: "Are you sure?",
      text: `You will not be able to recover this Fetch at "${date}"!`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "No, cancel!",
      reverseButtons: true,
    }).then((result) => {
      if (result.dismiss === Swal.DismissReason.cancel) {
        // User clicked the cancel button
        // Swal.fire("Cancelled", "Your item is safe :)", "error");
      } else {
        handleDeleteFetchByDate();
      }
    });
  };

  return (
    <>
      <Spin tip="Loading..." spinning={loading}>
        {/* <ShowSeedDevice
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
            editRecord={editRecord}
          />
        )} */}

        {isImportModalVisible && (
          <Modal
            isModalVisible={isImportModalVisible}
            setIsModalVisible={setIsImportModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            setRowCount={setRowCount}
            setLoading={setLoading}
            excelData={excelData}
          />
        )}

        <StyledHeading>
          PN Code Stats
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
            marginTop: "0px",
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <Search searchValue={searchValue} handleSeedInput={handleSeedInput} />
          {/* <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; Add Device
          </StyledButton> */}
          <div style={{ display: "flex" }}>
            Select Date: &nbsp;&nbsp;
            <Select
              defaultValue={dates ? dates[0] : null}
              style={{ width: 200 }}
              onChange={handleSelectChange}
              disabled={user?.user_role === roles.user}
            >
              {getOptions(dates)}
            </Select>
            &nbsp;
            <div>
              <StyledButton onClick={deleteFetch} color={"#bb0a1e"}>
                <RightSquareOutlined /> &nbsp; Delete Fetch
              </StyledButton>
            </div>
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
            <Spin spinning={fetchLoading}>
              <StyledButton
                color={"#3bbdc2"}
                onClick={fetch}
                disabled={user?.user_role !== roles.admin}
              >
                <RightSquareOutlined /> &nbsp; Fetch
              </StyledButton>
            </Spin>
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
            <StyledButton
              color={"#3bbdc2"}
              onClick={() => {
                setIsImportModalVisible(true);
              }}
            >
              <RightSquareOutlined /> &nbsp; Import
            </StyledButton>
          </div>
        </div>
        <StyledTable
          size="small"
          scroll={{ x: 1800, y: height - 350 }}
          onChange={handleChange}
          rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="pn_code"
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
