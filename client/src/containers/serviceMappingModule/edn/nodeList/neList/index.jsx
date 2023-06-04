import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import { Table, Button, notification, Spin, Menu, Dropdown } from "antd";
import Search from "../../../../../components/search";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../../../utils/axios";
// import axios from "axios";
import {
  PlusOutlined,
  ReloadOutlined,
  RightSquareOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import { useHistory } from "react-router-dom";
import { columnSearch } from "../../../../../utils";
import useWindowDimensions from "../../../../../hooks/useWindowDimensions";
// import { SEED_API } from "../../../GlobalVar";
// import ShowDevice from "../../../../seed/ShowSeedDevice";
import { StyledHeading } from "../../../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../../../components/input/main.styles";
import { StyledButton } from "../../../../../components/button/main.styles";
import Modal from "./modal";
import Swal from "sweetalert2";
let columnFilters = {};
let neData = [];

const Index = (props) => {
  const { height, width } = useWindowDimensions();
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [dataSource, setDataSource] = useState(neData);
  let [showDev, setShowDev] = useState(false);
  let [deviceData, setDeviceData] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  let [editRecord, setEditRecord] = useState(null);
  let [searchSecValue, setSearchSecValue] = useState(null);
  let [searchNeValue, setSearchNeValue] = useState(null);
  let [inputNEValue, setInputNeValue] = useState("");
  let [inputSecValue, setInputSecValue] = useState("");
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const inputNe = useRef(null);
  const history = useHistory();
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };

  const edit = (record) => {
    setEditRecord(record);
    showEditModal();
  };

  const showEditModal = () => {
    setIsModalVisible(true);
  };

  const opensweetalertdanger = () => {
    Swal.fire({
      title: "NO Device Data Found!",
      // text: "OOPS",
      type: "warning",
    });
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      try {
        const neRes = await axios.get(baseUrl + "/getAllNeIps");
        neData = neRes.data;
        setDataSource(neData);
        setRowCount(neData.length);
        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const showDeviceData = async (device_ip, device_type) => {
    await axios
      .post(baseUrl + "/showEDNInventoryData", {
        ip: device_ip,
        type: device_type,
      })
      .then((res) => {
        if ("msg" in res.data) {
          opensweetalertdanger();
          // alert("NO Device Data Found");
        } else {
          setDeviceData(res.data);
          setShowDev(true);
          console.log("device data===>", res.data);
        }
      })
      .catch((er) => {
        console.log("error", er);
      });
  };

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter);
    setRowCount(extra.currentDataSource.length);
    setSortedInfo(sorter);
  };

  const clearAll = () => {
    setDataSource(neData);
    setSortedInfo(null);
  };

  const handleNeInput = (e) => {
    let filteredSuggestions = neData.filter(
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

  const postNe = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/addNetSeed", seed)
      .then((response) => {
        console.log("Ne post response===>", response);
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/getAllNeIps")
            .then((response) => {
              console.log("Ne response===>", response);
              neData = response.data;
              setDataSource(neData);
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

  const importNe = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    let data = null;
    reader.readAsBinaryString(file);
    reader.onload = (e) => {
      const bstr = e.target.result;
      const workbook = XLSX.read(bstr, { type: "binary" });
      const workSheetName = workbook.SheetNames[0];
      const workSheet = workbook.Sheets[workSheetName];
      const fileData = XLSX.utils.sheet_to_json(workSheet, { header: 1 });
      const headers = fileData[0];
      const heads = headers.map((head) => ({ title: head, field: head }));
      fileData.splice(0, 1);
      data = convertToJson(headers, fileData);
      postNe(data);
    };
  };

  useEffect(() => {
    inputNe.current.addEventListener("input", importNe);
  }, []);

  sortedInfo = sortedInfo || {};

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
      title: "Switch IP-Address",
      dataIndex: "switch_ip_address",
      key: "switch_ip_address",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "switch_ip_address",
        "Switch IP-Address",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Switch Id",
      dataIndex: "switch_id",
      key: "switch_id",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "switch_id",
        "Switch Id",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Region",
      dataIndex: "region",
      key: "region",
      // ...getColumnSearchProps("region"),
      ...getColumnSearchProps(
        "region",
        "Region",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.localeCompare(b.region),
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Segment",
      dataIndex: "segment",
      key: "segment",
      // ...getColumnSearchProps("segment"),
      ...getColumnSearchProps(
        "segment",
        "Segment",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.segment.localeCompare(b.segment),
      // sortOrder: sortedInfo.columnKey === "segment" && sortedInfo.order,
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
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.vendor.localeCompare(b.vendor),
      // sortOrder: sortedInfo.columnKey === "vendor" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "OS Type",
      dataIndex: "os_type",
      key: "os_type",
      // ...getColumnSearchProps("os_type"),
      ...getColumnSearchProps(
        "os_type",
        "OS Type",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.os_type.localeCompare(b.os_type),
      // sortOrder: sortedInfo.columnKey === "os_type" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "",
    //   key: "edit",
    //   width: "10%",
    //   render: (text, record) => (
    //     <StyledButton
    //       color={"#009BDB"}
    //       style={{ width: "90%" }}
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
    //   width: "10%",
    //   render: (text, record) => (
    //     <StyledButton
    //       color={"#009BDB"}
    //       style={{ width: "90%" }}
    //       onClick={() => {
    //         showDeviceData(record.switch_ip_address, "Ne");
    //       }}
    //     >
    //       show
    //     </StyledButton>
    //   ),
    // },
  ];

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
  };

  const handleDelete = () => {
    if (selectedRowKeys.length > 0) {
      axios
        .post(baseUrl + "/deleteEdnNetSeed", {
          ips: selectedRowKeys,
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllNeIps")
              .then((response) => {
                console.log(response.data);
                setDataSource(response.data);
                neData = response.data;
                setRowCount(neData.length);
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

  let seedTemp = [
    {
      switch_ip_address: "",
      switch_id: "",
      region: "",
      segment: "",
      vendor: "",
      os_type: "",
    },
  ];

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
    XLSX.utils.book_append_sheet(wb, binarySeedData, "ednnelist");
    XLSX.writeFile(wb, "ednnelist.xlsx");
    setExportLoading(false);
  };

  const exportTemplate = async () => {
    jsonToExcel(seedTemp);
    openNotification();
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(neData);
    setExportLoading(false);
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
        {/* {showDev ? (
          <ShowDevice
            showSeed={showDev}
            setShowSeed={setShowDev}
            seedRecord={deviceData}
          />
        ) : null} */}

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
          EDN NE List
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
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <Search searchValue={searchNeValue} handleSeedInput={handleNeInput} />
          <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; ADD DEVICE
          </StyledButton>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
            <RightSquareOutlined /> &nbsp; Delete
          </StyledButton>
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
            <StyledImportFileInput
              type="file"
              value={inputNEValue}
              onChange={() => importNe}
              ref={inputNe}
            />
          </div>
        </div>
        <Table
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          size="small"
          scroll={{ x: 1500, y: height - 350 }}
          onChange={handleChange}
          rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="switch_ip_address"
        />
      </Spin>
    </>
  );
};

export default Index;
