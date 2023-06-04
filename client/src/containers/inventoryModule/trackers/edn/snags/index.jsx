import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import { Table, Button, notification, Spin, Modal, Menu, Dropdown } from "antd";
import Search from "../../../../../components/search";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../../../utils/axios";
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
import { StyledHeading } from "../../../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../../../components/input/main.styles";
import { StyledButton } from "../../../../../components/button/main.styles";
import Swal from "sweetalert2";
// import SnagForm from "./addSnagModal";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [dataSource, setDataSource] = useState(excelData);
  let [showDev, setShowDev] = useState(false);
  let [deviceData, setDeviceData] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  let [editRecord, setEditRecord] = useState(null);
  let [searchSecValue, setSearchSecValue] = useState(null);
  let [searchNeValue, setSearchNeValue] = useState(null);
  let [inputNEValue, setInputNeValue] = useState("");
  let [inputSecValue, setInputSecValue] = useState("");
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  //   const inputNe = useRef(null);
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

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      try {
        const res = await axios.get(baseUrl + "/snags");
        excelData = res.data;
        setDataSource(excelData);
        // setDataSource([{}]);
        setRowCount(excelData.length);
        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter);
    setRowCount(extra.currentDataSource.length);
    setSortedInfo(sorter);
  };

  const clearAll = () => {
    setDataSource(excelData);
    setSortedInfo(null);
  };

  const handleNeInput = (e) => {
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

  const postNe = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/ednHandoverTracker", seed)
      .then((response) => {
        if (response?.response?.status == 500) {
          openSweetAlert(response?.response?.data?.response, "error");
        } else {
          openSweetAlert("Items Added/Updated Successfully", "success");
        }
        console.log("rebd post response===>", response);
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/ednHandoverTracker")
            .then((response) => {
              console.log("rebd response===>", response);
              excelData = response.data;
              setDataSource(excelData);
              setRowCount(excelData.length);
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
      console.log(data);
    };
  };

  //   useEffect(() => {
  //     inputNe.current.addEventListener("input", importExcel);
  //   }, []);

  sortedInfo = sortedInfo || {};

  const columns = [
    {
      dataIndex: "ho_ref_id",
      key: "ho_ref_id",
      ...getColumnSearchProps(
        "ho_ref_id",
        "Ho Ref Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "device_name",
      key: "device_name",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "device_name",
        "Device Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "snag_name",
      key: "snag_name",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "snag_name",
        "Snag Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "snag_status",
      key: "snag_status",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "snag_status",
        "Snag Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "snag_criticality",
      key: "snag_criticality",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "snag_criticality",
        "Snag Criticality",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "reported_date",
      key: "reported_date",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "reported_date",
        "Reported Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "closure_date",
      key: "closure_date",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "closure_date",
        "Closure Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "snag_closure_date",
      key: "snag_closure_date",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "snag_closure_date",
        "Snag Closure Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
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
        .delete(baseUrl + "/ednHandoverTracker", {
          data: {
            ips: selectedRowKeys,
          },
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/ednHandoverTracker")
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
      openSweetAlert("No item is selected to delete.", "danger");
    }
  };

  let seedTemp = [
    {
      ip_address: "", //Not Null
      device_id: "", //drop down (Completed/Pending)
      assigned_to: "", //drop down from endpoint "/getAssignees"
      region: "",
      project_type: "", //Not Null
      site_type: "",
      asset_type: "", //Not Null
      pid: "", //drop down (Yes/No)
      serial_number: "",
      handover_submisson_date: "",
      handover_completion_date: "", //Not Null
      handover_review_status: "",
      remedy_incident: "", //Not Null
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
    XLSX.utils.book_append_sheet(wb, binarySeedData, "snaglist");
    XLSX.writeFile(wb, "snaglist.xlsx");
    setExportLoading(false);
  };

  const exportTemplate = async () => {
    jsonToExcel(seedTemp);
    openNotification();
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
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
    <Spin tip="Loading..." spinning={loading}>
      <>
        <StyledHeading>
          Snag List
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
          {/* <StyledButton onClick={showModal} color={"#009BDB"}>
                  <PlusOutlined /> &nbsp; Add New Snag
                </StyledButton> */}
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <div></div>
          {/* <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
            <RightSquareOutlined /> &nbsp; Delete
          </StyledButton> */}
          <div style={{ display: "flex" }}>
            {/* <StyledButton onClick={showModal} color={"#009BDB"}>
              <PlusOutlined /> &nbsp; Add New Snag
            </StyledButton>
            &nbsp; */}
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
        <Table
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          size="small"
          scroll={{ x: 2000, y: height - 350 }}
          onChange={handleChange}
          //   rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="handover_tracker_id"
        />
      </>
    </Spin>
  );
};

export default Index;
